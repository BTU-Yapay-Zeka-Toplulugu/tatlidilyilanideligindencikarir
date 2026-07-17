# API Spesifikasyonu

Tüm uç noktalar FastAPI ile sunulur; canlı Swagger dokümantasyonu `GET /docs`
(OpenAPI) üzerinden otomatik üretilir. Temel yol öneki: `/api`.

## Genel

| Yöntem | Yol | Açıklama |
| --- | --- | --- |
| GET | `/` | API durumu (sağlık kontrolü) |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc UI |

## Bankalar

### `GET /api/banks`
Tüm bankaları listeler.
- **Yanıt:** `200` → `list[BankResponse]` (`id`, `name`, `url`)

### `POST /api/banks`
Yeni banka oluşturur.
- **İstek:** `BankCreate` (`name`, `url`)
- **Yanıt:** `201` → `BankResponse`

### `DELETE /api/banks/{bank_id}`
Bankayı (ve ilişkili kampanyaları cascade ile) siler.
- **Yanıt:** `204` (başarı), `404` (banka yok)

## Kampanyalar

### `GET /api/campaigns`
Kampanyaları listeler; her kayıda NLP detayı iliştirilir.
- **Sorgu:** `bank_id` (int, opsiyonel), `campaign_type` (str, opsiyonel)
- **Yanıt:** `200` → `list[CampaignDetailResponse]`

### `GET /api/campaigns/{campaign_id}`
Tek kampanya detayı (NLP çıktısıyla birlikte).
- **Yanıt:** `200` → `CampaignDetailResponse`, `404` (yok)

### `POST /api/campaigns`
Yeni kampanya oluşturur (NLP detayı otomatik çıkarılır).
- **İstek:** `CampaignCreate` (`bank_id`, `source_url`, `page_title`, `raw_text`)
- **Yanıt:** `201` → `CampaignDetailResponse`, `404` (banka yok)

### `PUT /api/campaigns/{campaign_id}`
Kampanyayı kısmi günceller.
- **İstek:** `CampaignUpdate` (alanların tümü opsiyonel)
- **Yanıt:** `200` → `CampaignDetailResponse`, `404` (yok / banka yok)

### `DELETE /api/campaigns/{campaign_id}`
Kampanyayı siler.
- **Yanıt:** `204` (başarı), `404` (yok)

## Karşılaştırma

### `GET /api/compare`
Mevduat/katılma hesabı kampanyalarını kâr payı oranına göre (yüksek→düşük) sıralar.
- **Sorgu:** `term_months` (int, opsiyonel), `amount` (float, opsiyonel),
  `campaign_type` (str, opsiyonel)
- **Yanıt:** `200` → `list[CompareResponse]`
  (`bank_name`, `campaign_title`, `profit_share_rate`, `term_months`,
  `min_amount`, `advantage_description`, `target_audience`, `source_url`,
  `normalized_rate`, `normalized_amount`, `normalized_term`)

### `GET /api/compare/best`
En yüksek kâr payı oranına sahip kampanyayı döner.
- **Sorgu:** `campaign_type` (str, opsiyonel)
- **Yanıt:** `200` → `CompareResponse | null`

## Arama (Vektör / RAG)

### `POST /api/search/index`
Tüm kampanya metinlerini vektör deposuna indeksler (çevrimdışı gömme).
- **Yanıt:** `200` → `{"indexed": int}`

### `GET /api/search`
Metne vektör benzerliğiyle en yakın kampanyaları döner.
- **Sorgu:** `query` (str, zorunlu), `top_k` (int, vars. 5)
- **Yanıt:** `200` → `list[{id, text, metadata, score}]`

## Chatbot (RAG)

### `GET /api/chat`
Vektör aramasından bağlam toplayıp yerel LLM (Ollama) ile yanıt üretir.
- **Sorgu:** `question` (str, zorunlu), `top_k` (int, vars. 3)
- **Yanıt:** `200` → `{answer: str, sources: [{id, source_url, score}]}`

## Veri Modelleri (Pydantic)

- **BankResponse**: `id`, `name`, `url`
- **CampaignDetailResponse**: `id`, `bank_id`, `source_url`, `page_title`,
  `content_length`, `scraped_at`, `extracted_detail`
- **ExtractedDetailResponse**: `profit_share_rate`, `term_months`, `min_amount`,
  `max_amount`, `advantage_description`, `target_audience`, `campaign_type`,
  `is_processed`, `processed_at`
- **CompareResponse**: normalize edilmiş oran/tutar/vade alanları dahil.

## Çalıştırma

```bash
conda activate katilim-nlp
uvicorn src.backend.main:app --reload
# Swagger: http://localhost:8000/docs
```

## Frontend Köprü Uç Noktaları (React/Vite ön yüz)

Bu uç noktalar `src/backend/api/routes/frontend_bridge.py` içinde tanımlıdır ve
ön yüzün beklediği Türkçe alan adlı response sözleşmesine uygundur. Eski
`/api/*` uç noktaları geriye dönük uyumluluk için korunur.

### `GET /finansman/ozet`
Tüm kampanyaların finansman özet kalemlerini döner.
- **Yanıt:** `200` → `FinansmanKalemi[]`
  (`id`, `bankaAdi`, `urunAdi`, `tutar`, `karOrani`, `vade`, `tarih`)

### `GET /finansman/karsilastirma`
Bankalara göre gruplanmış karşılaştırma verisini döner.
- **Sorgu:** `bankaIds` (string[], opsiyonel), `urunTuru` (str, opsiyonel)
- **Yanıt:** `200` → `KarsilastirmaKalemi[]`
  (`bankaId`, `bankaAdi`, `urunler: FinansmanKalemi[]`)

### `GET /finansman/bankalar`
Ön yüz filtre seçenekleri için banka listesini döner.
- **Yanıt:** `200` → `BankaKalemi[]` (`id`, `ad`, `logo`)

### `POST /chat/mesaj`
Chatbot'a REST üzerinden mesaj gönderir.
- **İstek:** `{ mesaj: str, oturumId?: str }`
- **Yanıt:** `200` → `{ oturumId: str, mesaj: Mesaj }`
  (`Mesaj`: `id`, `rol`, `icerik`, `atiflar: Atif[]`, `zaman`, `akisDevam`)
  (`Atif`: `bankaAdi`, `urunAdi`, `url?`)

### `GET /chat/gecmis`
Bir oturuma ait mesaj geçmişini döner.
- **Sorgu:** `oturumId` (str, opsiyonel)
- **Yanıt:** `200` → `Mesaj[]`

### `POST /chat/temizle`
Oturum geçmişini temizler.
- **İstek:** `{ oturumId: str }`
- **Yanıt:** `200` → `{ status, oturumId }`

### `WS /ws/chat`
RAG chatbot streaming WebSocket'u. İstemci `{ mesaj, oturumId }` gönderir;
sunucu sırasıyla `{tur:'chunk', icerik}`, `{tur:'atiflar', atiflar}`,
`{tur:'bitti'}` paketleri gönderir.

