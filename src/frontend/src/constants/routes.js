// src/constants/routes.js
// Magic string önlemi — tüm route path'leri buradan merkezi olarak yönetilir
// Kural: component içinde asla string literal path kullanılmaz

export const ROUTES = {
  LANDING:         '/',
  DASHBOARD:       '/dashboard',
  CHATBOT:         '/asistan',
  LOGIN:           '/login',
  REGISTER:        '/register',
  FORGOT_PASSWORD: '/forgot-password',
  NOT_FOUND:       '*',
};
