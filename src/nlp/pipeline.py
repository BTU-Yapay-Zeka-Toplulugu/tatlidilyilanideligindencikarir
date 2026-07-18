"""Birleşik bilgi çıkarım pipeline'ı (regex + model, uzlaştırma + kanonik form).

ADR-013: Ham metin (HTML veya PDF kaynaklı — fark etmez) tek bir ortak
pipeline'dan geçer:

  1. Regex katmanı (``RegexExtractor``) — net, yüksek güvenilirlikli kalıplar.
  2. Model/NER katmanı (``ModelExtractor``) — regex'in bulamadığı/bağlam
     gerektiren alanlar (kampanya türü sınıflandırma, serbest metin oranları).
  3. Uzlaştırma (reconcile) — çelişen sonuçlarda açık öncelik kuralı:
     regex net bir değer bulduysa regex kazanır; regex hiçbir şey bulamadıysa
     model sonucu kullanılır (bkz. ``merge_field``).
  4. Kanonik normalizasyon — tüm sayısal/formatlı alanlar TEK standart
     forma indirgenir (``%X.XX``, ``X.XXX TL``, ``YYYY-MM-DD``).

Hem HTML hem PDF kaynaklı veri AYNI fonksiyonla (``run_extraction_pipeline``)
çağrılır; iki ayrı tutarsız uygulama YOKTUR.
"""

from abc import ABC, abstractmethod
from typing import Any

from src.nlp.extractor import (
    extract_all_campaign_details,
    extract_amounts,
    extract_dates,
    extract_profit_share_rate,
    extract_term_months,
)
from src.nlp.normalizer import (
    normalize_amount,
    normalize_profit_share_rate,
    normalize_term,
)
from src.nlp.classifier import CampaignClassifier


# ---------------------------------------------------------------------------
# Strateji arayüzü (CLAUDE.md: Strategy Pattern)
# ---------------------------------------------------------------------------

class ExtractorStrategy(ABC):
    """Bilgi çıkarım stratejileri için ortak arayüz."""

    @abstractmethod
    def extract(self, text: str) -> dict[str, Any]:
        """Metinden yapılandırılmış alanları çıkarır."""
        ...


class RegexExtractor(ExtractorStrategy):
    """Kural tabanlı (regex) bilgi çıkarım stratejisi."""

    def extract(self, text: str) -> dict[str, Any]:
        """Regex desenleriyle oran, vade, tutar, tarih ve türü ayıklar."""
        min_amt, max_amt = extract_amounts(text)
        start_date, end_date = extract_dates(text)
        return {
            "profit_share_rate": extract_profit_share_rate(text),
            "term_months": extract_term_months(text),
            "min_amount": min_amt,
            "max_amount": max_amt,
            "start_date": start_date,
            "end_date": end_date,
            # Avantaj/hedef kitle/tür regex katmanından (extractor içinde kural).
            **{
                k: v
                for k, v in extract_all_campaign_details(text).items()
                if k in ("advantage_description", "target_audience", "campaign_type")
            },
        }


class ModelExtractor(ExtractorStrategy):
    """Model/NER tabanlı bilgi çıkarım stratejisi (fallback/bağlam).

    Mevcut sistemde kampanya TÜRÜ için eğitilmiş bir ML modeli
    (``CampaignClassifier``) vardır; oran/tutar alanları için model yoksa
    regex'e güvenilir. Bu strateji, regex'in boş bıraktığı alanları doldurur
    ve türü model ile (varsa) yeniden tahmin eder.
    """

    def __init__(self) -> None:
        """Sınıflandırıcıyı ilklendirir."""
        self._classifier = CampaignClassifier()

    def extract(self, text: str) -> dict[str, Any]:
        """Model tabanlı alanları (özellikle kampanya türü) üretir."""
        campaign_type = self._classifier.predict(text) if text else "Diğer"
        return {
            "profit_share_rate": None,  # model tabanlı oran çıkarımı henüz yok
            "term_months": None,
            "min_amount": None,
            "max_amount": None,
            "start_date": None,
            "end_date": None,
            "advantage_description": None,
            "target_audience": None,
            "campaign_type": campaign_type,
        }


# ---------------------------------------------------------------------------
# Uzlaştırma + kanonik normalizasyon
# ---------------------------------------------------------------------------

def merge_field(regex_val: Any, model_val: Any) -> Any:
    """Bir alan için regex ve model sonucunu uzlaştırır (ADR-013 kuralı).

    Kural: regex net (boş/None değil) bir değer bulduysa regex kazanır;
    regex boşsa model sonucu kullanılır. Böylece regex'in yüksek güvenilirliği
    korunur, regex'in kaçırdığı alanlar model ile doldurulur.
    """
    return regex_val if regex_val not in (None, "", []) else model_val


def _canonicalize(result: dict[str, Any]) -> dict[str, Any]:
    """Sayısal/formatlı alanları TEK kanonik forma indirger."""
    return {
        "profit_share_rate_raw": result.get("profit_share_rate"),
        "profit_share_rate": normalize_profit_share_rate(result.get("profit_share_rate")),
        "term_months_raw": result.get("term_months"),
        "term_months": normalize_term(result.get("term_months")),
        "min_amount_raw": result.get("min_amount"),
        "min_amount": normalize_amount(result.get("min_amount")),
        "max_amount_raw": result.get("max_amount"),
        "max_amount": normalize_amount(result.get("max_amount")),
        "start_date": result.get("start_date"),
        "end_date": result.get("end_date"),
        "advantage_description": result.get("advantage_description"),
        "target_audience": result.get("target_audience") or "Herkes",
        "campaign_type": result.get("campaign_type") or "Diğer",
    }


def run_extraction_pipeline(text: str) -> dict[str, Any]:
    """Ham metni birleşik regex+model pipeline'ından geçirip kanonik çıktı döner.

    HTML ve PDF kaynaklı metin AYNI fonksiyonla işlenir. Döner: alanlar hem
    ham (``*_raw``) hem kanonik (``%X.XX`` / ``X.XXX TL`` / ``YYYY-MM-DD``)
    formda.
    """
    regex_layer = RegexExtractor().extract(text)
    model_layer = ModelExtractor().extract(text)

    merged: dict[str, Any] = {}
    for key in (
        "profit_share_rate", "term_months", "min_amount", "max_amount",
        "start_date", "end_date", "advantage_description",
        "target_audience", "campaign_type",
    ):
        merged[key] = merge_field(regex_layer.get(key), model_layer.get(key))

    return _canonicalize(merged)
