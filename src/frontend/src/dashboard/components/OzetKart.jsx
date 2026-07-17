// src/dashboard/components/OzetKart.jsx
// Finansman özet kartı — Stripe tarzı, Tam Siyah/Beyaz tema
// Named Export — export default YASAKTIR

import PropTypes from 'prop-types';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '../../utils/styleUtils';

const TREND_IKON = {
  yukari: TrendingUp,
  asagi:  TrendingDown,
  sabit:  Minus,
};

const TREND_RENK = {
  yukari: 'text-emerald-600 dark:text-emerald-400',
  asagi:  'text-red-500 dark:text-red-400',
  sabit:  'text-black/40 dark:text-white/40',
};

/**
 * @param {object} props
 * @param {string}  props.baslik
 * @param {string}  props.deger
 * @param {string}  [props.trend]       — 'yukari' | 'asagi' | 'sabit'
 * @param {string}  [props.trendMetni]
 * @param {React.ElementType} [props.ikon]
 * @param {string}  [props.ikonRenk]
 */
export const OzetKart = ({ baslik, deger, trend = 'sabit', trendMetni, ikon: Ikon, ikonRenk = 'bg-black/5 dark:bg-white/10' }) => {
  const TrendIkon = TREND_IKON[trend] ?? Minus;

  return (
    <div className={cn(
      'group relative overflow-hidden rounded-xl border p-5 transition-shadow hover:shadow-md duration-200',
      'border-black/10 bg-white',
      'dark:border-white/10 dark:bg-black',
    )}>
      {/* Hover accent çizgisi */}
      <div className="absolute inset-x-0 top-0 h-0.5 scale-x-0 rounded-t-xl bg-emerald-500 transition-transform duration-300 group-hover:scale-x-100" />

      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-black/50 dark:text-white/50">
            {baslik}
          </p>
          <p className="mt-2 text-2xl font-bold tabular-nums text-black dark:text-white">
            {deger}
          </p>
        </div>
        {Ikon && (
          <div className={cn('flex h-10 w-10 items-center justify-center rounded-lg', ikonRenk)}>
            <Ikon size={20} className="text-black dark:text-white" aria-hidden="true" />
          </div>
        )}
      </div>

      {trendMetni && (
        <div className={cn('mt-3 flex items-center gap-1 text-xs font-medium', TREND_RENK[trend])}>
          <TrendIkon size={13} aria-hidden="true" />
          <span className="text-black/60 dark:text-white/60">{trendMetni}</span>
        </div>
      )}
    </div>
  );
};

OzetKart.propTypes = {
  baslik:    PropTypes.string.isRequired,
  deger:     PropTypes.string.isRequired,
  trend:     PropTypes.oneOf(['yukari', 'asagi', 'sabit']),
  trendMetni:PropTypes.string,
  ikon:      PropTypes.elementType,
  ikonRenk:  PropTypes.string,
};
