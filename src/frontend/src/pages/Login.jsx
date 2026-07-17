// src/pages/Login.jsx
// Giriş Yap Sayfası — Tam Ekran Minimalist Tasarım
// Named Export — export default YASAKTIR (ADR-001)
// Özellikler: Minimalist responsive siyah/beyaz kart, focus:ring-gray-500 inputları, dil desteği, anasayfa linki, sosyal giriş, şifremi unuttum, form doğrulama, dikey sığma optimizasyonu

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bot, ArrowLeft, Mail, Lock, Eye, EyeOff, Sun, Moon } from 'lucide-react';
import { ROUTES } from '../constants/routes';
import { useI18n } from '../context/I18nContext';
import { useTheme } from '../context/ThemeContext';
import { cn } from '../utils/styleUtils';

const TRANSLATIONS = {
  tr: {
    title: "Giriş Yap",
    subtitle: "Hesabınıza erişmek için bilgilerinizi girin.",
    emailLabel: "E-posta Adresi",
    emailPlaceholder: "ornek@domain.com",
    passwordLabel: "Şifre",
    passwordPlaceholder: "••••••••",
    submitBtn: "Giriş Yap",
    noAccount: "Hesabınız yok mu?",
    signUpNow: "Şimdi Kayıt Olun",
    backHome: "Ana Sayfaya Dön",
    toggleLight: "Açık temaya geç",
    toggleDark: "Koyu temaya geç",
    signIn: "Giriş Yap",
    signUp: "Kayıt Ol",
    forgotPassword: "Şifremi Unuttum?",
    continueWithGoogle: "Google ile Devam Et",
    orText: "veya",
    errorRequired: "Bu alan zorunludur.",
    errorInvalidEmail: "Geçersiz e-posta formatı.",
    errorMinLength: "Şifre en az 6 karakter olmalıdır."
  },
  en: {
    title: "Sign In",
    subtitle: "Enter your credentials to access your account.",
    emailLabel: "Email Address",
    emailPlaceholder: "example@domain.com",
    passwordLabel: "Password",
    passwordPlaceholder: "••••••••",
    submitBtn: "Sign In",
    noAccount: "Don't have an account?",
    signUpNow: "Sign Up Now",
    backHome: "Back to Home",
    toggleLight: "Switch to light theme",
    toggleDark: "Switch to dark theme",
    signIn: "Sign In",
    signUp: "Sign Up",
    forgotPassword: "Forgot Password?",
    continueWithGoogle: "Continue with Google",
    orText: "or",
    errorRequired: "This field is required.",
    errorInvalidEmail: "Invalid email format.",
    errorMinLength: "Password must be at least 6 characters."
  }
};

