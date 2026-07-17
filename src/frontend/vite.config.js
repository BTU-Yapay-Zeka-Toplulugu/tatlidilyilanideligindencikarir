import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Backend bulunamazsa (VITE_API_BASE_URL tanımsız) API ve WebSocket
    // isteklerini geliştirme sunucusu üzerinden backend'e yönlendirir.
    proxy: {
      '/finansman': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/chat': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  resolve: {
    alias: {
      // '@/' ile src/ klasörüne kısa yol — import yollarını temizler
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        // Bölüm 7: Büyük kütüphanelerin ayrı chunk'lara bölünmesi (Code Splitting)
        manualChunks: {
          // React ekosistemi
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          // Recharts — finansal grafik kütüphanesi
          'vendor-recharts': ['recharts'],
          // Syntax highlighting — chatbot kod blokları
          'vendor-highlighter': ['react-syntax-highlighter'],
          // Markdown render
          'vendor-markdown': ['react-markdown'],
        },
      },
    },
  },
});
