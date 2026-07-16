"""Ham kampanya verilerini temizleyip standart formata dönüştüren modül."""

import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Optional

from src.scraper.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

logger = logging.getLogger(__name__)

# Temizleme sırasında kaldırılacak kontrol karakter desenleri
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_MULTI_WHITESPACE = re.compile(r"[ \t]+")
_MULTI_NEWLINES = re.compile(r"\n{3,}")
_URL_PATTERN = re.compile(r"https?://\S+")


def normalize_unicode(text: str) -> str:
    """Unicode NFC normalizasyonu uygular (Türkçe karakterler için tutarlılık)."""
    return unicodedata.normalize("NFC", text)


def remove_control_characters(text: str) -> str:
    """Görünmez kontrol karakterlerini metinden kaldırır."""
    return _CONTROL_CHARS.sub("", text)


def collapse_whitespace(text: str) -> str:
    """Ardışık boşluk ve tab karakterlerini tek boşluğa indirger."""
    text = _MULTI_WHITESPACE.sub(" ", text)
    text = _MULTI_NEWLINES.sub("\n\n", text)
    return text.strip()


def remove_navigation_noise(text: str) -> str:
    """Menü öğeleri, cookie uyarıları gibi tekrar eden kalıpları temizler."""
    noise_patterns = [
        re.compile(r"(?i)çerez\s*(politikası|kullanımı|ayarları).*?(?:\n|$)"),
        re.compile(r"(?i)cookie\s*(policy|settings|notice).*?(?:\n|$)"),
        re.compile(r"(?i)tüm\s+hakları\s+saklıdır.*?(?:\n|$)"),
        re.compile(r"(?i)copyright\s*©.*?(?:\n|$)"),
        re.compile(r"(?i)gizlilik\s*(politikası|sözleşmesi).*?(?:\n|$)"),
    ]
    for pattern in noise_patterns:
        text = pattern.sub("", text)
    return text


def clean_text(text: str) -> str:
    """Tüm metin temizleme adımlarını sırasıyla uygular."""
    text = normalize_unicode(text)
    text = remove_control_characters(text)
    text = remove_navigation_noise(text)
    text = collapse_whitespace(text)
    return text


def clean_record(record: dict) -> Optional[dict]:
    """Tek bir kampanya kaydını temizler, geçersiz kayıtlar için None döner."""
    raw_text = record.get("raw_text", "")
    if not raw_text:
        return None

    cleaned_text = clean_text(raw_text)

    # Temizleme sonrası minimum uzunluk kontrolü
    if len(cleaned_text) < 50:
        logger.debug(
            "Temizleme sonrası çok kısa metin, atlanıyor: %s",
            record.get("source_url", "?"),
        )
        return None

    # Temiz kaydı oluştur
    cleaned = record.copy()
    cleaned["raw_text"] = cleaned_text
    cleaned["content_length"] = len(cleaned_text)

    # Başlık temizliği
    title = cleaned.get("page_title", "")
    if title:
        cleaned["page_title"] = clean_text(title)

    return cleaned


def get_latest_raw_file() -> Optional[Path]:
    """data/raw dizinindeki en son campaigns JSON dosyasını bulur."""
    files = sorted(RAW_DATA_DIR.glob("campaigns_*.json"))
    return files[-1] if files else None


def clean_dataset(
    input_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
) -> Optional[Path]:
    """Ham veri setini temizleyip data/processed altına kaydeder."""
    input_path = input_path or get_latest_raw_file()
    if not input_path or not input_path.exists():
        logger.error("Ham veri dosyası bulunamadı.")
        return None

    output_dir = output_dir or PROCESSED_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Yükle
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    logger.info("Ham veri yüklendi: %d kayıt (%s)", len(raw_data), input_path.name)

    # Temizle
    cleaned_data = []
    skipped = 0
    for record in raw_data:
        cleaned = clean_record(record)
        if cleaned:
            cleaned_data.append(cleaned)
        else:
            skipped += 1

    logger.info(
        "Temizleme tamamlandı: %d kayıt tutuldu, %d kayıt atlandı.",
        len(cleaned_data), skipped,
    )

    # Kaydet (JSON)
    output_json = output_dir / "campaigns_cleaned.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    # Kaydet (CSV)
    if cleaned_data:
        import csv

        output_csv = output_dir / "campaigns_cleaned.csv"
        fieldnames = list(cleaned_data[0].keys())
        with open(output_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_data)
        logger.info("Temiz CSV kaydedildi: %s", output_csv)

    logger.info("Temiz JSON kaydedildi: %s", output_json)
    return output_json


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    result = clean_dataset()
    if result:
        print(f"Temiz veri seti oluşturuldu: {result}")
    else:
        print("HATA: Veri temizleme başarısız.")
        sys.exit(1)
