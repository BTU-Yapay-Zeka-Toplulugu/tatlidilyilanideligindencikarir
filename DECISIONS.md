# DECISIONS.md

ADR (Architecture Decision Record) tarzında alınan kararlar. Yeni bir karar alındığında en alta yeni bir bölüm olarak eklenir, mevcut kararlar silinmez/değiştirilmez (gerekirse "Durum: Değiştirildi → bkz. ADR-00X" notu eklenir).

Format:
```
## ADR-00X: [Başlık]
- **Tarih:**
- **Durum:** Kabul edildi / Değiştirildi / Reddedildi
- **Bağlam:** Neden bu karar gerekti
- **Karar:** Ne karar verildi
- **Gerekçe:** Neden bu seçim yapıldı
- **Alternatifler:** Değerlendirilen diğer seçenekler
- **Sonuçlar:** Bu kararın etkileri
```

---

## ADR-001: Teknoloji Yığını Seçimi

- **Tarih:** Proje planlama aşaması
- **Durum:** Kabul edildi
- **Bağlam:** Yarışma kuralları gereği tüm çözüm açık kaynak ve on-premise olmalı, ücretli servis/LLM API kullanılamaz.
- **Karar:** Python tabanlı stack (FastAPI, spaCy, scikit-learn/BERTurk, LangChain/LlamaIndex, Chroma/FAISS), React veya Streamlit frontend, Docker Compose dağıtım.
- **Gerekçe:** Tamamen açık kaynak, on-premise çalıştırılabilir, Türkçe NLP için topluluk desteği (spaCy Türkçe model, BERTurk) mevcut.
- **Alternatifler:** Ücretli LLM API'leri (OpenAI vb.) — yarışma kuralı gereği elendi. Bulut tabanlı vektör DB'ler (Pinecone vb.) — on-premise kısıtı gereği elendi, yerine Chroma/FAISS seçildi.
- **Sonuçlar:** Yerel LLM performansı ücretli API'lere göre daha sınırlı olabilir; bu yüzden kural tabanlı + NER hibrit yaklaşım öncelikli tutuldu.

## ADR-002: Bilgi Çıkarımında Hibrit Yaklaşım (Kural Tabanlı + LLM)

- **Tarih:** Proje planlama aşaması
- **Durum:** Kabul edildi
- **Bağlam:** Değerlendirmenin %30'u model başarısına dayanıyor; bilgi çıkarımı kalitesi kritik.
- **Karar:** Kâr payı oranı, vade, tutar gibi yapılandırılmış alanlar için önce regex/kural tabanlı çıkarım, belirsiz durumlarda yerel LLM desteği.
- **Gerekçe:** Kural tabanlı yöntemler yüksek doğruluk ve hız sağlar; LLM ise regex'in yakalayamadığı doğal dil varyasyonlarını tolere eder.
- **Alternatifler:** Sadece LLM tabanlı çıkarım — daha az öngörülebilir ve daha yavaş olacağından elendi. Sadece kural tabanlı — doğal dil varyasyonlarında kırılgan olacağından tek başına yetersiz bulundu.
- **Sonuçlar:** İki katmanlı bir pipeline gerektirir; Kişi 2'nin iş yükünü artırır ama doğruluğu yükseltir.

## ADR-003: Yerel LLM Seçimi

