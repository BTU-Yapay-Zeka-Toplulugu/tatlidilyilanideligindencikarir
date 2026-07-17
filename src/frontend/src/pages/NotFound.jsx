// src/pages/NotFound.jsx
// 404 — Bilinmeyen rota için fallback sayfası — Tam Ekran Minimalist Tasarım (Sol menüsüz)
// Named Export — export default YASAKTIR (ADR-001)
// Özellikler: Büyük 404 başlığı, siyah/beyaz tema, dil/tema toggler, ana sayfaya dönüş butonu

import { Link } from 'react-router-dom';
import { FileQuestion, ArrowLeft, Sun, Moon } from 'lucide-react';
import { ROUTES } from '../constants/routes';
import { useI18n } from '../context/I18nContext';
import { useTheme } from '../context/ThemeContext';

const TRANSLATIONS = {
  tr: {
    code: "404",
    title: "Sayfa Bulunamadı",
    desc: "Aradığınız sayfa mevcut değil veya taşınmış olabilir.",
    backHome: "Ana Sayfaya Dön",
    toggleLight: "Açık temaya geç",
    toggleDark: "Koyu temaya geç"
  },
  en: {
    code: "404",
    title: "Page Not Found",
    desc: "The page you are looking for does not exist or might have been moved.",
    backHome: "Back to Home",
    toggleLight: "Switch to light theme",
    toggleDark: "Switch to dark theme"
  }
};

export const NotFound = () => {
  const { dil, dilDegistir } = useI18n();
  const { koyuMu, temaDegistir } = useTheme();

  const t = (key) => {
    return TRANSLATIONS[dil]?.[key] ?? TRANSLATIONS['tr'][key] ?? key;
  };

  return (
    <div className="relative min-h-screen flex flex-col justify-center items-center px-4 bg-white text-black dark:bg-black dark:text-white transition-colors duration-300 select-none">
      
      {/* Üst Sağ Köşe Tema & Dil Seçici */}
      <div className="absolute top-6 right-6 flex items-center gap-4 z-50">
        <button
          onClick={temaDegistir}
          aria-label={koyuMu ? t('toggleLight') : t('toggleDark')}
          className="p-2 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors text-neutral-600 dark:text-neutral-300 focus:outline-none outline-none"
        >
          {koyuMu ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        <button
          onClick={() => dilDegistir(dil === 'tr' ? 'en' : 'tr')}
          className="text-xs font-bold uppercase p-2 hover:bg-neutral-100 dark:hover:bg-neutral-900 rounded-full transition-colors focus:outline-none outline-none"
          aria-label={`Switch language to ${dil === 'tr' ? 'EN' : 'TR'}`}
        >
          {dil === 'tr' ? 'en' : 'tr'}
        </button>
      </div>

      {/* 404 Kapsayıcısı */}
      <div className="flex flex-col items-center text-center max-w-md w-full">
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-neutral-100 dark:bg-neutral-900 text-neutral-500 dark:text-neutral-400 shadow-sm border border-neutral-100 dark:border-neutral-800">
          <FileQuestion size={32} />
        </div>
        
        <h1 className="text-8xl sm:text-9xl font-black tracking-tight text-neutral-300 dark:text-neutral-800 leading-none">
          {t('code')}
        </h1>
        
        <h2 className="mt-4 text-2xl font-bold tracking-tight">
          {t('title')}
        </h2>
        
        <p className="mt-2 text-sm text-neutral-500 dark:text-neutral-400 max-w-xs leading-relaxed">
          {t('desc')}
        </p>
        
        <Link
          to={ROUTES.LANDING}
          className="mt-10 flex items-center gap-2 px-6 py-3.5 rounded-xl text-sm font-semibold shadow-md bg-black text-white hover:bg-neutral-900 dark:bg-white dark:text-black dark:hover:bg-neutral-100 transition-all active:scale-[0.98] focus:outline-none"
        >
          <ArrowLeft size={16} />
          <span>{t('backHome')}</span>
        </Link>
      </div>

    </div>
  );
};
