"""RAG chatbot servisi ve /api/chat uç noktası için testler."""

import pytest
from src.backend.core.vector_store import InMemoryVectorStore
from src.backend.services.chatbot_service import ChatbotService


class _FakeLLM:
    """Test için sabit yanıt döndüren sahte LLM istemcisi."""

    def generate(self, prompt: str) -> str:
        """İstem metninden bağlamı çıkarıp sabit bir yanıt üretir."""
        return "Bu bir test yanıtıdır."


class MockLexicalEmbedder:
    """Testler için basit, metin uzunluğundan etkilenmeyen kelime eşleşmeli gömme üreteci."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Metin listesini basit kelime-var/yok vektörlerine gömer."""
        vocab = ["katılma", "hesabı", "kâr", "payı", "vade", "mevduat", "bankası"]
        vectors = []
        for t in texts:
            vec = [1.0 if w in t.lower() else 0.0 for w in vocab]
            norm = sum(x*x for x in vec) ** 0.5
            if norm > 0:
                vec = [x / norm for x in vec]
            else:
                vec = [0.0] * len(vocab)
            vectors.append(vec)
        return vectors


def _store_with_data() -> InMemoryVectorStore:
    """Örnek kampanya verisiyle dolu bir vektör deposu döner."""
    store = InMemoryVectorStore(embedder=MockLexicalEmbedder())
    store.add(
        ["campaign-1"],
        ["katılma hesabı kâr payı %20 vade 3 ay mevduat"],
        [{"source_url": "https://bank.com/k", "title": "Katılma"}],
    )
    return store


def test_chatbot_answer_with_mock_llm():
    """Chatbot retrieval bağlamını toplayıp LLM'den yanıt üretir."""
    service = ChatbotService(vector_store=_store_with_data(), llm=_FakeLLM())
    result = service.answer("en yüksek kâr payı hangisi?")
    assert result["answer"] == "Bu bir test yanıtıdır."
    assert result["sources"][0]["id"] == "campaign-1"
    assert result["sources"][0]["source_url"] == "https://bank.com/k"


def test_chatbot_empty_store():
    """Veri yokken chatbot boş bağlamla çalışır ve kaynak döndürmez."""
    service = ChatbotService(vector_store=InMemoryVectorStore(embedder=MockLexicalEmbedder()), llm=_FakeLLM())
    result = service.answer("merhaba")
    assert result["answer"] == "Bu bir test yanıtıdır."
    assert result["sources"] == []


def test_chatbot_deduplication():
    """Benzer/aynı kaynakların chatbot retrieval aşamasında tekilleştirildiğini doğrular."""
    store = InMemoryVectorStore(embedder=MockLexicalEmbedder())
    store.add(
        ["campaign-1", "campaign-1", "campaign-2"],
        [
            "katılma hesabı kâr payı %20 vade 3 ay mevduat",
            "farklı metin ama aynı ID hesabı",
            "katılma hesabı başka metin ama aynı URL"
        ],
        [
            {"source_url": "https://bank.com/a", "bank_name": "A Bank"},
            {"source_url": "https://bank.com/b", "bank_name": "B Bank"},
            {"source_url": "https://bank.com/a", "bank_name": "C Bank"},
        ]
    )
    service = ChatbotService(vector_store=store, llm=_FakeLLM())
    result = service.answer("katılma hesabı kâr payı vade mevduat", top_k=3, threshold=0.0)
    assert len(result["sources"]) == 1
    assert result["sources"][0]["id"] == "campaign-1"
    assert result["sources"][0]["source_url"] == "https://bank.com/a"


def test_chatbot_relevance_threshold():
    """Eşik değerin altında kalan alakasız kaynakların filtrelendiğini doğrular."""
    store = InMemoryVectorStore(embedder=MockLexicalEmbedder())
    store.add(
        ["campaign-1"],
        ["tamamen alakasız metin"],
        [{"source_url": "https://bank.com/a", "bank_name": "A Bank"}]
    )
    service = ChatbotService(vector_store=store, llm=_FakeLLM())
    result = service.answer("katılma hesabı kâr payı", threshold=0.5)
    assert len(result["sources"]) == 0


def test_chatbot_comparative_diversity():
    """Karşılaştırma içeren sorularda farklı banka kaynaklarının önceliklendirildiğini doğrular."""
    store = InMemoryVectorStore(embedder=MockLexicalEmbedder())
    store.add(
        ["camp-a1", "camp-a2", "camp-b1"],
        [
            "katılma hesabı A bankası yüksek oran",
            "başka bir A bankası kampanyası",
            "katılma hesabı B bankası mevduat"
        ],
        [
            {"source_url": "https://bank-a.com/1", "bank_name": "A Bank"},
            {"source_url": "https://bank-a.com/2", "bank_name": "A Bank"},
            {"source_url": "https://bank-b.com/1", "bank_name": "B Bank"},
        ]
    )
    service = ChatbotService(vector_store=store, llm=_FakeLLM())
    result = service.answer("hangisi daha iyi kâr payı sunuyor?", top_k=2, threshold=0.0)
    sources = result["sources"]
    assert len(sources) == 2
    banks = [s["metadata"]["bank_name"] for s in sources]
    assert "A Bank" in banks
    assert "B Bank" in banks