- **Tarih:** 16 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** Ollama üzerinden çalıştırılacak Türkçe/multilingual açık kaynak modelin hangisi olacağı netleşmemişti.
- **Karar:** Model doğrudan **llama.cpp (llama-cpp-python)** ile çalıştırılır; Ollama sunucusu kullanılmaz. Test/model için seçilen model: **`qwen2.5-3b-instruct-q4_k_m.gguf`** (Qwen2.5 3B, Q4_K_M quantized, multilingual/TR dostu, çevrimdışı). Model dosyası `model/` dizinine konur ve `LOCAL_MODEL_PATH` (`.env`) ile gösterilir; dizin ise içindeki ilk `.gguf` otomatik yüklenir. Daha iyi bir model için sadece yeni `.gguf` `model/` altına bırakılır.
- **Gerekçe:** llama.cpp saf Python + C binding ile çevrimdışı, açık kaynak ve hızlıdır; Ollama'ya bağımlılık gerektirmez. `LLMClientFactory` (auto→gguf) ile model değişimi kodsuz yapılır (ADR-003 sonucu karşılandı).
- **Alternatifler:** Ollama (ayrı servis/indirme gerektirir; elendi), Türkçe Llama/Mistral fine-tune (ileride `model/` altına GGUF olarak eklenebilir), HuggingFace üzerinden ağırlık indirme (internet bağımlılığı yasağı gereği elendi).
- **Sonuçlar:** `src/backend/core/llm_factory.py` → `GgufLLMClient` (llama.cpp) eklendi; `LLM_BACKEND=auto|gguf|ollama` desteği. `requirements.txt`'e `llama-cpp-python` eklendi. Chatbot için instruct şablonu (`<|im_start|>`/`) kullanılır. Her görev için ayrı model dizini: `model/{main_responser,data_cleaner,extractor,classifier,embedder,comparison}/`; fabrika `LLMClientFactory.<görev>()` ile ilgili yolu kullanır, böylece ileride her modüle ayrı `.gguf` kolayca atanabilir (sistemsel tek model yerine görev bazlı modeller).

## ADR-004: Veri Deposu — PostgreSQL vs SQLite

- **Tarih:** 16 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** Hem PostgreSQL hem SQLite seçenek olarak planda yer alıyordu. Docker Compose ve on-premise kalıcılık/çoklu erişim desteği gereklilikleri bulunmaktaydı.
- **Karar:** Veri tabanı olarak PostgreSQL seçilmiştir. SQLAlchemy ORM kullanılarak veritabanı işlemleri soyutlanacaktır.
- **Gerekçe:** PostgreSQL, Docker ortamlarında ölçeklenebilir, eşzamanlı erişimde daha güvenlidir ve üretim ortamına uygundur. SQLAlchemy kullanımı ise gerektiğinde SQLite'a veya başka bir SQL veri tabanına geçişi kolaylaştırır.
- **Alternatifler:** SQLite (prototipleme kolaylığı için düşünüldü ancak eşzamanlı yazma sınırları nedeniyle elendi).
- **Sonuçlar:** Docker Compose dosyasına PostgreSQL servisi eklenmelidir. Veri saklama ve FastAPI backend işlemlerinde PostgreSQL bağlantısı kullanılacaktır.

## ADR-005: Vektör Veritabanı — Chroma (RAG için)

- **Tarih:** 16 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** RAG tabanlı chatbot için açık kaynak, on-premise çalışabilen bir vektör DB gerekiyordu (ADR-003 bağlamı). TASKS.md Chroma/FAISS seçeneklerini sunuyordu; net karar yoktu.
- **Karar:** Vektör DB olarak **Chroma** seçilmiştir. Üretimde diskte kalıcı (`PersistentClient`) kullanılır. Test/prototip için harici bağımlılık gerektirmeyen saf-Python `InMemoryVectorStore` (sklearn cosine similarity) varsayılan olarak kullanılır.
- **Gerekçe:** Chroma; metadata filtreleme, diskte kalıcılık ve Python ile kolay entegrasyon sunar, tamamen açık kaynak ve on-premise'dir. Embedding üretimi için `LOCAL_MODEL_PATH` (ADR-003) üzerinden çevrimdışı `sentence-transformers` modeli kullanılır; harici indirme olmadan çalışması için varsayılan olarak çevrimdışı `LocalLexicalEmbedder` (bag-of-words) sağlanmıştır.
- **Alternatifler:** FAISS (düşük seviyeli, kalıcılık/metadata yöneticisi manuel; elendi), Pinecone (ücretli/bulut; ADR-001 gereği elendi).
- **Sonuçlar:** `src/backend/core/vector_store.py` (VectorStoreFactory + Chroma/InMemory) ve `src/backend/core/embeddings.py` (Embedder arayüzü) oluşturuldu. Docker imajına `chromadb` bağımlılığı eklenmelidir.

