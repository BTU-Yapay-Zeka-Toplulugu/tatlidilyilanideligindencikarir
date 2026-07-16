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

- **Tarih:** Açık — henüz kesinleşmedi
- **Durum:** Beklemede (karar gerekiyor)
- **Bağlam:** Ollama üzerinden çalıştırılacak Türkçe/multilingual açık kaynak modelin hangisi olacağı netleşmedi.
- **Karar:** (Henüz verilmedi)
- **Gerekçe:** (Kick-off sonrası Kişi 2/3 tarafından donanım kısıtları ve Türkçe performansına göre belirlenecek.)
- **Alternatifler:** Değerlendirilecek adaylar: Türkçe fine-tune edilmiş Llama/Mistral varyantları, multilingual modeller (Ollama kütüphanesinde mevcut olanlar).
- **Sonuçlar:** Bu karar netleşene kadar `src/nlp/` modülü model-agnostik bir arayüz (interface) ile yazılmalı.

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