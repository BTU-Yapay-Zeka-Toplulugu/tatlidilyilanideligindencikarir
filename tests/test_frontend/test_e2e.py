"""Uçtan uca (scraper→NLP→backend→frontend) entegrasyon testi."""

import pytest
from fastapi.testclient import TestClient

from src.backend.main import app, get_db
from src.database.models import Base, Bank, Campaign
from src.frontend.api_client import ApiClient


@pytest.fixture(name="e2e_client")
def fixture_e2e_client():
    """Gerçek backend'i test DB ile başlatır ve TestClient döner."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    bank = Bank(name="E2E Bank", url="https://e2e.com")
    db.add(bank)
    db.commit()
    db.add(
        Campaign(
            bank_id=bank.id,
            source_url="https://e2e.com/k",
            page_title="Katılma Hesabı",
            raw_text="Katılma hesabı kâr payı %22.0 ve 6 ay vadeli, en az 5000 TL.",
            content_length=60,
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
    # Önceki testlerden arta kalan küresel vektör deposunu sıfırla
    import src.backend.api.routes.search as search_routes
    import src.backend.core.vector_store as vs

    search_routes._STORE = None
    vs._STORE = None
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


class _Bridge:
    """ApiClient GET çağrılarını TestClient'e yönlendirir."""

    def __init__(self, test_client: TestClient) -> None:
        """Hedef TestClient'i saklar."""
        self.test_client = test_client

    def get(self, url: str, params=None, timeout=10):
        """GET isteğini TestClient üzerinden yapar."""
        path = url.replace("http://localhost:8000", "")
        return self.test_client.get(path, params=params)


def test_end_to_end_flow(e2e_client):
    """Kampanya indeksleme, arama, karşılaştırma ve chatbot akışı uçtan uca çalışır."""
    client = ApiClient(base_url="http://localhost:8000")
    client._get = lambda path, params=None: _Bridge(e2e_client).get(
        "http://localhost:8000" + path, params
    ).json()

    # 1) Vektör arama indeksleme (POST uç noktası)
    idx = e2e_client.post("/api/search/index").json()
    assert idx["indexed"] >= 1

    # 2) Benzerlik araması
    search = client._get("/api/search", {"query": "kâr payı vade", "top_k": 1})
    assert search[0]["id"] == "campaign-1"

    # 3) Karşılaştırma
    compare = client.compare(term_months=6)
    assert compare[0]["profit_share_rate"] == 22.0
    assert compare[0]["min_amount"] == 5000.0

    # 4) Chatbot (LLM çevrimdışı olsa da bağlam/source akışı zarifçe döner)
    chat_resp = e2e_client.get("/api/chat", params={"question": "en yüksek oran?", "top_k": 1})
    assert chat_resp.status_code == 200
    assert chat_resp.json()["sources"][0]["id"] == "campaign-1"
