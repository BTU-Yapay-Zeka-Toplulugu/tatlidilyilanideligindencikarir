"""Frontend (React/Vite) sözleşmesine uyan köprü uç noktaları.

Mevcut /api/* uç noktaları korunur; bu modül frontend'in beklediği
Türkçe alan adlı response'ları ve chatbot REST + WebSocket akışını sunar.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query, Request, WebSocket
from fastapi.concurrency import run_in_threadpool
from fastapi.websockets import WebSocketDisconnect

from src.backend.core.database import get_db
from src.backend.core.vector_store import get_vector_store
from src.backend.repositories.campaign_repository import CampaignRepository
from src.backend.schemas import (
    Atif,
    BankaKalemi,
    ChatYaniti,
    FinansmanKalemi,
    Mesaj,
)
from src.backend.services.campaign_service import CampaignService
from src.backend.services.chatbot_service import ChatbotService

router = APIRouter(tags=["frontend-bridge"])

logger = logging.getLogger("frontend_bridge")

_chat_history: dict[str, list[dict[str, Any]]] = {}


def _get_chatbot(request: Request) -> ChatbotService:
    """Chatbot servisini döner; yoksa (lifespan dışı) tembel olarak oluşturur."""
    chatbot = getattr(request.app.state, "chatbot", None)
    if chatbot is None:
        chatbot = ChatbotService(vector_store=get_vector_store())
        request.app.state.chatbot = chatbot
    return chatbot


def _now_iso() -> str:
    """Geçerli UTC zamanı ISO 8601 formatında döner."""
    return datetime.now(timezone.utc).isoformat()


def _bank_adi(service: CampaignService, bank_id: int) -> str:
    """Kampanyanın bağlı olduğu banka adını döner."""
    bank = service.get_bank(bank_id)
    return bank.name if bank else "Bilinmeyen Banka"


def _to_finansman_kalemi(campaign: Any, detail: Any, bank_name: str) -> FinansmanKalemi:
    """ORM kampanya+detay kaydını frontend FinansmanKalemi'ne dönüştürür."""
    tutar = detail.max_amount if detail.max_amount is not None else detail.min_amount
    return FinansmanKalemi(
        id=str(campaign.id),
        bankaAdi=bank_name,
        urunAdi=campaign.page_title or "Kampanya",
        tutar=float(tutar or 0.0),
        karOrani=float(detail.profit_share_rate or 0.0),
        vade=str(detail.term_months) if detail.term_months is not None else "—",
        tarih=campaign.scraped_at.isoformat() if campaign.scraped_at else _now_iso(),
    )


def _campaign_service(db: Any = Depends(get_db)) -> CampaignService:
    """CampaignService örneğini repository ile enjekte eder (DI)."""
    return CampaignService(CampaignRepository(db))


@router.get("/finansman/ozet", response_model=list[FinansmanKalemi])
def finansman_ozeti(service: CampaignService = Depends(_campaign_service)):
    """Tüm kampanyaların finansman özet kalemlerini döner."""
    items: list[FinansmanKalemi] = []
    for campaign in service.list_campaigns():
        detail = service.ensure_nlp_processed(campaign)
        items.append(
            _to_finansman_kalemi(campaign, detail, _bank_adi(service, campaign.bank_id))
        )
    return items


@router.get("/finansman/karsilastirma", response_model=list[FinansmanKalemi])
def finansman_karsilastirma(
    banka_ids: list[str] | None = Query(None, alias="bankaIds"),
    urun_turu: str | None = Query(None, alias="urunTuru"),
    service: CampaignService = Depends(_campaign_service),
):
    """Karşılaştırma tablosu ve grafiği için düz FinansmanKalemi listesi döner.

    Frontend (KarsilastirmaTablosu, FinansmanGrafigi, csvExporter, sıralama
    hook'u) veriyi düz `FinansmanKalemi[]` olarak tüketir; her satırda
    doğrudan `tutar`, `karOrani`, `urunAdi`, `vade`, `tarih` alanları beklenir.
    Bu nedenle burada bankaya göre iç içe (nested) gruplama YAPILMAZ; aksi
    halde tablo/tutar/oran alanları boş (—/0) görünür.
    """
    items: list[FinansmanKalemi] = []
    for campaign in service.list_campaigns():
        if banka_ids and str(campaign.bank_id) not in banka_ids:
            continue
        detail = service.ensure_nlp_processed(campaign)
        if urun_turu and (detail.campaign_type or "") != urun_turu:
            continue
        bank_name = _bank_adi(service, campaign.bank_id)
        items.append(_to_finansman_kalemi(campaign, detail, bank_name))
    return items


@router.get("/finansman/bankalar", response_model=list[BankaKalemi])
def finansman_bankalar(service: CampaignService = Depends(_campaign_service)):
    """Frontend filtre seçenekleri için banka listesini döner."""
    return [
        BankaKalemi(id=str(b.id), ad=b.name, logo=None)
        for b in service.list_banks()
    ]


