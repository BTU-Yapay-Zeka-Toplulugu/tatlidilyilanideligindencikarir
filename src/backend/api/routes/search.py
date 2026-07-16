"""Kampanya benzerlik araması (RAG vektör arama) servisi ve uç noktası."""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.backend.core.database import get_db
from src.backend.core.vector_store import VectorStore, VectorStoreFactory
from src.backend.repositories.campaign_repository import CampaignRepository
from src.backend.services.campaign_service import CampaignService

router = APIRouter(prefix="/api", tags=["search"])

# Uygulama ömrü boyunca tek bir vektör deposu (basit singleton).
_STORE: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Vektör deposunu (yoksa bellek içi olarak) döner."""
    global _STORE
    if _STORE is None:
        _STORE = VectorStoreFactory.create(kind="memory")
    return _STORE


def _campaign_service(db: Session = Depends(get_db)) -> CampaignService:
    """CampaignService örneğini enjekte eder (DI)."""
    return CampaignService(CampaignRepository(db))


@router.post("/search/index", status_code=200)
def index_campaigns(
    db: Session = Depends(get_db),
    store: VectorStore = Depends(get_vector_store),
    service: CampaignService = Depends(_campaign_service),
):
    """Tüm kampanya metinlerini vektör deposuna indeksler."""
    campaigns = service.list_campaigns()
    if not campaigns:
        return {"indexed": 0}
    ids = [f"campaign-{c.id}" for c in campaigns]
    texts = [c.raw_text for c in campaigns]
    metadatas = [
        {"bank_id": c.bank_id, "source_url": c.source_url, "title": c.page_title}
        for c in campaigns
    ]
    store.add(ids, texts, metadatas)
    return {"indexed": len(ids)}


@router.get("/search", response_model=list[dict[str, Any]])
def search_campaigns(
    query: str = Query(..., description="Benzerlik araması yapılacak metin"),
    top_k: int = Query(5, description="Dönecek en benzer kayıt sayısı"),
    store: VectorStore = Depends(get_vector_store),
):
    """Metne en benzer kampanyaları vektör benzerliği ile döner."""
    return store.query(query, top_k=top_k)
