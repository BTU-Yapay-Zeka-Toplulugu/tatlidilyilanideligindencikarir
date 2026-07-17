// src/components/ErrorState.jsx
// Hata durumu bileşeni — i18n + tam siyah/beyaz tema
// Named Export — export default YASAKTIR

import PropTypes from 'prop-types';
import { AlertTriangle } from 'lucide-react';
import { useI18n } from '../context/I18nContext';

/**
 * @param {object}    props
 * @param {string}    props.mesaj        — Hata açıklaması
 * @param {()=>void}  [props.onYeniDene]
 * @param {string}    [props.butonMetni] — Özel buton metni (yoksa i18n'den alınır)
 */
export const ErrorState = ({ mesaj, onYeniDene, butonMetni }) => {
  const { t } = useI18n();
  const btnMetni = butonMetni ?? t('common.error.retryBtn');

  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-red-200 bg-red-50 px-8 py-14 text-center dark:border-red-500/20 dark:bg-red-950/10">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 dark:bg-red-950/40">
        <AlertTriangle size={22} className="text-red-500" aria-hidden="true" />
      </div>
      {/* i18n: başlık artık sabit değil — t('common.error.title') */}
      <h3 className="text-sm font-semibold text-black dark:text-white">
        {t('common.error.title')}
      </h3>
      <p className="mt-1 max-w-xs text-sm text-black/50 dark:text-white/50">
        {mesaj}
      </p>
      {onYeniDene && (
        <button
          onClick={onYeniDene}
          className="mt-6 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700 focus:outline-none focus:ring-0"
        >
          {btnMetni}
        </button>
      )}
    </div>
  );
};

ErrorState.propTypes = {
  mesaj:      PropTypes.string.isRequired,
  onYeniDene: PropTypes.func,
  butonMetni: PropTypes.string,
};
