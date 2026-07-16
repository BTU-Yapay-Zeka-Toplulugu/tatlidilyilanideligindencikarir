"""Türkçe metin ön işleme, tokenizasyon ve normalizasyon modülü."""

import re
import spacy

# spaCy Türkçe modelini boş olarak yükle
nlp = spacy.blank("tr")


def turkish_lower(text: str) -> str:
    """Türkçe karakterleri (I->ı, İ->i) doğru şekilde küçük harfe dönüştürür."""
    if not text:
        return ""
    # Türkçe harf dönüşümleri
    text = text.replace("İ", "i").replace("I", "ı")
    return text.lower()


def clean_text_nlp(text: str) -> str:
    """Metindeki ekstra boşlukları ve gereksiz özel karakterleri temizler."""
    if not text:
        return ""
    # Birden fazla boşluğu teklendir
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_text(
    text: str, remove_stopwords: bool = False, remove_punct: bool = True
) -> list[str]:
    """Metni spaCy Türkçe tokenizatörü kullanarak tokenize eder ve filtreler uygular."""
    if not text:
        return []

    # Türkçe harfleri küçült
    lowered_text = turkish_lower(text)
    doc = nlp(lowered_text)
    tokens = []

    for token in doc:
        # Punctuation kontrolü
        if remove_punct and token.is_punct:
            continue
        # Stopword kontrolü
        if remove_stopwords and token.is_stop:
            continue
        # Boşluk tokenlarını atla
        if token.is_space:
            continue

        tokens.append(token.text)

    return tokens


def preprocess_text(text: str, remove_stopwords: bool = True) -> str:
    """Metni küçültür, temizler, tokenize eder ve kelimeleri boşlukla birleştirir."""
    tokens = tokenize_text(text, remove_stopwords=remove_stopwords, remove_punct=True)
    return " ".join(tokens)