## ADR-006: Frontend Teknoloji Seçimi — Streamlit

- **Tarih:** 16 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** README/ARCHITECTURE "React + Recharts/Plotly ya da Streamlit" diyordu; net seçim yoktu. Yarışma demosu için hızlı, çevrimdışı, Python-tabanlı ve backend ile aynı dilde çalışan bir ön yüz gerekiyordu.
- **Karar:** Dashboard ve chatbot arayüzü için **Streamlit** kullanılacaktır. Backend FastAPI'ye HTTP ile bağlanır; grafikler için `plotly`/`streamlit` yerleşik bileşenleri kullanılır.
- **Gerekçe:** Sıfır frontend build adımı, hızlı prototip, Python ekibi için düşük öğrenme eğrisi; tamamen açık kaynak ve on-premise. Gerekirse ileride React'e geçiş için arayüz API üzerinden ayrık tutulur.
- **Alternatifler:** React + Recharts/Plotly (daha üretim kaliteli ama ayrı build zinciri/JS ekibi gerektirir; elendi).
- **Sonuçlar:** `src/frontend/` altına Streamlit uygulaması (`app.py`) yazılacak; `requirements.txt`'e `streamlit`, `plotly` eklenecek.

## ADR-008: Backend'in Hazır Frontend'e Uyarlanması

- **Tarih:** 17 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** Frontend (Kişi 4) bir **Vite + React + Tailwind** uygulamasıdır (Streamlit değil; ARCHITECTURE/PROGRESS.md eski bilgi içeriyor). Backend ise PostgreSQL + FastAPI `/api/*` uç noktaları sunmaktadır. Frontend'in beklediği endpoint isimleri, response alan adları ve WebSocket akışı mevcut backend ile **uyumsuzdur**. Frontend'e dokunmadan backend adapte edilecektir. Docker kapsam dışıdır (Bölüm 3 kısıtı).
- **Karar:** Backend'e frontend'in beklediği sözleşmeye uyan yeni router'lar eklenir; var olan `/api/*` uç noktaları geriye dönük uyumluluk için korunur.
  - **Dashboard (REST):**
    - `GET /finansman/ozet` → `FinansmanKalemi[]` (`id`, `bankaAdi`, `urunAdi`, `tutar`, `karOrani`, `vade`, `tarih`)
    - `GET /finansman/karsilastirma` (query: `bankaIds`, `urunTuru`) → `KarsilastirmaKalemi[]` (`bankaId`, `bankaAdi`, `urunler[]`)
    - `GET /finansman/bankalar` → `BankaKalemi[]` (`id`, `ad`, `logo`)
  - **Chatbot:**
    - `POST /chat/mesaj` (`{mesaj, oturumId}`) → `{oturumId, mesaj:{id,rol,icerik,atiflar,zaman}}`
    - `GET /chat/gecmis?oturumId` → `Mesaj[]`
    - `POST /chat/temizle` (`{oturumId}`)
    - **WebSocket** `/ws/chat` → RAG streaming (`{tur:'chunk'|'atiflar'|'bitti', icerik/atiflar}`)
  - CORS `*` (zaten var). Chat geçmişi oturum başına bellek-içi saklanır (demo amaçlı).
