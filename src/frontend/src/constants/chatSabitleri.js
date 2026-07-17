// src/constants/chatSabitleri.js
// Magic String YASAK — Chatbot modülüne ait tüm sabitler burada merkezi olarak tanımlanır

// Streaming durum değerleri — useStreamingResponse ile uyumlu
export const STREAMING_DURUM = {
  BEKLEME:    'bekleme',
  BAGLANIYOR: 'baglaniyor',
  AKIS:       'akis',
  TAMAMLANDI: 'tamamlandi',
  HATA:       'hata',
};

// Mesaj rol sabitleri
export const MESAJ_ROLU = {
  KULLANICI: 'user',
  ASISTAN:   'assistant',
};

// Öneri sorular — Katılım bankacılığı bağlamında
export const ONERI_SORULAR = [
  'Araç finansmanı için en düşük kâr oranı nedir?',
  'Konut finansmanında hangi bankalar öne çıkıyor?',
  'Katılım hesabı ile vadeli hesap arasındaki fark nedir?',
  'Bireysel emeklilik sisteminde katılım bankası seçenekleri neler?',
  'Altın hesabı açmak için ne gerekli?',
];

// Scroll threshold — kullanıcının altta olup olmadığını belirleyen piksel eşiği
export const SCROLL_ESIGI_PX = 60;
