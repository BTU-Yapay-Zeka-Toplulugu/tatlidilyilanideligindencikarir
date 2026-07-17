// src/App.jsx
// Örnek 7.1: Route Splitting ve Lazy Loading — Bölüm 7
// Named Export — export default YASAKTIR (ADR-001)
// Tüm sayfalar sadece ihtiyaç anında yüklenir (Code Splitting)

import { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ROUTES } from './constants/routes';

// Lazy loading — her sayfa kendi chunk'ı (vite.config.js manualChunks ile optimize edildi)
const LandingPage = lazy(() =>
  import('./pages/Landing').then((m) => ({ default: m.Landing }))
);

const LoginPage = lazy(() =>
  import('./pages/Login').then((m) => ({ default: m.Login }))
);

const RegisterPage = lazy(() =>
  import('./pages/Register').then((m) => ({ default: m.Register }))
);

const ForgotPasswordPage = lazy(() =>
  import('./pages/ForgotPassword').then((m) => ({ default: m.ForgotPassword }))
);

const DashboardPage = lazy(() =>
  import('./dashboard').then((m) => ({ default: m.DashboardPage }))
);

const ChatbotPage = lazy(() =>
  import('./chatbot').then((m) => ({ default: m.ChatbotPage }))
);

const NotFoundPage = lazy(() =>
  import('./pages/NotFound').then((m) => ({ default: m.NotFound }))
);

// Sayfa geçişi sırasında kurumsal spinner fallback
const PageLoader = () => (
  <div className="flex h-full w-full items-center justify-center">
    <div className="h-7 w-7 animate-spin rounded-full border-4 border-black/10 border-t-black dark:border-white/10 dark:border-t-white" />
  </div>
);

const LayoutWrapper = () => (
  <Layout>
    <Outlet />
  </Layout>
);

export const App = () => {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Landing Page (Açılış Sayfası) - Layoutsuz */}
          <Route path={ROUTES.LANDING} element={<LandingPage />} />

          {/* Giriş ve Kayıt Sayfaları - Layoutsuz (Tam Ekran) */}
          <Route path={ROUTES.LOGIN} element={<LoginPage />} />
          <Route path={ROUTES.REGISTER} element={<RegisterPage />} />
          <Route path={ROUTES.FORGOT_PASSWORD} element={<ForgotPasswordPage />} />

          {/* 404 — Bilinmeyen rotalar - Layoutsuz (Tam Ekran) */}
          <Route path={ROUTES.NOT_FOUND} element={<NotFoundPage />} />

          {/* Diğer sayfalar Layout ile sarmalanır */}
          <Route element={<LayoutWrapper />}>
            {/* Dashboard */}
            <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />

            {/* AI Asistan Chatbot */}
            <Route path={ROUTES.CHATBOT} element={<ChatbotPage />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
};
