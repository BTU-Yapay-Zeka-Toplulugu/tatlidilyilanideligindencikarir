// src/chatbot/services/chatApi.js
// Bölüm 5: RAG Chatbot servisi — REST ve WebSocket katmanları
// Kural: Axios bu dosyadan dışarıya sızmaz.
// Kural: Tüm URL'ler sabitlerden okunur — Magic String YASAK.
// Named Export — export default YASAKTIR

import { apiClient } from '../../services/apiClient';
import { API_ENDPOINTS } from '../../constants/apiEndpoints';
import { CHATBOT_WS_URL } from '../../constants/environment';

/**
 * Kullanıcı mesajını REST endpoint'e gönderir (streaming olmayan mod).
 * @param {string} mesaj
 * @param {string} [oturumId]
 * @param {AbortSignal} [signal]
 * @returns {Promise<import('../types/chat.types').ChatYanitiResponse>}
 */
export const mesajGonder = async (mesaj, oturumId, signal) => {
  const response = await apiClient.post(
    API_ENDPOINTS.CHATBOT.MESAJ_GONDER,
    { mesaj, oturumId },
    { signal }
  );
  return response.data;
};

/**
 * Sohbet geçmişini getirir.
 * @param {string} [oturumId]
 * @param {AbortSignal} [signal]
 * @returns {Promise<import('../types/chat.types').MesajListesiResponse>}
 */
export const sohbetGecmisiniGetir = async (oturumId, signal) => {
  const response = await apiClient.get(API_ENDPOINTS.CHATBOT.GECMIS, {
    params: { oturumId },
    signal,
  });
  return response.data;
};

/**
 * Oturumu temizler.
 * @param {string} oturumId
 * @returns {Promise<void>}
 */
export const oturumuTemizle = async (oturumId) => {
  await apiClient.post(API_ENDPOINTS.CHATBOT.OTURUM_TEMIZLE, { oturumId });
};

/**
 * WebSocket bağlantısı oluşturur — RAG streaming için.
 * Bölüm 5: Streaming Ready UI — WebSocket üzerinden chunk'lar anlık ekrana basılır.
 * ADR-005: Scroll işlemi bu bağlantıdan bağımsız olarak useRef ile yönetilir.
 *
 * @param {object} yapilandiriciler
 * @param {(chunk: string) => void} yapilandiriciler.onChunk     - Yeni metin parçası gelince
 * @param {(atiflar: import('../types/chat.types').Atif[]) => void} yapilandiriciler.onAtiflar  - Kaynakça gelince
 * @param {() => void} yapilandiriciler.onBitti                  - Akış tamamlanınca
 * @param {(hata: Event) => void} yapilandiriciler.onHata        - Bağlantı hatası
 * @returns {WebSocket} - Caller tarafından .close() ile kapatılabilir
 */
export const streamingBaglantiOlustur = ({ onChunk, onAtiflar, onBitti, onHata }) => {
  const ws = new WebSocket(CHATBOT_WS_URL);

  ws.onmessage = (event) => {
    let paket;
    try {
      paket = JSON.parse(event.data);
    } catch {
      // JSON olmayan ham metin de chunk olarak işle
      onChunk(event.data);
      return;
    }

    if (paket.tur === 'chunk') {
      onChunk(paket.icerik);
    } else if (paket.tur === 'atiflar') {
      onAtiflar(paket.atiflar ?? []);
    } else if (paket.tur === 'bitti') {
      onBitti();
    }
  };

  ws.onerror = onHata;

  return ws;
};
