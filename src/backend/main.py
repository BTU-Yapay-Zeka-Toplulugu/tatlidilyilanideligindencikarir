"""FastAPI web backend uygulaması; katmanlı mimari ile uç noktaları toplar."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.api.routes.campaigns import router as campaigns_router
from src.backend.api.routes.compare import router as compare_router
from src.backend.core.database import ensure_schema, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü: başlangıçta şemayı garanti eder."""
    ensure_schema()
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


@app.get("/")
def read_root():
    """API durumu ve karşılama mesajını döner."""
    return {"status": "ok", "message": "Katılım Bankası API Servisi Çalışıyor"}
