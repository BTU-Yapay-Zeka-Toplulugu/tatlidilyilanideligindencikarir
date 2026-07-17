// src/hooks/useScrollToBottom.js
// ADR-005: Auto Scroll Mantığının Ref Yönetimi
// Kural: Scroll işlemi React state'e bağlanmaz; doğrudan useRef + requestAnimationFrame ile yapılır.
// Kural: Kullanıcı yukarı kaydırırsa otomatik scroll duraklar — "Aşağı Kaydır" butonu belirir.
// Named Export — export default YASAKTIR

import { useRef, useState, useCallback, useEffect } from 'react';
import { SCROLL_ESIGI_PX } from '../constants/chatSabitleri';

/**
 * ADR-005 uyumlu auto-scroll yönetimi.
 * @param {*} bagimlilik - Bu değer değişince scroll tetiklenir (örn: mesaj listesi uzunluğu)
 * @returns {{
 *   scrollRef: React.RefObject,
 *   otomatikKaydirma: boolean,
 *   handleScroll: () => void,
 *   asagiyaKaydır: () => void
 * }}
 */
export const useScrollToBottom = (bagimlilik) => {
  const scrollRef = useRef(null);
  const [otomatikKaydirma, setOtomatikKaydirma] = useState(true);

  /**
   * requestAnimationFrame: 60 FPS scroll, React render döngüsünden bağımsız (ADR-005).
   */
  const asagiyaKaydır = useCallback(() => {
    requestAnimationFrame(() => {
      if (!scrollRef.current) return;
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    });
    setOtomatikKaydirma(true);
  }, []);

  /**
   * Kullanıcı kaydırma olayı — alttan SCROLL_ESIGI_PX piksel uzaktaysa otomatik scroll durur.
   */
  const handleScroll = useCallback(() => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const altindaMi = scrollHeight - scrollTop - clientHeight < SCROLL_ESIGI_PX;
    setOtomatikKaydirma(altindaMi);
  }, []);

  // Bağımlılık değişince ve otomatik kaydırma açıksa scroll tetikle
  useEffect(() => {
    if (!otomatikKaydirma) return;
    asagiyaKaydır();
  }, [bagimlilik, otomatikKaydirma, asagiyaKaydır]);

  return { scrollRef, otomatikKaydirma, handleScroll, asagiyaKaydır };
};
