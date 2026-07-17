// src/chatbot/components/SuggestionChips.jsx
// Bölüm 5 / Tablo 5.1: Ready suggestions — Süzülen saydam arka planlı yapı
// Named Export — export default YASAKTIR

import PropTypes from 'prop-types';
import { useI18n } from '../../context/I18nContext';

/**
 * Yatay kaydırılabilir hazır soru önerileri.
 */
export const SuggestionChips = ({ onSec, gizle = false }) => {
  const { t } = useI18n();

  if (gizle) return null;

  const sorular = t('chatbot.questions');
  if (!Array.isArray(sorular) || sorular.length === 0) return null;

  return (
    <div
      className="px-4 py-3 bg-transparent border-0 shadow-none"
      aria-label={t('chatbot.suggestionsLabel')}
    >
      <p className="mb-2 text-xs font-medium text-black/40 dark:text-white/40">
        {t('chatbot.suggestionsLabel')}
      </p>

      {/* Yatay kaydırılabilir */}
      <div className="flex gap-2 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {sorular.map((soru) => (
          <button
            key={soru}
            onClick={() => onSec(soru)}
            className="shrink-0 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors focus:outline-none focus:ring-0 outline-none border-black/10 bg-black/5 text-black/80 hover:bg-black/10 dark:border-white/10 dark:bg-white/5 dark:text-white/80 dark:hover:bg-white/10"
          >
            {soru}
          </button>
        ))}
      </div>
    </div>
  );
};

SuggestionChips.propTypes = {
  onSec: PropTypes.func.isRequired,
  gizle: PropTypes.bool,
};
