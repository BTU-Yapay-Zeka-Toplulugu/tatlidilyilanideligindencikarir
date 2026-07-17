"""Temizlenmiş kampanya verisini veritabanına yükleyen seeder (demo/BAREMETAL).

Kullanım:
    conda activate katilim-nlp
    python -m src.database.seed
"""

import json
import os

from dotenv import load_dotenv

from src.database.connection import SessionLocal, init_db
from src.database.models import Bank, Campaign

SEED_FILE = os.path.join("data", "processed", "campaigns_cleaned.json")


def seed() -> None:
    """Bankaları ve kampanyaları veritabanına toplu olarak ekler."""
    load_dotenv()
    init_db()
    with open(SEED_FILE, encoding="utf-8") as fh:
        records = json.load(fh)

    db = SessionLocal()
    try:
        bank_map: dict[int, Bank] = {}
        for rec in records:
            bid = rec["bank_id"]
            if bid not in bank_map:
                bank = db.query(Bank).filter_by(id=bid).first()
                if bank is None:
                    bank = Bank(id=bid, name=rec["bank_name"], url="")
                    db.add(bank)
                    db.flush()
                bank_map[bid] = bank

        existing_urls = {
            u for (u,) in db.query(Campaign.source_url).all()
        }
        added = 0
        for rec in records:
            if rec["source_url"] in existing_urls:
                continue
            db.add(
                Campaign(
                    bank_id=rec["bank_id"],
                    source_url=rec["source_url"],
                    page_title=rec.get("page_title"),
                    raw_text=rec["raw_text"],
                    content_length=len(rec["raw_text"]),
                )
            )
            added += 1
        db.commit()
        print(f"Seed tamamlandı: {len(bank_map)} banka, {added} yeni kampanya eklendi.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
