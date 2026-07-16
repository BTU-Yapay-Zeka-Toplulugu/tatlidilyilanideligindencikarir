"""Frontend arayüz yardımcı mantığı (filtre) birim testi."""

from src.frontend.ui_helpers import filter_by_bank


def test_filter_by_bank_all_returns_all():
    """'Tümü' seçildiğinde tüm sonuçlar döner."""
    data = [{"bank_name": "A"}, {"bank_name": "B"}]
    assert filter_by_bank(data, "Tümü") == data


def test_filter_by_bank_specific():
    """Belirli banka seçildiğinde yalnızca o banka filtrelenir."""
    data = [{"bank_name": "A"}, {"bank_name": "B"}, {"bank_name": "A"}]
    result = filter_by_bank(data, "B")
    assert len(result) == 1
    assert result[0]["bank_name"] == "B"
