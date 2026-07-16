# Katkı ve Depo Dokümantasyonu (GitHub)

Bu depo, Yapay Zeka Dil Ajanları Yarışması (Senaryo 2) kapsamında geliştirilen
katılım bankası kampanya analiz sistemini içerir.

## Çalışma Ortamı

Proje hazırda var olan `katilim-nlp` conda ortamında çalıştırılır; sıfırdan
ortam oluşturulmaz.

```bash
conda activate katilim-nlp
cp .env.example .env
docker compose up --build
```

## Testlerin Çalıştırılması

```bash
pytest tests/
```

Tüm birim, entegrasyon ve uçtan uca testleri bu komutla geçmelidir.

## Kod Standartları

- Python PEP8, type hints zorunlu.
- Her fonksiyonun tek satırlık docstring'i bulunur.
- Backend katmanlı mimari kullanır: `api/routes` (thin), `services`,
  `repositories`, `core` (config, db, embeddings, vector_store, llm_factory).
- Her modül için `tests/` altında en az bir test yazılır.
- Her görev sonrası anlamlı conventional-commit yapılır.

## Yasaklar

- Ücretli API tabanlı LLM (OpenAI/Anthropic/Gemini API) KULLANILMAZ.
- İnternet bağımlılığı yoktur; modeller çevrimdışı `data/models/` altından yüklenir.
- Tüm bağımlılıklar açık kaynaktır.

## Dizin Yapısı

```
src/scraper/   → veri toplama, temizleme
src/nlp/       → ön işleme, bilgi çıkarımı, sınıflandırma
src/database/  → SQLAlchemy modelleri ve bağlantı
src/backend/   → FastAPI (routes/services/repositories/core)
src/frontend/  → Streamlit dashboard + chatbot
tests/         → tüm testler
docks/         → teknik dokümantasyon (data-schema, api-spec, nlp-approach, results-metrics)
```

## Lisans

Apache 2.0 — etiket: `BilisimVadisi2026`
