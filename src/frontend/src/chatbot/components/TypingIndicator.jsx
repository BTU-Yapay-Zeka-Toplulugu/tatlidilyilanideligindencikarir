// src/chatbot/components/TypingIndicator.jsx
// Bot düşünürken gösterilen indicator — Tam Siyah/Beyaz tema
// Named Export — export default YASAKTIR

import { useI18n } from '../../context/I18nContext';

export const TypingIndicator = () => {
  const { t } = useI18n();

  return (
    <div
      className="flex w-full gap-3 px-4 py-4 bg-black/[0.02] dark:bg-white/[0.04]"
      role="status"
      aria-label={t('chatbot.thinking')}
    >
      {/* Bot avatar */}
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-black/10 text-black dark:bg-white/10 dark:text-white">
        <span className="text-xs font-bold" aria-hidden="true">AI</span>
      </div>

      {/* Üç nokta dalga animasyonu */}
      <div className="flex items-center gap-1.5 rounded-2xl bg-black/5 px-4 py-3 dark:bg-white/5">
        <span className="typing-dot h-2 w-2 rounded-full bg-black/40 dark:bg-white/40" />
        <span className="typing-dot h-2 w-2 rounded-full bg-black/40 dark:bg-white/40" />
        <span className="typing-dot h-2 w-2 rounded-full bg-black/40 dark:bg-white/40" />
      </div>
    </div>
  );
};
