"""Toplanan kampanya verilerini JSON/CSV formatında kaydeden depolama modülü."""

import csv
import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.scraper.config import RAW_DATA_DIR
from src.scraper.models import CampaignData, CampaignPage

logger = logging.getLogger(__name__)


def _ensure_directory(directory: Path) -> None:
    """Dizin yoksa oluşturur."""
    directory.mkdir(parents=True, exist_ok=True)


def _generate_filename(prefix: str, extension: str) -> str:
    """Tarih damgalı benzersiz dosya adı üretir."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def save_campaign_data_json(
    data: list[CampaignData],
    output_dir: Optional[Path] = None,
    filename: Optional[str] = None,
) -> Path:
    """Kampanya verilerini JSON dosyasına kaydeder."""
    output_dir = output_dir or RAW_DATA_DIR
    _ensure_directory(output_dir)

    filename = filename or _generate_filename("campaigns", "json")
    filepath = output_dir / filename

    records = [asdict(d) for d in data]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    logger.info("%d kampanya verisi JSON'a kaydedildi: %s", len(data), filepath)
    return filepath


def save_campaign_data_csv(
    data: list[CampaignData],
    output_dir: Optional[Path] = None,
    filename: Optional[str] = None,
) -> Path:
    """Kampanya verilerini CSV dosyasına kaydeder."""
    output_dir = output_dir or RAW_DATA_DIR
    _ensure_directory(output_dir)

    filename = filename or _generate_filename("campaigns", "csv")
    filepath = output_dir / filename

    if not data:
        logger.warning("Kaydedilecek veri yok.")
        filepath.touch()
        return filepath

    fieldnames = list(asdict(data[0]).keys())

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for d in data:
            writer.writerow(asdict(d))

    logger.info("%d kampanya verisi CSV'ye kaydedildi: %s", len(data), filepath)
    return filepath


def save_discovered_pages_json(
    pages: list[CampaignPage],
    output_dir: Optional[Path] = None,
    filename: Optional[str] = None,
) -> Path:
    """Keşfedilen kampanya sayfalarını JSON dosyasına kaydeder."""
    output_dir = output_dir or RAW_DATA_DIR
    _ensure_directory(output_dir)

    filename = filename or _generate_filename("discovered_pages", "json")
    filepath = output_dir / filename

    records = [asdict(p) for p in pages]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    logger.info("%d keşfedilen sayfa JSON'a kaydedildi: %s", len(pages), filepath)
    return filepath


def load_campaign_data_json(filepath: Path) -> list[dict]:
    """JSON dosyasından kampanya verilerini yükler."""
    if not filepath.exists():
        logger.error("Dosya bulunamadı: %s", filepath)
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info("%d kayıt yüklendi: %s", len(data), filepath)
    return data
