# DECISIONS.md

ADR (Architecture Decision Record) tarzında alınan kararlar. Yeni bir karar alındığında en alta yeni bir bölüm olarak eklenir, mevcut kararlar silinmez/değiştirilmez (gerekirse "Durum: Değiştirildi → bkz. ADR-00X" notu eklenir).

Format:
```
## ADR-00X: [Başlık]
- **Tarih:**
- **Durum:** Kabul edildi / Değiştirildi / Reddedildi
- **Bağlam:** Neden bu karar gerekti
- **Karar:** Ne karar verildi
- **Gerekçe:** Neden bu seçim yapıldı
- **Alternatifler:** Değerlendirilen diğer seçenekler
- **Sonuçlar:** Bu kararın etkileri
```

---

## ADR-001: Teknoloji Yığını Seçimi

- **Tarih:** Proje planlama aşaması
- **Durum:** Kabul edildi
- **Bağlam:** Yarışma kuralları gereği tüm çözüm açık kaynak ve on-premise olmalı, ücretli servis/LLM API kullanılamaz.
- **Karar:** Python tabanlı stack (FastAPI, spaCy, scikit-learn/BERTurk, LangChain/LlamaIndex, Chroma/FAISS), React veya Streamlit frontend, Docker Compose dağıtım.
- **Gerekçe:** Tamamen açık kaynak, on-premise çalıştırılabilir, Türkçe NLP için topluluk desteği (spaCy Türkçe model, BERTurk) mevcut.
- **Alternatifler:** Ücretli LLM API'leri (OpenAI vb.) — yarışma kuralı gereği elendi. Bulut tabanlı vektör DB'ler (Pinecone vb.) — on-premise kısıtı gereği elendi, yerine Chroma/FAISS seçildi.
- **Sonuçlar:** Yerel LLM performansı ücretli API'lere göre daha sınırlı olabilir; bu yüzden kural tabanlı + NER hibrit yaklaşım öncelikli tutuldu.

## ADR-002: Bilgi Çıkarımında Hibrit Yaklaşım (Kural Tabanlı + LLM)

- **Tarih:** Proje planlama aşaması
- **Durum:** Kabul edildi
- **Bağlam:** Değerlendirmenin %30'u model başarısına dayanıyor; bilgi çıkarımı kalitesi kritik.
- **Karar:** Kâr payı oranı, vade, tutar gibi yapılandırılmış alanlar için önce regex/kural tabanlı çıkarım, belirsiz durumlarda yerel LLM desteği.
- **Gerekçe:** Kural tabanlı yöntemler yüksek doğruluk ve hız sağlar; LLM ise regex'in yakalayamadığı doğal dil varyasyonlarını tolere eder.
- **Alternatifler:** Sadece LLM tabanlı çıkarım — daha az öngörülebilir ve daha yavaş olacağından elendi. Sadece kural tabanlı — doğal dil varyasyonlarında kırılgan olacağından tek başına yetersiz bulundu.
- **Sonuçlar:** İki katmanlı bir pipeline gerektirir; Kişi 2'nin iş yükünü artırır ama doğruluğu yükseltir.

## ADR-003: Yerel LLM Seçimi

- **Tarih:** 16 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** Ollama üzerinden çalıştırılacak Türkçe/multilingual açık kaynak modelin hangisi olacağı netleşmemişti.
- **Karar:** Model doğrudan **llama.cpp (llama-cpp-python)** ile çalıştırılır; Ollama sunucusu kullanılmaz. Test/model için seçilen model: **`qwen2.5-3b-instruct-q4_k_m.gguf`** (Qwen2.5 3B, Q4_K_M quantized, multilingual/TR dostu, çevrimdışı). Model dosyası `model/` dizinine konur ve `LOCAL_MODEL_PATH` (`.env`) ile gösterilir; dizin ise içindeki ilk `.gguf` otomatik yüklenir. Daha iyi bir model için sadece yeni `.gguf` `model/` altına bırakılır.
- **Gerekçe:** llama.cpp saf Python + C binding ile çevrimdışı, açık kaynak ve hızlıdır; Ollama'ya bağımlılık gerektirmez. `LLMClientFactory` (auto→gguf) ile model değişimi kodsuz yapılır (ADR-003 sonucu karşılandı).
- **Alternatifler:** Ollama (ayrı servis/indirme gerektirir; elendi), Türkçe Llama/Mistral fine-tune (ileride `model/` altına GGUF olarak eklenebilir), HuggingFace üzerinden ağırlık indirme (internet bağımlılığı yasağı gereği elendi).
- **Sonuçlar:** `src/backend/core/llm_factory.py` → `GgufLLMClient` (llama.cpp) eklendi; `LLM_BACKEND=auto|gguf|ollama` desteği. `requirements.txt`'e `llama-cpp-python` eklendi. Chatbot için instruct şablonu (`<|im_start|>`/`) kullanılır.

## ADR-004: Veri Deposu — PostgreSQL vs SQLite

