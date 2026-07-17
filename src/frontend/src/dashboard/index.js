// src/dashboard/index.js
// Barrel export — Dashboard modülünün Public API noktası
// İç yapı değişse bile import yolları kırılmaz (Bölüm 2 Best Practices)

// Sayfalar
export { DashboardPage } from './pages/DashboardPage';

// Bileşenler
export { OzetKart }             from './components/OzetKart';
export { KarsilastirmaTablosu } from './components/KarsilastirmaTablosu';
export { FinansmanGrafigi }     from './components/FinansmanGrafigi';

// Servisler
export { fetchFinansmanOzeti, fetchFinansmanKarsilastirma, fetchBankaListesi } from './services/dashboardService';

// Hook'lar
export { useFinansmanOzeti }        from './hooks/useFinansmanOzeti';
export { useFinansmanKarsilastirma } from './hooks/useFinansmanKarsilastirma';
