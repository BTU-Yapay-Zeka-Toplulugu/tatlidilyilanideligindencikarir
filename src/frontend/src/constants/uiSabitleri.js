// src/constants/uiSabitleri.js
// Magic String YASAK — UI durum değerleri ve tablo sütun anahtarları buradan yönetilir

export const DURUM = {
  YUKLENIYOR: 'loading',
  BASARILI:   'success',
  BOS:        'empty',
  HATA:       'error',
};

// FinansmanKalemi nesnesinin property anahtarları — tablo sıralama için
export const TABLO_SUTUNLARI = {
  BANKA_ADI:  'bankaAdi',
  URUN_ADI:   'urunAdi',
  TUTAR:      'tutar',
  KAR_ORANI:  'karOrani',
  VADE:       'vade',
  TARIH:      'tarih',
};

export const SIRALAMA_YONU = {
  ARTAN:  'asc',
  AZALAN: 'desc',
};
