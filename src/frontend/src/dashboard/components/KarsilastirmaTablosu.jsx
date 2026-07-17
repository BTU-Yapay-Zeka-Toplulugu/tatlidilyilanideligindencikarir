// src/dashboard/components/KarsilastirmaTablosu.jsx
// Bölüm 4: Karşılaştırma Tablosu — sıralanabilir, dışa aktarılabilir, responsive
// Named Export — export default YASAKTIR

import { useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import { ChevronUp, ChevronDown, ChevronsUpDown, Download } from 'lucide-react';
import { formatParaBirimi, formatOran, formatTarih } from '../../utils/formatters';
import { csvOlarakIndir } from '../../utils/csvExporter';
import { TABLO_SUTUNLARI, SIRALAMA_YONU } from '../../constants/uiSabitleri';
import { cn } from '../../utils/styleUtils';
import { useI18n } from '../../context/I18nContext';

/**
 * Hücre değerini formatlar.
 */
const hucreDegeriniFormatla = (anahtar, deger, ayMetni) => {
  if (anahtar === TABLO_SUTUNLARI.TUTAR)     return formatParaBirimi(deger);
  if (anahtar === TABLO_SUTUNLARI.KAR_ORANI) return formatOran(deger);
  if (anahtar === TABLO_SUTUNLARI.TARIH)     return formatTarih(deger);
  if (anahtar === TABLO_SUTUNLARI.VADE)      return `${deger} ${ayMetni}`;
  return deger ?? '—';
};

/**
 * Sıralama ikonu — aktif sütuna göre yön gösterir.
 */
const SiralamaIkonu = ({ anahtar, aktifSutun, aktifYon }) => {
  if (aktifSutun !== anahtar)
    return <ChevronsUpDown size={14} className="text-black/20 dark:text-white/20" />;
  return aktifYon === SIRALAMA_YONU.ARTAN
    ? <ChevronUp size={14} className="text-black dark:text-white" />
    : <ChevronDown size={14} className="text-black dark:text-white" />;
};

SiralamaIkonu.propTypes = {
  anahtar:    PropTypes.string.isRequired,
  aktifSutun: PropTypes.string,
  aktifYon:   PropTypes.string,
};

/**
 * Presentational karşılaştırma tablosu bileşeni.
 */
export const KarsilastirmaTablosu = ({ veri, siralamaAlani, siralamaYonu, onSiralama }) => {
  const { t } = useI18n();

  const SUTUN_TANIMLARI = useMemo(() => [
    { baslik: t('dashboard.table.cols.bank'),    anahtar: TABLO_SUTUNLARI.BANKA_ADI,  hizalama: 'left'  },
    { baslik: t('dashboard.table.cols.product'), anahtar: TABLO_SUTUNLARI.URUN_ADI,   hizalama: 'left'  },
    { baslik: t('dashboard.table.cols.amount'),  anahtar: TABLO_SUTUNLARI.TUTAR,      hizalama: 'right' },
    { baslik: t('dashboard.table.cols.rate'),    anahtar: TABLO_SUTUNLARI.KAR_ORANI,  hizalama: 'right' },
    { baslik: t('dashboard.table.cols.term'),    anahtar: TABLO_SUTUNLARI.VADE,       hizalama: 'right' },
    { baslik: t('dashboard.table.cols.date'),    anahtar: TABLO_SUTUNLARI.TARIH,      hizalama: 'left'  },
  ], [t]);

  const ayMetni = t('dashboard.table.months');
  const sortLabel = t('dashboard.table.sortLabel');

  const handleIndir = useCallback(() => {
    csvOlarakIndir(veri, 'finansman-karsilastirma');
  }, [veri]);

  return (
    <div className="rounded-xl border bg-white shadow-sm border-black/10 dark:border-white/10 dark:bg-black transition-colors duration-200">
      {/* Tablo Başlık Alanı */}
      <div className="flex items-center justify-between border-b px-5 py-4 border-black/10 dark:border-white/10">
        <div>
          <h2 className="text-sm font-semibold text-black dark:text-white">
            {t('dashboard.table.title')}
          </h2>
          <p className="mt-0.5 text-xs text-black/50 dark:text-white/50">
            {veri.length} {t('dashboard.table.listing')}
          </p>
        </div>
        <button
          onClick={handleIndir}
          disabled={veri.length === 0}
          aria-label="Tabloyu CSV olarak dışa aktar"
          className="inline-flex items-center gap-1.5 rounded-lg border bg-white px-3 py-1.5 text-xs font-medium text-black shadow-sm transition-colors hover:bg-black/5 focus:outline-none focus:ring-0 outline-none dark:border-white/10 dark:bg-black dark:text-white dark:hover:bg-white/5"
        >
          <Download size={13} aria-hidden="true" />
          {t('dashboard.table.export')}
        </button>
      </div>

      {/* Tablo — overflow-x-auto mobil uyum */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm" aria-label="Finansman Karşılaştırma Tablosu">
          <thead>
            <tr className="bg-black/[0.02] dark:bg-white/[0.04]">
              {SUTUN_TANIMLARI.map((sutun) => (
                <th
                  key={sutun.anahtar}
                  scope="col"
                  aria-sort={
                    siralamaAlani === sutun.anahtar
                      ? siralamaYonu === SIRALAMA_YONU.ARTAN ? 'ascending' : 'descending'
                      : 'none'
                  }
                  className={cn(
                    'whitespace-nowrap border-b px-4 py-3 text-xs font-semibold uppercase tracking-wide text-black/50 border-black/10 dark:border-white/10 dark:text-white/50',
                    sutun.hizalama === 'right' ? 'text-right' : 'text-left'
                  )}
                >
                  <button
                    onClick={() => onSiralama(sutun.anahtar)}
                    className="inline-flex items-center gap-1 transition-colors hover:text-black dark:hover:text-white focus:outline-none focus:ring-0 outline-none"
                    aria-label={`${sutun.baslik} ${sortLabel}`}
                  >
                    {sutun.baslik}
                    <SiralamaIkonu
                      anahtar={sutun.anahtar}
                      aktifSutun={siralamaAlani}
                      aktifYon={siralamaYonu}
                    />
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {veri.map((satir, index) => (
              <tr
                key={satir.id ?? index}
                className="border-b transition-colors last:border-0 border-black/5 dark:border-white/5 hover:bg-black/[0.02] dark:hover:bg-white/[0.04]"
              >
                {SUTUN_TANIMLARI.map((sutun) => (
                  <td
                    key={sutun.anahtar}
                    className={cn(
                      'whitespace-nowrap px-4 py-3.5 text-sm text-black/80 dark:text-white/80',
                      sutun.hizalama === 'right' ? 'text-right font-medium tabular-nums' : 'text-left',
                      sutun.anahtar === TABLO_SUTUNLARI.KAR_ORANI && 'font-semibold text-emerald-700 dark:text-emerald-400'
                    )}
                  >
                    {hucreDegeriniFormatla(sutun.anahtar, satir[sutun.anahtar], ayMetni)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

KarsilastirmaTablosu.propTypes = {
  veri:          PropTypes.arrayOf(PropTypes.object).isRequired,
  siralamaAlani: PropTypes.string,
  siralamaYonu:  PropTypes.oneOf([SIRALAMA_YONU.ARTAN, SIRALAMA_YONU.AZALAN]),
  onSiralama:    PropTypes.func.isRequired,
};
