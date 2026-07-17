// src/chatbot/hooks/useStreamingResponse.js
// Bölüm 5 / ADR-005: Streaming UI Hook — WebSocket üzerinden RAG yanıtı
// Kural: Scroll işlemi bu hook'tan bağımsız; caller useRef ile yönetir (ADR-005).
// Kural: Akış sırasında UI kilitlenmez — kullanıcı input alanıyla etkileşime devam eder.
// Named Export — export default YASAKTIR

import { useState, useCallback, useRef } from 'react';
import { streamingBaglantiOlustur } from '../services/chatApi';

/**
 * @typedef {'bekleme'|'baglaniyor'|'akis'|'tamamlandi'|'hata'} StreamingDurum
 */

/**
 * WebSocket üzerinden RAG streaming yanıtını yöneten hook.
 *
 * @returns {{
 *   akisIcerigi: string,
 *   akisAtiflar: import('../types/chat.types').Atif[],
 *   streamingDurum: StreamingDurum,
 *   streamingBaslat: (mesaj: string, oturumId: string) => void,
 *   streamingDurdur: () => void
 * }}
 */
export const useStreamingResponse = () => {
  const [akisIcerigi, setAkisIcerigi] = useState('');
  const [akisAtiflar, setAkisAtiflar] = useState([]);
  const [streamingDurum, setStreamingDurum] = useState('bekleme');

  // WebSocket referansı — render tetiklemez, ADR-005 uyumu
  const wsRef = useRef(null);

  /**
   * WebSocket bağlantısını kapatır ve durumu sıfırlar.
   */
  const streamingDurdur = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setStreamingDurum('bekleme');
  }, []);

  /**
   * Yeni bir mesaj için streaming başlatır.
   * Varsa önceki bağlantıyı temizler, yeni WebSocket açar.
   * @param {string} mesaj
   * @param {string} oturumId
   */
  const streamingBaslat = useCallback(
    (mesaj, oturumId) => {
      // Önceki bağlantıyı temizle
      streamingDurdur();

      // Önceki içeriği sıfırla
      setAkisIcerigi('');
      setAkisAtiflar([]);
      setStreamingDurum('baglaniyor');

      const ws = streamingBaglantiOlustur({
        onChunk: (chunk) => {
          setStreamingDurum('akis');
          // Metin parçaları biriktirilir — Bölüm 5 Streaming UI
          setAkisIcerigi((onceki) => onceki + chunk);
        },

        onAtiflar: (atiflar) => {
          setAkisAtiflar(atiflar);
        },

        onBitti: () => {
          setStreamingDurum('tamamlandi');
          wsRef.current = null;
        },

        onHata: (_event) => {
          setStreamingDurum('hata');
          wsRef.current = null;
        },
      });

      // Bağlantı açılınca mesajı gönder
      ws.onopen = () => {
        ws.send(JSON.stringify({ mesaj, oturumId }));
      };

      wsRef.current = ws;
    },
    [streamingDurdur]
  );

  return { akisIcerigi, akisAtiflar, streamingDurum, streamingBaslat, streamingDurdur };
};
