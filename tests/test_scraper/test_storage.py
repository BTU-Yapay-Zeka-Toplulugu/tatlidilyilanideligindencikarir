"""storage modülü birim testleri."""

import json
import csv
import tempfile
from pathlib import Path

from src.scraper.models import CampaignData, CampaignPage
from src.scraper.storage import (
    save_campaign_data_json,
    save_campaign_data_csv,
    save_discovered_pages_json,
    load_campaign_data_json,
)


def _create_sample_data() -> list[CampaignData]:
    """Test için örnek CampaignData listesi oluşturur."""
    return [
        CampaignData(
            bank_id=1,
            bank_name="TEST BANKA 1",
            source_url="https://test1.com/kampanya",
            page_title="Test Kampanya 1",
            raw_text="Aylık %1,29 kâr payı oranıyla konut finansmanı fırsatı!",
        ),
        CampaignData(
            bank_id=2,
            bank_name="TEST BANKA 2",
            source_url="https://test2.com/kampanya",
            page_title="Test Kampanya 2",
            raw_text="36 ay vade ile 500.000 TL'ye kadar finansman imkanı.",
        ),
    ]


def _create_sample_pages() -> list[CampaignPage]:
    """Test için örnek CampaignPage listesi oluşturur."""
    return [
        CampaignPage(
            bank_id=1,
            bank_name="TEST BANKA",
            page_url="https://test.com/kampanyalar",
            page_title="Kampanyalar",
        ),
    ]


class TestSaveJson:
    """JSON kaydetme fonksiyonu testleri."""

    def test_save_and_load_json(self) -> None:
        """JSON olarak kaydedilip geri yüklenebilir."""
        data = _create_sample_data()
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = save_campaign_data_json(
                data, output_dir=Path(tmpdir), filename="test.json"
            )
            assert filepath.exists()

            loaded = load_campaign_data_json(filepath)
            assert len(loaded) == 2
            assert loaded[0]["bank_name"] == "TEST BANKA 1"
            assert loaded[1]["raw_text"].startswith("36 ay")

    def test_json_encoding_turkish(self) -> None:
        """Türkçe karakterler JSON'da düzgün saklanır."""
        data = _create_sample_data()
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = save_campaign_data_json(
                data, output_dir=Path(tmpdir), filename="test_tr.json"
            )
            content = filepath.read_text(encoding="utf-8")
            assert "kâr payı" in content
            assert "\\u" not in content  # ensure_ascii=False


class TestSaveCsv:
    """CSV kaydetme fonksiyonu testleri."""

    def test_save_csv(self) -> None:
        """CSV olarak doğru kaydeder."""
        data = _create_sample_data()
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = save_campaign_data_csv(
                data, output_dir=Path(tmpdir), filename="test.csv"
            )
            assert filepath.exists()

            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            assert len(rows) == 2
            assert rows[0]["bank_name"] == "TEST BANKA 1"

    def test_empty_data_csv(self) -> None:
        """Boş veri listesinde dosya oluşturur ama boş bırakır."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = save_campaign_data_csv(
                [], output_dir=Path(tmpdir), filename="empty.csv"
            )
            assert filepath.exists()


class TestSaveDiscoveredPages:
    """Keşfedilen sayfa kaydetme fonksiyonu testleri."""

    def test_save_pages_json(self) -> None:
        """Keşfedilen sayfaları JSON olarak kaydeder."""
        pages = _create_sample_pages()
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = save_discovered_pages_json(
                pages, output_dir=Path(tmpdir), filename="pages.json"
            )
            assert filepath.exists()

            with open(filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            assert len(loaded) == 1
            assert loaded[0]["page_url"] == "https://test.com/kampanyalar"


class TestLoadJson:
    """JSON yükleme fonksiyonu testleri."""

    def test_missing_file(self) -> None:
        """Dosya yoksa boş liste döner."""
        result = load_campaign_data_json(Path("/nonexistent/file.json"))
        assert result == []
