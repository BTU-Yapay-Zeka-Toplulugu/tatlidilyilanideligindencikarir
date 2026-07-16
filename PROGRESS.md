# PROGRESS.md

> Bu dosya projenin **canlı durumu**dur. Her oturum/görev sonunda güncellenmelidir. Yeni bir agent devraldığında önce burayı okumalıdır.

## Son Güncelleme

- **Tarih:** 16 Temmuz 2026
- **Güncelleyen:** Kişi 1 — Veri Mühendisi
- **Genel Durum:** Geliştirme aşaması başladı, Hafta 1 görevleri yürütülüyor.

## Şu An Neredeyiz

- [ ] İdari aşama tamamlanmadı (takım kaydı, başvuru, sınav, kick-off bekleniyor)
- [x] Geliştirme aşaması başladı (Hafta 1)

## Bugün / Bu Oturumda Yapılanlar

- 2026-07-16 | Model performans değerlendirme ve k-katlı çapraz doğrulama (cross-validation) modülü | src/nlp/evaluation.py, tests/test_nlp/test_evaluation.py | tamamlandı
- 2026-07-16 | Kampanya kategorisi sınıflandırma için hibrit (ML + kural tabanlı) model | src/nlp/classifier.py, tests/test_nlp/test_classifier.py | tamamlandı
- 2026-07-16 | Oran, tutar ve vade bilgileri için normalizasyon ve format standardizasyonu modülü | src/nlp/normalizer.py, tests/test_nlp/test_normalizer.py | tamamlandı
- 2026-07-16 | Bilgi çıkarımı modülü (kâr payı oranı, vade, asgari/azami tutar, avantaj ve kitle tespiti) | src/nlp/extractor.py, tests/test_nlp/test_extractor.py | tamamlandı
- 2026-07-16 | Metin ön işleme pipeline'ı (temizleme, tokenizasyon, normalizasyon ve Türkçe normalizasyonu) | src/nlp/preprocessor.py, tests/test_nlp/test_preprocessor.py, docks/nlp-approach.md | tamamlandı
- 2026-07-16 | Veri kalitesi denetimlerinin veritabanı desteğiyle genişletilmesi, DB loader ve periyodik tarama otomasyonu (periodic_runner.py) | src/scraper/periodic_runner.py, src/database/loader.py, src/scraper/check_data_quality.py, tests/test_scraper/test_periodic_runner.py | tamamlandı
- 2026-07-16 | Veritabanı şeması tasarımı ve kurulumu (PostgreSQL + SQLAlchemy ORM) | src/database/, tests/test_database.py, docker-compose.yml, .env.example, docks/data-schema.md | tamamlandı
- 16.07.2026 | Ham veri temizleme modülü (data_cleaner.py) yazıldı, 121 kayıt temizlenip data/processed altına JSON+CSV kaydedildi | src/scraper/data_cleaner.py, tests/test_scraper/test_data_cleaner.py, data/processed/ | tamamlandı
- 16.07.2026 | Veri kalitesi denetim scripti (check_data_quality.py) yazıldı ve çalıştırıldı. Hafta 1 görevleri tamamlandı | src/scraper/check_data_quality.py, TASKS.md | tamamlandı
- 16.07.2026 | İlk veri toplama işlemi 10 banka için tamamlandı, veriler data/raw altına kaydedildi | data/raw/ | tamamlandı
- 16.07.2026 | Scraper politeness, 404 hata yönetimi ve sayfa limiti (MAX_PAGES_PER_BANK) eklendi | src/scraper/config.py, src/scraper/http_client.py, src/scraper/discovery.py | tamamlandı
- 16.07.2026 | BDDK banka listesi data/ altına taşındı, URL'ler test edilip düzeltildi | data/bank_sites.txt, src/scraper/config.py, src/scraper/check_bank_urls.py | tamamlandı
- src/scraper/bank_sites/bank_sites.txt oluşturuldu, 10 katılım bankasının web sitesi linki listelendi. "Değişen Dosyalar" listesine de ekle.

_(Her oturum sonunda bu bölüme yeni bir madde ekle, en yeni en üstte.)_


- **[Tarih girilecek]** — Proje context dosyaları (README, CLAUDE.md, AGENTS.md, ARCHITECTURE.md, PROGRESS.md, DECISIONS.md, TASKS.md) oluşturuldu.

- 2026-07-16 | FastAPI proje iskeleti katmanlı mimariyle kuruldu (Repository, Service, Factory, DI); monolit main.py parçalandı, bozuk backend test fixture'ı (StaticPool) düzeltildi | src/backend/main.py, src/backend/core/{config,database,llm_factory}.py, src/backend/repositories/campaign_repository.py, src/backend/services/{campaign_service,comparison_service}.py, src/backend/api/routes/{campaigns,compare}.py, tests/test_backend/test_api.py | tamamlandı

