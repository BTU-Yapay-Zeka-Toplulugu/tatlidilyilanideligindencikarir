"""RAG chatbot API uç noktası (Frontend ile entegre edilecek)."""

from fastapi import APIRouter, Depends, Query

from src.backend.core.llm_factory import LLMClientFactory
from src.backend.core.vector_store import VectorStore, get_vector_store
from src.backend.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/api", tags=["chatbot"])


def _chatbot_service(
    store: VectorStore = Depends(get_vector_store),
) -> ChatbotService:
    """ChatbotService örneğini vektör deposu ve LLM ile enjekte eder (DI)."""
    return ChatbotService(vector_store=store, llm=LLMClientFactory.create())


@router.get("/chat")
def chat(
    question: str = Query(..., description="Kullanıcının sorusu"),
    top_k: int = Query(3, description="Retrieval için çekilecek bağlam sayısı"),
    service: ChatbotService = Depends(_chatbot_service),
):
    """Vektör araması ve yerel LLM ile soruyu yanıtlar."""
    return service.answer(question, top_k=top_k)
