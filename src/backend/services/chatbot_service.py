"""RAG tabanlı chatbot iş mantığı (Service Layer Pattern)."""

from typing import Any

from src.backend.core.llm_factory import LLMClient, LLMClientFactory
from src.backend.core.vector_store import VectorStore


class ChatbotService:
    """Vektör aramadan bağlam toplayıp yerel LLM ile yanıt üreten RAG servisi."""

    def __init__(self, vector_store: VectorStore, llm: LLMClient | None = None) -> None:
        """Vektör deposunu ve LLM istemcisini enjekte eder."""
        self.vector_store = vector_store
        self.llm = llm or LLMClientFactory.main_responser()

    def _build_prompt(self, question: str, contexts: list[str]) -> str:
        """Retrieval bağlamından instruct uyumlu bir istem metni oluşturur."""
        context_block = "\n\n".join(f"- {c}" for c in contexts) if contexts else "(bağlam bulunamadı)"
        system = (
            "Sen bir katılım bankası kampanya asistanısın.\n"
            "KURALLAR:\n"
            "1. Sadece sana verilen BAĞLAM alanındaki bilgilere dayanarak cevap ver.\n"
            "2. Sorunun cevabı bağlamda yoksa veya emin değilsen, kesinlikle uydurma/anlamsız cümle kurma ve net olarak 'Bu bilgiye sahip değilim' de.\n"
            "3. Yanıtlarında asla varsayımlar yapma, uydurma veriler ekleme ve gramatik olarak düzgün, anlaşılır Türkçe cümleler kullan.\n"
            "4. Kullanıcı girdisindeki 'sence' gibi öznel ifadeleri aynen çıktıya karıştırma. Tamamen tarafsız ve profesyonel ol.\n"
            "5. Eğer soru karşılaştırma içeriyorsa ve bağlamda birden fazla banka bilgisi varsa, bu bankaların kampanya ve oranlarını objektif olarak karşılaştır."
        )
        user = (
            f"Aşağıdaki bağlam bilgilerine göre soruyu yanıtla.\n\n"
            f"BAĞLAM:\n{context_block}\n\n"
            f"SORU: {question}"
        )
        return (
            "<|im_start|>system\n"
            f"{system}<|im_end|>\n"
            "<|im_start|>user\n"
            f"{user}<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

    def answer(self, question: str, top_k: int = 3, threshold: float = 0.15) -> dict[str, Any]:
        """Soruyu yanıtlar ve kullanılan kaynakları döner."""
        # Karşılaştırma kelimelerini kontrol et
        comparative_keywords = ["hangisi", "nereden", "nerden", "karşılaştır", "karsilastir", "kıyasla", "en yüksek", "en yuksek", "en iyi", "en uygun", "fark"]
        is_comparative = any(k in question.lower() for k in comparative_keywords)

        # Karşılaştırmalı sorgularda daha geniş havuz çek
        pool_size = max(top_k * 4, 12) if is_comparative else max(top_k * 2, 6)
        retrieved = self.vector_store.query(question, top_k=pool_size)

        # 1. Relevance / Similarity Threshold Filtrelemesi
        valid_results = [r for r in retrieved if r.get("score", 0.0) >= threshold]

        # 2. Deduplication (Tekilleştirme)
        seen_urls = set()
        seen_texts = set()
        seen_ids = set()
        deduped = []
        for r in valid_results:
            doc_id = r.get("id")
            if doc_id in seen_ids:
                continue
            url = r.get("metadata", {}).get("source_url")
            if url:
                if url in seen_urls:
                    continue
            text = r.get("text", "")
            if text:
                if text in seen_texts:
                    continue
            seen_ids.add(doc_id)
            if url:
                seen_urls.add(url)
            if text:
                seen_texts.add(text)
            deduped.append(r)

        # 3. Karşılaştırma Desteği / Çeşitlendirme (Diversity)
        if is_comparative and len(deduped) > 1:
            bank_groups = {}
            for r in deduped:
                meta = r.get("metadata") or {}
                bank_name = str(meta.get("bank_name", meta.get("bankaAdi", "Bilinmeyen")))
                bank_groups.setdefault(bank_name, []).append(r)
            
            diverse_results = []
            max_rounds = max(len(g) for g in bank_groups.values()) if bank_groups else 0
            for round_idx in range(max_rounds):
                for bank, group in bank_groups.items():
                    if round_idx < len(group):
                        diverse_results.append(group[round_idx])
            final_retrieved = diverse_results[:top_k]
        else:
            final_retrieved = deduped[:top_k]

        contexts = [r["text"] for r in final_retrieved]
        sources = [
            {
                "id": r["id"],
                "source_url": r.get("metadata", {}).get("source_url"),
                "score": r["score"],
                "metadata": r.get("metadata", {}),
                "text": r["text"],
            }
            for r in final_retrieved
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
