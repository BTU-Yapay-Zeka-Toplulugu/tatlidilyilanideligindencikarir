/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class', // Sınıf tabanlı dark mode — ThemeContext tarafından yönetilir
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Tablo 6.1: Tasarım Sistemi Token'ları
        // Primary: slate-900, Accent: emerald-600
      },
      borderRadius: {
        DEFAULT: '0.375rem', // rounded-md — Kurumsal net köşe dönüşü
      },
    },
  },
  plugins: [],
};
