// src/pages/NotFoundPage.jsx
// 404 — Bilinmeyen rota için fallback sayfası — Tam Siyah/Beyaz tema + i18n
// Named Export — export default YASAKTIR

import { Link } from 'react-router-dom';
import { FileQuestion } from 'lucide-react';
import { ROUTES } from '../constants/routes';
import { useI18n } from '../context/I18nContext';

export const NotFoundPage = () => {
  const { t } = useI18n();

  return (
    <div className="flex h-full flex-col items-center justify-center text-center bg-white text-black dark:bg-black dark:text-white transition-colors duration-200">
      <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-black/5 dark:bg-white/5">
        <FileQuestion size={32} className="text-black/40 dark:text-white/40" aria-hidden="true" />
      </div>
      <h1 className="text-3xl font-bold text-black dark:text-white">
        {t('common.notFound.code')}
      </h1>
      <p className="mt-2 text-sm font-medium text-black/50 dark:text-white/50">
        {t('common.notFound.title')}
      </p>
      <p className="mt-1 max-w-xs text-sm text-black/40 dark:text-white/40">
        {t('common.notFound.desc')}
      </p>
      <Link
        to={ROUTES.DASHBOARD}
        className="mt-8 inline-flex items-center rounded-lg bg-black text-white px-5 py-2.5 text-sm font-medium shadow-sm transition-colors hover:bg-black/80 focus:outline-none focus:ring-0 outline-none dark:bg-white dark:text-black dark:hover:bg-white/80"
      >
        {t('common.notFound.back')}
      </Link>
    </div>
  );
};
