// src/dashboard/types/dashboard.types.js
// JSDoc tip tanımları — TypeScript olmadan tip güvenliği sağlar
// Servis fonksiyonları bu tipleri JSDoc @returns ile referans alır

/**
 * @typedef {object} FinansmanKalemi
 * @property {string} id
 * @property {string} bankaAdi
 * @property {string} urunAdi
 * @property {number} tutar          - Ham sayı (formatParaBirimi ile gösterilir)
 * @property {number} karOrani       - Ham yüzde (formatOran ile gösterilir)
 * @property {string} vade           - Ay sayısı
 * @property {string} tarih          - ISO 8601 formatı (formatTarih ile gösterilir)
 */

/**
 * @typedef {FinansmanKalemi[]} FinansmanOzetiResponse
 */

/**
 * @typedef {object} KarsilastirmaKalemi
 * @property {string} bankaId
 * @property {string} bankaAdi
 * @property {FinansmanKalemi[]} urunler
 */

/**
 * @typedef {KarsilastirmaKalemi[]} KarsilastirmaResponse
 */

/**
 * @typedef {object} BankaKalemi
 * @property {string} id
 * @property {string} ad
 * @property {string} [logo]
 */

/**
 * @typedef {BankaKalemi[]} BankaListesiResponse
 */

// Bu dosya yalnızca tip tanımları içerir — çalışma zamanı kodu yoktur.
export {};
