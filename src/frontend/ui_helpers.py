"""Frontend arayüz yardımcı saf-Python mantığı (streamlit bağımsız)."""

from typing import Any


def filter_by_bank(results: list[dict], selected_bank: str) -> list[dict]:
    """Sonuçları seçili bankaya göre süzer."""
    if selected_bank == "Tümü":
        return results
    return [r for r in results if r.get("bank_name") == selected_bank]
