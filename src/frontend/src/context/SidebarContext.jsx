// src/context/SidebarContext.jsx
// Sidebar durumunun alt bileşenlerce (sayfa başlıkları vb.) erişilebilmesini sağlayan Context
// Named Export — export default YASAKTIR

import { createContext, useContext, useState, useCallback } from 'react';
import PropTypes from 'prop-types';

const SidebarContext = createContext(null);

export const SidebarProvider = ({ children }) => {
  const [sidebarAcik, setSidebarAcik] = useState(() => {
    try {
      return window.innerWidth >= 768;
    } catch {
      return true;
    }
  });
  const [sohbetBasladi, setSohbetBasladi] = useState(false);
  const [aktifOturumId, setAktifOturumId] = useState('oturum-001');

  const sidebarToggle = useCallback(() => {
    setSidebarAcik((prev) => !prev);
  }, []);

  const yeniSohbetBaslat = useCallback(() => {
    setAktifOturumId('oturum-' + Date.now());
  }, []);

  const gecmisSohbeteGec = useCallback((id) => {
    setAktifOturumId(id);
  }, []);

  return (
    <SidebarContext.Provider
      value={{
        sidebarAcik,
        sidebarToggle,
        sohbetBasladi,
        setSohbetBasladi,
        setSidebarAcik,
        aktifOturumId,
        yeniSohbetBaslat,
        gecmisSohbeteGec,
      }}
    >
      {children}
    </SidebarContext.Provider>
  );
};

SidebarProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export const useSidebar = () => {
  const ctx = useContext(SidebarContext);
  if (!ctx) {
    throw new Error('useSidebar, SidebarProvider içinde kullanılmalıdır');
  }
  return ctx;
};
