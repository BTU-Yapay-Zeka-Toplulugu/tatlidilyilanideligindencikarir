"""Vektör deposu, karşılaştırma ve arama uç noktaları için testler."""

from fastapi.testclient import TestClient

from src.backend.core.embeddings import LocalLexicalEmbedder
from src.backend.core.vector_store import InMemoryVectorStore, VectorStoreFactory
from src.backend.main import app


def test_inmemory_vector_store_similarity():
    """Vektör deposu sorguya en benzer metni en üstte döner."""
    store = InMemoryVectorStore(embedder=LocalLexicalEmbedder())
    store.add(
        ["a", "b"],
        ["katılma hesabı kâr payı vade mevduat", "kredi kartı aidat puan"],
        [{"t": 1}, {"t": 2}],
    )
    results = store.query("katılma hesabı kâr payı", top_k=1)
    assert results[0]["id"] == "a"


def test_vector_store_factory_returns_inmemory():
    """Fabrika varsayılan olarak bellek içi vektör deposu döner."""
    store = VectorStoreFactory.create()
    assert isinstance(store, InMemoryVectorStore)


def test_search_index_and_query(client, test_db):
    """Kampanyalar indekslenir ve benzerlik araması sonuç döner."""
    from src.database.models import Bank, Campaign

    bank = Bank(name="Arama Bank", url="https://arama.com")
    test_db.add(bank)
    test_db.commit()
    test_db.add(
        Campaign(
            bank_id=bank.id,
            source_url="https://arama.com/k",
            page_title="Katılma Hesabı",
            raw_text="katılma hesabı kâr payı vade mevduat avantaj",
            content_length=50,
        )
    )
    test_db.commit()

    idx = client.post("/api/search/index")
    assert idx.status_code == 200
    assert idx.json()["indexed"] == 1

    res = client.get("/api/search", params={"query": "kâr payı vade", "top_k": 3})
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_compare_best_rate(client, test_db):
    """En yüksek orana sahip kampanya best-rate ucundan döner."""
    from src.database.models import Bank, Campaign

    b = Bank(name="Best Bank", url="https://best.com")
    test_db.add(b)
    test_db.commit()
    test_db.add(
        Campaign(
            bank_id=b.id,
            source_url="https://best.com/k",
            page_title="Yüksek Oran",
            raw_text="Katılma hesabı kâr payı %30.0 ve 3 ay vadeli.",
            content_length=50,
        )
    )
    test_db.commit()

    res = client.get("/api/compare/best")
    assert res.status_code == 200
    assert res.json()["profit_share_rate"] == 30.0
