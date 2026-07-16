# CLAUDE.md

Bu dosya Claude Code (ve benzeri coding agent'lar) için proje context'idir. Repoya her girişte önce bu dosya, sonra `PROGRESS.md` okunmalıdır.

> Agent-agnostic context için bkz. `AGENTS.md`. Bu dosya onun Claude Code'a özel kısa bir wrapper'ıdır.

## Proje Ne Yapıyor

Katılım bankalarının kampanya metinlerinden NLP ile bilgi çıkaran (kâr payı oranı, vade, kampanya avantajı, hedef kitle), standart formata dönüştüren, bankalar arası karşılaştırma sunan ve dashboard + chatbot (RAG) ile erişim sağlayan bir sistem. Yarışma projesi — Senaryo 2, Yapay Zeka Dil Ajanları Yarışması.

## 🚫 KESİN YASAKLAR (asla ihlal etme)

- **Ücretli API tabanlı LLM kullanma** (OpenAI API, Anthropic API, Google Gemini API vb.). Sadece yerel/açık kaynak model (Ollama üzerinden yerel çalıştırılabilir Türkçe/multilingual model).
- **Ücretli hiçbir yazılım/servis/kütüphane ekleme.** Her şey açık kaynak olmalı.
- **İnternet bağımlılığı ekleme.** Sistem tamamen on-premise / Docker Compose ile kurum içi çalışabilmeli.
- Bu kısıtlardan biri ihlal edilecek gibiyse, kodu yazmadan önce dur ve bunu `PROGRESS.md`'ye "bilinen sorun / karar gerekiyor" olarak not et.

## 🔒 %100 ÇEVRİMDIŞI MODEL KURALI (ON-PREMISE)

DİKKAT: Proje kapalı ağda çalışmaktadır. Transformers, HuggingFace veya herhangi bir kütüphane aracılığıyla internet üzerinden model/ağırlık (weights) indirmeye çalışmak KESİNLİKLE YASAKTIR. Modellerin internet bağlantısı ile indirilmesi engellenmiştir. Ajan, modelin kullanıcı tarafından önceden `data/models/` klasörüne konduğunu ve buradan çevrimdışı olarak yükleneceğini varsayarak kod yazacaktır. Model yolu her zaman `.env` dosyasındaki `LOCAL_MODEL_PATH` değişkeninden okunmalıdır.

## ⚙️ Ortam Kuralı

- Proje ve tüm kodlar İSTİSNASIZ olarak sadece `conda activate katilim-nlp` komutu ile mevcut/hazır ortamda çalıştırılır.
- Sıfırdan ortam oluşturma (`conda create`, `python -m venv` vb.) komutları kullanılmaz ve dokümantasyona eklenmez.

## Teknoloji Stack (kesin, değiştirme)

| Katman | Teknoloji |
| --- | --- |
| Veri Toplama | Python: requests, BeautifulSoup / Scrapy, Selenium (gerekirse) |
| Veri Deposu | PostgreSQL veya SQLite + JSON alanları |
| Bilgi Çıkarımı | spaCy (Türkçe model) + regex + yerel LLM (Ollama) |
| Sınıflandırma | scikit-learn (TF-IDF+SVM) veya BERTurk fine-tune |
| Backend API | FastAPI (Python) |
| Dashboard | React + Recharts/Plotly ya da Streamlit |
| Chatbot | RAG: LangChain/LlamaIndex + yerel LLM + Chroma/FAISS |
| Dağıtım | Docker Compose |

## Klasör Yapısı

```
src/scraper/    → Kişi 1: veri toplama, temizleme
src/nlp/        → Kişi 2: ön işleme, bilgi çıkarımı, sınıflandırma
src/backend/    → Kişi 3: FastAPI, karşılaştırma motoru, RAG backend
src/frontend/   → Kişi 4: dashboard, chatbot arayüzü
docs/           → data-schema.md, api-spec.md, nlp-approach.md
tests/          → her modül için testler
```

## Kod Konvansiyonları

- Python: PEP8, tip ipuçları (type hints) kullan.
- Kodlar Design Patterns kullanılarak, API mimarisi şeklinde ve Clean Code prensiplerine uygun yazılacaktır.
- **İSTİSNASIZ olarak her fonksiyonun/metodun hemen üstünde, sadece ne yaptığını açıklayan TEK SATIRLIK kısa bir docstring/yorum bulunmak zorundadır** (örn. `"""Kâr payı oranını metinden ayıklayıp standart float formata çevirir."""`). Uzun paragraf docstring yazma, tek satır yeterli.
- Commit mesajları: `[kişiX] kısa açıklama` formatında (örn. `[kişi2] normalizasyon fonksiyonu eklendi`).
- Her yeni modül için `tests/` altında en az temel bir test yaz.
- Format standardizasyonu kritik: `%2,05 / 2.05% / 500 TL / 500₺` gibi varyasyonlar birleştirilmeli — bkz. `docs/nlp-approach.md`.

## Clean Code Prensipleri

- **Tek Sorumluluk (SRP):** Her fonksiyon/sınıf tek bir iş yapmalı. Bir fonksiyon hem veri çekip hem parse edip hem kaydediyorsa üçe böl.
- **Anlamlı isimlendirme:** Kısaltma yerine açıklayıcı isim (`extract_profit_rate`, `x` veya `tmp` değil).
- **Küçük fonksiyonlar:** Bir fonksiyon ekrana sığmalı (~20-30 satır üst sınır); büyürse alt fonksiyonlara böl.
- **DRY:** Tekrar eden mantığı (özellikle regex/normalizasyon kuralları) ortak yardımcı fonksiyonlara/modüllere çıkar (`src/nlp/normalizers.py` gibi).
- **Erken dönüş (early return):** İç içe if bloklarından kaçın, guard clause kullan.
- **Sabit değerler:** Regex pattern'leri, magic number'lar dosya başında sabit (`CONST_CASE`) olarak tanımlanmalı.
- **Hata yönetimi:** Sessizce geçme (`except: pass` yasak); en azından logla.

## Uygulanacak Design Pattern'ler (API / Backend Katmanı)

Backend (`src/backend/`) ve NLP pipeline (`src/nlp/`) için aşağıdaki pattern'ler uygulanmalı:

- **Repository Pattern:** DB erişimi doğrudan endpoint içinde değil, `repositories/` katmanında (örn. `CampaignRepository`) soyutlanmalı. Endpoint'ler DB'yi bilmez, sadece repository'yi çağırır.
- **Service Layer Pattern:** İş mantığı (karşılaştırma motoru, sınıflandırma çağrısı vb.) `services/` katmanında toplanmalı; FastAPI route fonksiyonları ince (thin) kalmalı, sadece request/response + service çağrısı yapmalı.
- **Strategy Pattern:** Bilgi çıkarımında birden fazla yöntem olduğundan (regex kural tabanlı vs. LLM tabanlı), her biri ortak bir arayüzü (`ExtractorStrategy`) implemente eden ayrı sınıflar olmalı — hangi stratejinin kullanılacağı çalışma zamanında seçilebilsin.
- **Factory Pattern:** Yerel LLM (Ollama) modeli değişebileceğinden (bkz. DECISIONS.md ADR-003), model erişimi bir `LLMClientFactory` üzerinden soyutlanmalı; model değişince sadece factory güncellenir.
- **Dependency Injection:** FastAPI'nin kendi `Depends()` mekanizması kullanılarak repository/service'ler route'lara enjekte edilmeli — test edilebilirlik için.
- **DTO / Pydantic Schema Ayrımı:** DB modeli (ORM) ile API request/response şeması (Pydantic) ayrı tutulmalı, birbirine karıştırılmamalı.

### Önerilen Backend Klasör Yapısı

```
src/backend/
├── main.py                # FastAPI app, route include
├── api/
│   └── routes/            # ince route handler'lar (thin controllers)
├── services/               # iş mantığı (comparison_service.py, chatbot_service.py)
├── repositories/            # DB erişim katmanı (campaign_repository.py)
├── models/                  # ORM modelleri (SQLAlchemy)
├── schemas/                  # Pydantic request/response şemaları
└── core/                     # config, DB session, factory'ler
```

### Örnek: Tek Satır Yorum + Pattern Kullanımı

```python
class ExtractorStrategy(ABC):
    """Bilgi çıkarım stratejileri için ortak arayüz."""

    @abstractmethod
    def extract(self, text: str) -> dict:
        """Metinden yapılandırılmış alanları çıkarır."""
        ...


class RegexExtractor(ExtractorStrategy):
    """Kural tabanlı (regex) bilgi çıkarım stratejisi."""

    def extract(self, text: str) -> dict:
        """Regex desenleriyle oran, vade ve tutarı ayıklar."""
        ...


class CampaignRepository:
    """Kampanya verisine DB erişimini soyutlayan repository."""

    def get_by_bank(self, bank_id: str) -> list[dict]:
        """Belirli bir bankaya ait tüm kampanyaları getirir."""
        ...
```

## Doğrulama / Test Nasıl Çalıştırılır

```bash
# Python testleri
pytest tests/

# Backend'i lokal çalıştırma
uvicorn src.backend.main:app --reload

# Tüm sistemi Docker ile ayağa kaldırma
docker compose up --build
```

Agent, bir görevi tamamladıktan sonra ilgili testleri çalıştırıp sonucu `PROGRESS.md`'ye not etmelidir.

## Oturum Başlangıç Ritüeli (Her Yeni Agent / Oturum)

1. `README.md`, `CLAUDE.md`, `PROGRESS.md`, `DECISIONS.md` dosyalarını oku.
2. Kullanıcıya kısa bir özet ver: proje nerede, sırada ne var.
3. `TASKS.md`'den kendi rolüne/haftaya denk gelen görevleri kontrol et.
4. Çalışmaya başlamadan önce yasaklar bölümünü (yukarıda) tekrar gözden geçir.
5. Görev bitince `PROGRESS.md`'yi güncelle ve commit at.

## Referans Dosyalar

- Genel mimari kararları ve gerekçeleri → `DECISIONS.md`
- Şu anki durum / sıradaki adım → `PROGRESS.md`
- Görev takvimi ve sorumluluklar → `TASKS.md`
- Veri şeması → `docs/data-schema.md`
- API dokümantasyonu → `docs/api-spec.md`
- NLP / bilgi çıkarım yaklaşımı → `docs/nlp-approach.md`