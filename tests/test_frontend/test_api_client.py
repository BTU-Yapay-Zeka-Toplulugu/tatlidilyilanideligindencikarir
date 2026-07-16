"""Frontend API istemcisi birim testi (HTTP mock'lanır)."""

from src.frontend.api_client import ApiClient


class _FakeRequests:
    """requests.get çağrılarını yakalayıp sabit JSON döndüren sahte nesne."""

    def __init__(self, payload: object) -> None:
        """Döndürülecek sabit yükü saklar."""
        self.payload = payload
        self.last_call = None

    def get(self, url: str, params=None, timeout=10):
        """GET çağrısını kaydeder ve sahte yanıt döner."""

        class _Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        resp = _Resp()
        resp._data = self.payload
        self.last_call = (url, params)
        return resp


def test_get_banks(monkeypatch):
    """ApiClient.get_banks backend'den banka listesini çeker."""
    fake = _FakeRequests([{"id": 1, "name": "Bank A", "url": "https://a.com"}])
    client = ApiClient()
    monkeypatch.setattr(client, "_get", lambda path, params=None: fake.get(fake.payload, params).json())
    banks = client.get_banks()
    assert banks[0]["name"] == "Bank A"


def test_compare_filters_params(monkeypatch):
    """ApiClient.compare doğru sorgu parametreleriyle çağrılır."""
    captured = {}

    def fake_get(path, params=None):
        captured["path"] = path
        captured["params"] = params
        return [{"bank_name": "Bank A", "profit_share_rate": 20.0}]

    client = ApiClient()
    monkeypatch.setattr(client, "_get", fake_get)
    result = client.compare(term_months=3, amount=1000)
    assert captured["path"] == "/api/compare"
    assert captured["params"]["term_months"] == 3
    assert result[0]["profit_share_rate"] == 20.0


def test_chat_returns_answer(monkeypatch):
    """ApiClient.chat chatbot yanıtını döner."""
    def fake_get(path, params=None):
        return {"answer": "Merhaba", "sources": []}

    client = ApiClient()
    monkeypatch.setattr(client, "_get", fake_get)
    resp = client.chat("selam")
    assert resp["answer"] == "Merhaba"
