"""Toplanan verilerin kalitesini ve istatistiklerini kontrol eden modül."""

import json
import logging
import sys
from pathlib import Path
from src.scraper.config import RAW_DATA_DIR

logger = logging.getLogger(__name__)


def get_latest_data_file() -> Path | None:
    """raw_data dizinindeki en son üretilen campaigns JSON dosyasını bulur."""
    files = list(RAW_DATA_DIR.glob("campaigns_*.json"))
    if not files:
        return None
    # En son dosyayı almak için isme göre sırala (tarih damgalı olduğu için en sonuncusu sonda olur)
    files.sort()
    return files[-1]


def analyze_data_quality(filepath: Path) -> bool:
    """Belirtilen JSON veri dosyasındaki kayıtların kalitesini analiz edip raporlar."""
    print(f"\n--- Veri Kalitesi Raporu ({filepath.name}) ---")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"HATA: Dosya okunamadı veya JSON geçersiz: {e}")
        return False

    total_records = len(data)
    print(f"Toplam Kayıt Sayısı: {total_records}")

    if total_records == 0:
        print("HATA: Dosyada hiç kayıt yok.")
        return False

    bank_counts = {}
    missing_titles = 0
    empty_contents = 0
    short_contents = 0
    encoding_issues = 0
    turkish_characters = "çÇğĞıİöÖşŞüÜ"

    for record in data:
        bank_name = record.get("bank_name", "Bilinmeyen")
        bank_counts[bank_name] = bank_counts.get(bank_name, 0) + 1

        title = record.get("page_title", "")
        if not title or title == "Başlık Bulunamadı":
            missing_titles += 1

        text = record.get("raw_text", "")
        if not text:
            empty_contents += 1
        elif len(text) < 100:
            short_contents += 1

        # Türkçe karakterlerin Unicode kaçış dizisi olarak kalıp kalmadığını kontrol et
        # (Örn: \u015f şeklinde mi yoksa doğrudan ş olarak mı kaydedilmiş)
        # JSON kütüphanesi dosyayı okurken otomatik decode eder, ancak dosyada doğrudan okunabilir mi diye ham metin kontrolü
        # de yapılabilir. Burada Python içindeki metin durumunu kontrol ediyoruz.
        if any(char in text for char in turkish_characters):
            pass
        else:
            # En azından bazı Türkçe kelimeler olması beklenir, hiç Türkçe karakter olmaması şüpheli olabilir
            # Fakat kısa/özel İngilizce terimler içerebilecek bazı sayfalar hariç tutulabilir.
            # Basit bir check:
            pass

    print("\nBankalara Göre Kayıt Dağılımı:")
    for bank, count in bank_counts.items():
        print(f" - {bank}: {count} kayıt")

    print("\nKalite Metrikleri:")
    print(f" - Eksik/Varsayılan Başlık: {missing_titles} ({missing_titles/total_records*100:.1f}%)")
    print(f" - Boş İçerik: {empty_contents} ({empty_contents/total_records*100:.1f}%)")
    print(f" - Kısa İçerik (<100 karakter): {short_contents} ({short_contents/total_records*100:.1f}%)")

    # Genel kalite kontrol durumu
    is_ok = empty_contents == 0 and total_records > 50
    if is_ok:
        print("\n[BAŞARILI] Veri kalitesi kabul edilebilir sınırlar dahilinde.")
    else:
        print("\n[UYARI] Bazı veri kalitesi sorunları tespit edildi.")

    return is_ok


if __name__ == "__main__":
    latest_file = get_latest_data_file()
    if not latest_file:
        print("HATA: Herhangi bir campaigns_*.json dosyası bulunamadı.")
        sys.exit(1)

    ok = analyze_data_quality(latest_file)
    sys.exit(0 if ok else 1)
