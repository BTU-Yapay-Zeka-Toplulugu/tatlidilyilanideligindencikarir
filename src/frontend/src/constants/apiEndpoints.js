// src/constants/apiEndpoints.js
// Magic String YASAK — Tüm API endpoint path'leri buradan merkezi olarak yönetilir
// Kural: Servis fonksiyonları içinde asla string literal URL kullanılmaz

export const API_ENDPOINTS = {
  // Dashboard modülü
  DASHBOARD: {
    FINANSMAN_OZET: '/finansman/ozet',
    FINANSMAN_KARSILASTIRMA: '/finansman/karsilastirma',
    BANKA_LISTESI: '/finansman/bankalar',
  },

  // Chatbot modülü
  CHATBOT: {
    MESAJ_GONDER: '/chat/mesaj',
    GECMIS: '/chat/gecmis',
    OTURUM_TEMIZLE: '/chat/temizle',
  },
};
