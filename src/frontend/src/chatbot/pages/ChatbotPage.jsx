// src/chatbot/pages/ChatbotPage.jsx
// Bölüm 5: RAG Chatbot UI/UX — streaming, auto-scroll, tam entegrasyon
// ADR-005: Scroll ref ile yönetilir, requestAnimationFrame
// ADR-007: dangerouslySetInnerHTML kullanılmaz
// Named Export — export default YASAKTIR

import { useCallback, useEffect } from 'react';
import { ChevronDown, Bot } from 'lucide-react';
import { useChat }           from '../hooks/useChat';
import { useScrollToBottom } from '../../hooks/useScrollToBottom';
import { ChatMessage }       from '../components/ChatMessage';
import { TypingIndicator }   from '../components/TypingIndicator';
import { SuggestionChips }   from '../components/SuggestionChips';
import { ChatInput }         from '../components/ChatInput';
import { STREAMING_DURUM, MESAJ_ROLU } from '../../constants/chatSabitleri';
import { cn }                from '../../utils/styleUtils';
import { useI18n }           from '../../context/I18nContext';
import { useSidebar }        from '../../context/SidebarContext';

export const ChatbotPage = () => {
  const { t } = useI18n();
  const { setSohbetBasladi } = useSidebar();
  const {
    mesajlar,
    girisMetni,
    girisMetniGuncelle,
    mesajGonderHandler,
    gecmisYukluyor,
    gonderiyor,
    streamingDurum,
  } = useChat();

  // Sohbet durumunu Layout katmanıyla senkronize et (Aurora yavaşlatma ve yıldız gizleme için)
  useEffect(() => {
    const gecmisVar = mesajlar.some((m) => m.rol === MESAJ_ROLU.KULLANICI);
    setSohbetBasladi(gecmisVar);
    return () => setSohbetBasladi(false);
  }, [mesajlar, setSohbetBasladi]);

  // ADR-005: Mesaj sayısı değişince scroll tetikle
  const { scrollRef, otomatikKaydirma, handleScroll, asagiyaKaydır } =
    useScrollToBottom(mesajlar.length);

  const akisDevamEdiyor =
    streamingDurum === STREAMING_DURUM.AKIS ||
    streamingDurum === STREAMING_DURUM.BAGLANIYOR;

  const typingGoster = streamingDurum === STREAMING_DURUM.BAGLANIYOR;
  const gecmisVarMi  = mesajlar.some((m) => m.rol === MESAJ_ROLU.KULLANICI);

  const oneriSec = useCallback(
    (soru) => girisMetniGuncelle(soru),
    [girisMetniGuncelle]
  );

  return (
    <div className="relative flex h-full flex-col overflow-hidden bg-transparent text-black dark:text-white transition-colors duration-200">

      {/* ── HEADER ────────────────────────────────────── */}
      <header className="flex h-14 shrink-0 items-center gap-3 border-b px-5 bg-white/80 border-black/10 dark:border-white/10 dark:bg-black/80 backdrop-blur-sm z-10">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-black/5 text-black dark:bg-white/10 dark:text-white">
          <Bot size={16} aria-hidden="true" />
        </div>
        <div>
          <h1 className="text-sm font-semibold text-black dark:text-white">
            {t('chatbot.title')}
          </h1>
          <p className="text-xs text-black/55 dark:text-white/55">
            {t('chatbot.subtitle')}
          </p>
        </div>
        {akisDevamEdiyor && (
          <div className="ml-auto flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" aria-hidden="true" />
            <span className="text-xs text-black/40 dark:text-white/40">
              {t('chatbot.responding')}
            </span>
          </div>
        )}
      </header>

      {/* ── MESAJ LİSTESİ ─────────────────────────────── */}
      <main
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto bg-transparent pb-44 pt-2"
        aria-label={t('chatbot.title')}
        aria-live="polite"
        aria-relevant="additions"
      >
        {gecmisYukluyor && (
          <div className="flex h-full items-center justify-center">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-black/20 border-t-black dark:border-white/20 dark:border-t-white" />
          </div>
        )}

        {!gecmisYukluyor && mesajlar.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center px-8 text-center pb-20">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-black/5 dark:bg-white/5">
              <Bot size={28} className="text-black/40 dark:text-white/40" aria-hidden="true" />
            </div>
            <h2 className="text-lg font-semibold text-black dark:text-white">
              {t('chatbot.welcome')}
            </h2>
            <p className="mt-2 max-w-sm text-sm text-black/60 dark:text-white/60">
              {t('chatbot.welcomeDesc')}
            </p>
          </div>
        )}

        {!gecmisYukluyor && (mesajlar.length > 0 || typingGoster) && (
          <div className="max-w-3xl mx-auto w-full px-4 flex flex-col">
            {mesajlar.map((mesaj) => (
              <ChatMessage key={mesaj.id} mesaj={mesaj} />
            ))}
            {typingGoster && <TypingIndicator />}
          </div>
        )}
      </main>

      {/* ── AŞAĞI KAYDIR BUTONU ─────────────────────── */}
      {!otomatikKaydirma && (
        <div className="pointer-events-none absolute bottom-48 left-1/2 -translate-x-1/2 z-20">
          <button
            onClick={asagiyaKaydır}
            className={cn(
              'pointer-events-auto flex items-center gap-1.5 rounded-full px-4 py-2 text-xs font-medium shadow-lg transition-colors border focus:outline-none focus:ring-0 outline-none',
              'border-black/10 bg-white text-black hover:bg-black/5',
              'dark:border-white/10 dark:bg-black dark:text-white dark:hover:bg-white/5'
            )}
            aria-label="En alt mesaja kaydır"
          >
            <ChevronDown size={14} aria-hidden="true" />
            {t('chatbot.newMessage')}
          </button>
        </div>
      )}

      {/* ── YÜZEN (FLOATING) ALT INPUT ALANI ── */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-white via-white/95 to-transparent dark:from-black dark:via-black/95 dark:to-transparent pt-12 pb-4 px-4 pointer-events-none z-10">
        <div className="max-w-3xl mx-auto w-full pointer-events-auto flex flex-col gap-2">
          <SuggestionChips onSec={oneriSec} gizle={gecmisVarMi} />
          <ChatInput
            deger={girisMetni}
            onDegisim={girisMetniGuncelle}
            onGonder={mesajGonderHandler}
            gonderiyor={gonderiyor}
            streamingDurum={streamingDurum}
          />
        </div>
      </div>
    </div>
  );
};
