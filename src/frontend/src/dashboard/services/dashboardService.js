// src/dashboard/services/dashboardService.js
// Örnek 3.2: Component'ten İzole Edilmiş Service Layer
// Kural: Axios bu dosyadan dışarıya sızmaz; componentler sadece bu fonksiyonları çağırır.
// Kural: Tüm endpoint'ler API_ENDPOINTS sabitinden okunur — Magic String YASAK.
// Named Export — export default YASAKTIR

import { apiClient } from '../../services/apiClient';
import { API_ENDPOINTS } from '../../constants/apiEndpoints';

/**
 * Finansman özet verisini getirir.
 * AbortController ile iptal desteği — bellek sızıntısı önlemi (Best Practices).
 * @param {AbortSignal} [signal]
 * @returns {Promise<import('../types/dashboard.types').FinansmanOzetiResponse>}
 */
export const fetchFinansmanOzeti = async (signal) => {
  const response = await apiClient.get(API_ENDPOINTS.DASHBOARD.FINANSMAN_OZET, { signal });
  return response.data;
};

/**
 * Bankalar arası finansman karşılaştırma verisini getirir.
 * @param {{ bankaIds?: string[], urunTuru?: string }} [filtreler]
 * @param {AbortSignal} [signal]
 * @returns {Promise<import('../types/dashboard.types').KarsilastirmaResponse>}
 */
export const fetchFinansmanKarsilastirma = async (filtreler = {}, signal) => {
  const response = await apiClient.get(API_ENDPOINTS.DASHBOARD.FINANSMAN_KARSILASTIRMA, {
    params: filtreler,
    signal,
  });
  return response.data;
};

/**
 * Mevcut banka listesini getirir (filtre seçenekleri için).
 * @param {AbortSignal} [signal]
 * @returns {Promise<import('../types/dashboard.types').BankaListesiResponse>}
 */
export const fetchBankaListesi = async (signal) => {
  const response = await apiClient.get(API_ENDPOINTS.DASHBOARD.BANKA_LISTESI, { signal });
  return response.data;
};
