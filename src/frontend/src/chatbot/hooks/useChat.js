// src/chatbot/hooks/useChat.js
// Bölüm 5: Sohbet state yönetimi — mesaj listesi, oturum, streaming entegrasyonu
// Kural: Componentler bu hook'u çağırır; chatApi'ye doğrudan erişmez.
// Named Export — export default YASAKTIR

import { useState, useCallback, useEffect, useRef } from 'react';
import { sohbetGecmisiniGetir } from '../services/chatApi';
import { useStreamingResponse } from './useStreamingResponse';
import { useSidebar } from '../../context/SidebarContext';

/**
 * Sohbet akışını ve mesaj listesini yöneten ana hook.
 * useStreamingResponse ile entegre çalışır.
 *
 * @returns {{
 *   mesajlar: import('../types/chat.types').Mesaj[],
 *   girisMetni: string,
 *   girisMetniGuncelle: (metin: string) => void,
 *   mesajGonderHandler: () => void,
 *   gecmisYukluyor: boolean,
 *   gonderiyor: boolean,
 *   streamingDurum: string,
 *   akisIcerigi: string
 * }}
 */
export const useChat = () => {
  const { aktifOturumId } = useSidebar();
  const [mesajlar, setMesajlar] = useState([]);
  const [girisMetni, setGirisMetni] = useState('');
  const [gecmisYukluyor, setGecmisYukluyor] = useState(true);
  const [gonderiyor, setGonderiyor] = useState(false);

  const { akisIcerigi, akisAtiflar, streamingDurum, streamingBaslat } = useStreamingResponse();

  // Streaming tamamlandığında bot mesajını listeye ekle
  const oncekiDurumRef = useRef(streamingDurum);
  useEffect(() => {
    if (oncekiDurumRef.current === 'akis' && streamingDurum === 'tamamlandi') {
      const botMesaji = {
        id: `bot-${Date.now()}`,
        rol: 'assistant',
        icerik: akisIcerigi,
        atiflar: akisAtiflar,
        zaman: new Date().toISOString(),
        akisDevam: false,
      };
      setMesajlar((onceki) => {
        // Geçici streaming mesajını kaldır, gerçekle değiştir
        const streaming = onceki.filter((m) => !m.akisDevam);
        return [...streaming, botMesaji];
      });
      setGonderiyor(false);
    }
    oncekiDurumRef.current = streamingDurum;
  }, [streamingDurum, akisIcerigi, akisAtiflar]);

  // Akış başladıkça geçici mesajı güncelle
  useEffect(() => {
    if (streamingDurum === 'akis') {
      setMesajlar((onceki) => {
        const digerler = onceki.filter((m) => !m.akisDevam);
        return [
          ...digerler,
          {
            id: 'bot-streaming',
            rol: 'assistant',
            icerik: akisIcerigi,
            atiflar: [],
            zaman: new Date().toISOString(),
            akisDevam: true,
          },
        ];
      });
    }
  }, [akisIcerigi, streamingDurum]);

  // Sohbet geçmişini yükle
  useEffect(() => {
    const controller = new AbortController();
    setGecmisYukluyor(true);

    sohbetGecmisiniGetir(aktifOturumId, controller.signal)
      .then((gecmis) => {
        setMesajlar(gecmis ?? []);
      })
      .catch((err) => {
        if (err.name === 'CanceledError' || err.name === 'AbortError') return;
        setMesajlar([]);
      })
      .finally(() => setGecmisYukluyor(false));

    return () => controller.abort();
  }, [aktifOturumId]);

  /**
   * Giriş metnini günceller.
   * @param {string} metin
   */
  const girisMetniGuncelle = useCallback((metin) => {
    setGirisMetni(metin);
  }, []);

  /**
   * Kullanıcı mesajını gönderir ve streaming başlatır.
   */
  const mesajGonderHandler = useCallback(async () => {
    const temizMetin = girisMetni.trim();
    if (!temizMetin || gonderiyor) return;

    // Kullanıcı mesajını hemen listeye ekle
    const kullaniciMesaji = {
      id: `kullanici-${Date.now()}`,
      rol: 'user',
      icerik: temizMetin,
      zaman: new Date().toISOString(),
    };

    setMesajlar((onceki) => [...onceki, kullaniciMesaji]);
    setGirisMetni('');
    setGonderiyor(true);

    // Streaming başlat (WebSocket üzerinden)
    streamingBaslat(temizMetin, aktifOturumId);
  }, [girisMetni, gonderiyor, streamingBaslat, aktifOturumId]);

  return {
    mesajlar,
    girisMetni,
    girisMetniGuncelle,
    mesajGonderHandler,
    gecmisYukluyor,
    gonderiyor,
    streamingDurum,
    akisIcerigi,
  };
};
