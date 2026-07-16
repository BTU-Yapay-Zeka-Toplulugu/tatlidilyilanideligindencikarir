"""Backend FastAPI'ye HTTP ile erişen ön yüz istemci katmanı."""

from typing import Any

import requests


class ApiClient:
    """FastAPI backend uç noktalarını saran basit istemci."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        """Backend taban URL'sini yapılandırır."""
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str, params: dict | None = None) -> Any:
        """GET isteği gönderir ve JSON yanıtı döner."""
        response = requests.get(f"{self.base_url}{path}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_banks(self) -> list[dict]:
        """Tüm bankaları getirir."""
        return self._get("/api/banks")

    def get_campaigns(self, bank_id: int | None = None, campaign_type: str | None = None) -> list[dict]:
        """Kampanyaları (opsiyonel filtrelerle) getirir."""
        params: dict[str, Any] = {}
        if bank_id is not None:
            params["bank_id"] = bank_id
        if campaign_type:
            params["campaign_type"] = campaign_type
        return self._get("/api/campaigns", params)

    def compare(self, term_months: int | None = None, amount: float | None = None, campaign_type: str | None = None) -> list[dict]:
        """Karşılaştırma sonuçlarını getirir."""
        params: dict[str, Any] = {}
        if term_months is not None:
            params["term_months"] = term_months
        if amount is not None:
            params["amount"] = amount
        if campaign_type:
            params["campaign_type"] = campaign_type
        return self._get("/api/compare", params)

    def chat(self, question: str, top_k: int = 3) -> dict:
        """Chatbot'a soru sorar ve yanıtı döner."""
        return self._get("/api/chat", params={"question": question, "top_k": top_k})