- **Gerekçe:** Frontend sabit ve ekip arkadaşı tarafından teslim edildi; adaptasyon backend (serializer/DTO) katmanında yapılarak risk minimize edildi.
- **Alternatifler:** Frontend'i `/api/*` kullanacak şekilde değiştirmek — reddedildi (görev: frontend'e dokunma).
- **Sonuçlar:** Yeni `frontend_bridge` router'ları + `ChatHistoryStore` + WebSocket endpoint'i eklendi; DB boş olduğu için test verisi (seeder) sağlandı.

## ADR-009: Sistem Geneli Debug ve Stabilizasyon (WebSocket + Dashboard + Veri Kalitesi)

- **Tarih:** 17 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** Sistem "çalışıyor gibi" görünüyordu ama üç alanda güvenilir değildi: (A) chatbot/WebSocket, (B) frontend dashboard, (C) CSV/JSON kampanya verisinin çıkarım kalitesi. Kanıta dayalı (log/test/örnek veri) teşhis yapıldı.

### A) WebSocket / Chatbot — Teşhis Mini-Spec
- **Belirti:** Mesaj yazınca cevap "geliyor gibi" ama atıflar (kaynakça) hep "Bilinmeyen" görünüyor; uzun cevaplarda bağlantı düşüyor.
- **Beklenen:** Gerçek cevap + doğru banka/ürün/URL atıfları; bağlantı stabil.
- **Kök sebep 1 (atıflar):** `ChatbotService.answer()` `sources` içine `metadata` koymuyordu; `frontend_bridge._atiflari_olustur()` ise `s["metadata"]` okuyordu → tüm atıflar boş.
- **Kök sebep 2 (sessiz hata):** WS `except Exception: return` tüm hataları yutuyor, frontend askıda kalıyordu; ayrıca her WS bağlantısı yeni `ChatbotService`/LLM kuruyordu (lifespan'daki 2GB model yeniden yükleniyor).
- **Kök sebep 3 (bağlantı düşmesi):** Bloke edici (senkron) LLM çıkarımı async WS handler içinde olay döngüsünü kilitliyor; uzun yanıtta WebSocket keepalive ping'i cevaplanamayınca "keepalive ping timeout" ile kopuyordu.
- **Çözüm:** `answer()` `sources`'a tam `metadata`+`text` ekler; WS `app.state.chatbot`'u yeniden kullanır, hataları loglar ve `bitti` göndererek UI'ı askıda bırakmaz; LLM çağrısı `run_in_threadpool` ile çalıştırılır (olay döngüsü ve ping'ler serbest kalır); `WebSocketDisconnect` ayrıca ele alınır.
- **Doğrulama:** wscat benzeri Python istemcisiyle uçtan uca test — gerçek cevap + gerçek banka/ürün/URL atıfları döndü; uzun (>keepalive) yanıt kopmadan tamamlandı; aynı bağlantıda çoklu mesaj çalıştı. REST `/chat/mesaj` de doğru atıf döndürdü.

