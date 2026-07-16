"""İnce (thin) karşılaştırma API uç noktası."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.backend.core.database import get_db
from src.backend.repositories.campaign_repository import CampaignRepository
from src.backend.schemas import CompareResponse
from src.backend.services.campaign_service import CampaignService
from src.backend.services.comparison_service import ComparisonService

router = APIRouter(prefix="/api", tags=["compare"])


def _comparison_service(db: Session = Depends(get_db)) -> ComparisonService:
    """ComparisonService örneğini bağımlılıklarıyla enjekte eder (DI)."""
    repository = CampaignRepository(db)
    campaign_service = CampaignService(repository)
    return ComparisonService(campaign_service, repository)


@router.get("/compare", response_model=list[CompareResponse])
def compare_campaigns(
    term_months: int | None = Query(None, description="Vade filtresi (Ay)"),
    amount: float | None = Query(None, description="Yatırım tutarı filtresi (TL)"),
    service: ComparisonService = Depends(_comparison_service),
):
    """Mevduat/katılma hesabı kampanyalarını kâr payı oranına göre karşılaştırır."""
    return service.compare(term_months=term_months, amount=amount)
