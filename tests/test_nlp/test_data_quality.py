"""Gerçek ham veri seti üzerinde çıkarım kalitesi (precision) regresyon testleri.

Bu testler, kâr payı oranı çıkarımının gerçek taranmış metinlerde ilgisiz
yüzdeleri (nakit iade, indirim, iştirak, LTV, devlet katkısı, vergi vb.)
yanlışlıkla kâr payı oranı olarak üretmediğini garanti eder.
"""

import json
import os

import pytest

from src.nlp.extractor import extract_all_campaign_details, extract_profit_share_rate

RAW_FILE = os.path.join("data", "raw", "campaigns_20260716_205849.json")


def _load_raw():
    if not os.path.exists(RAW_FILE):
        pytest.skip("Ham veri seti bulunamadı")
    with open(RAW_FILE, encoding="utf-8") as fh:
        return json.load(fh)


def test_gercek_veride_makul_olmayan_oran_uretilmez():
    """Ham veri setinde %50'nin üzerinde kâr payı oranı ÜRETİLMEMELİDİR.

    Katılım bankacılığında kâr payı oranı bu bandın üstünde olmaz; daha
    önce "%75 nakit iade", "%100 asgari ödeme" gibi ifadeler yanlışlıkla
    oran olarak çıkarılıyordu (regresyon).
    """
    records = _load_raw()
    kotu = []
    for c in records:
        rate = extract_profit_share_rate(c.get("raw_text", ""))
        if rate is not None and rate > 50.0:
            kotu.append((c.get("page_title", "")[:50], rate))
    assert kotu == [], f"Makul olmayan oranlar üretildi: {kotu}"


def test_gercek_veride_uretilen_oranlar_pozitif_ve_makul():
    """Üretilen tüm oranlar 0 < r <= 50 aralığında olmalıdır."""
    records = _load_raw()
    for c in records:
        rate = extract_profit_share_rate(c.get("raw_text", ""))
        if rate is not None:
            assert 0 < rate <= 50.0


def test_extract_all_details_sozluk_yapisini_korur():
    """Uçtan uca çıkarım beklenen tüm anahtarları döner."""
    records = _load_raw()
    beklenen = {
        "profit_share_rate",
        "term_months",
        "min_amount",
        "max_amount",
        "advantage_description",
        "target_audience",
        "campaign_type",
    }
    d = extract_all_campaign_details(records[0].get("raw_text", ""))
    assert beklenen.issubset(d.keys())
