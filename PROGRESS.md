# PROGRESS.md

> Bu dosya projenin **canlı durumu**dur. Her oturum/görev sonunda güncellenmelidir. Yeni bir agent devraldığında önce burayı okumalıdır.

## Son Güncelleme

- **Tarih:** 19 Temmuz 2026
- **Güncelleyen:** Antigravity AI Coding Agent
- **Genel Durum:** RAG Chatbot'un backend ve frontend (React-Vite) entegrasyonu tamamlandı. Arayüzün backend ile sorunsuz konuşabilmesi için `.env` yapılandırıldı, CORS ve API proxy kanalları REST ve WebSocket için doğrulandı. Chatbot arayüzündeki atıflar tıklanabilir linklere (`<a>` tag) dönüştürülerek kullanıcı deneyimi iyileştirildi. SQLite tabanlı canlı backend ve Vite dev server üzerinde yapılan E2E UI testleri (veri getirme, streaming mesajlaşma, atıf listeleme ve alakasız soru filtreleme) başarıyla tamamlandı. `pytest tests/` → 126 passed, 8 skipped.

## Bu Oturumda Yapılanlar (2026-07-19, Frontend Entegrasyonu ve UI E2E Doğrulama)

### 1. Vite Frontend API & WebSocket Bağlantısı
- **Ortam Değişkenleri (`src/frontend/.env`):** Vite projesinin kök dizinine yerel backend adreslerini (`VITE_API_BASE_URL` ve `VITE_CHATBOT_WS_URL`) tanımlayan `.env` dosyası eklendi.
- **Tıklanabilir Atıflar (`ChatMessage.jsx`):** Chatbot arayüzünde listelenen atıfların (kaynakların) banka ismi ve kampanya başlığı bilgileriyle birlikte tıklanabilir link (`<a>` tag) olarak açılması sağlandı. `PropTypes` şeması `url` alanını da kapsayacak şekilde güncellendi.
- **Vite Proxy Doğrulaması:** Vite geliştirme sunucusunun (port 5173) `/finansman` ve `/chat` proxy yönlendirmeleri ile WebSocket (`/ws`) tünellemesinin FastAPI backend sunucusuna (port 8000) veri kaybı olmadan bağlandığı kanıtlandı.

### 2. Tam Entegrasyon ve UI E2E Testleri
- **Vite Build Başarısı:** React-Vite uygulamasının derleme zinciri `npm run build` komutuyla test edildi; kod blokları ve markdown bileşenleriyle birlikte **0 hata ile başarıyla derlendi**.
- **Dashboard Veri Yükleme:** Arayüz dev sunucusu üzerinden yapılan GET isteklerinde `/finansman/bankalar`, `/finansman/ozet` ve `/finansman/karsilastirma` uç noktalarından gelen gerçekçi kampanya ve banka kayıtlarının başarıyla çekildiği doğrulandı.
- **Chatbot UI Streaming & Atıf Testi:** WebSocket proxy kanalı üzerinden gönderilen karşılaştırmalı sorunun (`"vadeli katılım hesabı sence nerden acmaliyim"`) RAG motorundan 3 farklı bankanın (T.O.M., Ziraat ve Adil Katılım) atıflarını (isim, başlık, url) ve cevap chunk'larını UI'a başarıyla akıttığı doğrulandı. Alakasız sorularda benzerlik eşiğinin doğru çalışarak arayüzde doğrudan "Bu konuda bilgiye sahip değilim." yanıtını döndürdüğü kanıtlandı.

## Bu Oturumda Yapılanlar (2026-07-18, Faz 1–5)

### Faz 1 — Dinamik & Recursive Keşif (ZATEN MEVCUT, ADR-012)
- Statik path/liste YOK; `recursive_discovery.py` BFS + `config.DISCOVERY_KEYWORDS`
  + katı limitler (`max_depth=3`, `max_pages=60`, per-request timeout, retry).
- **Kanıt:** Banka 1 (ADİL) foreground'da 18 sayfa ~22s'de tarandı, her sayfada
  `visiting:` logu; 10 banka tam crawl ~22 dk'da, hiçbir bankada takılmadan bitti
  (her banka `recursive keşif bitti` logu üretti). 1442 HTML + PDF havuzu keşfedildi.

