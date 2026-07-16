"""Gerçek yerel GGUF LLM ile chatbot entegrasyon testi (model varsa çalışır)."""

import os
from pathlib import Path

import pytest

from src.backend.core.config import settings
from src.backend.core.llm_factory import GgufLLMClient, LLMClientFactory

_GGUF_PRESENT = (
    Path(settings.local_model_path).is_file()
    and Path(settings.local_model_path).suffix.lower() == ".gguf"
) or (
    Path(settings.local_model_path).is_dir()
    and any(Path(settings.local_model_path).glob("*.gguf"))
)

pytestmark = pytest.mark.skipif(
    not _GGUF_PRESENT, reason="Yerel .gguf modeli bulunamadı (model/ dizinine ekleyin)"
)


def test_factory_selects_gguf_when_model_present():
    """Model mevcutsa fabrika GGUF istemcisini seçer."""
    client = LLMClientFactory.create()
    assert isinstance(client, GgufLLMClient)


def test_gguf_llm_generates_answer():
    """GGUF modeli verilen istem için boş olmayan bir yanıt üretir."""
    client = GgufLLMClient(model_path=settings.local_model_path)
    answer = client.generate("Katılım bankası nedir?", max_tokens=48)
    assert isinstance(answer, str)
    assert len(answer.strip()) > 0
