// src/pages/ForgotPassword.jsx
// Şifremi Unuttum Sayfası — Tam Ekran Minimalist Tasarım
// Named Export — export default YASAKTIR (ADR-001)
// Özellikler: E-posta form doğrulama, absolute top-right dil/tema kontrolü, responsive minimalist kart, anasayfa/giriş linkleri

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Bot, ArrowLeft, Mail, Sun, Moon } from 'lucide-react';
import { ROUTES } from '../constants/routes';
import { useI18n } from '../context/I18nContext';
import { useTheme } from '../context/ThemeContext';
import { cn } from '../utils/styleUtils';

const TRANSLATIONS = {
  tr: {
    title: "Şifremi Unuttum",
    subtitle: "Şifrenizi sıfırlamak için kayıtlı e-posta adresinizi girin.",
    emailLabel: "E-posta Adresi",
    emailPlaceholder: "ornek@domain.com",
    submitBtn: "Sıfırlama Linki Gönder",
    successMsg: "Sıfırlama linki e-postanıza gönderildi!",
    backLogin: "Giriş Ekranına Dön",
    backHome: "Ana Sayfaya Dön",
    toggleLight: "Açık temaya geç",
    toggleDark: "Koyu temaya geç",
    errorRequired: "Bu alan zorunludur.",
    errorInvalidEmail: "Geçersiz e-posta formatı."
  },
  en: {
    title: "Forgot Password",
    subtitle: "Enter your registered email address to reset your password.",
    emailLabel: "Email Address",
    emailPlaceholder: "example@domain.com",
    submitBtn: "Send Reset Link",
    successMsg: "Reset link has been sent to your email!",
    backLogin: "Back to Sign In",
    backHome: "Back to Home",
    toggleLight: "Switch to light theme",
    toggleDark: "Switch to dark theme",
    errorRequired: "This field is required.",
    errorInvalidEmail: "Invalid email format."
  }
};

export const ForgotPassword = () => {
  const { dil, dilDegistir } = useI18n();
  const { koyuMu, temaDegistir } = useTheme();
  
  // State
  const [email, setEmail] = useState('');
  const [emailHata, setEmailHata] = useState('');
  const [gonderildi, setGonderildi] = useState(false);

  const t = (key) => {
    return TRANSLATIONS[dil]?.[key] ?? TRANSLATIONS['tr'][key] ?? key;
  };

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
    if (emailHata) setEmailHata('');
  };

  const validate = () => {
    let gecerli = true;
    if (!email.trim()) {
      setEmailHata(t('errorRequired'));
      gecerli = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setEmailHata(t('errorInvalidEmail'));
      gecerli = false;
    }
    return gecerli;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      setGonderildi(true);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col justify-center items-center px-4 bg-white text-black dark:bg-black dark:text-white transition-colors duration-300">
      
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

      {/* Şifre Sıfırlama Kartı */}
      <div className="w-full max-w-md mx-auto rounded-3xl border border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-900/30 backdrop-blur-sm p-6 shadow-sm">
        
        {/* Logo & Başlık */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="h-10 w-10 rounded-full bg-black dark:bg-white flex items-center justify-center text-white dark:text-black shadow-md mb-4">
            <Bot size={22} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
          <p className="mt-2 text-xs text-neutral-500 dark:text-neutral-400 max-w-[280px]">
            {t('subtitle')}
          </p>
        </div>

        {gonderildi ? (
          <div className="text-center py-6">
            <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 mb-4 font-bold text-lg">
              ✓
            </div>
            <p className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">
              {t('successMsg')}
            </p>
            <Link
              to={ROUTES.LOGIN}
              className="mt-6 inline-flex items-center justify-center w-full py-3.5 rounded-xl text-sm font-semibold shadow-md bg-black text-white hover:bg-neutral-900 dark:bg-white dark:text-black dark:hover:bg-neutral-100 transition-all focus:outline-none"
            >
              {t('backLogin')}
            </Link>
          </div>
        ) : (
          /* Form */
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            {/* E-posta */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-neutral-600 dark:text-neutral-300">
                {t('emailLabel')}
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
                  <Mail size={16} />
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={handleEmailChange}
                  placeholder={t('emailPlaceholder')}
                  className={cn(
                    "w-full pl-10 pr-4 py-3 rounded-xl border bg-white dark:bg-black text-sm focus:outline-none transition-all placeholder:text-neutral-400",
                    emailHata
                      ? "border-red-500 ring-1 ring-red-500"
                      : "border-neutral-200 dark:border-neutral-800 focus:ring-1 focus:ring-gray-500"
                  )}
                />
              </div>
              {emailHata && (
                <span className="text-[10px] font-semibold text-red-500 mt-0.5 pl-1 animate-fade-in">
                  {emailHata}
                </span>
              )}
            </div>

            {/* Gönder Butonu */}
            <button
              type="submit"
              className="w-full py-3.5 mt-2 rounded-xl text-sm font-semibold shadow-md bg-black text-white hover:bg-neutral-900 dark:bg-white dark:text-black dark:hover:bg-neutral-100 transition-all active:scale-[0.99] focus:outline-none"
            >
              {t('submitBtn')}
            </button>
          </form>
        )}

        {!gonderildi && (
          <div className="mt-6 text-center text-xs text-neutral-500 dark:text-neutral-400">
            <Link
              to={ROUTES.LOGIN}
              className="font-bold text-black dark:text-white hover:underline focus:outline-none"
            >
              {t('backLogin')}
            </Link>
          </div>
        )}

      </div>

      {/* Ana Sayfaya Dön */}
      <Link
        to={ROUTES.LANDING}
        className="mt-4 sm:mt-8 flex items-center gap-1.5 text-xs font-semibold text-neutral-500 dark:text-neutral-400 hover:text-neutral-800 dark:hover:text-neutral-200 transition-colors focus:outline-none"
      >
        <ArrowLeft size={14} />
        <span>{t('backHome')}</span>
      </Link>

    </div>
  );
};
