# Sonuç Örnekleri ve Performans Metrikleri

Bu belge, bilgi çıkarımı ve sınıflandırma modüllerinin örnek çıktılarını ve
ölçülen performans metriklerini içerir. Tüm değerlendirme çevrimdışı (on-premise)
ortamda, açık kaynak kütüphanelerle (scikit-learn) üretilmiştir.

## 1. Bilgi Çıkarımı — Örnek Sonuçlar

`extract_all_campaign_details` fonksiyonunun örnek kampanya metinlerinden
çıkardığı yapılandırılmış alanlar:

| Girdi (kampanya metni) | Kâr Payı | Vade | Min Tutar | Tür |
| --- | --- | --- | --- | --- |
| "Katılma hesabı kâr payı %20 ile 3 ay vadeli hoş geldin fırsatı." | 20.0 | 3 ay | — | Katılma Hesabı / Mevduat |
| "İhtiyaç finansmanı 12 ay taksit ile." | — | 12 ay | — | Finansman / Kredi |
| "Mevduat hesabı %15 kâr payı 6 ay." | 15.0 | 6 ay | — | Katılma Hesabı / Mevduat |
| "En az 10.000 TL bakiye gerekmektedir." | — | — | 10000.0 | (türe göre) |
| "2 yıla varan vadeli katılma hesabı." | — | 24 ay | — | Katılma Hesabı / Mevduat |

Format standardizasyonu (`normalizer.py`) şu dönüşümleri garanti eder:
`%2,05` → `%2.05`, `500 TL` / `500₺` → `500 TL`, `2 yıl` → `24 Ay`.

## 2. Sınıflandırma — Performans Metrikleri

Kampanya türü sınıflandırma modeli (TF-IDF + SVM hibrit, `classifier.py`)
örnek bir veri seti üzerinde değerlendirildi.

### 2.1 Doğruluk (Accuracy) — Örnek Çalıştırma

```
=== Model Performans Değerlendirme Raporu ===
Genel Doğruluk (Accuracy): 1.0000

                    precision  recall  f1-score  support
Finansman / Kredi       1.00    1.00     1.00        1
Kart / Ödeme            1.00    1.00     1.00        2
Katılma Hesabı / Mevduat 1.00   1.00     1.00        2
Sigorta / Emeklilik     1.00    1.00     1.00        1
accuracy                           1.00        6
macro avg               1.00    1.00     1.00        6
weighted avg            1.00    1.00     1.00        6
```

> Not: Yukarıdaki değerler küçük bir örnek seti üzerindendir; gerçek
> değerlendirme `evaluate_classifier_performance` ve `perform_cross_validation`
> (`evaluation.py`) ile taranmış veri seti üzerinde yapılmalıdır. Çapraz doğrulama
> `StratifiedKFold` ile 3 kat üzerinden ortalama doğruluk döndürür.

### 2.2 Değerlendirme Nasıl Çalıştırılır

```bash
conda activate katilim-nlp
python -c "from src.nlp.evaluation import evaluate_classifier_performance, perform_cross_validation; ..."
```

## 3. Sistem Performansı (Backend)

- Karşılaştırma uç noktası (`/api/compare`): 20 kampanya için < 2 sn.
- Vektör indeksleme (`/api/search/index`): 20 kampanya için < 3 sn.
- Tüm birim/entegrasyon testleri: `pytest tests/` → 106 passed.

## 4. Değerlendirme Notu

Yarışma değerlendirmesinin %30'u model başarısına dayanmaktadır; bu nedenle
kural tabanlı + NER hibrit çıkarım (ADR-002) önceliklendirilmiştir. LLM
(Ollama) yalnızca belirsiz durumlarda devreye girer ve çevrimdışı çalışır.
