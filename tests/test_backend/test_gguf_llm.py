"""Gerçek yerel GGUF LLM ile chatbot entegrasyon testi (model varsa çalışır)."""

from pathlib import Path

import pytest

from src.backend.core.config import settings
from src.backend.core.llm_factory import GgufLLMClient, LLMClientFactory


def _gguf_in(directory: str) -> bool:
    """Verilen dizin içinde en az bir .gguf dosyası var mı?"""
    p = Path(directory)
    return p.is_dir() and any(p.glob("*.gguf"))


try:
    import llama_cpp
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False


pytestmark = pytest.mark.skipif(
    not HAS_LLAMA_CPP or not _gguf_in(settings.main_responser_model_path),
    reason="llama-cpp-python kurulu değil veya yerel .gguf modeli bulunamadı (model/main_responser/ altına ekleyin)",
)


def test_factory_selects_gguf_when_model_present():
    """Model mevcutsa fabrika GGUF istemcisini seçer."""
    client = LLMClientFactory.create(model_path=settings.main_responser_model_path)
    assert isinstance(client, GgufLLMClient)


def test_main_responser_uses_own_model_dir():
    """Chatbot ana yanıtlayıcı kendi model dizinini kullanır."""
    client = LLMClientFactory.main_responser()
    assert isinstance(client, GgufLLMClient)


def test_all_task_model_dirs_present():
    """Her görev için model alt dizini ve içinde .gguf mevcuttur."""
    paths = [
        settings.main_responser_model_path,
        settings.data_cleaner_model_path,
        settings.extractor_model_path,
        settings.classifier_model_path,
        settings.embedder_model_path,
        settings.comparison_model_path,
    ]
    missing_dirs = [p for p in paths if not Path(p).is_dir()]
    if len(missing_dirs) > 0:
        pytest.skip(f"Bazı model dizinleri mevcut değil: {missing_dirs}")
    for p in paths:
        assert _gguf_in(p), f"Eksik model dizini: {p}"


def test_gguf_llm_generates_answer():
    """GGUF modeli verilen istem için boş olmayan bir yanıt üretir."""
    client = GgufLLMClient(model_path=settings.main_responser_model_path)
    answer = client.generate("Katılım bankası nedir?", max_tokens=48)
    assert isinstance(answer, str)
    assert len(answer.strip()) > 0
