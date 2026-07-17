# ARCHITECTURE.md

## 1. Genel Akış

```
Veri Toplama (Scraper) → Ham Metin Deposu
        ↓
Ön İşleme (temizleme, normalizasyon) → Yapılandırılmış Metin
        ↓
Bilgi Çıkarımı (NER / Kural Tabanlı + LLM Hibrit) → Yapılandırılmış Veri (JSON/DB)
        ↓
Kampanya Sınıflandırma → Kategori Etiketleri
        ↓
Karşılaştırma Motoru → Dashboard API
        ↓
Chatbot (RAG tabanlı) → Kullanıcı Arayüzü
```

## 2. Katmanlar ve Teknoloji Seçimleri

| Katman | Teknoloji | Gerekçe |
| --- | --- | --- |
| Veri Toplama | Python: requests, BeautifulSoup / Scrapy, Selenium (gerekirse) | Hafif, esnek, JS-render gereken sitelerde Selenium fallback |
| Veri Deposu | PostgreSQL veya SQLite + JSON alanları | Yapılandırılmamış alanlar için JSON, ilişkisel sorgular için SQL |
| Bilgi Çıkarımı | spaCy (Türkçe model) + regex + yerel LLM (Ollama) | Kural tabanlı hız + LLM esnekliği hibrit yaklaşım |
| Sınıflandırma | scikit-learn (TF-IDF+SVM) veya BERTurk fine-tune | Basit başlangıç (SVM), gerekirse BERTurk'e geçiş |
| Backend API | FastAPI (Python) | Hızlı, async destekli, otomatik Swagger/OpenAPI |
| Dashboard | React + Vite + Tailwind + Recharts | Streamlit hızlı prototip, React üretim kalitesi için |
| Chatbot | RAG: LangChain/LlamaIndex + yerel LLM + Chroma/FAISS | Açık kaynak, on-premise çalışabilir RAG stack |
| Dağıtım | Docker Compose | Tek komutla tüm sistemin ayağa kalkması, on-premise uyum |

## 3. Veri Akışı Detayları

### 3.1 Veri Toplama
- BDDK listesindeki katılım bankalarının web siteleri taranır.
- Kampanya/ürün metinleri toplanır, ham metin deposuna (CSV/JSON) yazılır.
- Periyodik yeniden tarama (crawl) mekanizması ile veri güncel tutulur.

### 3.2 Ön İşleme
- Metin temizleme, tokenizasyon, normalizasyon.
- Terminoloji sözlüğü (kâr payı, finansman vb.) oluşturulur.

### 3.3 Bilgi Çıkarımı
- Kâr payı oranı, vade, tutar, tarih, avantaj tespiti: kural tabanlı + NER hibrit.
- Format standardizasyonu: `%2,05 / 2.05% / 500 TL / 500₺` gibi varyasyonlar tek bir standart formata birleştirilir.

### 3.4 Sınıflandırma
- Kampanya türü sınıflandırma modeli (TF-IDF+SVM veya BERTurk).
- Model performansı test seti ile doğruluk ölçümüyle değerlendirilir.

### 3.5 Karşılaştırma Motoru
- En düşük oran, en avantajlı kampanya gibi karşılaştırma mantığı FastAPI endpoint'lerinde kodlanır.

### 3.6 Chatbot (RAG)
- Vektör DB (Chroma/FAISS) ile doküman/parça embedding'leri saklanır.
- Yerel LLM (Ollama) ile RAG pipeline'ı çalıştırılır.

## 4. Dağıtım Mimarisi

- Tüm servisler Docker Compose ile orkestre edilir: scraper (cron/job), backend (FastAPI), vektör DB, dashboard/frontend.
- İnternet bağımlılığı yok; tüm modeller yerel olarak çalıştırılır (Ollama üzerinden).

## 5. Kısıtlar ve Öncelikler

- Ücretli hiçbir yazılım/servis kullanılamaz.
- Ücretli API tabanlı LLM'ler kullanılamaz.
- Model başarısı değerlendirmenin %30'u — bilgi çıkarımı kalitesine öncelik verilmeli.