"""Sınıflandırma modelinin doğruluğunu ve performans metriklerini ölçen değerlendirme modülü."""

import logging
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import StratifiedKFold
from src.nlp.classifier import CampaignClassifier

logger = logging.getLogger(__name__)


def evaluate_classifier_performance(texts: list[str], labels: list[str]) -> dict:
    """Verilen metin ve etiketler üzerinde modelin doğruluk, precision, recall ve f1 skorlarını hesaplar."""
    if not texts or not labels:
        return {}

    clf = CampaignClassifier()

    # Eğer model eğitilmemişse önce eğit
    if clf.model is None:
        logger.info("Model eğitilmemiş, değerlendirme öncesi eğitiliyor...")
        clf.train(texts, labels)

    # Tahminleri al
    predictions = [clf.predict(t) for t in texts]

    # Metrikleri hesapla
    acc = accuracy_score(labels, predictions)
    report = classification_report(labels, predictions, output_dict=True, zero_division=0)

    print("\n=== Model Performans Değerlendirme Raporu ===")
    print(f"Genel Doğruluk (Accuracy): {acc:.4f}\n")
    print(classification_report(labels, predictions, zero_division=0))

    return {
        "accuracy": acc,
        "classification_report": report,
    }


def perform_cross_validation(texts: list[str], labels: list[str], n_splits: int = 3) -> float:
    """Metinler ve etiketler üzerinde k-katlı çapraz doğrulama gerçekleştirerek ortalama doğruluğu döndürür."""
    if len(texts) < n_splits:
        raise ValueError("Veri miktarı kat sayısından az olamaz.")

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores = []

    for fold, (train_idx, test_idx) in enumerate(skf.split(texts, labels)):
        train_texts = [texts[i] for i in train_idx]
        train_labels = [labels[i] for i in train_idx]
        test_texts = [texts[i] for i in test_idx]
        test_labels = [labels[i] for i in test_idx]

        # Her kat için geçici classifier eğit
        clf = CampaignClassifier()
        clf.train(train_texts, train_labels)

        # Test seti tahmini
        preds = [clf.predict(t) for t in test_texts]
        acc = accuracy_score(test_labels, preds)
        scores.append(acc)
        logger.info(f"Kat {fold+1} Doğruluğu: {acc:.4f}")

    avg_score = sum(scores) / len(scores)
    print(f"\n{n_splits}-Katlı Çapraz Doğrulama Ortalama Doğruluğu: {avg_score:.4f}")
    return avg_score
