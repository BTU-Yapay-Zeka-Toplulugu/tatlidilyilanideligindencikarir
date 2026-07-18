"""Veritabanı bağlantısı ve oturum yönetimi modülü."""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# .env dosyasını yükle
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://katilim_user:katilim_password@localhost:5433/katilim_db",
)

# SQLAlchemy engine ve sessionmaker oluştur
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Veritabanı oturumu oluşturur ve kullanım sonrası kapatılmasını sağlar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Modellerdeki tüm veritabanı tablolarını oluşturur.

    Mevcut tablolarda yeni eklenen kolonlar (ör. start_date/end_date) için
    idempotent ALTER migration uygular — create_all yalnızca yeni tablo
    oluşturur, var olan tabloya kolon eklemez.
    """
    from sqlalchemy import inspect

    from src.database.models import Base

    Base.metadata.create_all(bind=engine)

    # ADR-013: ExtractedCampaignDetail'a eklenen tarih kolonları için migration.
    _migrate_add_columns(
        engine,
        "extracted_campaign_details",
        {"start_date": "VARCHAR(20)", "end_date": "VARCHAR(20)"},
    )


def _migrate_add_columns(engine, table: str, columns: dict[str, str]) -> None:
    """Var olan tabloya eksik kolonları ekler (idempotent)."""
    from sqlalchemy import inspect

    inspector = inspect(engine)
    with engine.begin() as conn:
        existing = {c["name"] for c in inspector.get_columns(table, bind=conn)}
        for col, col_type in columns.items():
            if col not in existing:
                conn.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
                )
