// src/dashboard/hooks/useFinansmanKarsilastirma.js
// Bölüm 4: Karşılaştırma tablosu verisi + filtre yönetimi
// Kural: useMemo/useCallback ile gereksiz re-render önleme (Best Practices).
// Named Export — export default YASAKTIR

import { useState, useEffect, useCallback, useMemo } from 'react';
import { fetchFinansmanKarsilastirma } from '../services/dashboardService';

/**
 * @typedef {'loading'|'success'|'empty'|'error'} DurumTipi
 */

/**
 * Finansman karşılaştırma verisi + istemci taraflı sıralama ve filtre yönetimi.
 *
 * @param {{ bankaIds?: string[], urunTuru?: string }} [baslangiçFiltreleri={}]
 * @returns {{
 *   data: import('../types/dashboard.types').KarsilastirmaResponse,
 *   filtrelenmisData: import('../types/dashboard.types').KarsilastirmaResponse,
 *   status: DurumTipi,
 *   hata: string|null,
 *   siralamaAlani: string|null,
 *   siralamaYonu: 'asc'|'desc',
 *   siralama: (alan: string) => void,
 *   yenile: () => void
 * }}
 */
export const useFinansmanKarsilastirma = (baslangiçFiltreleri = {}) => {
  const [data, setData] = useState([]);
  const [status, setStatus] = useState('loading');
  const [hata, setHata] = useState(null);
  const [siralamaAlani, setSiralamaAlani] = useState(null);
  const [siralamaYonu, setSiralamaYonu] = useState('asc');

  const veriGetir = useCallback(() => {
    const controller = new AbortController();
    setStatus('loading');
    setHata(null);

    fetchFinansmanKarsilastirma(baslangiçFiltreleri, controller.signal)
      .then((res) => {
        if (!res || res.length === 0) {
          setStatus('empty');
        } else {
          setData(res);
          setStatus('success');
        }
      })
      .catch((err) => {
        if (err.name === 'CanceledError' || err.name === 'AbortError') return;
        setHata(err.message || 'Veriler yüklenirken bir sorun oluştu.');
        setStatus('error');
      });

    return () => controller.abort();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const temizle = veriGetir();
    return temizle;
  }, [veriGetir]);

  /**
   * Tablo başlığına tıklandığında istemci taraflı sıralama — sayfa yenilemez.
   * ADR-004: Skeleton loading ve istemci taraflı sıralama.
   * @param {string} alan
   */
  const siralama = useCallback(
    (alan) => {
      setSiralamaYonu((mevcutYon) =>
        siralamaAlani === alan && mevcutYon === 'asc' ? 'desc' : 'asc'
      );
      setSiralamaAlani(alan);
    },
    [siralamaAlani]
  );

  /**
   * useMemo: Sıralama her render'da yeniden hesaplanmaz — sadece bağımlılıklar değişince.
   * Bölüm 4 Best Practices: Memoization.
   */
  const filtrelenmisData = useMemo(() => {
    if (!siralamaAlani || status !== 'success') return data;

    return [...data].sort((a, b) => {
      const aVal = a[siralamaAlani];
      const bVal = b[siralamaAlani];

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return siralamaYonu === 'asc' ? aVal - bVal : bVal - aVal;
      }

      const aStr = String(aVal ?? '');
      const bStr = String(bVal ?? '');
      return siralamaYonu === 'asc' ? aStr.localeCompare(bStr, 'tr') : bStr.localeCompare(aStr, 'tr');
    });
  }, [data, siralamaAlani, siralamaYonu, status]);

  return { data, filtrelenmisData, status, hata, siralamaAlani, siralamaYonu, siralama, yenile: veriGetir };
};
