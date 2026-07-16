# Veri Şeması (Data Schema)

## Veritabanı: PostgreSQL 15

Bağlantı bilgileri `.env` dosyasındaki `DATABASE_URL` değişkeninden okunur.
Docker Compose ile ayağa kalkar (`docker-compose up -d db`).

## Tablolar

### `banks`
Katılım bankalarının temel bilgileri.

| Kolon | Tip | Kısıtlar | Açıklama |
|-------|-----|----------|----------|
| id | INTEGER | PK, AUTO | Benzersiz banka kimliği |
| name | VARCHAR(255) | UNIQUE, NOT NULL | Banka tam adı |
| url | VARCHAR(512) | NOT NULL | Bankanın web sitesi |
| created_at | DATETIME | DEFAULT now() | Kayıt oluşturulma zamanı |

### `campaigns`
Bankalardan taranan kampanya metinleri.

| Kolon | Tip | Kısıtlar | Açıklama |
|-------|-----|----------|----------|
| id | INTEGER | PK, AUTO | Benzersiz kampanya kimliği |
| bank_id | INTEGER | FK → banks.id, NOT NULL | İlişkili banka |
| source_url | VARCHAR(1024) | UNIQUE, NOT NULL | Kampanyanın kaynak URL'si |
| page_title | VARCHAR(512) | NULL | Sayfa başlığı |
| raw_text | TEXT | NOT NULL | Temizlenmiş kampanya metni |
| scraped_at | DATETIME | DEFAULT now() | Tarama zamanı |
| content_length | INTEGER | NOT NULL | Metin uzunluğu (karakter) |

### `extracted_campaign_details`
NLP modülü tarafından çıkarılan yapılandırılmış kampanya bilgileri.

| Kolon | Tip | Kısıtlar | Açıklama |
|-------|-----|----------|----------|
| id | INTEGER | PK, AUTO | Benzersiz detay kimliği |
| campaign_id | INTEGER | FK → campaigns.id, UNIQUE, NOT NULL | İlişkili kampanya |
| profit_share_rate | FLOAT | NULL | Kâr payı oranı (%) |
| term_months | INTEGER | NULL | Vade süresi (ay) |
| min_amount | FLOAT | NULL | Asgari tutar (TL) |
| max_amount | FLOAT | NULL | Azami tutar (TL) |
| advantage_description | TEXT | NULL | Kampanya avantajı açıklaması |
| target_audience | VARCHAR(255) | NULL | Hedef kitle |
| campaign_type | VARCHAR(100) | NULL | Sınıflandırma etiketi |
| is_processed | BOOLEAN | NOT NULL, DEFAULT false | NLP işlemi tamamlandı mı |
| processed_at | DATETIME | NULL | NLP işlem zamanı |

## İlişkiler

```
banks 1 ──── N campaigns 1 ──── 1 extracted_campaign_details
```

- `Bank → Campaign`: Bir banka birden çok kampanyaya sahip olabilir. Cascade delete aktif.
- `Campaign → ExtractedCampaignDetail`: Her kampanyanın en fazla bir detay kaydı olabilir (1:1). Cascade delete aktif.

## ORM

SQLAlchemy 2.x DeclarativeBase kullanılır. Model dosyası: `src/database/models.py`.
Bağlantı yönetimi: `src/database/connection.py`.
