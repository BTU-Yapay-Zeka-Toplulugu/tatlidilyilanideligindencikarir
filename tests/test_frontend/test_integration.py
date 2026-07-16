"""Frontend ↔ Backend uçtan uca bağlantı testi (gerçek FastAPI üzerinden)."""

import pytest
from fastapi.testclient import TestClient

from src.backend.main import app, get_db
from src.database.models import Base, Bank, Campaign
from src.frontend.api_client import ApiClient


@pytest.fixture(name="live_client")
def fixture_live_client(test_db):
    """Gerçek FastAPI uygulamasını TestClient ile ve test DB ile başlatır."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    bank = Bank(name="Bağlantı Bank", url="https://baglanti.com")
    db.add(bank)
    db.commit()
    db.add(
        Campaign(
            bank_id=bank.id,
            source_url="https://baglanti.com/k",
            page_title="Katılma Hesabı",
            raw_text="Katılma hesabı kâr payı %18.0 ve 3 ay vadeli.",
            content_length=50,
        )
    )
    db.commit()
    db.close()

    def override_get_db():
        try:
            yield TestingSessionLocal()
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


class _Bridge:
    """ApiClient'in requests çağrılarını TestClient'e yönlendiren köprü."""

    def __init__(self, test_client: TestClient) -> None:
        """Hedef TestClient'i saklar."""
        self.test_client = test_client

    def get(self, url: str, params=None, timeout=10):
        """GET isteğini TestClient üzerinden yapar."""
        path = url.replace("http://localhost:8000", "")
        response = self.test_client.get(path, params=params)
        return response


def test_frontend_consumes_real_backend(live_client):
    """Frontend API istemcisi gerçek backend'den kampanya ve karşılaştırma çeker."""
    client = ApiClient(base_url="http://localhost:8000")
    client._get = lambda path, params=None: _Bridge(live_client).get(
        "http://localhost:8000" + path, params
    ).json()

    banks = client.get_banks()
    assert any(b["name"] == "Bağlantı Bank" for b in banks)

    campaigns = client.get_campaigns()
    assert len(campaigns) == 1
    assert campaigns[0]["extracted_detail"]["profit_share_rate"] == 18.0

    comparison = client.compare(term_months=3)
    assert comparison[0]["bank_name"] == "Bağlantı Bank"
    assert comparison[0]["profit_share_rate"] == 18.0
