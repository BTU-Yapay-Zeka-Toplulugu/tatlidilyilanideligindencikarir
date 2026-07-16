"""Metin gömme (embedding) soyutlaması; tamamen çevrimdışı ve açık kaynak."""

from abc import ABC, abstractmethod

import numpy as np


class Embedder(ABC):
    """Metinleri vektörlere çeviren ortak arayüz."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Metin listesini gömme vektörlerine çevirir."""
        ...


class LocalLexicalEmbedder(Embedder):
    """İndirme gerektirmeyen, çevrimdışı bag-of-words (TF) gömme üreteci.

    Üretimde sentence-transformers modeli ile değiştirilebilir; bu sınıf
    ağ bağımlılığı olmadan test ve prototip için kullanılır.
    """

    def __init__(self, vocab: list[str] | None = None, dimension: int = 256) -> None:
        """Sözlük ve vektör boyutunu yapılandırır."""
        self.dimension = dimension
        self.vocab = vocab or []
        self._seed_terms = [
            "kâr payı", "kar payi", "vade", "mevduat", "katılma", "kredi",
            "finansman", "taksit", "sigorta", "bes", "emekli", "esnaf", "genç",
            "kart", "aidat", "faizsiz", "indirim", "puan", "hediye", "avantaj",
        ]

    def _term_vector(self, text: str) -> np.ndarray:
        """Metnin sabit boyutlu sözcük-tabanlı gömme vektörünü üretir."""
        vec = np.zeros(self.dimension, dtype=np.float32)
        lower = (text or "").lower()
        for i, term in enumerate(self._seed_terms):
            count = lower.count(term)
            if i < self.dimension:
                vec[i] = float(count)
        # Karakter uzunluğu gibi deterministik bir öznitelik de ekle
        if self.dimension > len(self._seed_terms):
            vec[len(self._seed_terms)] = float(len(text))
        return vec

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Her metin için gömme vektörü döner."""
        return [self._term_vector(t).tolist() for t in texts]


class SentenceTransformerEmbedder(Embedder):
    """Yerel sentence-transformers modelinden (çevrimdışı) gömme üreteci.

    Model dosyası .env içindeki LOCAL_MODEL_PATH'ten yüklenir (ADR-003).
    """

    def __init__(self, model_path: str | None = None) -> None:
        """Yerel model yolunu yapılandırır ve modeli tembel şekilde yükler."""
        from src.backend.core.config import settings

        self.model_path = model_path or settings.local_model_path
        self._model = None

    def _lazy_model(self):
        """sentence-transformers modelini gerektiğinde yükler."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError("sentence_transformers kurulu değil") from exc
            self._model = SentenceTransformer(self.model_path)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Metinleri sentence-transformers ile gömer."""
        model = self._lazy_model()
        vectors = model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vectors]
