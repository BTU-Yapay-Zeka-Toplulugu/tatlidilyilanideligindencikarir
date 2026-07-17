// src/main.jsx
// Uygulama giriş noktası — React 18 createRoot API
// ThemeProvider → I18nProvider → App

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { App } from './App';
import { ThemeProvider } from './context/ThemeContext';
import { I18nProvider } from './context/I18nContext';
import { SidebarProvider } from './context/SidebarContext';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <I18nProvider>
        <SidebarProvider>
          <App />
        </SidebarProvider>
      </I18nProvider>
    </ThemeProvider>
  </StrictMode>
);
