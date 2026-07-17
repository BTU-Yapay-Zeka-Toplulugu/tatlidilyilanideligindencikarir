// src/pages/Landing.jsx
// Projenin vitrini olacak modern ve minimalist Açılış Sayfası (Landing Page)
// Named Export — export default YASAKTIR (ADR-001)
// Özellikler: Fizik tabanlı kuyruklu partikül trail, Framer Motion scroll animasyonları, çift dil desteği, koyu/açık tema uyumu

import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Bot, LayoutDashboard, ArrowRight, ShieldCheck, BarChart3, MessageSquare, Sun, Moon } from 'lucide-react';
import { ROUTES } from '../constants/routes';
import { useI18n } from '../context/I18nContext';
import { useTheme } from '../context/ThemeContext';

const TRANSLATIONS = {
  tr: {
    brand: "Tatlıdil Platform",
    tagline: "Katılım Bankacılığı",
    title: "Katılım Bankacılığının Akıllı Arayüzü",
    subtitle: "RAG destekli yapay zekâ asistanı ve finansal karşılaştırma platformu ile katılım bankacılığında yeni bir dönem.",
    tryBtn: "Asistanı Dene",
    dashboardBtn: "Panel'e Git",
    featuresTitle: "Öne Çıkan Özellikler",
    feature1Title: "RAG Destekli Doğruluk",
    feature1Desc: "Katılım bankacılığı mevzuat ve ürünlerine tam uyumlu, güncel ve kaynakçalı yanıtlar sunan yapay zekâ altyapısı.",
    feature2Title: "Finansal Analiz Paneli",
    feature2Desc: "Banka bazlı finansman tutarları, kâr oranları karşılaştırmaları ve eğilimleri gösteren dinamik grafikler.",
    feature3Title: "Gelişmiş AI Sohbeti",
    feature3Desc: "Gerçek zamanlı akış (streaming) desteği, hızlı yönlendirmeler ve zengin kullanıcı deneyimi sunan sohbet ekranı.",
    footerText: "© 2026 Tatlıdil Platform. Tüm Hakları Saklıdır.",
    toggleLight: "Açık temaya geç",
    toggleDark: "Koyu temaya geç",
    signIn: "Giriş Yap",
    signUp: "Kayıt Ol"
  },
  en: {
    brand: "Tatlıdil Platform",
    tagline: "Participation Banking",
    title: "The Intelligent Interface of Participation Banking",
    subtitle: "A new era in participation banking with a RAG-powered AI assistant and financial comparison platform.",
    tryBtn: "Try Assistant",
    dashboardBtn: "Go to Dashboard",
    featuresTitle: "Key Features",
    feature1Title: "RAG-Powered Accuracy",
    feature1Desc: "An AI infrastructure providing fully compliant, up-to-date, and cited answers for participation banking products.",
    feature2Title: "Financial Analytics Dashboard",
    feature2Desc: "Dynamic charts showing bank-based financing amounts, rate comparisons, and historical trends.",
    feature3Title: "Advanced AI Chat",
    feature3Desc: "A chat interface offering real-time streaming support, quick question suggestions, and a rich experience.",
    footerText: "© 2026 Tatlıdil Platform. All Rights Reserved.",
    toggleLight: "Switch to light theme",
    toggleDark: "Switch to dark theme",
    signIn: "Sign In",
    signUp: "Sign Up"
  }
};

