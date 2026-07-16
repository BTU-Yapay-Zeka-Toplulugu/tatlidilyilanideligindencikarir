"""http_client modülü birim testleri."""

from unittest.mock import patch, MagicMock

import requests
from bs4 import BeautifulSoup

from src.scraper.http_client import fetch_page, parse_html, fetch_and_parse


SAMPLE_HTML = "<html><head><title>Test</title></head><body><p>Merhaba</p></body></html>"


class TestFetchPage:
    """fetch_page fonksiyonu testleri."""

    @patch("src.scraper.http_client.requests.get")
    def test_successful_fetch(self, mock_get: MagicMock) -> None:
        """Başarılı HTTP isteğinde HTML döner."""
        mock_response = MagicMock()
        mock_response.text = SAMPLE_HTML
        mock_response.apparent_encoding = "utf-8"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch_page("https://example.com")
        assert result == SAMPLE_HTML
        mock_get.assert_called_once()

    @patch("src.scraper.http_client.requests.get")
    def test_timeout_retry(self, mock_get: MagicMock) -> None:
        """Zaman aşımında retry yapıp sonunda None döner."""
        mock_get.side_effect = requests.exceptions.Timeout()

        result = fetch_page("https://example.com")
        assert result is None
        assert mock_get.call_count == 3  # MAX_RETRIES = 3

    @patch("src.scraper.http_client.requests.get")
    def test_http_error(self, mock_get: MagicMock) -> None:
        """HTTP hatasında retry yapıp sonunda None döner."""
        mock_get.side_effect = requests.exceptions.HTTPError("404")

        result = fetch_page("https://example.com")
        assert result is None

    @patch("src.scraper.http_client.requests.get")
    def test_connection_error(self, mock_get: MagicMock) -> None:
        """Bağlantı hatasında retry yapıp sonunda None döner."""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        result = fetch_page("https://example.com")
        assert result is None


class TestParseHtml:
    """parse_html fonksiyonu testleri."""

    def test_parse_valid_html(self) -> None:
        """Geçerli HTML'i doğru parse eder."""
        soup = parse_html(SAMPLE_HTML)
        assert isinstance(soup, BeautifulSoup)
        assert soup.title.string == "Test"
        assert soup.find("p").string == "Merhaba"


class TestFetchAndParse:
    """fetch_and_parse fonksiyonu testleri."""

    @patch("src.scraper.http_client.fetch_page")
    def test_successful_fetch_and_parse(self, mock_fetch: MagicMock) -> None:
        """Başarılı çekme ve parse işlemi."""
        mock_fetch.return_value = SAMPLE_HTML
        result = fetch_and_parse("https://example.com")
        assert result is not None
        assert result.title.string == "Test"

    @patch("src.scraper.http_client.fetch_page")
    def test_fetch_failure_returns_none(self, mock_fetch: MagicMock) -> None:
        """Çekme başarısız olduğunda None döner."""
        mock_fetch.return_value = None
        result = fetch_and_parse("https://example.com")
        assert result is None
