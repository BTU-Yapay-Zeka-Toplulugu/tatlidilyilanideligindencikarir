// src/utils/csvExporter.js
// Bölüm 4 Best Practices: İstemci taraflı CSV dışa aktarma — sunucu isteği olmadan
// Pure function — yan etkisiz, test edilebilir

/**
 * FinansmanKalemi dizisini CSV formatında indirir.
 * @param {import('../dashboard/types/dashboard.types').FinansmanKalemi[]} veri
 * @param {string} [dosyaAdi='finansman-raporu']
 */
export const csvOlarakIndir = (veri, dosyaAdi = 'finansman-raporu') => {
  if (!veri || veri.length === 0) return;

  const sutunlar = [
    { baslik: 'Banka Adı',    anahtar: 'bankaAdi' },
    { baslik: 'Ürün Adı',    anahtar: 'urunAdi' },
    { baslik: 'Tutar (TRY)', anahtar: 'tutar' },
    { baslik: 'Kâr Oranı (%)',anahtar: 'karOrani' },
    { baslik: 'Vade (Ay)',   anahtar: 'vade' },
    { baslik: 'Tarih',       anahtar: 'tarih' },
  ];

  const baslikSatiri = sutunlar.map((s) => `"${s.baslik}"`).join(',');

  const satirlar = veri.map((satir) =>
    sutunlar
      .map((s) => {
        const deger = satir[s.anahtar] ?? '';
        // Virgül ve tırnak içeren değerleri güvenli hale getir
        return `"${String(deger).replace(/"/g, '""')}"`;
      })
      .join(',')
  );

  const csvIcerigi = [baslikSatiri, ...satirlar].join('\n');

  // BOM: Excel'in UTF-8 Türkçe karakterleri doğru okuması için
  const bom = '\uFEFF';
  const blob = new Blob([bom + csvIcerigi], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `${dosyaAdi}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
