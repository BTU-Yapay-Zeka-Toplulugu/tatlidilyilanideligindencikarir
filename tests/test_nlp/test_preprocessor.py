"""NLP ön işleme modülü için birim testleri."""

import pytest
from src.nlp.preprocessor import (
    clean_text_nlp,
    preprocess_text,
    tokenize_text,
    turkish_lower,
)


def test_turkish_lower():
    """Türkçe büyük harfleri doğru şekilde küçük harflere dönüştürür."""
    assert turkish_lower("İSTANBUL") == "istanbul"
    assert turkish_lower("ILIK") == "ılık"
    assert turkish_lower("KÂR PAYI") == "kâr payı"
    assert turkish_lower("Şube") == "şube"
    assert turkish_lower("") == ""


def test_clean_text_nlp():
    """Metin içindeki gereksiz boşlukları temizler."""
    assert clean_text_nlp("  metin  boşluk   ") == "metin boşluk"
    assert clean_text_nlp("satır\nbaşı\tsekme") == "satır başı sekme"
    assert clean_text_nlp("") == ""


def test_tokenize_text():
    """Metni doğru şekilde tokenize eder ve filtreleri uygular."""
    text = "Adil Katılım Bankası ile kâr payı kazanın!"

    # Varsayılan filtreleme (noktalama işaretlerini kaldır, stopword'leri koru)
    tokens = tokenize_text(text, remove_stopwords=False, remove_punct=True)
    assert "!" not in tokens
    assert "ile" in tokens
    assert "kâr" in tokens

    # Stopword'leri de filtrele
    tokens_no_stop = tokenize_text(text, remove_stopwords=True, remove_punct=True)
    assert "ile" not in tokens_no_stop
    assert "kâr" in tokens_no_stop


def test_preprocess_text():
    """Ön işleme pipeline'ını baştan sona çalıştırıp temiz metin döndürür."""
    text = "  Bu   bir  kampanya  metnidir!   "
    # "bu", "bir" genellikle stopword olduğu için filtrelenir
    processed = preprocess_text(text, remove_stopwords=True)
    assert "kampanya" in processed
    assert "metnidir" in processed
    assert "bu" not in processed
    assert "!" not in processed
