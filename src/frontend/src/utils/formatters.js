// src/utils/formatters.js
// Tablo 4.2: Kurumsal Formatlama Standartları
// Tüm fonksiyonlar pure function (yan etkisiz) — test edilebilir yapıda

/**
 * Para formatı: 50000 → "50.000 ₺"
 * Kural: Binlik ayracı nokta, para birimi sonda boşluklu.
 * @param {number} deger
 * @returns {string}
 */
export const formatParaBirimi = (deger) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(deger);
};

/**
 * Oran formatı: 2.35 → "%2,35"
 * Kural: Yüzde işareti başta bitişik, ondalık ayracı virgül.
 * @param {number} deger
 * @returns {string}
 */
export const formatOran = (deger) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(deger / 100);
};

/**
 * Tarih formatı: "2026-07-13" → "13.07.2026"
 * Kural: GG.AA.YYYY formatı, ayraç nokta.
 * @param {string|Date} tarih
 * @returns {string}
 */
export const formatTarih = (tarih) => {
  const date = typeof tarih === 'string' ? new Date(tarih) : tarih;
  return new Intl.DateTimeFormat('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date);
};
