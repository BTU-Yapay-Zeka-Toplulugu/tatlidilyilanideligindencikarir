// src/dashboard/hooks/useFinansmanOzeti.js
// Bölüm 4 / Örnek 4.1: 4 Temel State Yönetimi (Loading, Error, Empty, Success)
// Kural: Sayfa bileşeni veriyi nasıl çekeceğini bilmez — bu hook'u çağırır.
// Kural: AbortController ile temizleme — bellek sızıntısı önlemi.
// Named Export — export default YASAKTIR

import { useState, useEffect, useCallback } from 'react';
import { fetchFinansmanOzeti } from '../services/dashboardService';

/**
 * Finansman özet verisini yöneten custom hook.
 * Loading / Success / Empty / Error durumlarını sağlar.
 *
 * @returns {{
 *   data: import('../types/dashboard.types').FinansmanOzetiResponse,
 *   status: 'loading'|'success'|'empty'|'error',
 *   hata: string|null,
 *   yenile: () => void
 * }}
 */
export const useFinansmanOzeti = () => {
  const [data, setData] = useState([]);
  const [status, setStatus] = useState('loading');
  const [hata, setHata] = useState(null);

  const veriGetir = useCallback(() => {
    const controller = new AbortController();
    setStatus('loading');
    setHata(null);

    fetchFinansmanOzeti(controller.signal)
      .then((res) => {
        if (res.length === 0) {
          setStatus('empty');
        } else {
          setData(res);
          setStatus('success');
        }
      })
      .catch((err) => {
        // AbortController iptali hata sayılmaz
        if (err.name === 'CanceledError' || err.name === 'AbortError') return;
        setHata(err.message || 'Bilinmeyen bir hata oluştu.');
        setStatus('error');
      });

    // Cleanup: bileşen unmount olduğunda veya re-fetch yapıldığında isteği iptal et
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const temizle = veriGetir();
    return temizle;
  }, [veriGetir]);

  return { data, status, hata, yenile: veriGetir };
};
