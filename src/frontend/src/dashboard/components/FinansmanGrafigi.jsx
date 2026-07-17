// src/dashboard/components/FinansmanGrafigi.jsx
// Bölüm 4: Recharts tabanlı finansman görselleştirme
// Kural: Recharts renk paletine DOKUNULMAZ (kullanıcı talebi)
// Container: Tam Siyah/Beyaz tema
// Named Export — export default YASAKTIR

import { useMemo } from 'react';
import PropTypes from 'prop-types';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { formatOran, formatParaBirimi } from '../../utils/formatters';
import { useI18n } from '../../context/I18nContext';

// Grafik renk sabitleri — Recharts paleti kuralı
const GRAFIK_RENKLERI = {
  TUTAR:     '#0f172a', // slate-900
  KAR_ORANI: '#059669', // emerald-600
};

// YAxis tick formatı
const PARA_BIRIM_KISALT = (deger) => {
  if (deger >= 1000000) return `${(deger / 1000000).toFixed(1)}M ₺`;
  if (deger >= 1000)    return `${(deger / 1000).toFixed(0)}K ₺`;
  return `${deger} ₺`;
};

/**
 * Özel Tooltip
 */
const OzelTooltip = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="rounded-md border border-black/10 bg-white px-4 py-3 shadow-lg dark:border-white/10 dark:bg-black">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-black/50 dark:text-white/50">{label}</p>
      {payload.map((giris) => (
        <div key={giris.dataKey} className="flex items-center justify-between gap-6 text-sm">
          <span className="flex items-center gap-1.5 text-black/70 dark:text-white/70">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: giris.color }}
            />
            {giris.name}
          </span>
          <span className="font-semibold text-black dark:text-white">
            {giris.dataKey === 'ortalamaTutar'
              ? formatParaBirimi(giris.value)
              : formatOran(giris.value)}
          </span>
        </div>
      ))}
    </div>
  );
};

OzelTooltip.propTypes = {
  active:  PropTypes.bool,
  payload: PropTypes.array,
  label:   PropTypes.string,
};

/**
 * @param {object} props
 * @param {import('../types/dashboard.types').FinansmanKalemi[]} props.veri
 */
export const FinansmanGrafigi = ({ veri }) => {
  const { t } = useI18n();

  const grafikVerisi = useMemo(() => {
    if (!veri || veri.length === 0) return [];

    const gruplar = veri.reduce((acc, kalem) => {
      const banka = kalem.bankaAdi;
      if (!acc[banka]) {
        acc[banka] = { bankaAdi: banka, toplamTutar: 0, toplamOran: 0, adet: 0 };
      }
      acc[banka].toplamTutar += kalem.tutar ?? 0;
      acc[banka].toplamOran  += kalem.karOrani ?? 0;
      acc[banka].adet        += 1;
      return acc;
    }, {});

    return Object.values(gruplar)
      .map((g) => ({
        bankaAdi:      g.bankaAdi,
        ortalamaTutar: Math.round(g.toplamTutar / g.adet),
        ortalamaOran:  parseFloat((g.toplamOran / g.adet).toFixed(2)),
      }))
      .sort((a, b) => b.ortalamaTutar - a.ortalamaTutar);
  }, [veri]);

  return (
    <div className="rounded-xl border bg-white shadow-sm border-black/10 dark:border-white/10 dark:bg-black transition-colors duration-200">
      <div className="border-b px-5 py-4 border-black/10 dark:border-white/10">
        <h2 className="text-sm font-semibold text-black dark:text-white">
          {t('dashboard.chart.title')}
        </h2>
        <p className="mt-0.5 text-xs text-black/50 dark:text-white/50">
          {t('dashboard.chart.subtitle')}
        </p>
      </div>

      <div className="px-2 py-5">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={grafikVerisi} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis
              dataKey="bankaAdi"
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              yAxisId="tutar"
              orientation="left"
              tickFormatter={PARA_BIRIM_KISALT}
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={false}
              tickLine={false}
              width={60}
            />
            <YAxis
              yAxisId="oran"
              orientation="right"
              tickFormatter={(v) => `%${v}`}
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={false}
              tickLine={false}
              width={40}
            />
            <Tooltip content={<OzelTooltip />} cursor={{ fill: '#f8fafc' }} />
            <Legend
              wrapperStyle={{ fontSize: '11px', color: '#64748b', paddingTop: '12px' }}
            />
            <Bar
              yAxisId="tutar"
              dataKey="ortalamaTutar"
              name={t('dashboard.chart.avgAmount')}
              fill={GRAFIK_RENKLERI.TUTAR}
              radius={[3, 3, 0, 0]}
              maxBarSize={48}
            />
            <Bar
              yAxisId="oran"
              dataKey="ortalamaOran"
              name={t('dashboard.chart.avgRate')}
              fill={GRAFIK_RENKLERI.KAR_ORANI}
              radius={[3, 3, 0, 0]}
              maxBarSize={48}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

FinansmanGrafigi.propTypes = {
  veri: PropTypes.arrayOf(PropTypes.object).isRequired,
};