def _atiflari_olustur(sources: list[dict[str, Any]]) -> list[Atif]:
    """RAG kaynaklarını frontend citation formatına dönüştürür."""
    atiflar: list[Atif] = []
    for s in sources:
        meta = s.get("metadata") or {}
        atiflar.append(
            Atif(
                bankaAdi=str(meta.get("bank_name", meta.get("bankaAdi", "Bilinmeyen"))),
                urunAdi=str(meta.get("title", meta.get("urunAdi", "Kampanya"))),
                url=meta.get("source_url") or meta.get("url"),
            )
        )
    return atiflar


@router.post("/chat/mesaj")
def chat_mesaj(payload: dict[str, Any], request: Request):
    """Chatbot'a REST üzerinden mesaj gönderir (streaming olmayan mod)."""
    mesaj = payload.get("mesaj", "")
    oturum_id = payload.get("oturumId") or "oturum-001"
    chatbot: ChatbotService = _get_chatbot(request)
    result = chatbot.answer(mesaj, top_k=3)
    atiflar = _atiflari_olustur(result.get("sources", []))
    bot_mesaji = Mesaj(
        id=f"bot-{datetime.now(timezone.utc).timestamp()}",
        rol="assistant",
        icerik=result.get("answer", ""),
        atiflar=atiflar,
        zaman=_now_iso(),
    )
    _chat_history.setdefault(oturum_id, []).append(
        {
            "id": f"user-{datetime.now(timezone.utc).timestamp()}",
            "rol": "user",
            "icerik": mesaj,
            "atiflar": [],
            "zaman": _now_iso(),
        }
    )
    _chat_history[oturum_id].append(bot_mesaji.model_dump())
    return ChatYaniti(oturumId=oturum_id, mesaj=bot_mesaji)


@router.get("/chat/gecmis")
def chat_gecmis(oturum_id: str | None = Query(None, alias="oturumId")):
    """Bir oturuma ait mesaj geçmişini döner."""
    oturum_id = oturum_id or "oturum-001"
    return _chat_history.get(oturum_id, [])


@router.post("/chat/temizle")
def chat_temizle(payload: dict[str, Any]):
    """Oturum geçmişini temizler."""
    oturum_id = payload.get("oturumId") or "oturum-001"
    _chat_history.pop(oturum_id, None)
    return {"status": "ok", "oturumId": oturum_id}


def _ws_chatbot(websocket: WebSocket) -> ChatbotService:
    """Lifespan'da yüklenmiş (2GB GGUF) chatbot'u yeniden kullanır.

    app.state.chatbot yoksa (ör. testte lifespan çalışmadıysa) tembel olarak
    tek sefer oluşturur ve state'e yazar; böylece her WS bağlantısında modelin
    yeniden yüklenmesi engellenir.
    """
    chatbot = getattr(websocket.app.state, "chatbot", None)
    if chatbot is None:
        chatbot = ChatbotService(vector_store=get_vector_store())
        websocket.app.state.chatbot = chatbot
    return chatbot


@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    """RAG chatbot streaming WebSocket'u (frontend useStreamingResponse ile uyumluluk)."""
    await websocket.accept()
    logger.info("WS /ws/chat bağlantısı açıldı")
    chatbot: ChatbotService = _ws_chatbot(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except Exception:
                data = {"mesaj": raw, "oturumId": "oturum-001"}
            mesaj = data.get("mesaj", "")
            oturum_id = data.get("oturumId") or "oturum-001"
            logger.info("WS mesaj alındı (oturum=%s): %r", oturum_id, mesaj[:120])
            try:
                # LLM çıkarımı bloke edicidir; olay döngüsünü (ve WebSocket
                # keepalive ping'lerini) kilitlememek için thread havuzunda
                # çalıştırılır. Aksi halde uzun süren yanıtlarda bağlantı
                # "keepalive ping timeout" ile düşer.
                result = await run_in_threadpool(chatbot.answer, mesaj, 3)
            except Exception:
                # Sessizce yutma: hatayı logla ve frontend'in askıda kalmaması
                # için 'bitti' göndererek akışı sonlandır.
                logger.exception("WS chatbot.answer başarısız (oturum=%s)", oturum_id)
                await websocket.send_json(
                    {
                        "tur": "chunk",
                        "icerik": "Üzgünüm, yanıt üretilirken bir hata oluştu.",
                    }
                )
                await websocket.send_json({"tur": "atiflar", "atiflar": []})
                await websocket.send_json({"tur": "bitti"})
                continue
            answer = result.get("answer", "")
            logger.info(
                "WS yanıt üretildi (oturum=%s, %d karakter, %d kaynak)",
                oturum_id,
                len(answer),
                len(result.get("sources", [])),
            )
            chunk_size = 24
            for i in range(0, len(answer), chunk_size):
                await websocket.send_json(
                    {"tur": "chunk", "icerik": answer[i : i + chunk_size]}
                )
            await websocket.send_json(
                {
                    "tur": "atiflar",
                    "atiflar": [
                        a.model_dump() for a in _atiflari_olustur(result.get("sources", []))
                    ],
                }
            )
            await websocket.send_json({"tur": "bitti"})
    except WebSocketDisconnect:
        logger.info("WS /ws/chat bağlantısı kapandı (istemci ayrıldı)")
        return
    except Exception:
        logger.exception("WS /ws/chat beklenmeyen hata")
        return
