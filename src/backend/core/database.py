"""Veritabanı oturumu ve FastAPI bağımlılık enjeksiyonu (DI) yardımcıları."""

from typing import Iterator

from sqlalchemy.orm import Session

from src.database.connection import SessionLocal, init_db


def get_db() -> Iterator[Session]:
    """Her istek için bir veritabanı oturumu açar ve sonrasında kapatır (DI)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema() -> None:
    """Uygulama başlangıcında veritabanı tablolarının varlığını garanti eder."""
    init_db()
