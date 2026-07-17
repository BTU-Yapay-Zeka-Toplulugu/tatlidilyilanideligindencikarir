// src/dashboard/pages/DashboardPage.jsx
// Bölüm 4: Dashboard ana sayfası — Container bileşeni
// SRP: Hook çağırır ve alt bileşenlere prop olarak geçirir.
// Named Export — export default YASAKTIR

import { useMemo } from 'react';
import { Landmark, Percent, Building2, TrendingDown, CalendarDays } from 'lucide-react';
import { useFinansmanOzeti }        from '../hooks/useFinansmanOzeti';
import { useFinansmanKarsilastirma } from '../hooks/useFinansmanKarsilastirma';
import { OzetKart }                 from '../components/OzetKart';
import { KarsilastirmaTablosu }     from '../components/KarsilastirmaTablosu';
import { FinansmanGrafigi }         from '../components/FinansmanGrafigi';
import { OzetKartSkeleton, TabloSkeleton, GrafikSkeleton } from '../../components/SkeletonCard';
import { EmptyState }               from '../../components/EmptyState';
import { ErrorState }               from '../../components/ErrorState';
import { formatParaBirimi, formatOran, formatTarih } from '../../utils/formatters';
import { DURUM } from '../../constants/uiSabitleri';
import { useI18n } from '../../context/I18nContext';

const ozetMetrikleriniHesapla = (veri) => {
  if (!veri || veri.length === 0) return null;
  const toplamTutar       = veri.reduce((acc, k) => acc + (k.tutar ?? 0), 0);
  const ortalamaOran      = veri.reduce((acc, k) => acc + (k.karOrani ?? 0), 0) / veri.length;
  const enDusukOran       = Math.min(...veri.map((k) => k.karOrani ?? Infinity));
  const benzersizBankalar = new Set(veri.map((k) => k.bankaAdi)).size;
  return { toplamTutar, ortalamaOran, enDusukOran, benzersizBankalar };
};

export const DashboardPage = () => {
  const { t } = useI18n();
  const ozetHook          = useFinansmanOzeti();
  const karsilastirmaHook = useFinansmanKarsilastirma();

  const metrikler = useMemo(
    () => ozetMetrikleriniHesapla(ozetHook.data),
    [ozetHook.data]
  );

  const bugunTarih = formatTarih(new Date().toISOString());

  return (
    <div className="space-y-8 bg-transparent text-black dark:text-white min-h-screen transition-colors duration-200">
      {/* Sayfa Başlığı — Sidebar artık hep şerit şeklinde olduğu için ekstra butona ihtiyaç yoktur */}
      <div className="flex items-center">
        <div>
          <h1 className="text-xl font-bold text-black dark:text-white">
            {t('dashboard.title')}
          </h1>
          <p className="mt-1 flex items-center gap-1.5 text-sm text-black/50 dark:text-white/50">
            <CalendarDays size={14} aria-hidden="true" />
            {bugunTarih} {t('dashboard.subtitle')}
          </p>
        </div>
      </div>

      {/* ── ÖZET KARTLAR ─────────────────────────────── */}
      {ozetHook.status === DURUM.YUKLENIYOR && (
        <section aria-label="Özet kartlar yükleniyor">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[1, 2, 3, 4].map((n) => <OzetKartSkeleton key={n} />)}
          </div>
        </section>
      )}

      {ozetHook.status === DURUM.HATA && (
        <ErrorState mesaj={ozetHook.hata} onYeniDene={ozetHook.yenile} />
      )}

      {ozetHook.status === DURUM.BOS && (
        <EmptyState
          baslik={t('dashboard.empty.noData')}
          aciklama={t('dashboard.empty.noDataDesc')}
        />
      )}

      {ozetHook.status === DURUM.BASARILI && metrikler && (
        <section aria-label="Finansman özet metrikleri">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <OzetKart
              baslik={t('dashboard.cards.totalFinancing')}
              deger={formatParaBirimi(metrikler.toplamTutar)}
              ikon={Landmark}
              trend="yukari"
              trendMetni={t('dashboard.cards.trend.allProducts')}
            />
            <OzetKart
              baslik={t('dashboard.cards.avgRate')}
              deger={formatOran(metrikler.ortalamaOran)}
              ikon={Percent}
              trend="sabit"
              trendMetni={t('dashboard.cards.trend.weightedAvg')}
            />
            <OzetKart
              baslik={t('dashboard.cards.bankCount')}
              deger={String(metrikler.benzersizBankalar)}
              ikon={Building2}
              trend="sabit"
              trendMetni={t('dashboard.cards.trend.registered')}
            />
            <OzetKart
              baslik={t('dashboard.cards.bestRate')}
              deger={formatOran(metrikler.enDusukOran)}
              ikon={TrendingDown}
              trend="yukari"
              trendMetni={t('dashboard.cards.trend.lowest')}
            />
          </div>
        </section>
      )}

      {/* ── GRAFİK ──────────────────────────────────── */}
      {karsilastirmaHook.status === DURUM.YUKLENIYOR && <GrafikSkeleton />}

      {karsilastirmaHook.status === DURUM.HATA && (
        <ErrorState mesaj={karsilastirmaHook.hata} onYeniDene={karsilastirmaHook.yenile} />
      )}

      {karsilastirmaHook.status === DURUM.BASARILI && karsilastirmaHook.data.length > 0 && (
        <section aria-label="Finansman karşılaştırma grafiği">
          <FinansmanGrafigi veri={karsilastirmaHook.data} />
        </section>
      )}

      {/* ── KARŞILAŞTIRMA TABLOSU ───────────────────── */}
      {karsilastirmaHook.status === DURUM.YUKLENIYOR && <TabloSkeleton satirSayisi={6} />}

      {karsilastirmaHook.status === DURUM.BOS && (
        <EmptyState
          baslik={t('dashboard.empty.noComparison')}
          aciklama={t('dashboard.empty.noComparisonDesc')}
          butonMetni={t('dashboard.empty.refresh')}
          onButon={karsilastirmaHook.yenile}
        />
      )}

      {karsilastirmaHook.status === DURUM.BASARILI && (
        <section aria-label="Finansman karşılaştırma tablosu">
          <KarsilastirmaTablosu
            veri={karsilastirmaHook.filtrelenmisData}
            siralamaAlani={karsilastirmaHook.siralamaAlani}
            siralamaYonu={karsilastirmaHook.siralamaYonu}
            onSiralama={karsilastirmaHook.siralama}
          />
        </section>
      )}
    </div>
  );
};
