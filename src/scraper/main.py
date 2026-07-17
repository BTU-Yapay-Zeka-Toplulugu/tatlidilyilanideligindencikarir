"""Scraper ana pipeline — banka listesi yükleme, keşif, tarama ve kaydetme."""

import logging
import sys
import time
from typing import Optional

from src.scraper.bank_parser import load_bank_list
from src.scraper.campaign_scraper import scrape_all_campaign_pages
from src.scraper.config import RAW_DATA_DIR, REQUEST_DELAY
from src.scraper.discovery import discover_campaign_pages
from src.scraper.models import BankInfo, CampaignData, CampaignPage
from src.scraper.pdf_crawler import crawl_and_extract_pdfs
from src.scraper.storage import (
    save_campaign_data_csv,
    save_campaign_data_json,
    save_discovered_pages_json,
)

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Logging yapılandırmasını ayarlar."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def run_discovery(banks: list[BankInfo]) -> list[CampaignPage]:
    """Tüm bankalar için kampanya sayfalarını keşfeder."""
    all_pages: list[CampaignPage] = []

    for i, bank in enumerate(banks, 1):
        logger.info(
            "=== [%d/%d] Keşif: %s ===", i, len(banks), bank.name
        )
        pages = discover_campaign_pages(bank)
        all_pages.extend(pages)

        if i < len(banks):
            time.sleep(REQUEST_DELAY)

    logger.info("Toplam %d kampanya sayfası keşfedildi.", len(all_pages))
    return all_pages


def _collect_pdf_seeds(banks: list[BankInfo],
                       pages: list[CampaignPage]) -> dict[int, list[str]]:
    """Her banka için PDF crawler'ı başlatacak seed URL'lerini toplar.

    Seed = banka ana sayfası + keşfedilen kampanya/kurumsal sayfalar.
    Statik mapping YOK — dinamik keşif çıktısı kullanılır (ADR-011).
    """
    seeds: dict[int, list[str]] = {}
    bank_map = {b.id: b for b in banks}
    for bank in banks:
        seeds.setdefault(bank.id, [bank.url])
    for page in pages:
        if page.bank_id in seeds:
            seeds[page.bank_id].append(page.page_url)
    # Benzersizle
    for bid in seeds:
        seeds[bid] = list(dict.fromkeys(seeds[bid]))
    return seeds


def run_pdf_crawling(banks: list[BankInfo],
                     pages: list[CampaignPage]) -> list[CampaignData]:
    """Dinamik & recursive PDF crawler'ı tüm bankalar için çalıştırır."""
    seeds = _collect_pdf_seeds(banks, pages)
    bank_map = {b.id: b for b in banks}
    all_pdf_data: list[CampaignData] = []

    for bank_id, seed_urls in seeds.items():
        bank = bank_map.get(bank_id)
        if not bank:
            continue
        logger.info(
            "=== PDF Crawl: %s (%d seed) ===", bank.name, len(seed_urls)
        )
        pdf_data = crawl_and_extract_pdfs(bank, seed_urls)
        all_pdf_data.extend(pdf_data)

        # Siteye yük bindirmememek için bankalar arası bekleme
        time.sleep(REQUEST_DELAY)

    logger.info("Toplam %d kampanya PDF metni çıkarıldı.", len(all_pdf_data))
    return all_pdf_data


def run_scraping(
    banks: list[BankInfo], pages: list[CampaignPage]
) -> list[CampaignData]:
    """Keşfedilen sayfalardan kampanya metinlerini çıkarır."""
    all_data: list[CampaignData] = []

    # Sayfaları bankaya göre grupla
    pages_by_bank: dict[int, list[CampaignPage]] = {}
    for page in pages:
        pages_by_bank.setdefault(page.bank_id, []).append(page)

    bank_map = {b.id: b for b in banks}

    for bank_id, bank_pages in pages_by_bank.items():
        bank = bank_map.get(bank_id)
        if not bank:
            logger.warning("Banka bulunamadı (id=%d), atlanıyor.", bank_id)
            continue

        logger.info(
            "=== Tarama: %s (%d sayfa) ===", bank.name, len(bank_pages)
        )
        data = scrape_all_campaign_pages(bank, bank_pages)
        all_data.extend(data)

    logger.info("Toplam %d kampanya metni çıkarıldı.", len(all_data))
    return all_data


def run_pipeline(bank_ids: Optional[list[int]] = None) -> None:
    """Tam scraper pipeline'ını çalıştırır."""
    setup_logging()

    logger.info("=" * 60)
    logger.info("Katılım Bankası Kampanya Scraper Başlatılıyor")
    logger.info("=" * 60)

    # 1. Banka listesini yükle
    banks = load_bank_list()
    if not banks:
        logger.error("Banka listesi boş, çıkılıyor.")
        return

    # Belirli bankalar filtrele (opsiyonel)
    if bank_ids:
        banks = [b for b in banks if b.id in bank_ids]
        logger.info("%d banka filtrelendi.", len(banks))

    logger.info("%d banka yüklendi.", len(banks))

    # 2. Kampanya sayfalarını keşfet
    pages = run_discovery(banks)
    if not pages:
        logger.warning("Hiç kampanya sayfası keşfedilemedi.")
        return

    # Keşfedilen sayfaları kaydet
    save_discovered_pages_json(pages)

    # 3. Kampanya metinlerini çıkar (HTML)
    data = run_scraping(banks, pages)

    # 3b. Dinamik & recursive PDF crawler (yeni kaynak tipi)
    pdf_data = run_pdf_crawling(banks, pages)
    data.extend(pdf_data)

    if not data:
        logger.warning("Hiç kampanya metni çıkarılamadı.")
        return

    # 4. Verileri kaydet
    json_path = save_campaign_data_json(data)
    csv_path = save_campaign_data_csv(data)

    logger.info("=" * 60)
    logger.info("Pipeline tamamlandı!")
    logger.info("  Keşfedilen sayfalar: %d", len(pages))
    logger.info("  Çıkarılan kampanyalar: %d", len(data))
    logger.info("  JSON çıktısı: %s", json_path)
    logger.info("  CSV çıktısı: %s", csv_path)
    logger.info("=" * 60)


if __name__ == "__main__":
    # Komut satırından belirli banka ID'leri ile çalıştırılabilir
    # Örn: python -m src.scraper.main 1 5 8
    ids = [int(arg) for arg in sys.argv[1:]] if len(sys.argv) > 1 else None
    run_pipeline(bank_ids=ids)
