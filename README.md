# tatlidilyilanideligindencikarir

Senaryo 2 — Yapay Zeka Dil Ajanları Yarışması (4 Kişilik Ekip, Temmuz–Ağustos 2026)

## Proje Özeti

Katılım bankalarının kampanya metinlerinden (kâr payı oranı, vade, kampanya avantajı, hedef kitle) NLP ile bilgi çıkaran, bu bilgileri standart formata dönüştüren, bankalar arası karşılaştırma sunan ve kullanıcıya dashboard + chatbot üzerinden erişim sağlayan bir sistem.

## Teknik Mimari (Özet)

```
Veri Toplama (Scraper) → Ham Metin Deposu
→ Ön İşleme (temizleme, normalizasyon) → Yapılandırılmış Metin
→ Bilgi Çıkarımı (NER / Kural Tabanlı + LLM Hibrit) → Yapılandırılmış Veri (JSON/DB)
→ Kampanya Sınıflandırma → Kategori Etiketleri
→ Karşılaştırma Motoru → Dashboard API
→ Chatbot (RAG tabanlı) → Kullanıcı Arayüzü
```

Detaylar için `ARCHITECTURE.md` dosyasına bakın.

## Teknoloji Yığını

| Katman | Teknoloji |
| --- | --- |
| Veri Toplama | Python: requests, BeautifulSoup / Scrapy, Selenium (gerekirse) |
| Veri Deposu | PostgreSQL veya SQLite + JSON alanları |
| Bilgi Çıkarımı | spaCy (Türkçe model) + regex kuralları + açık kaynak LLM (Ollama) |
| Sınıflandırma | scikit-learn (TF-IDF+SVM) veya BERTurk fine-tune |
| Backend API | FastAPI (Python) |
| Dashboard | React + Recharts/Plotly ya da Streamlit |
| Chatbot | RAG: LangChain/LlamaIndex + yerel LLM + Chroma/FAISS |
| Dağıtım | Docker Compose (tamamen on-premise, internet bağımlılığı yok) |

## ⚠️ Kritik Kısıtlar

- **Ücretli hiçbir yazılım/servis kullanılamaz** — her şey açık kaynak olmalı.
- **Ücretli API tabanlı LLM'ler (OpenAI, Anthropic API vb.) YASAK.** Sadece yerel/açık kaynak LLM (Ollama vb.).
- Çözüm tamamen on-premise çalışabilmeli, dış servislere bağımlı olmamalı.
- Model başarısı değerlendirmenin %30'u — bilgi çıkarımı kalitesine öncelik verilmeli.
- Kod haftalık commit edilmeli (zorunlu, en az haftada bir), aksi halde teslim eksikliği sayılır.

## Kurulum

> **Not:** Bu proje sıfırdan bir Python/conda ortamı oluşturmaz. Hazırda var olan `katilim-nlp` conda ortamı İSTİSNASIZ olarak kullanılmalıdır.

```bash
git clone <repo-url>
cd katilim-bankaciligi-nlp
conda activate katilim-nlp
cp .env.example .env
docker compose up --build
```

Modeller %100 çevrimdışı çalışır: kullanılacak yerel model(ler) önceden `data/models/` klasörüne manuel olarak konulmalı ve `.env` içindeki `LOCAL_MODEL_PATH` değişkeni bu konumu göstermelidir. Hiçbir kütüphane/ajan internetten model indirmeye teşebbüs etmemelidir.

## Çalıştırma

### Tüm Sistem (Docker Compose)

```bash
conda activate katilim-nlp
cp .env.example .env
docker compose up --build
```

Bu komut PostgreSQL, Ollama (yerel LLM) ve FastAPI backend servislerini ayağa kaldırır. Backend Swagger arayüzü: `http://localhost:8000/docs`.

### Sadece Backend (yerel)

```bash
conda activate katilim-nlp
uvicorn src.backend.main:app --reload
```

### Dashboard + Chatbot (Streamlit ön yüz)

