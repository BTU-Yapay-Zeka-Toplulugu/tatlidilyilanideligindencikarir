"""Veritabanı bağlantısı ve oturum yönetimi modülü."""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
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
    """Modellerdeki tüm veritabanı tablolarını oluşturur."""
    from src.database.models import Base

    Base.metadata.create_all(bind=engine)
