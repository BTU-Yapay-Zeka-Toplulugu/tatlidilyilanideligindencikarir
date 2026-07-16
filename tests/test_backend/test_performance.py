"""Backend performans/yanıt süresi kontrol testleri (basit benchmark)."""

import time

from src.database.models import Bank, Campaign


def test_compare_endpoint_latency(client, test_db):
    """Karşılaştırma uç noktası makul sürede (2 sn) yanıt verir."""
    bank = Bank(name="Perf Bank", url="https://perf.com")
    test_db.add(bank)
    test_db.commit()
    for i in range(20):
        test_db.add(
            Campaign(
                bank_id=bank.id,
                source_url=f"https://perf.com/k{i}",
                page_title=f"Kampanya {i}",
                raw_text=f"Katılma hesabı kâr payı %{10 + i}.0 ve 3 ay vadeli.",
                content_length=50,
            )
        )
    test_db.commit()

    start = time.perf_counter()
    response = client.get("/api/compare?term_months=3")
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 2.0
    assert len(response.json()) == 20


def test_search_index_latency(client, test_db):
    """20 kampanyanın indekslenmesi makul sürede (3 sn) tamamlanır."""
    bank = Bank(name="Perf Bank 2", url="https://perf2.com")
    test_db.add(bank)
    test_db.commit()
    for i in range(20):
        test_db.add(
            Campaign(
                bank_id=bank.id,
                source_url=f"https://perf2.com/k{i}",
                page_title=f"Kampanya {i}",
                raw_text=f"katılma hesabı kâr payı vade mevduat {i}",
                content_length=40,
            )
        )
    test_db.commit()

    start = time.perf_counter()
    response = client.post("/api/search/index")
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert response.json()["indexed"] == 20
    assert elapsed < 3.0
