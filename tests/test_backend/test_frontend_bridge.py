"""Frontend (React/Vite) köprü uç noktaları için entegrasyon testleri."""

from src.database.models import Bank, Campaign


class _FakeChatbot:
    """ChatbotService yerine geçen hafif sahte (LLM yüklemez)."""

    def answer(self, question: str, top_k: int = 3) -> dict:
        return {
            "answer": f"Yanıt: {question}",
            "sources": [
                {
                    "id": "campaign-1",
                    "metadata": {
                        "bank_name": "Test Bankası",
                        "title": "Test Ürünü",
                        "source_url": "https://example.com",
                    },
                    "score": 0.9,
                }
            ],
        }


def _seed(client, test_db):
    """Test için bellek içi veritabanına banka ve kampanya ekler."""
    bank = Bank(id=1, name="Test Bankası", url="https://test.com")
    test_db.add(bank)
    test_db.add(
        Campaign(
            id=1,
            bank_id=1,
            source_url="https://test.com/kampanya",
            page_title="Test Ürünü",
            raw_text="Katılma hesabı %5 kâr payı oranı ile 12 ay vade.",
            content_length=50,
        )
    )
    test_db.commit()


def test_finansman_bankalar(client, test_db):
    """Banka listesi uç noktası doğru alan adlarıyla döner."""
    _seed(client, test_db)
    res = client.get("/finansman/bankalar")
    assert res.status_code == 200
    body = res.json()
    assert body[0]["id"] == "1"
    assert body[0]["ad"] == "Test Bankası"
    assert "logo" in body[0]


def test_finansman_ozet(client, test_db):
    """Özet uç noktası FinansmanKalemi şeklinde döner."""
    _seed(client, test_db)
    res = client.get("/finansman/ozet")
    assert res.status_code == 200
    item = res.json()[0]
    for field in ("id", "bankaAdi", "urunAdi", "tutar", "karOrani", "vade", "tarih"):
        assert field in item
    assert item["bankaAdi"] == "Test Bankası"


def test_finansman_karsilastirma_gruplama(client, test_db):
    """Karşılaştırma uç noktası bankaya göre gruplar."""
    _seed(client, test_db)
    res = client.get("/finansman/karsilastirma")
    assert res.status_code == 200
    body = res.json()
    assert body[0]["bankaId"] == "1"
    assert body[0]["bankaAdi"] == "Test Bankası"
    assert body[0]["urunler"][0]["urunAdi"] == "Test Ürünü"


def test_chat_mesaj_ve_gecmis(client, test_db):
    """Chatbot REST akışı (mesaj → geçmiş → temizle) çalışır."""
    _seed(client, test_db)
    client.app.state.chatbot = _FakeChatbot()

    res = client.post("/chat/mesaj", json={"mesaj": "Merhaba", "oturumId": "oturum-x"})
    assert res.status_code == 200
    body = res.json()
    assert body["oturumId"] == "oturum-x"
    assert body["mesaj"]["rol"] == "assistant"
    assert body["mesaj"]["atiflar"][0]["bankaAdi"] == "Test Bankası"

    res = client.get("/chat/gecmis", params={"oturumId": "oturum-x"})
    assert res.status_code == 200
    assert len(res.json()) >= 2

    res = client.post("/chat/temizle", json={"oturumId": "oturum-x"})
    assert res.status_code == 200
    res = client.get("/chat/gecmis", params={"oturumId": "oturum-x"})
    assert res.json() == []