### B) Frontend Dashboard — Teşhis Mini-Spec
- **Belirti:** Karşılaştırma tablosu tutar/oran hücreleri boş (—); grafik barları düz/0.
- **Beklenen:** Tablo/grafik gerçek tutar ve kâr oranlarıyla dolu.
- **Kök sebep:** Backend `/finansman/karsilastirma` iç içe (nested) `{bankaId,bankaAdi,urunler[]}` dönüyordu; ancak frontend bileşenleri (KarsilastirmaTablosu, FinansmanGrafigi, csvExporter, sıralama hook'u) veriyi **düz `FinansmanKalemi[]`** olarak, her satırda doğrudan `tutar/karOrani/urunAdi/vade/tarih` okuyor. ADR-008'de sözleşme doğrulanmadan varsayılmıştı.
- **Çözüm:** Endpoint düz `FinansmanKalemi[]` dönecek şekilde düzeltildi (`bankaIds`/`urunTuru` filtreleri korundu). Frontend'e dokunulmadı (görev kısıtı). İlgili backend testi güncellendi.
- **Doğrulama:** Canlı backend'e karşı bileşen hesaplama mantığı (reduce/format) simüle edildi: 121 satırda 0 undefined alan, 9/9 grafik barı > 0, özet kartlar gerçek toplam üretiyor. `npm run build` temiz derlendi.

### C) Veri Kalitesi / Extraction — Teşhis Mini-Spec
- **Belirti:** Kâr payı oranları %70–%100 gibi imkânsız değerler; sınıflandırma bazı sayfalarda yanlış.
- **Beklenen:** Sadece gerçek kâr payı oranları (makul band), doğru kategori.
- **Kök sebep (oran):** `extract_profit_share_rate` metindeki İLK `%N`'i, neye ait olduğuna bakmadan alıyordu → "%75 nakit iade", "%70 iştirak", "%80 ekspertiz (LTV)", "asgari ödeme %100", "%X devlet katkısı", "%20 KDV", "stopaj %10" gibi ifadeler kâr payı oranı sanılıyordu. Sorun **scraping'de değil, çıkarım (extraction) adımında** (ham metin doğru, atıf yanlış).
- **Kök sebep (Türkçe casefold):** Anahtar kelime eşleşmeleri `str.lower()` kullanıyordu; Python'da `"İ".lower()` → `"i̇"` (birleşik nokta) olduğundan `"İndirim"`, `"FİNANSMAN"` gibi büyük-İ'li kelimeler eşleşmiyordu (sessiz hata). Bu hem eleme kelimelerini hem sınıflandırmayı bozuyordu (`classify_campaign_type("İHTİYAÇ FİNANSMANI")` → "Diğer").
- **Çözüm:** Bağlam-duyarlı oran çıkarımı: yalnızca kâr payı/getiri/oran bağlamına **bitişik** ve makul (`0 < r <= %50`) yüzdeler kabul edilir; iade/indirim/iştirak/LTV/asgari ödeme/devlet katkısı/stopaj/KDV/puan/mil gibi ilgisiz bağlamlar geniş pencerede elenir; binlik ayraçlı sayı (`10.000`) oran sayılmaz. Türkçe-duyarlı `_tr_fold` (casefold + İ/I eşlemesi) tüm anahtar kelime eşleşmelerinde kullanılır (oran, hedef kitle, avantaj, sınıflandırma).
- **Yeniden üretim:** `src/database/reprocess.py` eklendi; 121 kampanya için çıkarım yeniden çalıştırılıp DB güncellendi.
- **Doğrulama (önce/sonra):** Oranlar — ÖNCE: 36 kayıt, maks %100, 10 adet > %50; SONRA: 3 kayıt, maks %36, 0 adet > %50 (sadece gerçek "Kâr/Getiri/Taksit Oranı" bağlamları). Sınıflandırma büyük-İ regresyonu düzeldi. Birim testler eklendi (format varyasyonları + yanlış-atıf elemesi + gerçek veri precision regresyonu).

### Ek Temizlik
- `tests/test_frontend/*` (eski Streamlit `api_client`/`ui_helpers` modüllerini import eden 4 ölü test) kaldırıldı; frontend artık React (ADR-008) olduğundan bu modüller yok ve testler `pytest tests/`'i toplama (collection) aşamasında kırıyordu.
- **Sonuç:** `pytest tests/` → 113 passed.

## ADR-010: 10. Banka (ADİL Katılım) Eksikliği ve Scraper Sağlamlaştırması

- **Tarih:** 17 Temmuz 2026
- **Durum:** Kabul edildi
- **Bağlam:** Yarışma, BDDK listesindeki **10** katılım bankasının kullanılmasını şart koşuyor; ancak sistemde yalnızca 9 banka vardı. Kök sebep: `data/bank_sites.txt` 10 bankayı doğru listelese de **ADİL KATILIM (bank_id=1)** ilk tarama sırasında keşif aşamasında 0 sayfa ürettiği için hiç veri toplanmamış (ne raw, ne processed, ne DB).
- **Kök sebep analizi (kanıta dayalı):**
  1. **Keşif boşluğu:** ADİL yeni lisanslı, minimal içerikli bir kurumsal sitedir; hiç "kampanya" anahtar kelimeli sayfası yok (yalnızca Hakkımızda / Katılım Bankacılığı / bir PDF). Discovery 0 sayfa buluyordu.
  2. **PDF yanlış eşleşmesi:** Tek "kampanya" bağı, link metni "Ürün ve Hizmet Ücretleri" olan bir **.pdf** idi; HTML olarak parse edilemediğinden 0 içerik veriyordu.
  3. **Encoding hatası:** `fetch_page` `response.apparent_encoding` (chardet) kullanıyordu; charset başlığı olmayan ADİL sitesinde bu yanlış tahmin edilip **mojibake** ("Hakk─▒m─▒zda") üretiyordu.
- **Karar/Çözüm (frontend'e ve mevcut 9 bankaya dokunmadan):**
  - **Encoding:** `http_client._resolve_encoding` eklendi — sırayla HTTP başlığı charset → HTML `<meta charset>` → UTF-8 (kayıpsız çözülüyorsa) → chardet. Türkçe siteler artık doğru çözülüyor.
  - **PDF/ikili eleme:** discovery'de `_is_binary_url` ile `.pdf/.png/...` uzantılı bağlar (parse edilemez) atlanıyor.
  - **Kurumsal fallback:** `discover_institutional_pages` — hiç kampanya sayfası bulunamayan bankalar için Hakkımızda/Katılım Bankacılığı/Ürün-Hizmet gibi kurumsal sayfalar toplanır; böylece **her banka sistemde temsil edilir**.
  - ADİL gerçek olarak tarandı (2 sayfa), mevcut veriyle birleştirilip temizlendi ve DB'ye seed + NLP reprocess edildi.
- **Doğrulama:** `python -m src.scraper.main 1` → ADİL 2 sayfa, doğru Türkçe encoding. `/finansman/bankalar` → 10 banka; `/finansman/ozet` ve `/finansman/karsilastirma` → 124 kayıt, ADİL dahil, 0 undefined alan. Vektör indeksinde ADİL sayfaları retrieve ediliyor (RAG). Birim testler: encoding çözümü (4), PDF/kurumsal keşif (3), 10-banka veri seti (1). `pytest tests/` → 121 passed.
- **Sonuçlar:** ADİL institutional sayfaları kâr payı/tutar içermez (tutar/karOrani=0), bu doğru davranıştır (kampanya değil kurumsal içerik). Scraper artık minimal/yeni bankalarda da veri toplayabilir.

## ADR-007: Demo Videosu ve Sunum (PDF/PPTX) Üretimi

- **Tarih:** 16 Temmuz 2026
- **Durum:** Kabul edildi (kapsam sınırı)
- **Bağlam:** TASKS.md Hafta 5, Kişi 4 "Demo videosu çekimi ve sunum (PDF+PPTX) hazırlığı" maddesi, fiziksel/insan işi gerektirir; bir coding agent video çekemez ve binary sunum dosyası üretemez.
- **Karar:** Agent; README finalize, proje dokümantasyonu (`docks/`) ve kaynak kodu tamamlar. Demo videosu ve PPTX/PDF sunum dosyaları **ekip tarafından manuel** hazırlanır. Gerekli anlatım içeriği dokümantasyonlardan türetilebilir şekilde bırakılır.
- **Gerekçe:** Üretim dışı binary varlıkları otomatik üretmek mümkün değil; yarışma teslimi için insan onayı gereklidir.
- **Alternatifler:** Yok (fiziksel kısıt).
- **Sonuçlar:** README "Teslim Edilecekler Durumu" tablosunda bu kalemler "ekip tarafından tamamlanacak" olarak işaretlendi.