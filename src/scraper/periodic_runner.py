"""Periyodik tarama, temizleme, veritabanına yükleme ve kalite kontrol adımlarını otomatikleştiren modül."""

import argparse
import logging
import sys
import time
from pathlib import Path
from src.database.connection import init_db
from src.database.loader import load_cleaned_data_to_db
from src.scraper.check_data_quality import analyze_data_quality, analyze_db_quality
from src.scraper.data_cleaner import clean_dataset
from src.scraper.main import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_full_cycle() -> bool:
    """Tüm tarama, temizleme, veritabanına yükleme ve kalite kontrol döngüsünü baştan sona çalıştırır."""
    logger.info("=== Yeniden Tarama ve Güncelleme Döngüsü Başlatıldı ===")
    try:
        # 1. Veritabanını ilklendir (tablolar yoksa oluşturulur)
        init_db()

        # 2. Scraper'ı çalıştır (Ham veri toplama)
        logger.info("Adım 1: Banka web sitelerinden ham verilerin toplanması...")
        run_pipeline()

        # 3. Veri temizleme işlemini çalıştır
        logger.info("Adım 2: Toplanan ham verilerin temizlenmesi ve normalizasyonu...")
        cleaned_json_path, _ = clean_dataset()
        if not cleaned_json_path:
            logger.error("Temizlenmiş veri seti oluşturulamadı.")
            return False

        # 4. Veritabanına yükleme işlemini çalıştır
        logger.info("Adım 3: Temizlenen verilerin PostgreSQL veritabanına aktarılması...")
        load_cleaned_data_to_db(Path(cleaned_json_path))

        # 5. Kalite denetimlerini çalıştır
        logger.info("Adım 4: Veri ve veritabanı kalite kontrollerinin yapılması...")
        file_ok = analyze_data_quality(Path(cleaned_json_path))
        db_ok = analyze_db_quality()

        logger.info("=== Yeniden Tarama ve Güncelleme Döngüsü Tamamlandı ===")
        return file_ok and db_ok

    except Exception as e:
        logger.exception(f"Döngü sırasında kritik hata oluştu: {e}")
        return False


def main() -> None:
    """Komut satırı argümanlarına göre periyodik tarama döngüsünü başlatır."""
    parser = argparse.ArgumentParser(description="Katılım Bankası Periyodik Tarama ve Güncelleme Servisi")
    parser.add_argument("--once", action="store_true", help="Döngüyü sadece bir kez çalıştırır ve çıkar")
    parser.add_argument("--interval", type=int, default=86400, help="Saniye cinsinden tarama sıklığı (varsayılan: 24 saat)")

    args = parser.parse_args()

    if args.once:
        success = run_full_cycle()
        sys.exit(0 if success else 1)

    logger.info(f"Servis başlatıldı. Tarama sıklığı: {args.interval} saniye.")
    while True:
        run_full_cycle()
        logger.info(f"{args.interval} saniye boyunca bekleniyor...")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