export const Login = () => {
  const { dil, dilDegistir } = useI18n();
  const { koyuMu, temaDegistir } = useTheme();
  const navigate = useNavigate();
  const [sifreGoster, setSifreGoster] = useState(false);
  
  // Form State
  const [email, setEmail] = useState('');
  const [sifre, setSifre] = useState('');
  
  // Validation State
  const [emailHata, setEmailHata] = useState('');
  const [sifreHata, setSifreHata] = useState('');

  const t = (key) => {
    return TRANSLATIONS[dil]?.[key] ?? TRANSLATIONS['tr'][key] ?? key;
  };

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
    if (emailHata) setEmailHata('');
  };

  const handleSifreChange = (e) => {
    setSifre(e.target.value);
    if (sifreHata) setSifreHata('');
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

    if (!sifre) {
      setSifreHata(t('errorRequired'));
      gecerli = false;
    } else if (sifre.length < 6) {
      setSifreHata(t('errorMinLength'));
      gecerli = false;
    }
    return gecerli;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      // Simülasyon: Giriş başarılı ise Dashboard'a git
      navigate(ROUTES.DASHBOARD);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col justify-center items-center px-4 bg-white text-black dark:bg-black dark:text-white transition-colors duration-300">
      
      {/* Üst Sağ Köşe Tema & Dil Seçici */}
      <div className="absolute top-8 right-8 md:top-6 md:right-6 flex items-center gap-4 z-50">
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

      {/* Giriş Kartı (Dikey sığma için iç boşluklar p-6 yapıldı) */}
      <div className="w-full max-w-md mx-auto rounded-3xl border border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-900/30 backdrop-blur-sm p-6 shadow-sm">
        
        {/* Logo & Başlık (Dikey sığma için mb-6 yapıldı) */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="h-9 w-9 rounded-full bg-black dark:bg-white flex items-center justify-center text-white dark:text-black shadow-md mb-3">
            <Bot size={20} />
          </div>
          <h1 className="text-xl font-bold tracking-tight">{t('title')}</h1>
          <p className="mt-1.5 text-xs text-neutral-500 dark:text-neutral-400 max-w-[280px]">
            {t('subtitle')}
          </p>
        </div>

        {/* Form (Dikey sığma için space-y-4 yapıldı) */}
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {/* E-posta */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-neutral-600 dark:text-neutral-300">
              {t('emailLabel')}
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
                <Mail size={15} />
              </span>
              <input
                type="email"
                value={email}
                onChange={handleEmailChange}
                placeholder={t('emailPlaceholder')}
                className={cn(
                  "w-full pl-9 pr-4 py-2.5 rounded-xl border bg-white dark:bg-black text-sm focus:outline-none transition-all placeholder:text-neutral-400",
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

          {/* Şifre */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-neutral-600 dark:text-neutral-300">
              {t('passwordLabel')}
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
                <Lock size={15} />
              </span>
              <input
                type={sifreGoster ? "text" : "password"}
                value={sifre}
                onChange={handleSifreChange}
                placeholder={t('passwordPlaceholder')}
                className={cn(
                  "w-full pl-9 pr-10 py-2.5 rounded-xl border bg-white dark:bg-black text-sm focus:outline-none transition-all placeholder:text-neutral-400",
                  sifreHata
                    ? "border-red-500 ring-1 ring-red-500"
                    : "border-neutral-200 dark:border-neutral-800 focus:ring-1 focus:ring-gray-500"
                )}
              />
              <button
                type="button"
                onClick={() => setSifreGoster(!sifreGoster)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 focus:outline-none"
              >
                {sifreGoster ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
            {sifreHata && (
              <span className="text-[10px] font-semibold text-red-500 mt-0.5 pl-1 animate-fade-in">
                {sifreHata}
              </span>
            )}
            
            {/* Şifremi Unuttum Linki */}
            <div className="flex justify-end mt-0.5">
              <Link
                to={ROUTES.FORGOT_PASSWORD}
                className="text-[11px] font-medium text-neutral-500 dark:text-neutral-400 hover:text-black dark:hover:text-white transition-colors focus:outline-none"
              >
                {t('forgotPassword')}
              </Link>
            </div>
          </div>

          {/* Giriş Butonu */}
          <button
            type="submit"
            className="w-full py-3 mt-1 rounded-xl text-sm font-semibold shadow-md bg-black text-white hover:bg-neutral-900 dark:bg-white dark:text-black dark:hover:bg-neutral-100 transition-all active:scale-[0.99] focus:outline-none"
          >
            {t('submitBtn')}
          </button>
        </form>

        {/* Ayraç (Dikey sığma için my-4 yapıldı) */}
        <div className="relative my-4 flex items-center justify-center">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-neutral-200 dark:border-neutral-800" />
          </div>
          <span className="relative px-3 bg-neutral-50 dark:bg-neutral-900/60 backdrop-blur-sm text-[10px] font-bold uppercase text-neutral-400 dark:text-neutral-500">
            {t('orText')}
          </span>
        </div>

        {/* Google ile Giriş */}
        <button
          type="button"
          onClick={() => window.alert('Google Auth entegrasyonu backend ile yapılacaktır.')}
          className="w-full py-2.5 px-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-transparent hover:bg-neutral-100 dark:hover:bg-neutral-900 text-sm font-semibold transition-all flex items-center justify-center gap-2.5 focus:outline-none"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
          </svg>
          <span>{t('continueWithGoogle')}</span>
        </button>

        {/* Kayıt Ol Yönlendirme (Dikey sığma için mt-4 yapıldı) */}
        <div className="mt-4 text-center text-xs text-neutral-500 dark:text-neutral-400">
          <span>{t('noAccount')} </span>
          <Link
            to={ROUTES.REGISTER}
            className="font-bold text-black dark:text-white hover:underline focus:outline-none"
          >
            {t('signUpNow')}
          </Link>
        </div>

      </div>

      {/* Ana Sayfaya Dön (Dikey sığma için mt-6 yapıldı) */}
      <Link
        to={ROUTES.LANDING}
        className="mt-4 sm:mt-6 flex items-center gap-1.5 text-xs font-semibold text-neutral-500 dark:text-neutral-400 hover:text-neutral-800 dark:hover:text-neutral-200 transition-colors focus:outline-none"
      >
        <ArrowLeft size={14} />
        <span>{t('backHome')}</span>
      </Link>

    </div>
  );
};
