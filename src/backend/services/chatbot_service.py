"""RAG tabanlı chatbot iş mantığı (Service Layer Pattern)."""

from typing import Any

from src.backend.core.llm_factory import LLMClient, LLMClientFactory
from src.backend.core.vector_store import VectorStore


class ChatbotService:
    """Vektör aramadan bağlam toplayıp yerel LLM ile yanıt üreten RAG servisi."""

    def __init__(self, vector_store: VectorStore, llm: LLMClient | None = None) -> None:
        """Vektör deposunu ve LLM istemcisini enjekte eder."""
        self.vector_store = vector_store
        self.llm = llm or LLMClientFactory.create()

    def _build_prompt(self, question: str, contexts: list[str]) -> str:
        """Retrieval bağlamından LLM için bir istem metni oluşturur."""
        context_block = "\n\n".join(f"- {c}" for c in contexts) if contexts else "(bağlam bulunamadı)"
        return (
            "Aşağıdaki katılım bankası kampanya bilgilerini kullanarak "
            "soruyu Türkçe ve kısa şekilde yanıtla.\n\n"
            f"BAĞLAM:\n{context_block}\n\n"
            f"SORU: {question}\n\nYANIT:"
        )

    def answer(self, question: str, top_k: int = 3) -> dict[str, Any]:
        """Soruyu yanıtlar ve kullanılan kaynakları döner."""
        retrieved = self.vector_store.query(question, top_k=top_k)
        contexts = [r["text"] for r in retrieved]
        sources = [
            {"id": r["id"], "source_url": r.get("metadata", {}).get("source_url"), "score": r["score"]}
            for r in retrieved
        ]
        prompt = self._build_prompt(question, contexts)
        try:
            generated = self.llm.generate(prompt)
        except Exception as exc:  # LLM çevrimdışı/eksikse kaynaklarla zarifçe düş
            generated = (
                "Yerel LLM şu anda kullanılamıyor (model yüklenmemiş olabilir). "
                f"İlgili kampanya bağlamı {len(contexts)} kayıtta bulundu."
            )
            sources.append({"note": f"llm_error: {exc}"})
        return {"answer": generated, "sources": sources}
