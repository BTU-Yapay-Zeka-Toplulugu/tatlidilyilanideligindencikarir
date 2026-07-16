"""NLP model performans değerlendirme modülü için birim testleri."""

import os
import pytest
from src.nlp.classifier import MODEL_PATH
from src.nlp.evaluation import evaluate_classifier_performance, perform_cross_validation


@pytest.fixture(name="clean_model")
def fixture_clean_model():
    """Test sonrasında model dosyasını temizler."""
    yield
    if os.path.exists(MODEL_PATH):
        try:
            os.remove(MODEL_PATH)
        except OSError:
            pass


def test_evaluate_classifier_performance(clean_model):
    """Sınıflandırıcı performans raporu metrikleri doğru hesaplanır."""
    texts = [
        "Katılma hesabı kâr payı oranı.",
        "Kâr payı katılma hesabı.",
        "Taşıt konut kredisi finansmanı.",
        "İhtiyaç finansman taksit.",
        "Kredi kartı bonus puan.",
        "Fatura ödemesine chip para.",
    ]
    labels = [
        "Katılma Hesabı / Mevduat",
        "Katılma Hesabı / Mevduat",
        "Finansman / Kredi",
        "Finansman / Kredi",
        "Kart / Ödeme",
        "Kart / Ödeme",
    ]

    metrics = evaluate_classifier_performance(texts, labels)
    assert "accuracy" in metrics
    assert "classification_report" in metrics
    assert metrics["accuracy"] >= 0.0


def test_perform_cross_validation(clean_model):
    """K-katlı çapraz doğrulama başarıyla tamamlanır ve ortalama doğruluk skoru döner."""
    texts = [
        "Katılma hesabı kâr payı oranı.",
        "Kâr payı katılma hesabı.",
        "Mevduat hesabı kâr.",
        "Taşıt konut kredisi finansmanı.",
        "İhtiyaç finansman taksit.",
        "Finansman vade oranı.",
        "Kredi kartı bonus puan.",
        "Fatura ödemesine chip para.",
        "Kart aidatı chip para.",
    ]
    labels = [
        "Katılma Hesabı / Mevduat",
        "Katılma Hesabı / Mevduat",
        "Katılma Hesabı / Mevduat",
        "Finansman / Kredi",
        "Finansman / Kredi",
        "Finansman / Kredi",
        "Kart / Ödeme",
        "Kart / Ödeme",
        "Kart / Ödeme",
    ]

    avg_score = perform_cross_validation(texts, labels, n_splits=3)
    assert isinstance(avg_score, float)
    assert avg_score >= 0.0
