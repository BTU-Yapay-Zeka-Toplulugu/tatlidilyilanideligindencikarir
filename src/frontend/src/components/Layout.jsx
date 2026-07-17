// src/components/Layout.jsx
// Sayfa iskelet bileşeni — Bölüm 5 / Örnek 7.1
// Named Export — export default YASAKTIR (ADR-001)
// Özellikler: Mini-Sidebar, 4 Rengarenk Aurora Küresi (Dinamik Hız/Opasite), Fareyi İzleyen Yoğun Doğal Yıldız Spot Işığı (Starfield)

import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { createPortal } from 'react-dom';
import { LayoutDashboard, Sun, Moon, Menu, Settings, History, MessageSquarePlus, User } from 'lucide-react';
import { ROUTES } from '../constants/routes';
import { cn } from '../utils/styleUtils';
import { useTheme } from '../context/ThemeContext';
import { useI18n } from '../context/I18nContext';
import { useSidebar } from '../context/SidebarContext';

export const Layout = ({ children }) => {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { koyuMu, temaDegistir } = useTheme();
  const { dil, dilDegistir, t } = useI18n();
  const { sidebarAcik, sidebarToggle, sohbetBasladi, setSidebarAcik, yeniSohbetBaslat } = useSidebar();

  const [profilMenuAcik, setProfilMenuAcik] = useState(false);
  const [ayarlarAcik, setAyarlarAcik] = useState(false);

  const misafirAdi = dil === 'tr' ? 'Misafir' : 'Guest';
  const misafirAltMetni = dil === 'tr' ? 'Giriş yapılmadı' : 'Not logged in';

  const mobilMenuyuKapat = () => {
    if (window.innerWidth < 768) {
      setSidebarAcik(false);
    }
  };

  const chatbotRotasindaMi = pathname === ROUTES.CHATBOT;
  const dashboardRotasindaMi = pathname === ROUTES.DASHBOARD;

  const navItems = [
    { labelKey: 'nav.dashboard', path: ROUTES.DASHBOARD, icon: LayoutDashboard, action: null },
    { labelKey: 'nav.newChat',    path: ROUTES.CHATBOT,   icon: MessageSquarePlus, action: 'newChat' },
  ];

  // Fare koordinatlarını alıp CSS değişkenlerine aktarır (Mask Reveal efekti için)
  useEffect(() => {
    const handleMouseMove = (e) => {
      const x = `${e.clientX}px`;
      const y = `${e.clientY}px`;
      document.documentElement.style.setProperty('--mouse-x', x);
      document.documentElement.style.setProperty('--mouse-y', y);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div className={cn(
      "relative flex h-screen text-black dark:text-white overflow-hidden transition-colors duration-200",
      dashboardRotasindaMi ? "bg-white dark:bg-black" : "bg-transparent"
    )}>

      {/* ── HAREKETLİ RENGARENK AURORA ARKA PLANI (z-0) ────────────────── */}
      {/* Dashboard sayfasında KESİNLİKLE bloblar veya animasyonlar render edilmez */}
      {!dashboardRotasindaMi && (
        <div className={cn(
          "fixed inset-0 z-0 overflow-hidden pointer-events-none select-none transition-all duration-1000",
          sohbetBasladi
            ? "opacity-15 dark:opacity-10" // Sohbet anında hafif ambiyans (Açık temada opacity-15, koyu temada opacity-10)
            : "opacity-60 dark:opacity-40" // Hoş geldin ekranında canlı hava (Açık temada belirginlik için opacity-60, koyu temada opacity-40)
        )}>
          {/* Blob 1: Zümrüt Yeşili */}
          <div
            className={cn(
              "absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full bg-emerald-500/50 dark:bg-emerald-500/25 blur-[120px] animate-blob transition-[animation-duration] duration-1000",
              sohbetBasladi ? "[animation-duration:50s]" : "[animation-duration:12s]"
            )}
          />
          {/* Blob 2: Mor */}
          <div
            className={cn(
              "absolute bottom-1/4 right-1/4 w-[500px] h-[500px] rounded-full bg-purple-500/45 dark:bg-purple-500/25 blur-[120px] animate-blob-reverse transition-[animation-duration] duration-1000",
              sohbetBasladi ? "[animation-duration:60s]" : "[animation-duration:14s]"
            )}
          />
          {/* Blob 3: Gece Mavisi */}
          <div
            className={cn(
              "absolute top-1/3 right-1/3 w-[450px] h-[450px] rounded-full bg-blue-600/40 dark:bg-blue-600/20 blur-[110px] animate-blob-3 transition-[animation-duration] duration-1000",
              sohbetBasladi ? "[animation-duration:55s]" : "[animation-duration:16s]"
            )}
          />
          {/* Blob 4: Fuşya */}
          <div
            className={cn(
              "absolute bottom-1/3 left-1/3 w-[450px] h-[450px] rounded-full bg-fuchsia-500/35 dark:bg-fuchsia-500/15 blur-[110px] animate-blob-4 transition-[animation-duration] duration-1000",
              sohbetBasladi ? "[animation-duration:65s]" : "[animation-duration:18s]"
            )}
          />
        </div>
      )}

      {/* ── FAREYİ İZLEYEN GÖRÜNMEZ SPOT IŞIKLI YOĞUN DOĞAL YILDIZLAR (z-0) ── */}
      {/* Dashboard sayfasında veya sohbet başladığında yıldızlar render edilmez */}
      {!dashboardRotasindaMi && (
        <div className={cn(
          "fixed inset-0 z-0 pointer-events-none select-none stars-mask text-black/70 dark:text-white transition-opacity duration-1000",
          sohbetBasladi ? "opacity-0" : "opacity-100"
        )}>
          <div className="stars-natural-1 absolute inset-0" />
          <div className="stars-natural-2 absolute inset-0" />
        </div>
      )}

      {/* ── İÇERİK KATMANI (z-10) ────────────────── */}
      <div className="relative z-10 flex flex-col md:flex-row flex-1 h-full w-full overflow-hidden bg-transparent">
        
        {/* Mobil Üst Bar */}
        <header className="md:hidden flex h-14 shrink-0 items-center justify-between border-b border-black/10 dark:border-white/10 bg-white/95 dark:bg-black/95 backdrop-blur-md px-4 z-30">
          <button
            onClick={sidebarToggle}
            className="flex h-8 w-8 items-center justify-center rounded-md text-black/50 hover:bg-black/5 dark:text-white/50 dark:hover:bg-white/5 focus:outline-none"
            aria-label="Menüyü Aç"
          >
            <Menu size={20} />
          </button>
          <span className="font-bold text-sm tracking-tight text-black dark:text-white">
            {t('nav.brand')}
          </span>
          <div className="flex items-center gap-1">
            <button
              onClick={temaDegistir}
              className="flex h-8 w-8 items-center justify-center rounded-md text-black/50 hover:bg-black/5 dark:text-white/55 dark:hover:bg-white/5 focus:outline-none"
              aria-label="Tema değiştir"
            >
              {koyuMu ? <Sun size={15} /> : <Moon size={15} />}
            </button>
            <button
              onClick={() => dilDegistir(dil === 'tr' ? 'en' : 'tr')}
              className="flex h-8 w-8 items-center justify-center rounded-md text-xs font-bold uppercase text-black/55 hover:bg-black/5 dark:text-white/55 dark:hover:bg-white/5 focus:outline-none"
              aria-label="Dil değiştir"
            >
              {dil}
            </button>
          </div>
        </header>

        {/* Mobile Sidebar Backdrop */}
        {sidebarAcik && (
          <div
            onClick={mobilMenuyuKapat}
            className="md:hidden fixed inset-0 bg-black/40 backdrop-blur-xs z-40 transition-opacity duration-300"
          />
        )}

        <aside
          translate="no"
          className={cn(
            'notranslate flex shrink-0 flex-col border-r transition-all duration-300 ease-in-out',
            'border-black/10 dark:border-white/10 bg-white/90 dark:bg-black/90 backdrop-blur-md',
            // Desktop dimensions
            sidebarAcik ? 'md:w-64' : 'md:w-16',
            // Mobile dimensions & behavior
            sidebarAcik
              ? 'fixed md:relative inset-y-0 left-0 w-64 z-50 shadow-2xl'
              : 'hidden md:flex'
          )}
        >
          {/* Logo + Toggle Butonu (Buradaki gereksiz yön okları kaldırılmış ve sadece hamburger menü simgesi bırakılmıştır) */}
          <div className={cn(
            "flex h-14 items-center border-b border-black/10 dark:border-white/10 px-5",
            sidebarAcik ? "justify-between" : "justify-center px-0"
          )}>
            {sidebarAcik && (
              <span className="truncate text-sm font-bold tracking-tight text-black dark:text-white">
                {t('nav.brand')}
              </span>
            )}
            <button
              onClick={sidebarToggle}
              aria-label={sidebarAcik ? t('nav.closeMenu') : t('nav.openMenu')}
              className={cn(
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-gray-800 hover:bg-black/5 dark:text-gray-200 dark:hover:bg-white/5 focus:outline-none focus:ring-0 outline-none transition-colors",
                !sidebarAcik && "mx-auto"
              )}
            >
              <Menu size={16} className="text-gray-800 dark:text-gray-200" aria-hidden="true" />
            </button>
          </div>

          {/* Navigasyon */}
          <nav className="flex-1 px-3 py-4 flex flex-col justify-between overflow-hidden" aria-label="Ana Navigasyon">
            <div className="flex flex-col gap-4 overflow-y-auto overflow-x-hidden [&::-webkit-scrollbar]:hidden">
              <ul className="space-y-1" role="list">
                {navItems.map(({ labelKey, path, icon: Icon, action }) => (
                  <li key={path}>
                    <Link
                      to={path}
                      onClick={() => {
                        mobilMenuyuKapat();
                        if (action === 'newChat') {
                          yeniSohbetBaslat();
                        }
                      }}
                      className={cn(
                        'flex items-center rounded-md py-2 text-sm font-medium transition-colors whitespace-nowrap focus:outline-none focus:ring-0 outline-none',
                        sidebarAcik ? 'px-3 gap-3 justify-start' : 'px-0 justify-center h-9 w-10 mx-auto',
                        pathname === path
                          ? 'bg-black text-white dark:bg-white dark:text-black'
                          : 'text-black/60 hover:bg-black/5 hover:text-black dark:text-white/60 dark:hover:bg-white/5 dark:hover:text-white'
                      )}
                      aria-current={pathname === path ? 'page' : undefined}
                    >
                      <Icon size={17} aria-hidden="true" />
                      {sidebarAcik && <span>{t(labelKey)}</span>}
                    </Link>
                  </li>
                ))}
              </ul>

              {/* Geçmiş Sohbetler Bölümü */}
              {sidebarAcik && (
                <div className="mt-4 px-1 flex-1">
                  <div className="flex items-center gap-1.5 px-2 mb-2 text-xs font-semibold text-neutral-400 dark:text-neutral-500 uppercase tracking-wider">
                    <History size={12} />
                    <span>{t('nav.pastChats')}</span>
                  </div>
                  <ul className="space-y-1">
                    {/* Gerçek veriler gelene kadar boş bırakılmıştır */}
                  </ul>
                </div>
              )}
            </div>
          </nav>

          {/* Footer — Kullanıcı Profili & Ayarlar (Dar Sidebar popover menüleri React Portals ile düzeltildi) */}
          <div className="relative border-t px-3 py-4 border-black/10 dark:border-white/10">
            {sidebarAcik ? (
              <div className="flex items-center justify-between gap-2">
                {/* Profil Alanı */}
                <button
                  onClick={() => {
                    setProfilMenuAcik(!profilMenuAcik);
                    setAyarlarAcik(false);
                  }}
                  className="flex flex-1 items-center gap-2 overflow-hidden text-left p-1 rounded-xl hover:bg-black/5 dark:hover:bg-white/5 transition-all outline-none focus:outline-none"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-neutral-200 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-400 shadow-sm">
                    <User size={15} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold text-black dark:text-white truncate">{misafirAdi}</p>
                    <p className="text-[10px] text-neutral-500 dark:text-neutral-400 truncate">{misafirAltMetni}</p>
                  </div>
                </button>

                {/* Ayarlar İkonu */}
                <button
                  onClick={() => {
                    setAyarlarAcik(!ayarlarAcik);
                    setProfilMenuAcik(false);
                  }}
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl text-black/50 hover:bg-black/5 hover:text-black dark:text-white/50 dark:hover:bg-white/5 dark:hover:text-white transition-colors outline-none focus:outline-none"
                  aria-label="Ayarlar"
                >
                  <Settings size={16} />
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <button
                  onClick={() => {
                    setProfilMenuAcik(!profilMenuAcik);
                    setAyarlarAcik(false);
                  }}
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-neutral-200 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-400 shadow-sm hover:scale-105 transition-transform outline-none focus:outline-none"
                  title={misafirAdi}
                >
                  <User size={15} />
                </button>

                <button
                  onClick={() => {
                    setAyarlarAcik(!ayarlarAcik);
                    setProfilMenuAcik(false);
                  }}
                  className="flex h-8 w-8 items-center justify-center rounded-xl text-black/50 hover:bg-black/5 hover:text-black dark:text-white/50 dark:hover:bg-white/5 dark:hover:text-white transition-colors outline-none"
                  title={dil === 'tr' ? 'Ayarlar' : 'Settings'}
                >
                  <Settings size={16} />
                </button>
              </div>
            )}
          </div>
        </aside>

        {/* ANA İÇERİK ALANI */}
        <main
          id="main-content"
          className={cn(
            'relative flex-1 min-w-0 text-black dark:text-white transition-colors duration-200',
            dashboardRotasindaMi ? 'bg-white dark:bg-black' : 'bg-transparent',
            chatbotRotasindaMi
              ? 'overflow-hidden'
              : 'overflow-auto p-8'
          )}
        >
          {/* Header ve Buton Taşıma: Dil & Tema Seçici (Sadece masaüstünde) */}
          <div className="absolute top-3 right-4 z-30 hidden md:flex items-center gap-1.5 bg-white/40 dark:bg-black/40 backdrop-blur-xs px-2 py-1 rounded-xl border border-black/5 dark:border-white/5">
            {/* Tema Değiştir */}
            <button
              onClick={temaDegistir}
              aria-label={koyuMu ? t('theme.toggleLight') : t('theme.toggleDark')}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-black/55 hover:bg-black/5 hover:text-black dark:text-white/55 dark:hover:bg-white/5 dark:hover:text-white transition-colors focus:outline-none"
            >
              {koyuMu ? <Sun size={15} /> : <Moon size={15} />}
            </button>
            
            <span className="h-4 w-[1px] bg-black/10 dark:bg-white/10" />

            {/* Dil Değiştir */}
            <button
              onClick={() => dilDegistir(dil === 'tr' ? 'en' : 'tr')}
              className="flex h-8 px-2.5 items-center justify-center rounded-lg text-xs font-bold uppercase text-black/55 hover:bg-black/5 dark:text-white/55 dark:hover:bg-white/5 focus:outline-none"
              aria-label="Dil değiştir"
            >
              {dil}
            </button>
          </div>
          {children}
        </main>

      </div>

      {/* ── PORTAL POPMENÜLERİ (z-index ve overflow kırpılma problemleri fixed portal ile çözülmüştür) ── */}
      {profilMenuAcik && createPortal(
        <div className={cn(
          "fixed z-[100] bg-white dark:bg-neutral-950 border border-black/10 dark:border-white/10 rounded-2xl shadow-2xl p-3 animate-fade-in flex flex-col gap-1",
          sidebarAcik ? "bottom-16 left-3 w-[220px]" : "bottom-16 left-16 w-48"
        )}>
          <div className="px-2 py-1 text-xs font-semibold text-neutral-400">
            {misafirAdi}
          </div>
          <button 
            onClick={() => {
              navigate(ROUTES.LOGIN);
              setProfilMenuAcik(false);
            }}
            className="flex items-center gap-2 w-full text-left px-2.5 py-2 text-xs rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors text-black dark:text-white"
          >
            👤 {dil === 'tr' ? 'Giriş Yap' : 'Sign In'}
          </button>
        </div>,
        document.body
      )}

      {ayarlarAcik && createPortal(
        <div className={cn(
          "fixed z-[100] bg-white dark:bg-neutral-950 border border-black/10 dark:border-white/10 rounded-2xl shadow-2xl p-3 animate-fade-in flex flex-col gap-2",
          sidebarAcik ? "bottom-16 left-3 w-[220px]" : "bottom-4 left-16 w-48"
        )}>
          <div className="px-2 py-0.5 text-xs font-semibold text-neutral-400">
            {dil === 'tr' ? 'Ayarlar' : 'Settings'}
          </div>
          <div className="flex items-center justify-between px-2 text-xs text-black dark:text-white">
            <span>{dil === 'tr' ? 'Bildirimler' : 'Notifications'}</span>
            <input type="checkbox" defaultChecked className="rounded border-neutral-300 text-black focus:ring-0 focus:ring-offset-0" />
          </div>
          {sidebarAcik && (
            <div className="flex items-center justify-between px-2 text-xs text-black dark:text-white">
              <span>{dil === 'tr' ? 'Sesli Yanıt' : 'Voice Response'}</span>
              <input type="checkbox" className="rounded border-neutral-300 text-black focus:ring-0 focus:ring-offset-0" />
            </div>
          )}
        </div>,
        document.body
      )}

    </div>
  );
};

Layout.propTypes = {
  children: PropTypes.node.isRequired,
};