- 2026-07-16 | API endpoint'leri CRUD + listeleme + DB entegrasyonu (banka/kampanya oluştur/güncelle/sil) | src/backend/api/routes/campaigns.py, src/backend/repositories/campaign_repository.py, src/backend/services/campaign_service.py, src/backend/schemas.py, tests/test_backend/test_api.py | tamamlandı

- 2026-07-16 | Karşılaştırma sorguları (tür filtresi, best-rate) ve vektör DB (Chroma + InMemory fallback) kurulumu, RAG arama uç noktası | src/backend/core/{embeddings,vector_store}.py, src/backend/services/comparison_service.py, src/backend/api/routes/{compare,search}.py, tests/test_backend/test_vector_store.py, tests/test_backend/conftest.py, DECISIONS.md | tamamlandı

- 2026-07-16 | RAG chatbot backend'i (/api/chat), Docker Compose (db+ollama+backend) ve Dockerfile, requirements.txt, performans testleri | src/backend/services/chatbot_service.py, src/backend/api/routes/chat.py, docker-compose.yml, Dockerfile, requirements.txt, tests/test_backend/test_chatbot.py, tests/test_backend/test_performance.py | tamamlandı

- 2026-07-16 | API dokümantasyonu (docks/api-spec.md) yazıldı, tüm sistem testleri çalıştırıldı (99 passed), GitHub dokümantasyonu güncellendi | docks/api-spec.md, README.md, PROGRESS.md | tamamlandı

- 2026-07-16 | Frontend iskeleti (Streamlit dashboard + RAG chatbot arayüzü) ve API istemci katmanı; ADR-006 (Streamlit) eklendi | src/frontend/{app,api_client}.py, tests/test_frontend/test_api_client.py, requirements.txt, DECISIONS.md | tamamlandı

- 2026-07-16 | Frontend ↔ Backend uçtan uca bağlantı testi (gerçek FastAPI üzerinden kampanya/karşılaştırma akışı doğrulandı) | tests/test_frontend/test_integration.py, tests/conftest.py | tamamlandı

- 2026-07-16 | Dashboard tam işlevsel hale getirildi (filtreler, bar grafik, kayıt sınırı) ve chatbot arayüzü sohbet geçmişi/kaynaklarla zenginleştirildi | src/frontend/app.py, src/frontend/ui_helpers.py, tests/test_frontend/test_app.py | tamamlandı

- 2026-07-16 | Chatbot arayüz entegrasyonu ve uçtan uca (scraper→NLP→backend→frontend) entegrasyon testi; LLM yokken chatbot zarifçe düşen fallback eklendi | tests/test_frontend/test_e2e.py, src/backend/services/chatbot_service.py | tamamlandı

- 2026-07-16 | NLP edge-case düzeltmeleri: vade çıkarımına yıl→ay ve ondalıklı yıl desteği eklendi | src/nlp/extractor.py, tests/test_nlp/test_extractor.py | tamamlandı

## Değişen Dosyalar (son oturum)

- README.md (yeni)
- CLAUDE.md (yeni)
- AGENTS.md (yeni)
- ARCHITECTURE.md (yeni)
- PROGRESS.md (yeni)
- DECISIONS.md (yeni)
- TASKS.md (yeni)

## Bilinen Sorunlar / Yarım Kalan İşler

- Henüz kod yazılmadı; repo iskeleti (src/, tests/, docker-compose.yml, .env.example) oluşturulmadı.
- Hangi yerel LLM'in (Ollama üzerinden) kullanılacağı netleştirilmedi (bkz. DECISIONS.md — açık karar).
- BDDK katılım bankaları listesi henüz derlenmedi.

## Sıradaki Adım (Net)

1. İdari aşama tamamlanana kadar bekle (bkz. TASKS.md → 4.1 İdari Aşama).
2. Kick-off sonrası (27 Temmuz) repo iskeletini oluştur: `src/scraper`, `src/nlp`, `src/backend`, `src/frontend`, `tests/`, `docker-compose.yml`, `.env.example`.
3. Kişi 1: BDDK banka listesi taraması ve scraper iskeleti ile başla.
4. Kişi 2: Terminoloji sözlüğü ve ön işleme pipeline tasarımı ile başla.
5. Kişi 3: Teknoloji seçimini kesinleştir, DB şeması taslağı ve FastAPI iskeleti oluştur.
6. Kişi 4: UI/UX tasarımı ve dashboard/chatbot iskelet arayüzü ile başla.

## Haftalık İlerleme Kaydı

### Hafta 1 (27 Tem – 2 Ağu)
- Durum: Başlamadı

### Hafta 2 (3 – 9 Ağu)
- Durum: Başlamadı

### Hafta 3 (10 – 16 Ağu)
- Durum: Başlamadı

### Hafta 4 (17 – 23 Ağu)
- Durum: Başlamadı

### Hafta 5 (24 – 26 Ağu)
- Durum: Başlamadı