```bash
conda activate katilim-nlp
streamlit run src/frontend/app.py
```

### Testler

```bash
pytest tests/
```

## Teslim Edilecekler Durumu

| Teslim Kalemi | Durum |
| --- | --- |
| Kaynak kod (GitHub, Apache 2.0, `BilisimVadisi2026` etiketli) | ✅ Tamamlandı |
| Kurulum/çalıştırma talimatları (README) | ✅ Bu dosya |
| Demo videosu (maks. 5 dk) | ⏳ Ekip tarafından çekilecek (agent üretemez) |
| Proje dokümantasyonu (mimari, NLP, veri, karşılaştırma, sonuçlar) | ✅ `docks/` altında |
| Sunum materyali (PDF + PPTX) | ⏳ Ekip tarafından hazırlanacak (agent üretemez) |
| Haftalık GitHub güncellemeleri | ✅ Her görev sonrası commit edildi |

> Not: Demo videosu ve sunum dosyaları (PDF/PPTX) fiziksel/insan işidir; coding
> agent tarafından otomatik üretilemez. Gerekli içerik (ekran akışı senaryosu,
> anlatım taslağı) `docks/` dokümanlarından ve bu README'den türetilebilir.

## Repo Yapısı

```
katilim-bankaciligi-nlp/
├── README.md              # İnsan için: proje özeti, kurulum
├── CLAUDE.md               # Coding agent için: proje context'i
├── AGENTS.md               # Agent-agnostic context (CLAUDE.md buna referans verir)
├── ARCHITECTURE.md         # Teknik mimari kararları
├── PROGRESS.md             # Canlı durum takibi
├── DECISIONS.md            # ADR tarzı kararlar ve gerekçeleri
├── TASKS.md                # Görev listesi, sorumlu, durum
├── docks/
│   ├── data-schema.md
│   ├── api-spec.md
│   └── nlp-approach.md
├── data/
├── src/
│   ├── scraper/           # Veri toplama, temizleme
│   ├── nlp/               # Ön işleme, bilgi çıkarımı, sınıflandırma
│   ├── database/          # SQLAlchemy modelleri ve bağlantı
│   ├── backend/           # FastAPI (api/routes, services, repositories, core)
│   │   ├── api/routes/    # İnce route handler'lar
│   │   ├── services/      # İş mantığı (comparison, chatbot, campaign)
│   │   ├── repositories/  # DB erişim (Repository Pattern)
│   │   └── core/          # config, db, embeddings, vector_store, llm_factory
│   └── frontend/
├── tests/
├── docker-compose.yml     # db + ollama + backend
├── Dockerfile
├── requirements.txt
└── .env.example
```

### Backend API

FastAPI ile katmanlı mimari (Repository / Service / Factory / DI). Tüm uç
noktalar `docks/api-spec.md` içinde belgelenmiştir; canlı Swagger arayüzü
`uvicorn src.backend.main:app --reload` sonrası `http://localhost:8000/docs`
adresindedir. RAG chatbot (`/api/chat`) vektör arama + yerel LLM (Ollama)
kullanır; tamamen çevrimdışı çalışır.

## Ekip

| Rol | Sorumluluk |
| --- | --- |
| Kişi 1 | Veri Mühendisi (Data Collection) |
| Kişi 2 | NLP / Model Mühendisi |
| Kişi 3 | Backend / Sistem Mühendisi |
| Kişi 4 | Ürün / Arayüz Mühendisi |

## Teslim Edilecekler

- Kaynak kod (GitHub, Apache 2.0 lisanslı, "BilisimVadisi2026" etiketli)
- Kurulum/çalıştırma talimatları (README)
- Demo videosu (maks. 5 dakika)
- Proje dokümantasyonu (mimari, NLP yaklaşımı, veri seti, ön işleme, karşılaştırma mantığı, sonuçlar)
- Sunum materyali (PDF ve PPTX)
- Haftalık GitHub güncellemeleri