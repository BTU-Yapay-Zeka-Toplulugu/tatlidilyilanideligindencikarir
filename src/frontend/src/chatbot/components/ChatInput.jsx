// src/chatbot/components/ChatInput.jsx
// Bölüm 5: Kullanıcı mesaj giriş alanı — Gemini tarzı yuvarlak pill tasarımı
// rounded-3xl, hafif gölge, backdrop-blur, floating send butonu
// Focus outline ringler tamamen kaldırıldı
// Named Export — export default YASAKTIR

import { useCallback, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Send, Square } from 'lucide-react';
import { cn } from '../../utils/styleUtils';
import { STREAMING_DURUM } from '../../constants/chatSabitleri';
import { useI18n } from '../../context/I18nContext';

const TEXTAREA_MAKS_YUKSEKLIK_PX = 180;

/**
 * Gemini tarzı yuvarlak mesaj giriş alanı.
 */
export const ChatInput = ({ deger, onDegisim, onGonder, _gonderiyor = false, streamingDurum }) => {
  const { t, dil } = useI18n();
  const textareaRef = useRef(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, TEXTAREA_MAKS_YUKSEKLIK_PX)}px`;
  }, [deger]);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        onGonder();
      }
    },
    [onGonder]
  );

  const akisDevamEdiyor =
    streamingDurum === STREAMING_DURUM.AKIS ||
    streamingDurum === STREAMING_DURUM.BAGLANIYOR;

  const gonderAktif = deger.trim().length > 0 || akisDevamEdiyor;

  return (
    <div className="px-2 sm:px-4 pb-2 sm:pb-4 pt-1 sm:pt-2 bg-white dark:bg-black">
      {/* Gemini tarzı pill input — pure black/white theme */}
      <div
        className={cn(
          'relative rounded-3xl border bg-white/95 shadow-[0_4px_24px_rgba(0,0,0,0.04)]',
          'backdrop-blur-sm transition-all duration-200',
          'focus-within:shadow-[0_4px_32px_rgba(0,0,0,0.08)]',
          'dark:bg-black/95 dark:shadow-[0_4px_24px_rgba(255,255,255,0.05)]',
          'dark:focus-within:shadow-[0_4px_32px_rgba(255,255,255,0.08)]',
          'border-black/10 focus-within:border-black/20 dark:border-white/10 dark:focus-within:border-white/20'
        )}
      >
        {/* Textarea — Focus ring yok */}
        <textarea
          ref={textareaRef}
          value={deger}
          onChange={(e) => onDegisim(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder={t('chatbot.placeholder')}
          aria-label={t('chatbot.placeholder')}
          className={cn(
            'w-full resize-none bg-transparent',
            'pl-4 sm:pl-5 pr-12 sm:pr-14 py-3 sm:py-4',
            'text-xs sm:text-sm leading-relaxed text-black placeholder-black/30',
            'focus:outline-none focus:ring-0 outline-none',
            'dark:text-white dark:placeholder-white/30',
            'max-h-[180px]'
          )}
        />

        {/* Floating send/stop butonu — Focus ring yok */}
        <button
          onClick={onGonder}
          disabled={!gonderAktif}
          aria-label={akisDevamEdiyor ? t('chatbot.stopLabel') : t('chatbot.sendLabel')}
          className={cn(
            'absolute bottom-2 right-2 sm:bottom-3 sm:right-3',
            'flex h-8 w-8 sm:h-9 sm:w-9 shrink-0 items-center justify-center rounded-full',
            'transition-all duration-200 focus:outline-none focus:ring-0 outline-none',
            akisDevamEdiyor
              ? 'bg-red-500 text-white hover:bg-red-600'
              : gonderAktif
              ? 'bg-black text-white shadow-md hover:bg-black/80 dark:bg-white dark:text-black dark:hover:bg-white/80'
              : 'cursor-not-allowed bg-black/5 text-black/20 dark:bg-white/5 dark:text-white/20'
          )}
        >
          {akisDevamEdiyor
            ? <Square size={12} className="sm:h-3.5 sm:w-3.5" aria-hidden="true" />
            : <Send size={12} className="sm:h-3.5 sm:w-3.5" aria-hidden="true" />
          }
        </button>
      </div>

      {/* Kısayol ipucu (Dikey boşluk artırıldı) */}
      <p className="mt-5 text-center text-xs text-black/40 dark:text-white/40 hidden md:block">
        {dil === 'tr' ? (
          <>
            <kbd className="px-1.5 py-0.5 border border-gray-300 dark:border-gray-600 rounded-md text-xs font-mono">Enter</kbd> ile gönder · <kbd className="px-1.5 py-0.5 border border-gray-300 dark:border-gray-600 rounded-md text-xs font-mono">Shift</kbd> + <kbd className="px-1.5 py-0.5 border border-gray-300 dark:border-gray-600 rounded-md text-xs font-mono">Enter</kbd> ile satır atla
          </>
        ) : (
          <>
            <kbd className="px-1.5 py-0.5 border border-gray-300 dark:border-gray-600 rounded-md text-xs font-mono">Enter</kbd> to send · <kbd className="px-1.5 py-0.5 border border-gray-300 dark:border-gray-600 rounded-md text-xs font-mono">Shift</kbd> + <kbd className="px-1.5 py-0.5 border border-gray-300 dark:border-gray-600 rounded-md text-xs font-mono">Enter</kbd> to add new line
          </>
        )}
      </p>
    </div>
  );
};

ChatInput.propTypes = {
  deger:          PropTypes.string.isRequired,
  onDegisim:      PropTypes.func.isRequired,
  onGonder:       PropTypes.func.isRequired,
  _gonderiyor:    PropTypes.bool,
  streamingDurum: PropTypes.string,
};
