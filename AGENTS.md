# AGENTS.md

Bu dosya herhangi bir coding agent (Claude Code, Cursor, Copilot Workspace, vb.) için ortak, agent-bağımsız proje context'idir. Belirli bir agent'a özel dosyalar (örn. `CLAUDE.md`) bu dosyaya referans verir ve üzerine sadece agent'a özel küçük eklemeler yapar.

## Proje Ne Yapıyor

Katılım bankalarının kampanya metinlerinden NLP ile bilgi çıkaran (kâr payı oranı, vade, kampanya avantajı, hedef kitle), standart formata dönüştüren, bankalar arası karşılaştırma sunan ve dashboard + chatbot (RAG) ile erişim sağlayan bir sistem. Yarışma projesi — Senaryo 2, Yapay Zeka Dil Ajanları Yarışması, 4 kişilik ekip, Temmuz–Ağustos 2026.

## Kesin Yasaklar

- Ücretli API tabanlı LLM kullanımı yok (OpenAI/Anthropic/Google API vb.) — sadece yerel/açık kaynak LLM (Ollama).
- Ücretli yazılım/servis/kütüphane yok.
- İnternet bağımlılığı yok — tamamen on-premise, Docker Compose ile ayağa kalkmalı.

## Teknoloji Stack

Bkz. `README.md` → "Teknoloji Yığını" tablosu. Değiştirilmemesi gereken kesin kararlar `DECISIONS.md`'de listelidir.

## Klasör Yapısı

```
src/scraper/    → veri toplama, temizleme (Kişi 1)
src/nlp/        → ön işleme, bilgi çıkarımı, sınıflandırma (Kişi 2)
src/backend/    → FastAPI, karşılaştırma motoru, RAG backend (Kişi 3)
src/frontend/   → dashboard, chatbot arayüzü (Kişi 4)
docs/           → teknik dokümantasyon
tests/          → testler
```

## Handoff Ritüeli

Yeni bir agent veya oturum başladığında:

1. `README.md`, `CLAUDE.md` (veya ilgili agent dosyası), `PROGRESS.md`, `DECISIONS.md` oku.
2. Kullanıcıya durumu özetle.
3. `TASKS.md`'den ilgili görevleri kontrol et.
4. Çalış, test et, `PROGRESS.md`'yi güncelle, commit at.

## Test / Doğrulama

```bash
pytest tests/
uvicorn src.backend.main:app --reload
docker compose up --build
```

## Referans Dosyalar

- `PROGRESS.md` — canlı durum
- `DECISIONS.md` — alınan kararlar ve gerekçeleri
- `TASKS.md` — görev takvimi
- `docs/data-schema.md`, `docs/api-spec.md`, `docs/nlp-approach.md`