// src/constants/environment.js
// Tablo 3.1: Ortam Değişkenleri Standardı
// Hardcoded URL YASAKTIR — tüm değerler .env üzerinden okunur

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
export const API_TIMEOUT = Number(import.meta.env.VITE_APP_TIMEOUT) || 15000;
export const CHATBOT_WS_URL = import.meta.env.VITE_CHATBOT_WS_URL;
