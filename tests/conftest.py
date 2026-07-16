"""Backend testleri için paylaşılan pytest fixture'ları (test DB ve client)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.models import Base
from src.backend.main import app, get_db

# Testler için bellek içi SQLite veritabanı kurulumu (StaticPool ile bağlantı paylaşımı)
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(name="test_db")
def fixture_test_db():
    """Her test için temiz bir veritabanı şeması ve oturumu sağlar."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def fixture_client(test_db):
    """FastAPI TestClient nesnesi oluşturur ve get_db bağımlılığını geçersiz kılar."""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