- **Tarih:** 16 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** Hem PostgreSQL hem SQLite seçenek olarak planda yer alıyordu. Docker Compose ve on-premise kalıcılık/çoklu erişim desteği gereklilikleri bulunmaktaydı.
- **Karar:** Veri tabanı olarak PostgreSQL seçilmiştir. SQLAlchemy ORM kullanılarak veritabanı işlemleri soyutlanacaktır.
- **Gerekçe:** PostgreSQL, Docker ortamlarında ölçeklenebilir, eşzamanlı erişimde daha güvenlidir ve üretim ortamına uygundur. SQLAlchemy kullanımı ise gerektiğinde SQLite'a veya başka bir SQL veri tabanına geçişi kolaylaştırır.
- **Alternatifler:** SQLite (prototipleme kolaylığı için düşünüldü ancak eşzamanlı yazma sınırları nedeniyle elendi).
- **Sonuçlar:** Docker Compose dosyasına PostgreSQL servisi eklenmelidir. Veri saklama ve FastAPI backend işlemlerinde PostgreSQL bağlantısı kullanılacaktır.

## ADR-005: Vektör Veritabanı — Chroma (RAG için)

- **Tarih:** 16 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** RAG tabanlı chatbot için açık kaynak, on-premise çalışabilen bir vektör DB gerekiyordu (ADR-003 bağlamı). TASKS.md Chroma/FAISS seçeneklerini sunuyordu; net karar yoktu.
- **Karar:** Vektör DB olarak **Chroma** seçilmiştir. Üretimde diskte kalıcı (`PersistentClient`) kullanılır. Test/prototip için harici bağımlılık gerektirmeyen saf-Python `InMemoryVectorStore` (sklearn cosine similarity) varsayılan olarak kullanılır.
- **Gerekçe:** Chroma; metadata filtreleme, diskte kalıcılık ve Python ile kolay entegrasyon sunar, tamamen açık kaynak ve on-premise'dir. Embedding üretimi için `LOCAL_MODEL_PATH` (ADR-003) üzerinden çevrimdışı `sentence-transformers` modeli kullanılır; harici indirme olmadan çalışması için varsayılan olarak çevrimdışı `LocalLexicalEmbedder` (bag-of-words) sağlanmıştır.
- **Alternatifler:** FAISS (düşük seviyeli, kalıcılık/metadata yöneticisi manuel; elendi), Pinecone (ücretli/bulut; ADR-001 gereği elendi).
- **Sonuçlar:** `src/backend/core/vector_store.py` (VectorStoreFactory + Chroma/InMemory) ve `src/backend/core/embeddings.py` (Embedder arayüzü) oluşturuldu. Docker imajına `chromadb` bağımlılığı eklenmelidir.

## ADR-006: Frontend Teknoloji Seçimi — Streamlit

- **Tarih:** 16 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** README/ARCHITECTURE "React + Recharts/Plotly ya da Streamlit" diyordu; net seçim yoktu. Yarışma demosu için hızlı, çevrimdışı, Python-tabanlı ve backend ile aynı dilde çalışan bir ön yüz gerekiyordu.
- **Karar:** Dashboard ve chatbot arayüzü için **Streamlit** kullanılacaktır. Backend FastAPI'ye HTTP ile bağlanır; grafikler için `plotly`/`streamlit` yerleşik bileşenleri kullanılır.
- **Gerekçe:** Sıfır frontend build adımı, hızlı prototip, Python ekibi için düşük öğrenme eğrisi; tamamen açık kaynak ve on-premise. Gerekirse ileride React'e geçiş için arayüz API üzerinden ayrık tutulur.
- **Alternatifler:** React + Recharts/Plotly (daha üretim kaliteli ama ayrı build zinciri/JS ekibi gerektirir; elendi).
- **Sonuçlar:** `src/frontend/` altına Streamlit uygulaması (`app.py`) yazılacak; `requirements.txt`'e `streamlit`, `plotly` eklenecek.

## ADR-007: Demo Videosu ve Sunum (PDF/PPTX) Üretimi

- **Tarih:** 16 Temmuz 2026
- **Durum:** Kabul edildi (kapsam sınırı)
- **Bağlam:** TASKS.md Hafta 5, Kişi 4 "Demo videosu çekimi ve sunum (PDF+PPTX) hazırlığı" maddesi, fiziksel/insan işi gerektirir; bir coding agent video çekemez ve binary sunum dosyası üretemez.
- **Karar:** Agent; README finalize, proje dokümantasyonu (`docks/`) ve kaynak kodu tamamlar. Demo videosu ve PPTX/PDF sunum dosyaları **ekip tarafından manuel** hazırlanır. Gerekli anlatım içeriği dokümantasyonlardan türetilebilir şekilde bırakılır.
- **Gerekçe:** Üretim dışı binary varlıkları otomatik üretmek mümkün değil; yarışma teslimi için insan onayı gereklidir.
- **Alternatifler:** Yok (fiziksel kısıt).
- **Sonuçlar:** README "Teslim Edilecekler Durumu" tablosunda bu kalemler "ekip tarafından tamamlanacak" olarak işaretlendi.