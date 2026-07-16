"""Yerel LLM erişimini soyutan fabrika (Factory Pattern, ADR-003)."""

from abc import ABC, abstractmethod
from typing import Any

from src.backend.core.config import settings


class LLMClient(ABC):
    """Yerel LLM istemcileri için ortak arayüz."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Verilen istemi modele gönderir ve üretilen yanıtı döner."""
        ...


class OllamaLLMClient(LLMClient):
    """Ollama üzerinden yerel açık kaynak modeli kullanan istemci."""

    def __init__(self, model_name: str | None = None) -> None:
        """Model adını ve Ollama adresini yapılandırır."""
        self.model_name = model_name or settings.default_llm_model
        self.base_url = settings.ollama_base_url
        self._client: Any | None = None

    def _lazy_client(self) -> Any:
        """Ollama istemcisini gerektiğinde (tembel) başlatır."""
        if self._client is None:
            try:
                import ollama
            except ImportError as exc:
                raise RuntimeError("ollama kütüphanesi kurulu değil") from exc
            self._client = ollama.Client(host=self.base_url)
        return self._client

    def generate(self, prompt: str) -> str:
        """Ollama modelinden istem için yanıt üretir."""
        client = self._lazy_client()
        response = client.generate(model=self.model_name, prompt=prompt)
        return response.get("response", "")


class LLMClientFactory:
    """Model değişiminde yalnızca bu fabrikanın güncellenmesi için soyutlama."""

    @staticmethod
    def create(model_name: str | None = None) -> LLMClient:
        """Yapılandırmaya göre uygun yerel LLM istemcisini üretir."""
        return OllamaLLMClient(model_name=model_name)

    @staticmethod
    def from_local_path(local_model_path: str | None = None) -> LLMClient:
        """Yerel model dosyasından (çevrimdışı) LLM istemcisi üretir."""
        path = local_model_path or settings.local_model_path
        return OllamaLLMClient(model_name=path)
