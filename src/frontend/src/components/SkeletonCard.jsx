// src/components/SkeletonCard.jsx
// Yükleme durumu için iskelet animasyonları — Tam Siyah/Beyaz tema
// Named Export — export default YASAKTIR

import PropTypes from 'prop-types';

/**
 * Tek bir animate-pulse iskelet satırı.
 * @param {{ className?: string }} props
 */
export const Skeleton = ({ className = '' }) => (
  <div className={`animate-pulse rounded bg-black/5 dark:bg-white/10 ${className}`} />
);

Skeleton.propTypes = {
  className: PropTypes.string,
};

/** Dashboard Özet Kartı iskeleti */
export const OzetKartSkeleton = () => (
  <div className="rounded-xl border p-5 border-black/10 bg-white dark:border-white/10 dark:bg-black">
    <div className="flex items-start justify-between">
      <div className="space-y-2">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-7 w-32" />
      </div>
      <Skeleton className="h-9 w-9 rounded-lg" />
    </div>
    <Skeleton className="mt-4 h-3 w-40" />
  </div>
);

/** Karşılaştırma Tablosu iskeleti */
export const TabloSkeleton = () => (
  <div className="overflow-hidden rounded-xl border border-black/10 bg-white dark:border-white/10 dark:bg-black">
    <div className="border-b px-5 py-4 border-black/10 dark:border-white/10">
      <Skeleton className="h-4 w-48" />
    </div>
    <div className="divide-y divide-black/5 dark:divide-white/5">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="flex gap-4 px-5 py-3">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-3 w-32" />
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-12" />
          <Skeleton className="h-3 w-20" />
        </div>
      ))}
    </div>
  </div>
);

/** Grafik iskeleti */
export const GrafikSkeleton = () => (
  <div className="overflow-hidden rounded-xl border p-5 border-black/10 bg-white dark:border-white/10 dark:bg-black">
    <Skeleton className="mb-1 h-4 w-56" />
    <Skeleton className="mb-6 h-3 w-72" />
    <div className="flex h-64 items-end justify-around gap-2">
      {[60, 80, 45, 90, 70, 55].map((h, i) => (
        <Skeleton key={i} className="flex-1 rounded-t" style={{ height: `${h}%` }} />
      ))}
    </div>
  </div>
);
