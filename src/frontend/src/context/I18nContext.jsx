// src/context/I18nContext.jsx
// Basit JSON tabanlı i18n çözümü — react-i18next olmadan, sıfır bağımlılık
// t('chatbot.title') → string; t('chatbot.questions') → string[] (dizi de desteklenir)
// Named Export — export default YASAKTIR

import { createContext, useCallback, useContext, useState } from 'react';
import PropTypes from 'prop-types';
import tr from '../locales/tr.json';
import en from '../locales/en.json';

// Magic string önlemi
const DIL_STORAGE_ANAHTARI = 'tatlıdil-dil';
const VARSAYILAN_DIL = 'tr';

const sozluk = { tr, en };

const I18nContext = createContext(null);

export const I18nProvider = ({ children }) => {
  const [dil, setDil] = useState(() => {
    try {
      return localStorage.getItem(DIL_STORAGE_ANAHTARI) ?? VARSAYILAN_DIL;
    } catch {
      return VARSAYILAN_DIL;
    }
  });

  /**
   * Noktalı anahtarla çeviri getirir.
   * @param {string} anahtar - örn: 'chatbot.title', 'chatbot.questions'
   * @returns {string | string[] | *}  — string, dizi veya ham değer
   */
  const t = useCallback(
    (anahtar) => {
      const parcalar = anahtar.split('.');
      let deger = sozluk[dil];
      for (const parca of parcalar) {
        if (deger == null) return anahtar; // fallback: anahtarın kendisi
        deger = deger[parca];
      }
      return deger ?? anahtar;
    },
    [dil]
  );

  const dilDegistir = useCallback((yeniDil) => {
    setDil(yeniDil);
    try {
      localStorage.setItem(DIL_STORAGE_ANAHTARI, yeniDil);
    } catch { /* private mode */ }
  }, []);

  return (
    <I18nContext.Provider value={{ dil, dilDegistir, t }}>
      {children}
    </I18nContext.Provider>
  );
};

I18nProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export const useI18n = () => {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n, I18nProvider içinde kullanılmalıdır');
  return ctx;
};