### Faz 2 — PDF Extraction (İYİLEŞTİRME)
- **Donma riski KAPATILDI:** `pdf_crawler` parse (`pdfplumber`) VE download
  (`requests.get`, DNS takılması dahil) ayrı thread + duvar saati timeout ile
  korundu (`PDF_PARSE_TIMEOUT=30s`, download `timeout+10s`); executor
  `shutdown(wait=False)` ile takılan worker beklenmeden bırakılır. Tek PDF artık
  tüm taramayı donduramaz. (Önceki denemede "Genel Kredi Sözleşmesi.pdf" 10+ dk
  takıyordu → artık 30s'de atlanıyor.)
- **Filtre kalitesi:** Kampanya PDF filtresi güçlü anahtar kelimelere daraltıldı;
  KVKK/gizlilik/ücret tarifesi/fee disclosure artık kampanya sayılmaz. Dosya adı
  tabanlı resmi döküman elemesi (`IRRELEVANT_PDF_FILENAME`) indirmeye gitmeden
  uygulanır.
- **Kanıt:** Tam crawl'da 13 kampanya PDF'i işlendi (önceki 36'ya göre gürültü
  azaldı); taranmış/OCR gereken PDF'ler loglanıp atlandı, sistem çökmedi.

### Faz 3 — Birleşik Regex + Model Pipeline (YENİ, ADR-013)
- `src/nlp/pipeline.py`: `run_extraction_pipeline(text)` — regex katmanı →
  model/NER katmanı → `merge_field` uzlaştırma (regex netse kazanır, boşsa model)
  → kanonik normalizasyon (`%X.XX`, `X.XXX TL`, `YYYY-MM-DD`). HTML+PDF AYNI
  fonksiyondan geçer. Strategy Pattern (`ExtractorStrategy`).
- Tarih çıkarımı eklendi; çoklu-oran edge-case'i düzeltildi.
- `campaign_service.ensure_nlp_processed` + `reprocess` pipeline'a bağlandı;
  DB'ye `start_date`/`end_date` kolonu (idempotent migration).
- **Kanıt:** `tests/test_nlp/test_pipeline.py` 10 test (uzlaştırma/kanonik
  form/%2,05→2.05/"500 TL"=="500₺"/tarih/çoklu-oran). Tam suite 131 passed.

### Faz 4 — Veri Yeniden Üretimi + Kalite Kontrolü
- `python -m src.scraper.main` → `campaigns_20260718_173417.json`: **149 kayıt
  (136 HTML + 13 PDF), 10 banka**. `data_cleaner` → 149 temiz kayıt.
- Seed: 10 banka + 3 yeni kampanya. `reprocess`: 239 kampanya (236 güncelleme +
  3 yeni) birleşik pipeline ile. Oran dağılımı: 32 kayıtta oran, **max %50,
  >%50 değer YOK** (imkânsız %70–%100 elendi). Tarihler ISO'da çıkarıldı.

### Faz 5 — Tam E2E Doğrulama
| Alan | Sonuç | Kanıt |
| --- | --- | --- |
| Backend API (REST) | ✅ | `/` , `/finansman/bankalar` (10 banka), `/finansman/ozet` (239 kayıt, gerçek tutar/karOrani), `/finansman/karsilastirma` (239), `/api/campaigns`, `/api/compare` — hepsi 200 + gerçek veri |
| WebSocket / Chatbot | ✅ | `/ws/chat` gerçek mesajla 4 chunk + `bitti` + 3 GERÇEK atıf (banka/ürün/URL) döndü; REST `/chat/mesaj` de RAG kaynaklı cevap + atıf verdi |
| Frontend / Dashboard | ✅ | `npm run build` temiz; `vite preview` servisi `/finansman/ozet`,`/finansman/bankalar`,`/ws/chat` uç noktalarına bağlı (üretim JS'inde doğrulandı); backend 239 gerçek kayıtla dolu |
| Uçtan uca senaryo | ✅ | Tarama→NLP→DB→API→dashboard→chatbot zinciri tutarlı çalıştı |

> Not: WebSocket test istemcisinde `websockets` 16.x varsayılan ping davranışı
> nedeniyle ilk denemede gecikme oldu; sunucu tarafı doğru (ping params verilince
> 4 chunk + atıf akışı geldi). Bu bir backend hatası değil, test istemci ayarıdır.

## Şu An Neredeyiz

- [x] Faz 1: Dinamik/recursive keşif (statik path'ler kaldırıldı, ADR-012)
- [x] Faz 2: PDF extraction + donma riski kapatıldı + filtre kalitesi
- [x] Faz 3: Birleşik regex+model pipeline (ADR-013) + tarih çıkarımı
- [x] Faz 4: Tüm veri yeniden üretildi (149 kayıt, 10 banka) + seed + reprocess
- [x] Faz 5: E2E doğrulama (REST/WS/frontend) — 131 pytest passed
- [ ] Demo videosu (ADR-007 — ekip) ve PPTX/PDF sunum (ADR-007 — ekip)

## Bu Oturumda Yapılanlar (2026-07-17, Faz 1 + Faz 2)

### Faz 1 — Dinamik & Recursive Keşif + PDF Extraction (ADR-011/ADR-012)
- Eski statik `discovery.py` (sitemap-only + sabit `CAMPAIGN_KEYWORDS` + PDF atlama)
  TAMAMEN kaldırıldı. Yerine `recursive_discovery.py`: ana URL'den BFS, anahtar
  kelime filtresi `config.DISCOVERY_KEYWORDS`'te, `max_depth=3`/`max_pages`/`timeout`
  KATI limitli, aynı domain sınırı, **per-page ilerleme logu**.
- Tek akışta hem HTML kampanya sayfaları hem PDF havuzu bulunur. PDF'ler
  `pdf_crawler` ile indirilir → kampanya/anahtar kelime filtresinden geçer →
  pdfplumber ile metne çevrilir → HTML ile AYNI clean/NLP hattından geçer
  (`CampaignData.source_type="pdf"`).
- Taranmış (scanned) PDF'ler tespit edilip OCR yokken atlanır (loglanır), sistem çökmez.
- Tüm 10 banka için dinamik keşif KANITLANDI (per-bank log): örn. ADİL 1 HTML+8 PDF,
  T.O.M. 13 HTML+15 PDF (183 adaydan cap'li), KUVEYT 15 HTML+3 PDF, ZİRAAT 15 HTML+1 PDF.
- Tam pipeline (HTML+PDF) çalıştırıldı → `campaigns_COMBINED_10banks.json`:
  **170 kayıt (134 HTML + 36 PDF), 10 banka**.

### Faz 2.1 — Veri Katmanı
- `data_cleaner` → `campaigns_cleaned.json` (170 kayıt, 10 banka, html+pdf).
- `seed` → PostgreSQL (5440, yerel küme) 10 banka + 112 yeni kampanya.
- `reprocess` → 236 kampanya NLP çıkarımı (124 güncelleme + 112 yeni).
- Doğrulama: 36 PDF-kaynaklı kampanya DB'de; oranlar tutarlı sayısal formatta
  (%100+ imkânsız değer yok — ADR-009 kuralı PDF metninde de geçerli). **PASS**

| Tarih | Alan | Sonuç | Detay |
| --- | --- | --- | --- |
| 2026-07-17 | Veri katmanı (Dinamik Crawler + PDF) | ✅ | 170 kayıt (134 HTML+36 PDF), 10 banka, seed+reprocess hatasız; oran formatı tutarlı |

## Bu Oturumda Yapılan Debug/Düzeltmeler (2026-07-17)

| Tarih | Sorun | Kök sebep | Çözüm | Test sonucu |
| --- | --- | --- | --- | --- |
| 2026-07-17 | Chatbot atıfları hep "Bilinmeyen" | `answer()` sources'a metadata koymuyor, bridge metadata okuyor | sources'a tam metadata+text eklendi | WS+REST testinde gerçek banka/ürün/URL |
| 2026-07-17 | WS sessiz hata + her bağlantıda 2GB model | `except: return` yutuyor; yeni ChatbotService/LLM | app.state.chatbot yeniden kullanımı, loglama, hata'da `bitti` | çoklu mesaj + log OK |
| 2026-07-17 | Uzun yanıtta WS "keepalive ping timeout" | senkron LLM çağrısı olay döngüsünü kilitliyor | LLM `run_in_threadpool` ile çalıştırılıyor | uzun yanıt kopmadan tamamlandı |
| 2026-07-17 | Dashboard tablo/grafik boş (tutar/oran) | `/finansman/karsilastirma` nested dönüyor, frontend düz bekliyor | endpoint düz `FinansmanKalemi[]` döner | 121 satır 0 undefined, 9/9 bar>0 |
| 2026-07-17 | Kâr payı oranı %70–%100 imkânsız değerler | ilk `%N` bağlamsız alınıyor (iade/iştirak/LTV/KDV) | bağlam-duyarlı + makul-band + binlik-guard | önce 10 adet>%50 → sonra 0 |
| 2026-07-17 | Büyük-İ kelimeler eşleşmiyor (sınıflandırma/eleme) | `str.lower()` "İ"→"i̇" (birleşik nokta) | Türkçe-duyarlı `_tr_fold` casefold | `İHTİYAÇ FİNANSMANI`→doğru kategori |
| 2026-07-17 | `pytest tests/` collection kırılıyor | eski Streamlit test'leri kaldırılan modülleri import ediyor | ölü `tests/test_frontend/*` kaldırıldı | 113 passed |
| 2026-07-17 | Sadece 9 banka (10 olmalı - yarışma şartı) | ADİL Katılım keşifte 0 sayfa (kampanya yok/PDF/encoding) | scraper: encoding fix + PDF eleme + kurumsal fallback; ADİL tarandı+seed+reprocess | 10 banka API/dashboard/RAG'de, 121 passed |

## Şu An Neredeyiz

- [x] Geliştirme aşaması (Hafta 1–5) tümüyle tamamlandı — kod, test, dokümantasyon.
- [x] Backend: FastAPI katmanlı mimari (Repository/Service/Factory/DI), CRUD, karşılaştırma, RAG vektör DB, chatbot, Docker Compose.
- [x] Frontend: Streamlit dashboard + RAG chatbot arayüzü, uçtan uca entegrasyon testleri.
- [x] NLP: ön işleme, çıkarım, normalizasyon, sınıflandırma, değerlendirme modülleri + testler.
- [x] Scraper: BDDK tarama, temizleme, kalite kontrolü, periyodik tarama otomasyonu.
- [x] Testler: `pytest tests/` → 110 passed (temiz env ile).
- [ ] Demo videosu (ADR-007 — ekip tarafından) ve PPTX/PDF sunum (ADR-007 — ekip tarafından) kaldı; agent üretemez.

## Bugün / Bu Oturumda Yapılanlar

- 2026-07-17 | Frontend (React/Vite) ↔ Backend uyum çalışması: mevcut `/api/*` korunarak frontend sözleşmesine uyan köprü router'ı eklendi (`src/backend/api/routes/frontend_bridge.py`): `GET /finansman/ozet`, `GET /finansman/karsilastirma` (bankaIds/urunTuru), `GET /finansman/bankalar`, `POST /chat/mesaj`, `GET /chat/gecmis`, `POST /chat/temizle`, `WS /ws/chat` (RAG streaming). Turkish field mapping + ChatYaniti/Mesaj/Atif şemaları `schemas.py`'e eklendi. | frontend_bridge.py, schemas.py, main.py | tamamlandı
- 2026-07-17 | Chatbot servisi lifespan'da tek sefer yükleniyor (2GB GGUF), vektör indeksi başlangıçta kuruluyor; REST/WS uç noktaları `app.state.chatbot`'a bağlandı (tembel fallback ile). | main.py, frontend_bridge.py | tamamlandı
- 2026-07-17 | DB boş olduğu için `src/database/seed.py` seeder'ı eklendi ve 9 banka + 121 kampanya yüklendi. Frontend `.env` (VITE_API_BASE_URL / VITE_CHATBOT_WS_URL) eklendi. | seed.py, src/frontend/.env | tamamlandı
- 2026-07-17 | Uyum için 4 yeni backend testi (`tests/test_backend/test_frontend_bridge.py`) eklendi; tüm backend testleri geçiyor (24 passed). | tamamlandı
- 2026-07-17 | Bekleyen 2 düzeltme commit'lendi: chat uç noktasının her istekte 2GB GGUF modelini yeniden yüklemesini engelleyen önbellek + Streamlit API istemci zaman aşımı (120sn) | src/backend/api/routes/chat.py, src/frontend/api_client.py | tamamlandı
- 2026-07-17 | PROGRESS.md gerçek duruma güncellendi (eski "kod yazılmadı" ifadesi düzeltildi), TASKS.md rol-checkbox'ları Haftalık tablolarla uyumlu hale getirildi | PROGRESS.md, TASKS.md | tamamlandı

_(Her oturum sonunda bu bölüme yeni bir madde ekle, en yeni en üstte.)_

## Önceki Oturumların Özeti (16 Temmuz 2026)

- 2026-07-16 | Model performans değerlendirme ve k-katlı çapraz doğrulama (cross-validation) modülü | src/nlp/evaluation.py, tests/test_nlp/test_evaluation.py | tamamlandı
- 2026-07-16 | Kampanya kategorisi sınıflandırma için hibrit (ML + kural tabanlı) model | src/nlp/classifier.py, tests/test_nlp/test_classifier.py | tamamlandı
- 2026-07-16 | Oran, tutar ve vade bilgileri için normalizasyon ve format standardizasyonu modülü | src/nlp/normalizer.py, tests/test_nlp/test_normalizer.py | tamamlandı
- 2026-07-16 | Bilgi çıkarımı modülü (kâr payı oranı, vade, asgari/azami tutar, avantaj ve kitle tespiti) | src/nlp/extractor.py, tests/test_nlp/test_extractor.py | tamamlandı
- 2026-07-16 | Metin ön işleme pipeline'ı (temizleme, tokenizasyon, normalizasyon ve Türkçe normalizasyonu) | src/nlp/preprocessor.py, tests/test_nlp/test_preprocessor.py, docks/nlp-approach.md | tamamlandı
- 2026-07-16 | Veri kalitesi denetimlerinin veritabanı desteğiyle genişletilmesi, DB loader ve periyodik tarama otomasyonu (periodic_runner.py) | src/scraper/periodic_runner.py, src/database/loader.py, src/scraper/check_data_quality.py, tests/test_scraper/test_periodic_runner.py | tamamlandı
- 2026-07-16 | Veritabanı şeması tasarımı ve kurulumu (PostgreSQL + SQLAlchemy ORM) | src/database/, tests/test_database.py, docker-compose.yml, .env.example, docks/data-schema.md | tamamlandı
- 2026-07-16 | Ham veri temizleme modülü (data_cleaner.py) yazıldı, 121 kayıt temizlenip data/processed altına JSON+CSV kaydedildi | src/scraper/data_cleaner.py, tests/test_scraper/test_data_cleaner.py, data/processed/ | tamamlandı
- 2026-07-16 | İlk veri toplama işlemi 10 banka için tamamlandı, veriler data/raw altına kaydedildi | data/raw/ | tamamlandı
- 2026-07-16 | Scraper politeness, 404 hata yönetimi ve sayfa limiti (MAX_PAGES_PER_BANK) eklendi | src/scraper/config.py, src/scraper/http_client.py, src/scraper/discovery.py | tamamlandı
- 2026-07-16 | BDDK banka listesi data/ altına taşındı, URL'ler test edilip düzeltildi | data/bank_sites.txt, src/scraper/config.py, src/scraper/check_bank_urls.py | tamamlandı
- 2026-07-16 | FastAPI proje iskeleti katmanlı mimariyle kuruldu (Repository, Service, Factory, DI) | src/backend/main.py, core/{config,database,llm_factory}.py, repositories/campaign_repository.py, services/{campaign_service,comparison_service}.py, api/routes/{campaigns,compare}.py, tests/test_backend/test_api.py | tamamlandı
- 2026-07-16 | API endpoint'leri CRUD + listeleme + DB entegrasyonu | campaigns.py, campaign_repository.py, campaign_service.py, schemas.py, tests/test_backend/test_api.py | tamamlandı
- 2026-07-16 | Karşılaştırma sorguları ve vektör DB (Chroma + InMemory fallback) kurulumu, RAG arama uç noktası | core/{embeddings,vector_store}.py, services/comparison_service.py, api/routes/{compare,search}.py, tests/test_backend/test_vector_store.py, conftest.py, DECISIONS.md | tamamlandı
- 2026-07-16 | RAG chatbot backend'i (/api/chat), Docker Compose ve Dockerfile, performans testleri | services/chatbot_service.py, api/routes/chat.py, docker-compose.yml, Dockerfile, requirements.txt, tests/test_backend/test_chatbot.py, tests/test_backend/test_performance.py | tamamlandı
- 2026-07-16 | API dokümantasyonu (docks/api-spec.md), tüm sistem testleri (99 passed) | docks/api-spec.md, README.md | tamamlandı
- 2026-07-16 | Frontend iskeleti (Streamlit dashboard + RAG chatbot arayüzü) ve API istemci katmanı; ADR-006 | src/frontend/{app,api_client}.py, tests/test_frontend/test_api_client.py, DECISIONS.md | tamamlandı
- 2026-07-16 | Frontend ↔ Backend uçtan uca bağlantı testi | tests/test_frontend/test_integration.py, tests/conftest.py | tamamlandı
- 2026-07-16 | Dashboard tam işlevsel (filtreler, bar grafik, kayıt sınırı) ve chatbot arayüzü zenginleştirildi | src/frontend/app.py, ui_helpers.py, tests/test_frontend/test_app.py | tamamlandı
- 2026-07-16 | Chatbot arayüz entegrasyonu ve uçtan uca (scraper→NLP→backend→frontend) entegrasyon testi | tests/test_frontend/test_e2e.py, chatbot_service.py | tamamlandı
- 2026-07-16 | NLP edge-case düzeltmeleri: vade çıkarımına yıl→ay ve ondalıklı yıl desteği | src/nlp/extractor.py, tests/test_nlp/test_extractor.py | tamamlandı
- 2026-07-16 | Sonuç örnekleri ve performans metrikleri dokümanı | docks/results-metrics.md | tamamlandı
- 2026-07-16 | Son veri kalitesi kontrolü (121 kayıt, 9 banka) ve CONTRIBUTING.md | CONTRIBUTING.md | tamamlandı
- 2026-07-16 | README finalize ve ADR-007 | README.md, DECISIONS.md, TASKS.md | tamamlandı
- 2026-07-16 | Yerel LLM (qwen2.5-3b GGUF) llama.cpp entegrasyonu, ADR-003 kesinleştirildi | core/llm_factory.py, core/config.py, chatbot_service.py, model/, .env, requirements.txt, DECISIONS.md | tamamlandı
- 2026-07-16 | Görev bazlı model dizinleri (model/{main_responser,data_cleaner,extractor,classifier,embedder,comparison}/) ve fabrika yönlendirmesi | model/*, config.py, llm_factory.py, chatbot_service.py, tests/test_backend/test_gguf_llm.py | tamamlandı

## Bilinen Sorunlar / Yarım Kalan İşler

- Demo videosu ve PPTX/PDF sunum dosyaları fiziksel/insan işidir (ADR-007) — agent tarafından üretilemez, ekip tarafından tamamlanacak.
- `PROGRESS.md` eski oturumda güncel tutulmamıştı; 17.07.2026'da gerçek duruma getirildi.
- Yerel LLM modeli (`model/` altındaki `.gguf`) kullanıcının makinesinde bulunmalı; internetten indirme YASAK (CLAUDE.md/ADR-003).

## Sıradaki Adım (Net)

1. Kod ve dokümantasyon tamam — kalan tek "kodlanabilir" iş yok.
2. Demo videosu ve sunum (PDF/PPTX) ekip tarafından hazırlanır (ADR-007).
3. Haftalık GitHub push'unun yapılması (branch origin/main'in 39 commit önünde).

## Haftalık İlerleme Kaydı

### Hafta 1 (27 Tem – 2 Ağu)
- Durum: Tamamlandı

### Hafta 2 (3 – 9 Ağu)
- Durum: Tamamlandı

### Hafta 3 (10 – 16 Ağu)
- Durum: Tamamlandı

### Hafta 4 (17 – 23 Ağu)
- Durum: Tamamlandı

### Hafta 5 (24 – 26 Ağu)
- Durum: Tamamlandı
