// src/components/EmptyState.jsx
// Boş veri durumu bileşeni — Tam Siyah/Beyaz tema
// Named Export — export default YASAKTIR

import PropTypes from 'prop-types';
import { Inbox } from 'lucide-react';

/**
 * @param {object} props
 * @param {string}    props.baslik
 * @param {string}    props.aciklama
 * @param {string}    [props.butonMetni]
 * @param {()=>void}  [props.onButon]
 */
export const EmptyState = ({ baslik, aciklama, butonMetni, onButon }) => (
  <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-8 py-16 text-center border-black/10 bg-white dark:border-white/10 dark:bg-black">
    <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-black/5 dark:bg-white/5">
      <Inbox size={22} className="text-black/40 dark:text-white/40" aria-hidden="true" />
    </div>
    <h3 className="text-sm font-semibold text-black dark:text-white">{baslik}</h3>
    <p className="mt-1 max-w-xs text-sm text-black/50 dark:text-white/50">{aciklama}</p>
    {butonMetni && onButon && (
      <button
        onClick={onButon}
        className="mt-6 rounded-lg bg-black text-white px-4 py-2 text-sm font-medium transition-colors hover:bg-black/80 focus:outline-none focus:ring-0 outline-none dark:bg-white dark:text-black dark:hover:bg-white/80"
      >
        {butonMetni}
      </button>
    )}
  </div>
);

EmptyState.propTypes = {
  baslik:     PropTypes.string.isRequired,
  aciklama:   PropTypes.string.isRequired,
  butonMetni: PropTypes.string,
  onButon:    PropTypes.func,
};
