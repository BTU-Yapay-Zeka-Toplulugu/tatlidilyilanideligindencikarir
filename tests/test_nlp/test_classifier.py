"""NLP kampanya sınıflandırma modeli için birim testleri."""

import os
import pytest
from src.nlp.classifier import CampaignClassifier, MODEL_PATH


@pytest.fixture(name="clean_model_file")
def fixture_clean_model_file():
    """Test sonrasında oluşturulan model dosyasını temizler."""
    yield
    if os.path.exists(MODEL_PATH):
        try:
            os.remove(MODEL_PATH)
        except OSError:
            pass


def test_classifier_fallback():
    """Model dosyası yokken kural tabanlı fallback sınıflandırma çalışır."""
    clf = CampaignClassifier()
    # Model yüklenmemiş olmalı
    clf.model = None

    # Fallback tahminleri kontrol et
    assert clf.predict("Katılma hesabı açarak kâr payı kazanın.") == "Katılma Hesabı / Mevduat"
    assert clf.predict("Taşıt finansmanı kredisi 36 taksitle.") == "Finansman / Kredi"
    assert clf.predict("Fatura ödemelerinize özel chip para.") == "Kart / Ödeme"


def test_classifier_training(clean_model_file):
    """Sınıflandırıcı eğitilir, model kaydedilir ve yeni metinleri doğru sınıflandırır."""
    # Eğitim verisi
    texts = [
        "Katılma hesabı açarak yüksek kâr payı oranları elde edin ve birikim yapın.",
        "Kâr payı katılma hesabı kazandırıyor.",
        "İhtiyaç kredisi ve araç finansmanı için düşük oranlar.",
        "Konut finansmanı ile ev sahibi olun.",
        "Kredi kartı başvurusu yapın bonus kazanın.",
        "Fatura ödemelerine chip para veriyoruz.",
    ]
    labels = [
        "Katılma Hesabı / Mevduat",
        "Katılma Hesabı / Mevduat",
        "Finansman / Kredi",
        "Finansman / Kredi",
        "Kart / Ödeme",
        "Kart / Ödeme",
    ]

    clf = CampaignClassifier()
    clf.train(texts, labels)

    # Model dosyasının oluştuğunu doğrula
    assert os.path.exists(MODEL_PATH)

    # Yeni bir classifier nesnesi oluşturup diske kaydedilen modeli yüklediğini doğrula
    new_clf = CampaignClassifier()
    assert new_clf.model is not None

    # Eğitilen modelin tahmin yapabildiğini doğrula
    pred1 = new_clf.predict("Birikimlerinizi değerlendirmek için yeni bir katılma hesabı açın.")
    assert pred1 == "Katılma Hesabı / Mevduat"

    pred2 = new_clf.predict("Taşıt ve konut kredisi avantajları burada.")
    assert pred2 == "Finansman / Kredi"
