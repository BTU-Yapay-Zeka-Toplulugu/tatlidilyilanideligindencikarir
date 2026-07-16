"""Kampanya metinlerini makine öğrenmesi ve kural tabanlı hibrit yöntemle sınıflandıran modül."""

import os
import pickle
from typing import Sequence
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from src.nlp.extractor import classify_campaign_type as rule_based_classify
from src.nlp.preprocessor import preprocess_text

MODEL_PATH = os.path.join(os.path.dirname(__file__), "campaign_classifier.pkl")


class CampaignClassifier:
    """Kampanya metinlerini kategorilerine göre sınıflandıran model sınıfı."""

    def __init__(self):
        """Sınıflandırıcıyı ilklendirir ve kaydedilmiş model varsa yükler."""
        self.model = None
        self.load_model()

    def load_model(self) -> bool:
        """Kaydedilmiş makine öğrenmesi modelini diskten yükler."""
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                return True
            except Exception:
                self.model = None
        return False

    def train(self, texts: Sequence[str], labels: Sequence[str]) -> None:
        """Verilen metin ve etiket kümesi ile TF-IDF + Lojistik Regresyon hattını eğitir ve kaydeder."""
        # Metinleri ön işlemeden geçir
        processed_texts = [preprocess_text(t) for t in texts]

        # Pipeline oluştur: TF-IDF + LogisticRegression
        pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
                ("clf", LogisticRegression(C=1.0, max_iter=1000)),
            ]
        )

        pipeline.fit(processed_texts, labels)
        self.model = pipeline

        # Modeli diske kaydet
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)

    def predict(self, text: str) -> str:
        """Verilen kampanya metninin kategorisini tahmin eder; model yoksa kural tabanlı yönteme döner."""
        if not text:
            return "Diğer"

        # Makine öğrenmesi modeli yüklüyse tahminde bulun
        if self.model is not None:
            try:
                processed = preprocess_text(text)
                return str(self.model.predict([processed])[0])
            except Exception:
                pass

        # Model yoksa veya tahmin başarısız olduysa kural tabanlı tahmine dön
        return rule_based_classify(text)
