"""BDDK katılım bankası listesini dosyadan okuyup parse eden modül."""

import re
import logging
from pathlib import Path

from src.scraper.config import BANK_SITES_FILE
from src.scraper.models import BankInfo

logger = logging.getLogger(__name__)

# bank_sites.txt satır formatı: "1. ADİL KATILIM BANKASI A.Ş. - https://..."
BANK_LINE_PATTERN = re.compile(
    r"^(\d+)\.\s+(.+?)\s*-\s*(https?://\S+)$"
)


def parse_bank_line(line: str) -> BankInfo | None:
    """Tek bir satırı parse edip BankInfo döndürür, geçersizse None."""
    line = line.strip()
    if not line:
        return None

    match = BANK_LINE_PATTERN.match(line)
    if not match:
        logger.warning("Geçersiz satır formatı, atlanıyor: %s", line)
        return None

    bank_id = int(match.group(1))
    name = match.group(2).strip()
    url = match.group(3).strip().rstrip("/")

    return BankInfo(id=bank_id, name=name, url=url)


def load_bank_list(filepath: Path | None = None) -> list[BankInfo]:
    """bank_sites.txt dosyasını okuyup BankInfo listesi döndürür."""
    filepath = filepath or BANK_SITES_FILE

    if not filepath.exists():
        logger.error("Banka listesi dosyası bulunamadı: %s", filepath)
        return []

    banks: list[BankInfo] = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            bank = parse_bank_line(line)
            if bank:
                banks.append(bank)

    logger.info("%d banka başarıyla yüklendi.", len(banks))
    return banks
