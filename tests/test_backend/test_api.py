"""FastAPI API uç noktaları için entegrasyon ve birim testleri."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.models import Base, Bank, Campaign
from src.backend.main import app, get_db

# Testler için bellek içi SQLite veritabanı kurulumu (StaticPool ile bağlantı paylaşımı)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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


def test_read_root(client):
    """Kök dizin API durumunu başarılı şekilde döner."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_banks_empty(client):
    """Banka kaydı yokken boş liste döner."""
    response = client.get("/api/banks")
    assert response.status_code == 200
    assert response.json() == []


def test_get_banks(client, test_db):
    """Banka kayıtlarını listeler."""
    bank = Bank(name="Test Katılım Bankası", url="https://testkatilim.com.tr")
    test_db.add(bank)
    test_db.commit()

    response = client.get("/api/banks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Katılım Bankası"


def test_get_campaigns_and_dynamic_nlp(client, test_db):
    """Kampanya sorgulandığında NLP analizi dinamik olarak tetiklenir ve kaydedilir."""
    bank = Bank(name="Adil Bank", url="https://adil.com")
    test_db.add(bank)
    test_db.commit()

    campaign = Campaign(
        bank_id=bank.id,
        source_url="https://adil.com/kampanya",
        page_title="Katılma Hesabı Kampanyası",
        raw_text="Yeni müşterilerimize özel %20.5 kâr payı oranıyla 3 ay vadeli katılma hesabı fırsatı. En az 10.000 TL bakiye.",
        content_length=120,
    )
    test_db.add(campaign)
    test_db.commit()

    # Kampanya sorgulanmadan önce NLP detayı veritabanında yok
    response = client.get("/api/campaigns")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["page_title"] == "Katılma Hesabı Kampanyası"

    # Dinamik NLP çıktısını kontrol et
    detail = data[0]["extracted_detail"]
    assert detail is not None
    assert detail["profit_share_rate"] == 20.5
    assert detail["term_months"] == 3
    assert detail["min_amount"] == 10000.0
    assert detail["campaign_type"] == "Katılma Hesabı / Mevduat"


def test_compare_campaigns(client, test_db):
    """Farklı banka kâr payı oranlarını karşılaştırıp sıralar."""
    b1 = Bank(name="Bank A", url="https://banka.com")
    b2 = Bank(name="Bank B", url="https://bankb.com")
    test_db.add_all([b1, b2])
    test_db.flush()

    c1 = Campaign(
        bank_id=b1.id,
        source_url="https://banka.com/k",
        page_title="Banka A Kampanyası",
        raw_text="Katılma hesabı kâr payı %15.0 ve 3 ay vadeli.",
        content_length=100,
    )
    c2 = Campaign(
        bank_id=b2.id,
        source_url="https://bankb.com/k",
        page_title="Banka B Kampanyası",
        raw_text="Katılma hesabı kâr payı %25.0 ve 3 ay vadeli.",
        content_length=100,
    )
    test_db.add_all([c1, c2])
    test_db.commit()

    # Karşılaştırma endpoint'ini çağır
    response = client.get("/api/compare?term_months=3")
    assert response.status_code == 200
    data = response.json()

    # Sıralamayı kontrol et (en yüksek oran önce gelmeli: %25 -> %15)
    assert len(data) == 2
    assert data[0]["bank_name"] == "Bank B"
    assert data[0]["profit_share_rate"] == 25.0
    assert data[1]["bank_name"] == "Bank A"
    assert data[1]["profit_share_rate"] == 15.0
