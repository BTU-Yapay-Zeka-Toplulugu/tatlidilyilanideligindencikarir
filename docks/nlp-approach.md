# NLP Yaklaşımı (NLP Approach)

Bu belgede projemizde katılım bankası kampanya metinlerinden bilgi çıkarmak ve sınıflandırmak için kullandığımız NLP yaklaşımları açıklanmaktadır.

## 1. Metin Ön İşleme Pipeline'ı

Çevrimdışı (on-premise) kısıtlar ve yüksek hız/performans hedefleri doğrultusunda, Türkçe metin ön işleme adımları için **spaCy** kütüphanesinin boş Türkçe modeli (`spacy.blank("tr")`) taban alınmıştır. Bu sayede harici model dosyaları indirilmesine gerek kalmadan Türkçe uyumlu tokenizasyon ve stopword filtreleme işlemleri çevrimdışı yapılabilmektedir.

### Ön İşleme Aşamaları:
1. **Türkçe Karakter Normalizasyonu:** Dotted/dotless "I/İ" dönüşümlerinin bozulmaması için özel Türkçe küçük harfe çevirme (`turkish_lower`) fonksiyonu kullanılır.
2. **Genel Temizlik:** HTML etiketleri, mükerrer boşluklar ve gereksiz navigasyon metinleri temizlenir.
3. **Tokenizasyon:** Metinler kelime ve noktalama düzeyinde bölünür.
4. **Filtreleme:** İsteğe bağlı olarak noktalama işaretleri (`token.is_punct`) ve Türkçe stopword'ler (`token.is_stop`) elenir.

Modül: `src/nlp/preprocessor.py`  
Testler: `tests/test_nlp/test_preprocessor.py`
