"""Toplanan verilerin kalitesini, istatistiklerini ve veritabanı durumunu kontrol eden modül."""

import json
import logging
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.database.models import Bank, Campaign
from src.scraper.config import RAW_DATA_DIR

logger = logging.getLogger(__name__)


def get_latest_data_file() -> Path | None:
    """raw_data dizinindeki en son üretilen campaigns JSON dosyasını bulur."""
    files = list(RAW_DATA_DIR.glob("campaigns_*.json"))
    if not files:
        return None
    files.sort()
    return files[-1]


def analyze_data_quality(filepath: Path) -> bool:
    """Belirtilen JSON veri dosyasındaki kayıtların kalitesini analiz edip raporlar."""
    print(f"\n--- Dosya Veri Kalitesi Raporu ({filepath.name}) ---")
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

    print("\nBankalara Göre Kayıt Dağılımı:")
    for bank, count in bank_counts.items():
        print(f" - {bank}: {count} kayıt")

    print("\nKalite Metrikleri:")
    print(f" - Eksik/Varsayılan Başlık: {missing_titles} ({missing_titles/total_records*100:.1f}%)")
    print(f" - Boş İçerik: {empty_contents} ({empty_contents/total_records*100:.1f}%)")
    print(f" - Kısa İçerik (<100 karakter): {short_contents} ({short_contents/total_records*100:.1f}%)")

    is_ok = empty_contents == 0 and total_records > 50
    if is_ok:
        print("\n[BAŞARILI] Dosya veri kalitesi kabul edilebilir sınırlar dahilinde.")
    else:
        print("\n[UYARI] Bazı dosya veri kalitesi sorunları tespit edildi.")

    return is_ok


def analyze_db_quality(db: Session = None) -> bool:
    """Veritabanındaki banks ve campaigns tablolarının kalitesini ve doluluk oranlarını analiz eder."""
    print("\n--- Veritabanı Kalite ve Durum Raporu ---")
    own_session = False
    if not db:
        try:
            db = SessionLocal()
            own_session = True
        except Exception as e:
            print(f"HATA: Veritabanı bağlantısı kurulamadı: {e}")
            return False

    try:
        total_banks = db.query(Bank).count()
        total_campaigns = db.query(Campaign).count()

        print(f"Toplam Banka Sayısı: {total_banks}")
        print(f"Toplam Kampanya Sayısı: {total_campaigns}")

        if total_banks == 0:
            print("HATA: Veritabanında hiç banka kaydı yok.")
            return False

        if total_campaigns == 0:
            print("UYARI: Veritabanında hiç kampanya kaydı yok.")
            return False

        # Banka başına kampanya dağılımı
        print("\nBankalara Göre Kampanya Dağılımı:")
        banks = db.query(Bank).all()
        for bank in banks:
            count = db.query(Campaign).filter(Campaign.bank_id == bank.id).count()
            print(f" - {bank.name}: {count} kampanya")

        # Kalite kontrolleri
        missing_titles = db.query(Campaign).filter((Campaign.page_title == None) | (Campaign.page_title == "Başlık Bulunamadı")).count()
        short_campaigns = db.query(Campaign).filter(Campaign.content_length < 100).count()

        print("\nKalite Metrikleri (DB):")
        print(f" - Eksik/Varsayılan Başlık: {missing_titles} ({missing_titles/total_campaigns*100:.1f}%)")
        print(f" - Kısa İçerik (<100 karakter): {short_campaigns} ({short_campaigns/total_campaigns*100:.1f}%)")

        is_ok = total_campaigns > 50 and short_campaigns == 0
        if is_ok:
            print("\n[BAŞARILI] Veritabanı veri kalitesi kabul edilebilir sınırlar dahilinde.")
        else:
            print("\n[UYARI] Veritabanı verisinde eksiklikler veya kısa içerikler var.")
        return is_ok
    except Exception as e:
        print(f"HATA: Veritabanı sorgulanırken hata oluştu: {e}")
        return False
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    latest_file = get_latest_data_file()
    file_ok = False
    if latest_file:
        file_ok = analyze_data_quality(latest_file)
    else:
        print("HATA: Herhangi bir campaigns_*.json dosyası bulunamadı.")

    db_ok = analyze_db_quality()
    sys.exit(0 if (file_ok or db_ok) else 1)
