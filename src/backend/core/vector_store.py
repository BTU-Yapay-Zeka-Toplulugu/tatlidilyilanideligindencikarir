"""Vektör veritabanı soyutlaması ve fabrikası (Factory Pattern, RAG için).

Çevrimdışı, açık kaynak ve on-premise çalışır. Üretimde Chroma (diskte kalıcı)
kullanılır; test/prototip için harici bağımlılık gerektirmeyen saf-Python
InMemory vektör deposu kullanılır.
"""

from abc import ABC, abstractmethod

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.backend.core.embeddings import Embedder, LocalLexicalEmbedder


class VectorStore(ABC):
    """Vektör tabanlı benzerlik araması için ortak arayüz."""

    @abstractmethod
    def add(self, ids: list[str], texts: list[str], metadatas: list[dict] | None = None) -> None:
        """Metinleri gömer ve vektör deposuna ekler."""
        ...

    @abstractmethod
    def query(self, text: str, top_k: int = 5) -> list[dict]:
        """Sorgu metnine en benzer kayıtları döner."""
        ...


class InMemoryVectorStore(VectorStore):
    """Harici bağımlılık gerektirmeyen, çevrimdışı bellek içi vektör deposu."""

    def __init__(self, embedder: Embedder | None = None) -> None:
        """Gömme üretecini ve boş koleksiyonu başlatır."""
        self.embedder = embedder or LocalLexicalEmbedder()
        self._ids: list[str] = []
        self._texts: list[str] = []
        self._metadatas: list[dict] = []
        self._vectors: list[list[float]] = []

    def add(self, ids: list[str], texts: list[str], metadatas: list[dict] | None = None) -> None:
        """Metinleri gömer ve koleksiyona ekler."""
        metadatas = metadatas or [{} for _ in texts]
        vectors = self.embedder.embed(texts)
        self._ids.extend(ids)
        self._texts.extend(texts)
        self._metadatas.extend(metadatas)
        self._vectors.extend(vectors)

    def query(self, text: str, top_k: int = 5) -> list[dict]:
        """Sorguya kosinüs benzerliğine göre en yakın sonuçları döner."""
        if not self._vectors:
            return []
        query_vec = np.array(self.embedder.embed([text])[0]).reshape(1, -1)
        all_vecs = np.array(self._vectors)
        scores = cosine_similarity(query_vec, all_vecs)[0]
        order = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in order:
            results.append(
                {
                    "id": self._ids[idx],
                    "text": self._texts[idx],
                    "metadata": self._metadatas[idx],
                    "score": float(scores[idx]),
                }
            )
        return results


class ChromaVectorStore(VectorStore):
    """Chroma tabanlı, diskte kalıcı vektör deposu (on-premise RAG için)."""

    def __init__(self, collection_name: str, persist_directory: str, embedder: Embedder | None = None) -> None:
        """Chroma istemcisini ve koleksiyonu başlatır."""
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("chromadb kurulu değil") from exc
        self.embedder = embedder or LocalLexicalEmbedder()
        self._collection_name = collection_name
        self._client = chromadb.PersistentClient(path=persist_directory)
        self._collection = self._client.get_or_create_collection(name=collection_name)

    def _embed_fn(self, texts: list[str]) -> list[list[float]]:
        """Chroma için gömme fonksiyonu sarmalayıcısı."""
        return self.embedder.embed(texts)

    def add(self, ids: list[str], texts: list[str], metadatas: list[dict] | None = None) -> None:
        """Metinleri Chroma koleksiyonuna ekler."""
        self._collection.add(ids=ids, documents=texts, metadatas=metadatas or [{} for _ in texts])

    def query(self, text: str, top_k: int = 5) -> list[dict]:
        """Chroma üzerinden benzerlik araması yapar."""
        results = self._collection.query(query_texts=[text], n_results=top_k)
        output = []
        for doc_id, doc, meta, dist in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append(
                {"id": doc_id, "text": doc, "metadata": meta, "score": float(1.0 - dist)}
            )
        return output


class VectorStoreFactory:
    """Ortam yapılandırmasına göre uygun vektör deposunu üreten fabrika."""

    @staticmethod
    def create(kind: str = "memory", **kwargs) -> VectorStore:
        """İstenen türde ('memory' veya 'chroma') vektör deposu döner."""
        if kind == "chroma":
            return ChromaVectorStore(
                collection_name=kwargs.get("collection_name", "campaigns"),
                persist_directory=kwargs.get("persist_directory", "data/vector_store"),
                embedder=kwargs.get("embedder"),
            )
        return InMemoryVectorStore(embedder=kwargs.get("embedder"))


_STORE: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Uygulama ömrü boyunca paylaşılan vektör deposunu döner (DI için)."""
    global _STORE
    if _STORE is None:
        _STORE = VectorStoreFactory.create(kind="memory")
    return _STORE
