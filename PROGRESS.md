# PROGRESS.md

> Bu dosya projenin **canlı durumu**dur. Her oturum/görev sonunda güncellenmelidir. Yeni bir agent devraldığında önce burayı okumalıdır.

## Son Güncelleme

- **Tarih:** 17 Temmuz 2026
- **Güncelleyen:** Otonom agent (devralma oturumu)
- **Genel Durum:** Tüm kaynak kod, NLP, backend, frontend, Docker ve dokümantasyon tamamlandı. 110 test geçiyor. Bekleyen kalemler yalnızca insan işi olan demo videosu ve sunum dosyaları (ADR-007).

## Şu An Neredeyiz

- [x] Geliştirme aşaması (Hafta 1–5) tümüyle tamamlandı — kod, test, dokümantasyon.
- [x] Backend: FastAPI katmanlı mimari (Repository/Service/Factory/DI), CRUD, karşılaştırma, RAG vektör DB, chatbot, Docker Compose.
- [x] Frontend: Streamlit dashboard + RAG chatbot arayüzü, uçtan uca entegrasyon testleri.
- [x] NLP: ön işleme, çıkarım, normalizasyon, sınıflandırma, değerlendirme modülleri + testler.
- [x] Scraper: BDDK tarama, temizleme, kalite kontrolü, periyodik tarama otomasyonu.
- [x] Testler: `pytest tests/` → 110 passed (temiz env ile).
- [ ] Demo videosu (ADR-007 — ekip tarafından) ve PPTX/PDF sunum (ADR-007 — ekip tarafından) kaldı; agent üretemez.

## Bugün / Bu Oturumda Yapılanlar

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