export const Landing = () => {
  const { dil, dilDegistir } = useI18n();
  const { koyuMu, temaDegistir } = useTheme();
  const canvasRef = useRef(null);

  // Fizik tabanlı kuyruklu yıldız/toz bulutu imleç izi efekti
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    const particles = [];
    const maxParticles = 200;

    const mouse = { x: 0, y: 0, active: false };
    const lastMouse = { x: 0, y: 0 };
    const velocity = { x: 0, y: 0 };

    const handleMouseMove = (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;

      // Hız hesabı (velocity)
      velocity.x = mouse.x - lastMouse.x;
      velocity.y = mouse.y - lastMouse.y;

      lastMouse.x = mouse.x;
      lastMouse.y = mouse.y;

      // Mouse hızının büyüklüğü
      const speed = Math.sqrt(velocity.x * velocity.x + velocity.y * velocity.y);
      
      // Hızlı hareket edildiğinde kuyruk uzasın/belirginleşsin (hıza bağlı partikül sayısı)
      const spawnCount = Math.min(Math.ceil(speed * 0.4) + 1, 8);
      for (let i = 0; i < spawnCount; i++) {
        if (particles.length < maxParticles) {
          particles.push({
            x: mouse.x,
            y: mouse.y,
            // Mouse hareket yönünün tersine saçılma (kuyruk efekti)
            vx: -velocity.x * 0.15 + (Math.random() - 0.5) * 1.5,
            vy: -velocity.y * 0.15 + (Math.random() - 0.5) * 1.5,
            size: Math.random() * 2.0 + 0.8,
            alpha: 0.25, // Başlangıç opaklığı ciddi oranda düşürüldü (saydam/hayaletimsi görünüm)
            decay: Math.random() * 0.004 + 0.003, // Yavaşça sönümlenme için decay azaltıldı
          });
        }
      }
    };

    const handleMouseLeave = () => {
      mouse.active = false;
    };

    window.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', handleMouseLeave);

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Mouse durduğunda hızı yavaşça sönümle (fiziksel yavaşlama)
      velocity.x *= 0.95;
      velocity.y *= 0.95;

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        
        // Fiziksel güncelleme (konum ve hız)
        p.x += p.vx;
        p.y += p.vy;
        
        // Hava sürtünmesi sönümleme
        p.vx *= 0.97;
        p.vy *= 0.97;
        
        // Opaklık azalması
        p.alpha -= p.decay;

        if (p.alpha <= 0) {
          particles.splice(i, 1);
          continue;
        }

        ctx.save();
        ctx.globalAlpha = p.alpha;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        
        // Parlama (Glow) tamamen kapatıldı, sadece sade ve net şık dairesel toz taneleri bırakıldı
        if (koyuMu) {
          ctx.fillStyle = '#ffffff';
        } else {
          ctx.fillStyle = '#171717';
        }
        
        ctx.fill();
        ctx.restore();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
      window.cancelAnimationFrame(animationFrameId);
    };
  }, [koyuMu]);

  const t = (key) => {
    return TRANSLATIONS[dil]?.[key] ?? TRANSLATIONS['tr'][key] ?? key;
  };

  const kartVaryantlari = {
    gizli: { opacity: 0, y: 40 },
    goster: (i) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.15,
        duration: 0.8,
        ease: [0.16, 1, 0.3, 1]
      }
    })
  };

  return (
    <div className="relative min-h-screen bg-white text-black dark:bg-black dark:text-white transition-colors duration-300 overflow-x-hidden">
      
      {/* Fizik tabanlı imleç izi (cursor trail) canvas katmanı */}
      <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none z-50 w-full h-full" />

      {/* ── NAVBAR (Giriş / Kayıt Entegrasyonlu Absolute Header) ─────────────────────────── */}
      <header className="absolute top-0 left-0 w-full py-4 sm:py-0 sm:h-20 z-50 flex items-center bg-transparent">
        <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="h-8 w-8 rounded-full bg-black dark:bg-white flex items-center justify-center text-white dark:text-black shadow-md">
              <Bot size={18} />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-xs sm:text-sm tracking-tight">{t('brand')}</span>
              <span className="text-[10px] text-neutral-500 dark:text-neutral-400 font-medium -mt-0.5 hidden sm:block">{t('tagline')}</span>
            </div>
          </div>

          <div className="flex items-center gap-2.5 sm:gap-5">
            {/* Giriş Yap Butonu */}
            <Link
              to="/login"
              className="text-xs font-semibold text-neutral-800 dark:text-neutral-200 hover:text-neutral-500 dark:hover:text-neutral-400 transition-colors focus:outline-none"
            >
              {t('signIn')}
            </Link>

            {/* Kayıt Ol Butonu */}
            <Link
              to="/register"
              className="text-xs font-semibold px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-full shadow-sm bg-black text-white hover:bg-neutral-900 dark:bg-white dark:text-black dark:hover:bg-neutral-100 transition-all active:scale-[0.98] focus:outline-none"
            >
              {t('signUp')}
            </Link>
            
            <span className="h-4 w-[1px] bg-neutral-200 dark:bg-neutral-800 hidden sm:inline-block" />

            {/* Tema Değiştirme Butonu */}
            <button
              onClick={temaDegistir}
              aria-label={koyuMu ? t('toggleLight') : t('toggleDark')}
              className="p-1.5 sm:p-2 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors text-neutral-600 dark:text-neutral-300 focus:outline-none outline-none"
            >
              {koyuMu ? <Sun size={15} /> : <Moon size={15} />}
            </button>

            {/* Dil Seçimi */}
            <button
              onClick={() => dilDegistir(dil === 'tr' ? 'en' : 'tr')}
              className="text-xs font-bold uppercase p-1.5 sm:p-2 hover:bg-neutral-100 dark:hover:bg-neutral-900 rounded-full transition-colors focus:outline-none outline-none"
              aria-label={`Switch language to ${dil === 'tr' ? 'EN' : 'TR'}`}
            >
              {dil === 'tr' ? 'en' : 'tr'}
            </button>
          </div>
        </div>
      </header>

      {/* ── HERO SECTION (Tam Ekran Minimalist) ─────────────────────────── */}
      <section className="relative min-h-screen flex flex-col justify-center items-center px-6 pt-16 text-center select-none">
        
        {/* Dekoratif Arka Plan Spot Işığı */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-neutral-100 dark:bg-neutral-900/40 rounded-full blur-[150px] pointer-events-none z-0" />

        <div className="relative z-10 max-w-4xl mx-auto flex flex-col items-center">
          
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
            className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight leading-[1.1] text-black dark:text-white"
          >
            {t('title')}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
            className="mt-6 text-base sm:text-lg md:text-xl text-neutral-500 dark:text-neutral-400 max-w-2xl font-normal leading-relaxed"
          >
            {t('subtitle')}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 25 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
            className="mt-10 flex flex-col sm:flex-row gap-4 justify-center items-center w-full sm:w-auto"
          >
            <Link
              to={ROUTES.CHATBOT}
              className="flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-4 rounded-full text-sm font-semibold shadow-md bg-black text-white hover:bg-neutral-900 dark:bg-white dark:text-black dark:hover:bg-neutral-100 transition-all active:scale-[0.98] focus:outline-none"
            >
              <span>{t('tryBtn')}</span>
              <ArrowRight size={16} />
            </Link>
            
            <Link
              to={ROUTES.DASHBOARD}
              className="flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-4 rounded-full text-sm font-semibold border border-neutral-200 dark:border-neutral-800 bg-transparent hover:bg-neutral-50 dark:hover:bg-neutral-900 transition-all active:scale-[0.98] focus:outline-none"
            >
              <span>{t('dashboardBtn')}</span>
              <LayoutDashboard size={16} />
            </Link>
          </motion.div>

        </div>
      </section>

      {/* ── FEATURES SECTION (whileInView Scroll Animasyonu) ────────────────── */}
      <section className="relative py-32 px-6 border-t border-black/5 dark:border-white/5 bg-neutral-50/50 dark:bg-neutral-950/30">
        <div className="max-w-7xl mx-auto">
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-20"
          >
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight">
              {t('featuresTitle')}
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Kart 1 */}
            <motion.div
              custom={0}
              variants={kartVaryantlari}
              initial="gizli"
              whileInView="goster"
              viewport={{ once: true, margin: "-100px" }}
              className="flex flex-col rounded-3xl border border-neutral-100 dark:border-neutral-800 bg-white dark:bg-black p-8 shadow-sm hover:shadow-md transition-shadow duration-300"
            >
              <div className="h-12 w-12 rounded-2xl bg-neutral-50 dark:bg-neutral-900 flex items-center justify-center text-neutral-800 dark:text-neutral-200 mb-6 shadow-sm border border-neutral-100 dark:border-neutral-800">
                <ShieldCheck size={22} />
              </div>
              <h3 className="text-lg font-bold mb-3">{t('feature1Title')}</h3>
              <p className="text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed">
                {t('feature1Desc')}
              </p>
            </motion.div>

            {/* Kart 2 */}
            <motion.div
              custom={1}
              variants={kartVaryantlari}
              initial="gizli"
              whileInView="goster"
              viewport={{ once: true, margin: "-100px" }}
              className="flex flex-col rounded-3xl border border-neutral-100 dark:border-neutral-800 bg-white dark:bg-black p-8 shadow-sm hover:shadow-md transition-shadow duration-300"
            >
              <div className="h-12 w-12 rounded-2xl bg-neutral-50 dark:bg-neutral-900 flex items-center justify-center text-neutral-800 dark:text-neutral-200 mb-6 shadow-sm border border-neutral-100 dark:border-neutral-800">
                <BarChart3 size={22} />
              </div>
              <h3 className="text-lg font-bold mb-3">{t('feature2Title')}</h3>
              <p className="text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed">
                {t('feature2Desc')}
              </p>
            </motion.div>

            {/* Kart 3 */}
            <motion.div
              custom={2}
              variants={kartVaryantlari}
              initial="gizli"
              whileInView="goster"
              viewport={{ once: true, margin: "-100px" }}
              className="flex flex-col rounded-3xl border border-neutral-100 dark:border-neutral-800 bg-white dark:bg-black p-8 shadow-sm hover:shadow-md transition-shadow duration-300"
            >
              <div className="h-12 w-12 rounded-2xl bg-neutral-50 dark:bg-neutral-900 flex items-center justify-center text-neutral-800 dark:text-neutral-200 mb-6 shadow-sm border border-neutral-100 dark:border-neutral-800">
                <MessageSquare size={22} />
              </div>
              <h3 className="text-lg font-bold mb-3">{t('feature3Title')}</h3>
              <p className="text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed">
                {t('feature3Desc')}
              </p>
            </motion.div>

          </div>
        </div>
      </section>

      {/* ── FOOTER ─────────────────────────── */}
      <footer className="border-t border-black/5 dark:border-white/5 py-12 text-center bg-white dark:bg-black text-xs text-neutral-400 dark:text-neutral-500 transition-colors duration-200">
        <p>{t('footerText')}</p>
      </footer>

    </div>
  );
};
