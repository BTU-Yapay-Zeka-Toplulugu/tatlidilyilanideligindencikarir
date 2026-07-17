"""FastAPI web backend uygulaması; katmanlı mimari ile uç noktaları toplar."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.api.routes.campaigns import router as campaigns_router
from src.backend.api.routes.chat import router as chat_router
from src.backend.api.routes.compare import router as compare_router
from src.backend.api.routes.frontend_bridge import router as frontend_bridge_router
from src.backend.api.routes.search import router as search_router
from src.backend.core.database import ensure_schema, get_db
from src.backend.core.llm_factory import LLMClientFactory
from src.backend.core.vector_store import get_vector_store
from src.backend.services.campaign_service import CampaignService
from src.backend.services.chatbot_service import ChatbotService
from src.backend.repositories.campaign_repository import CampaignRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü: şema, vektör indeksi ve chatbot servisini hazırlar."""
    ensure_schema()
    # Chatbot servisini (ve 2GB GGUF modelini) uygulama ömrü boyunca tek sefer yükler.
    llm = LLMClientFactory.main_responser()
    app.state.chatbot = ChatbotService(vector_store=get_vector_store(), llm=llm)
    # Vektör araması için kampanyaları indeksle.
    db = next(get_db())
    try:
        repository = CampaignRepository(db)
        service = CampaignService(repository)
        for campaign in service.list_campaigns():
            service.ensure_nlp_processed(campaign)
        store = get_vector_store()
        campaigns = service.list_campaigns()
        if campaigns:
            store.add(
                [f"campaign-{c.id}" for c in campaigns],
                [c.raw_text for c in campaigns],
                [
                    {
                        "bank_id": c.bank_id,
                        "bank_name": repository.get_bank_name(c.bank_id),
                        "source_url": c.source_url,
                        "title": c.page_title,
                    }
                    for c in campaigns
                ],
            )
    finally:
        db.close()
    yield


app = FastAPI(
    title="Katılım Bankası Kampanya Analiz API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS yapılandırması (frontend/dashboard erişimi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaigns_router)
app.include_router(compare_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(frontend_bridge_router)


@app.get("/")
def read_root():
    """API durumu ve karşılama mesajını döner."""
    return {"status": "ok", "message": "Katılım Bankası API Servisi Çalışıyor"}
