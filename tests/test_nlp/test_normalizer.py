"""NLP normalizasyon modülü için birim testleri."""

import pytest
from src.nlp.normalizer import (
    normalize_amount,
    normalize_profit_share_rate,
    normalize_term,
    normalize_text_numbers,
)


def test_normalize_profit_share_rate():
    """Kâr payı oranlarını standart %X.XX formatına dönüştürür."""
    assert normalize_profit_share_rate(2.5) == "%2.50"
    assert normalize_profit_share_rate(12.053) == "%12.05"
    assert normalize_profit_share_rate(None) == "Belirtilmemiş"


def test_normalize_amount():
    """Tutar değerlerini Türkçe binlik ayraçlı ve TL birimli standart formata dönüştürür."""
    assert normalize_amount(500) == "500 TL"
    assert normalize_amount(10000) == "10.000 TL"
    assert normalize_amount(1500000) == "1.500.000 TL"
    assert normalize_amount(None) == "Belirtilmemiş"


def test_normalize_term():
    """Vade değerlerini standart ay birimiyle ifade eder."""
    assert normalize_term(3) == "3 Ay"
    assert normalize_term(12) == "12 Ay"
    assert normalize_term(None) == "Belirtilmemiş"


def test_normalize_text_numbers():
    """Metin içindeki para birimlerini ve yüzde sembollerini standart hale getirir."""
    assert normalize_text_numbers("Yıllık yüzde 5 kâr payı.") == "Yıllık %5 kâr payı."
    assert normalize_text_numbers("Hesap açılış limiti 500 ₺.") == "Hesap açılış limiti 500 TL."
    assert normalize_text_numbers("Komisyon tutarı 10 TRY.") == "Komisyon tutarı 10 TL."
    assert normalize_text_numbers("") == ""
