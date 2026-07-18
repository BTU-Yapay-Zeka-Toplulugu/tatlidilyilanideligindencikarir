"""Birleşik regex+model çıkarım pipeline'ı için birim testleri (ADR-013)."""

from src.nlp.extractor import extract_dates
from src.nlp.pipeline import (
    ModelExtractor,
    RegexExtractor,
    merge_field,
    run_extraction_pipeline,
)


def test_merge_field_regex_wins_when_present():
    """Regex net değer bulduğunda uzlaştırma regex'i kazanır."""
    assert merge_field(2.05, 3.5) == 2.05


def test_merge_field_model_used_when_regex_empty():
    """Regex boşsa model sonucu kullanılır."""
    assert merge_field(None, "Finansman / Kredi") == "Finansman / Kredi"
    assert merge_field("", "Diğer") == "Diğer"


def test_pipeline_regex_rate_canonical():
    """Pipeline %2,05 gibi oranı hem ham hem kanonik forme çevirir."""
    out = run_extraction_pipeline("Kâr payı oranımız %2,05 olarak belirlenmiştir.")
    assert out["profit_share_rate_raw"] == 2.05
    assert out["profit_share_rate"] == "%2.05"


def test_pipeline_normalizes_amount_variants():
    """'500 TL' ve '500₺' aynı kanonik forma normalize edilir."""
    a = run_extraction_pipeline("En az 500 TL ile başlayan finansman.")
    b = run_extraction_pipeline("En az 500 ₺ ile başlayan finansman.")
    assert a["min_amount_raw"] == 500.0
    assert a["min_amount"] == b["min_amount"] == "500 TL"


def test_pipeline_extracts_dates():
    """Türkçe tarih formatları ISO'ya çevrilir."""
    out = run_extraction_pipeline(
        "Kampanya 15.07.2026 - 31.12.2026 tarihleri arasında geçerlidir."
    )
    assert out["start_date"] == "2026-07-15"
    assert out["end_date"] == "2026-12-31"


def test_pipeline_date_month_name_format():
    """'DD Ay YYYY' formatı ISO'ya çevrilir."""
    assert extract_dates("Son başvuru 1 Ocak 2026 tarihine kadar.") == ("2026-01-01", None)


def test_pipeline_campaign_type_from_model_fallback():
    """Metinde tür anahtarı yoksa model (fallback) bir tür döndürür."""
    out = run_extraction_pipeline("Bankamızın yeni ürünleri müşterilerimize sunulmuştur.")
    assert out["campaign_type"] in (
        "Kart / Ödeme", "Katılma Hesabı / Mevduat",
        "Sigorta / Emeklilik", "Finansman / Kredi", "Diğer",
    )


def test_pipeline_multiple_rates_takes_contextual():
    """Aynı cümlede birden fazla oran varsa bağlam-duyarlı olan seçilir."""
    out = run_extraction_pipeline(
        "Biz Kart ile %75 Nakit İade; ayrıca Kâr payı oranı %2,05 olarak uygulanır."
    )
    assert out["profit_share_rate_raw"] == 2.05


def test_pipeline_no_rate_text():
    """Oran içermeyen metinde oran alanı Belirtilmemiş olur."""
    out = run_extraction_pipeline("Bu sayfada herhangi bir oran bilgisi yer almamaktadır.")
    assert out["profit_share_rate"] == "Belirtilmemiş"


def test_regex_and_model_strategies_run():
    """Her iki strateji de hatasız çalışır ve anahtarları üretir."""
    keys = {
        "profit_share_rate", "term_months", "min_amount", "max_amount",
        "start_date", "end_date", "advantage_description",
        "target_audience", "campaign_type",
    }
    assert keys.issubset(RegexExtractor().extract("Kâr payı %2,05, 12 ay vade.").keys())
    assert keys.issubset(ModelExtractor().extract("Kâr payı %2,05.").keys())
