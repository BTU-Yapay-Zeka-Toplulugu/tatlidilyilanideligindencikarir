# TASKS.md

## Ekip Rolleri ve Birincil Sorumluluklar

### Kişi 1 — Veri Mühendisi (Data Collection)
- [x] BDDK listesindeki katılım bankalarının web sitelerinin taranması
- [x] Scraper geliştirme (Python), kampanya/ürün metinlerinin toplanması
- [x] Ham verinin temizlenmesi, veri seti (CSV/JSON) oluşturulması
- [x] Veritabanı şeması tasarımı ve kurulumu
- [x] Veri kalitesi kontrolleri ve periyodik yeniden tarama (crawl) süreci

### Kişi 2 — NLP / Model Mühendisi
- [x] Metin ön işleme pipeline'ı (temizleme, tokenizasyon, normalizasyon)
- [x] Bilgi çıkarımı: kâr payı oranı, vade, tutar, tarih, avantaj tespiti (kural tabanlı + NER)
- [x] Format standardizasyonu (%2,05 / 2.05% / 500 TL / 500₺ gibi varyasyonların birleştirilmesi)
- [x] Kampanya türü sınıflandırma modeli
- [x] Model performans değerlendirmesi (varsa test seti ile doğruluk ölçümü)

### Kişi 3 — Backend / Sistem Mühendisi
- [ ] FastAPI backend endpoint'leri (veri okuma, karşılaştırma sorguları)
- [ ] Karşılaştırma mantığının (en düşük oran, en avantajlı kampanya vb.) kodlanması
- [ ] RAG için vektör DB entegrasyonu (Chroma/FAISS) ve chatbot backend'i
- [ ] On-premise dağıtım (Docker Compose) kurulumu
- [ ] Performans testleri ve API dokümantasyonu (Swagger/OpenAPI)

### Kişi 4 — Ürün / Arayüz Mühendisi
- [ ] Dashboard geliştirme (banka/ürün karşılaştırma tabloları, filtreler, grafikler)
- [ ] Chatbot arayüzü (frontend) ve backend ile entegrasyon
- [ ] Kullanıcı deneyimi ve arayüz tasarımı
- [ ] Demo videosu (maks. 5 dk) çekimi ve kurgusu
- [ ] Sunum materyali (PDF + PPTX) hazırlığı ve proje dokümantasyonunun derlenmesi

> **Not:** Roller birincil sorumluluk alanlarıdır; ekip küçük olduğundan darboğaz yaşanan noktalarda (özellikle bilgi çıkarımı ve entegrasyon haftalarında) tüm üyeler birbirine destek vermelidir.

---

## 4.1 İdari Aşama

| Tarih | Yapılacaklar | Sorumlu | Durum |
| --- | --- | --- | --- |
| 12–17 Temmuz | Takım/danışman kaydı, tanıtım sunumu, ön değerlendirme formu, Senaryo 2 başvurusu | Takım Kaptanı + Tümü | [ ] |
| 17 Temmuz | Son başvuru tarihi | Takım Kaptanı | [ ] |
| 19 Temmuz | Ön değerlendirme sonuçları açıklanır | — | [ ] |
| 21 Temmuz | Teknik Değerlendirme Sınavı | Tümü | [ ] |
| 24 Temmuz | Finalistler açıklanır | — | [ ] |
| 27 Temmuz | Kick Off | Tümü | [ ] |

---

## 4.2 Geliştirme Aşaması (27 Temmuz – 26 Ağustos, ~4.5 hafta)

### Hafta 1 (27 Tem – 2 Ağu)

| Kişi | Görev | Durum |
| --- | --- | --- |
| Kişi 1 | BDDK banka listesi taraması, scraper iskeleti, ilk veri toplama | [x] |
| Kişi 2 | Ön işleme pipeline tasarımı, terminoloji sözlüğü (kâr payı, finansman vb.) oluşturma | [x] |
| Kişi 3 | Teknoloji seçimi, DB şeması taslağı, FastAPI proje iskeleti | [x] |
| Kişi 4 | UI/UX tasarımı, dashboard/chatbot iskelet arayüz | [x] |

### Hafta 2 (3–9 Ağu)

| Kişi | Görev | Durum |
| --- | --- | --- |
| Kişi 1 | Veri setinin genişletilmesi, temizleme, DB'ye ilk yükleme | [ ] |
| Kişi 2 | Bilgi çıkarımı kural tabanlı prototip + normalizasyon fonksiyonları | [x] |
| Kişi 3 | API endpoint'leri (CRUD, listeleme), DB entegrasyonu | [x] |
| Kişi 4 | Backend API ile dashboard iskeletinin bağlanması | [ ] |

### Hafta 3 (10–16 Ağu)

| Kişi | Görev | Durum |
| --- | --- | --- |
| Kişi 1 | Veri kalite kontrolü, eksik/edge-case veri toplama | [x] |
| Kişi 2 | Kampanya sınıflandırma modeli, çıkarım doğruluğunun test edilmesi | [x] |
| Kişi 3 | Karşılaştırma sorguları, vektör DB kurulumu (Chroma/FAISS) | [x] |
| Kişi 4 | Dashboard tam işlevsel hale getirme, chatbot arayüz tasarımı | [ ] |

### Hafta 4 (17–23 Ağu)

| Kişi | Görev | Durum |
| --- | --- | --- |
| Kişi 1 | Periyodik yeniden tarama otomasyonu, veri dokümantasyonu | [x] |
| Kişi 2 | Model ince ayarları, hata analizi, edge-case düzeltmeleri | [ ] |
| Kişi 3 | RAG chatbot backend'i, Docker/on-premise kurulum, performans testleri | [x] |
| Kişi 4 | Chatbot arayüz entegrasyonu, uçtan uca entegrasyon testi | [ ] |

### Hafta 5 (24–26 Ağu)

| Kişi | Görev | Durum |
| --- | --- | --- |
| Kişi 1 | Son veri kontrolleri, GitHub dokümantasyonu | [ ] |
| Kişi 2 | Sonuç örnekleri, performans metrikleri dokümantasyonu | [ ] |
| Kişi 3 | API dokümantasyonu, son sistem testleri, GitHub dokümantasyonu | [x] |
| Kişi 4 | Demo videosu, sunum (PDF+PPTX), README finalize | [ ] |

---

## 5. Teslim Edilecekler Kontrol Listesi

- [ ] Kaynak kod (GitHub, Apache 2.0 lisanslı, "BilisimVadisi2026" etiketli)
- [ ] Kurulum/çalıştırma talimatları (README)
- [ ] Demo videosu (maks. 5 dakika)
- [ ] Proje dokümantasyonu (mimari, NLP yaklaşımı, veri seti, ön işleme, karşılaştırma mantığı, sonuçlar)
- [ ] Sunum materyali (PDF ve PPTX)
- [ ] Haftalık GitHub güncellemeleri (zorunlu, en az haftada bir)

---

## 6. Kritik Uyarılar

- Ücretli hiçbir yazılım/servis kullanılamaz — her şey açık kaynak olmalı.
- Çözüm on-premise çalışabilmeli, dış servislere bağımlı olmamalı (API tabanlı ücretli LLM'ler kullanılamaz).
- Model başarısı değerlendirmenin %30'u — bilgi çıkarımı kalitesine öncelik verin.
- Kod haftalık commit edilmeli, aksi halde teslim eksikliği sayılabilir.