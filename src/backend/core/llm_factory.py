"""Yerel LLM erişimini soyutan fabrika (Factory Pattern, ADR-003).

Model iki yolla çevrimdışı çalıştırılır:
- GGUF: llama.cpp (llama-cpp-python) ile diskteki .gguf dosyasından doğrudan yüklenir.
- Ollama: Ollama sunucusu üzerinden (ayrı servis) çalıştırılır.
Tercih LLM_BACKEND ayarıyla (auto | gguf | ollama) belirlenir; auto iken
LOCAL_MODEL_PATH geçerli bir .gguf dosyasıysa GGUF kullanılır.
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.backend.core.config import settings


class LLMClient(ABC):
    """Yerel LLM istemcileri için ortak arayüz."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Verilen istemi modele gönderir ve üretilen yanıtı döner."""
        ...


class GgufLLMClient(LLMClient):
    """llama.cpp (llama-cpp-python) ile diskteki .gguf dosyasını yükleyen istemci."""

    def __init__(self, model_path: str | None = None, n_ctx: int = 4096, n_threads: int | None = 1) -> None:
        """GGUF dosya yolunu ve çıkarım parametreelerini yapılandırır.

        ``n_threads`` varsayılan 1'dir: llama.cpp çoklu iş parçacığında
        bazı CPU'larda çıkarım sırasında Segmentation fault üretebiliyor;
        tek iş parçacığı çıkarımı kararlı kılar (daha yavaş ama çökmez).
        """
        self.model_path = model_path or settings.local_model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self._llm: Any | None = None

    def _resolve_path(self) -> str:
        """LOCAL_MODEL_PATH bir dizin ise içindeki ilk .gguf dosyasını bulur."""
        p = Path(self.model_path)
        if p.is_dir():
            ggufs = sorted(p.glob("*.gguf"))
            if not ggufs:
                raise FileNotFoundError(f"{p} içinde .gguf dosyası bulunamadı")
            return str(ggufs[0])
        return str(p)

    def _lazy_llm(self) -> Any:
        """llama.cpp modelini gerektiğinde (tembel) yükler."""
        if self._llm is None:
            try:
                from llama_cpp import Llama
            except ImportError as exc:
                raise RuntimeError("llama-cpp-python kurulu değil") from exc
            self._llm = Llama(
                model_path=self._resolve_path(),
                n_ctx=self.n_ctx,
                n_threads=self.n_threads or os.cpu_count() or 4,
                verbose=False,
            )
        return self._llm

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """GGUF modelinden istem için yanıt üretir."""
        llm = self._lazy_llm()
        output = llm(prompt, max_tokens=max_tokens, stop=["</s>", "<|im_end|>"])
        return output["choices"][0]["text"].strip()


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


def _is_gguf_path(value: str) -> bool:
    """Verilen yolun geçerli bir .gguf dosyası veya .gguf içeren dizin olup olmadığını döner."""
    p = Path(value)
    if p.is_file() and p.suffix.lower() == ".gguf":
        return True
    if p.is_dir() and any(p.glob("*.gguf")):
        return True
    return False


class LLMClientFactory:
    """Model değişiminde yalnızca bu fabrikanın güncellenmesi için soyutlama."""

    @staticmethod
    def create(model_name: str | None = None, model_path: str | None = None) -> LLMClient:
        """Yapılandırmaya göre uygun yerel LLM istemcisini üretir."""
        backend = settings.llm_backend.lower()
        path = model_path or settings.local_model_path

        if backend in ("auto", "gguf") and _is_gguf_path(path):
            return GgufLLMClient(model_path=path)
        if backend == "ollama" or not _is_gguf_path(path):
            return OllamaLLMClient(model_name=model_name)
        return GgufLLMClient(model_path=path)

    @staticmethod
    def from_local_path(local_model_path: str | None = None) -> LLMClient:
        """Yerel model dosyasından (çevrimdışı) LLM istemcisi üretir."""
        path = local_model_path or settings.local_model_path
        if _is_gguf_path(path):
            return GgufLLMClient(model_path=path)
        return OllamaLLMClient(model_name=path)

    @staticmethod
    def main_responser() -> LLMClient:
        """Chatbot ana yanıtlayıcı için kendi model dizinini kullanır."""
        return LLMClientFactory.create(model_path=settings.main_responser_model_path)

    @staticmethod
    def data_cleaner() -> LLMClient:
        """Veri temizleyici için kendi model dizinini kullanır."""
        return LLMClientFactory.create(model_path=settings.data_cleaner_model_path)

    @staticmethod
    def extractor() -> LLMClient:
        """Bilgi çıkarımı için kendi model dizinini kullanır."""
        return LLMClientFactory.create(model_path=settings.extractor_model_path)

    @staticmethod
    def classifier() -> LLMClient:
        """Sınıflandırma için kendi model dizinini kullanır."""
        return LLMClientFactory.create(model_path=settings.classifier_model_path)

    @staticmethod
    def embedder() -> LLMClient:
        """Vektör arama gömme için kendi model dizinini kullanır."""
        return LLMClientFactory.create(model_path=settings.embedder_model_path)

    @staticmethod
    def comparison() -> LLMClient:
        """Karşılaştırma servisi için kendi model dizinini kullanır."""
        return LLMClientFactory.create(model_path=settings.comparison_model_path)
