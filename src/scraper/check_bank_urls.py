"""Banka web sitelerinin erişilebilirliğini kontrol eden yardımcı script."""

import logging
import sys
import requests
from src.scraper.bank_parser import load_bank_list
from src.scraper.config import DEFAULT_HEADERS

logger = logging.getLogger(__name__)


def check_all_banks() -> bool:
    """Tüm banka web sitelerine basit HTTP GET istekleri atarak erişilebilirliği doğrular."""
    banks = load_bank_list()
    if not banks:
        print("HATA: Banka listesi yüklenemedi.")
        return False

    success = True
    print(f"Toplam {len(banks)} banka adresi kontrol ediliyor...")
    for bank in banks:
        try:
            # Sadece bağlantı kurulabiliyor mu diye kontrol etmek için timeout 10 sn
            response = requests.get(bank.url, headers=DEFAULT_HEADERS, timeout=10)
            status = response.status_code
            if status < 400:
                print(f"[OK] {bank.name}: {bank.url} (Durum Kodu: {status})")
            else:
                print(f"[UYARI] {bank.name}: {bank.url} (Durum Kodu: {status})")
                success = False
        except Exception as e:
            print(f"[HATA] {bank.name}: {bank.url} bağlantısı başarısız oldu. Hata: {e}")
            success = False

    return success


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    all_ok = check_all_banks()
    sys.exit(0 if all_ok else 1)
