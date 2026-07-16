"""Temizlenmiş verilerin PostgreSQL veritabanına yüklenmesini sağlayan modül."""

import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.database.models import Bank, Campaign

logger = logging.getLogger(__name__)


def load_cleaned_data_to_db(json_file_path: Path, db: Session = None) -> int:
    """Temizlenmiş JSON verilerini veritabanındaki banks ve campaigns tablolarına yükler veya günceller."""
    if not db:
        db = SessionLocal()
        own_session = True
    else:
        own_session = False

    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        loaded_count = 0
        for record in records:
            bank_name = record.get("bank_name")
            bank_url = record.get("bank_url", "")
            source_url = record.get("source_url")
            page_title = record.get("page_title")
            cleaned_text = record.get("raw_text")

            if not bank_name or not source_url or not cleaned_text:
                continue

            # 1. Banka kaydını bul veya oluştur
            bank = db.query(Bank).filter(Bank.name == bank_name).first()
            if not bank:
                bank = Bank(name=bank_name, url=bank_url)
                db.add(bank)
                db.flush()  # ID alabilmek için flush et

            # 2. Kampanya kaydını bul (varsa güncelle, yoksa ekle - Upsert mantığı)
            campaign = db.query(Campaign).filter(Campaign.source_url == source_url).first()
            if campaign:
                campaign.page_title = page_title
                campaign.raw_text = cleaned_text
                campaign.content_length = len(cleaned_text)
            else:
                campaign = Campaign(
                    bank_id=bank.id,
                    source_url=source_url,
                    page_title=page_title,
                    raw_text=cleaned_text,
                    content_length=len(cleaned_text),
                )
                db.add(campaign)

            loaded_count += 1

        db.commit()
        logger.info(f"{loaded_count} kampanya kaydı veritabanına başarıyla yüklendi.")
        return loaded_count
    except Exception as e:
        db.rollback()
        logger.error(f"Veritabanına veri yüklenirken hata oluştu: {e}")
        raise e
    finally:
        if own_session:
            db.close()
