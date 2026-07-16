"""RAG chatbot servisi ve /api/chat uç noktası için testler."""

from src.backend.core.embeddings import LocalLexicalEmbedder
from src.backend.core.vector_store import InMemoryVectorStore
from src.backend.services.chatbot_service import ChatbotService


class _FakeLLM:
    """Test için sabit yanıt döndüren sahte LLM istemcisi."""

    def generate(self, prompt: str) -> str:
        """İstem metninden bağlamı çıkarıp sabit bir yanıt üretir."""
        return "Bu bir test yanıtıdır."


def _store_with_data() -> InMemoryVectorStore:
    """Örnek kampanya verisiyle dolu bir vektör deposu döner."""
    store = InMemoryVectorStore(embedder=LocalLexicalEmbedder())
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
    service = ChatbotService(vector_store=InMemoryVectorStore(), llm=_FakeLLM())
    result = service.answer("merhaba")
    assert result["answer"] == "Bu bir test yanıtıdır."
    assert result["sources"] == []
