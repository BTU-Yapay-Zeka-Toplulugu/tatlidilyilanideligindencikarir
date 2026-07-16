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

- 16.07.2026 | Veri kalitesi denetim scripti (check_data_quality.py) yazıldı ve çalıştırıldı. Hafta 1 görevleri tamamlandı | src/scraper/check_data_quality.py, TASKS.md | tamamlandı
- 16.07.2026 | İlk veri toplama işlemi 10 banka için tamamlandı, veriler data/raw altına kaydedildi | data/raw/ | tamamlandı
- 16.07.2026 | Scraper politeness, 404 hata yönetimi ve sayfa limiti (MAX_PAGES_PER_BANK) eklendi | src/scraper/config.py, src/scraper/http_client.py, src/scraper/discovery.py | tamamlandı
- 16.07.2026 | BDDK banka listesi data/ altına taşındı, URL'ler test edilip düzeltildi | data/bank_sites.txt, src/scraper/config.py, src/scraper/check_bank_urls.py | tamamlandı
- src/scraper/bank_sites/bank_sites.txt oluşturuldu, 10 katılım bankasının web sitesi linki listelendi. "Değişen Dosyalar" listesine de ekle.

_(Her oturum sonunda bu bölüme yeni bir madde ekle, en yeni en üstte.)_


- **[Tarih girilecek]** — Proje context dosyaları (README, CLAUDE.md, AGENTS.md, ARCHITECTURE.md, PROGRESS.md, DECISIONS.md, TASKS.md) oluşturuldu.

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