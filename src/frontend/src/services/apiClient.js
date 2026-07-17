// src/services/apiClient.js
// Örnek 3.1: Merkezi Axios Instance ve Interceptor Kurulumu
// Bu yapı, bileşenleri API karmaşasından kurtarır.
// KURAL: Axios bu dosya dışında hiçbir component/hook içinde doğrudan import edilmez.

import axios from 'axios';
import { API_BASE_URL, API_TIMEOUT } from '../constants/environment';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Request Interceptor — Kurumsal token yönetimi
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor — Merkezi hata yönetimi (Tablo 3.2)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;

    if (status === 401) {
      // Oturum sonlandırma — Login sayfasına yönlendirme tetiklenir
      window.dispatchEvent(new Event('auth:unauthorized'));
    }

    if (status === 500) {
      // Global "Sistem Hatası" bildirimi tetiklenir
      window.dispatchEvent(new CustomEvent('api:server-error', { detail: error }));
    }

    return Promise.reject(error);
  }
);
