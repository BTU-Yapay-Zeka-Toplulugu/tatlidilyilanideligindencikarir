"""RAG chatbot API uç noktası (Frontend ile entegre edilecek)."""

from fastapi import APIRouter, Depends, Query

from src.backend.core.llm_factory import LLMClient, LLMClientFactory
from src.backend.core.vector_store import VectorStore, get_vector_store
from src.backend.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/api", tags=["chatbot"])

# Model (2GB GGUF) yalnızca bir kez yüklenir; her istekte yeniden yüklenmez.
_llm_cache: LLMClient | None = None


def _get_llm() -> LLMClient:
    """Chatbot için ana yanıtlayıcı modelini önbelleğe alır (tek yükleme)."""
    global _llm_cache
    if _llm_cache is None:
        _llm_cache = LLMClientFactory.main_responser()
    return _llm_cache


def _chatbot_service(
    store: VectorStore = Depends(get_vector_store),
) -> ChatbotService:
    """ChatbotService örneğini vektör deposu ve LLM ile enjekte eder (DI)."""
    return ChatbotService(vector_store=store, llm=_get_llm())


@router.get("/chat")
def chat(
    question: str = Query(..., description="Kullanıcının sorusu"),
    top_k: int = Query(3, description="Retrieval için çekilecek bağlam sayısı"),
    service: ChatbotService = Depends(_chatbot_service),
):
    """Vektör araması ve yerel LLM ile soruyu yanıtlar."""
    return service.answer(question, top_k=top_k)
