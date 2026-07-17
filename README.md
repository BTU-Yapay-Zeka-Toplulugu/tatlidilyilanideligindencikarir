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
| Dashboard | React + Vite + Tailwind + Recharts |
| Chatbot | RAG: yerel LLM (llama.cpp) + Chroma/InMemory vektör DB + WebSocket streaming |
| Dağıtım | Docker Compose (opsiyonel) veya lokal (uvicorn + npm run dev), tamamen on-premise |

## ⚠️ Kritik Kısıtlar

- **Ücretli hiçbir yazılım/servis kullanılamaz** — her şey açık kaynak olmalı.
- **Ücretli API tabanlı LLM'ler (OpenAI, Anthropic API vb.) YASAK.** Sadece yerel/açık kaynak LLM (Ollama vb.).
- Çözüm tamamen on-premise çalışabilmeli, dış servislere bağımlı olmamalı.
- Model başarısı değerlendirmenin %30'u — bilgi çıkarımı kalitesine öncelik verilmeli.
- Kod haftalık commit edilmeli (zorunlu, en az haftada bir), aksi halde teslim eksikliği sayılır.

## Kurulum

> **Not:** Bu proje sıfırdan bir Python/conda ortamı oluşturmaz. Hazırda var olan `katilim-nlp` conda ortamı İSTİSNASIZ olarak kullanılmalıdır.

**Backend (Python/FastAPI):**
```bash
git clone <repo-url>
cd katilim-bankaciligi-nlp
conda activate katilim-nlp
cp .env.example .env
# Veritabanını tohumla (bankalar + kampanyalar)
python -m src.database.seed
```

**Frontend (React/Vite):** `src/frontend/.env` içinde backend adresi tanımlıdır
(`VITE_API_BASE_URL`, `VITE_CHATBOT_WS_URL`). Gerekirse düzenleyin.
```bash
cd src/frontend
npm install
```

Modeller %100 çevrimdışı çalışır: kullanılacak yerel model(ler) `model/` dizinine (`.gguf` olarak) konulur ve `.env` içindeki `LOCAL_MODEL_PATH` değişkeni bu yolu gösterir. Dizin içindeki ilk `.gguf` otomatik yüklenir. LLM, **llama.cpp** (`llama-cpp-python`) ile doğrudan çalıştırılır; Ollama gerektirmez. Mevcut test modeli: `qwen2.5-3b-instruct-q4_k_m.gguf`. Hiçbir kütüphane/ajan internetten model indirmeye teşebbüs etmemelidir.

> **Docker:** Bu proje Docker Compose ile de dağıtılabilir (`docker-compose.yml` mevcuttur), ancak bu kılavuz lokal (Docker'sız) çalıştırmayı anlatır.

## Çalıştırma (Lokal, Docker'sız)

### 1) PostgreSQL'in çalışır durumda olması
Backend `.env` içindeki `DATABASE_URL` ile PostgreSQL'e bağlanır (varsayılan `localhost:5433`).

### 2) Backend (terminal 1)
```bash
conda activate katilim-nlp
uvicorn src.backend.main:app --reload
# Swagger: http://localhost:8000/docs
```

### 3) Frontend (terminal 2)
```bash
cd src/frontend
npm run dev
# Varsayılan: http://localhost:5173
```

Backend ve frontend aynı makinede çalıştığında frontend `src/frontend/.env` içindeki
`VITE_API_BASE_URL=http://localhost:8000` üzerinden backend'e bağlanır (CORS `*`).

### Testler
```bash
conda activate katilim-nlp
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

FastAPI ile katmanlı mimari (Repository / Service / Factory / DI). Canlı Swagger
arayüzü `uvicorn src.backend.main:app --reload` sonrası `http://localhost:8000/docs`
adresindedir.

Frontend'in kullandığı uç noktalar (Türkçe alan adlı response'lar):
- `GET /finansman/ozet` → finansman özet kalemleri
- `GET /finansman/karsilastirma` (`bankaIds`, `urunTuru`) → bankaya göre gruplu karşılaştırma
- `GET /finansman/bankalar` → banka listesi (filtre seçenekleri)
- `POST /chat/mesaj` (`{mesaj, oturumId}`) → chatbot yanıtı
- `GET /chat/gecmis?oturumId` → sohbet geçmişi
- `POST /chat/temizle` (`{oturumId}`) → oturum temizleme
- `WS /ws/chat` → RAG streaming (chunk/atiflar/bitti paketleri)

Eski `/api/*` uç noktaları geriye dönük uyumluluk için korunur. RAG chatbot
vektör arama + yerel LLM (llama.cpp) kullanır; tamamen çevrimdışı çalışır.

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