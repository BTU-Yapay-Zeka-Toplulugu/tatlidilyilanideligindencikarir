// src/context/ThemeContext.jsx
// Koyu/Açık tema yönetimi — html elementine 'dark' sınıfı ekler/kaldırır
// Named Export — export default YASAKTIR

import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import PropTypes from 'prop-types';

// Magic string önlemi
const TEMA_STORAGE_ANAHTARI = 'tatlıdil-tema';
const KOYU = 'dark';
const ACIK  = 'light';

const ThemeContext = createContext(null);

export const ThemeProvider = ({ children }) => {
  const [tema, setTema] = useState(() => {
    try {
      return localStorage.getItem(TEMA_STORAGE_ANAHTARI) ?? KOYU;
    } catch {
      return KOYU;
    }
  });

  // html elementine 'dark' sınıfını ekle/kaldır — Tailwind class strategy
  useEffect(() => {
    const html = document.documentElement;
    if (tema === KOYU) {
      html.classList.add(KOYU);
    } else {
      html.classList.remove(KOYU);
    }
    try {
      localStorage.setItem(TEMA_STORAGE_ANAHTARI, tema);
    } catch { /* private/incognito mode */ }
  }, [tema]);

  const temaDegistir = useCallback(() => {
    setTema((prev) => (prev === KOYU ? ACIK : KOYU));
  }, []);

  return (
    <ThemeContext.Provider value={{ tema, temaDegistir, koyuMu: tema === KOYU }}>
      {children}
    </ThemeContext.Provider>
  );
};

ThemeProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme, ThemeProvider içinde kullanılmalıdır');
  return ctx;
};
