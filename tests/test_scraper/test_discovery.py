"""discovery modülü birim testleri."""

from bs4 import BeautifulSoup

from src.scraper.discovery import (
    _is_same_domain,
    _url_contains_campaign_keyword,
    _link_text_contains_campaign_keyword,
    discover_links_from_page,
)
from src.scraper.models import BankInfo


SAMPLE_BANK = BankInfo(id=1, name="TEST BANKA", url="https://www.testbanka.com.tr")

SAMPLE_HTML = """
<html>
<body>
    <a href="/kampanyalar">Kampanyalar</a>
    <a href="/bireysel/finansman">Bireysel Finansman</a>
    <a href="/hakkimizda">Hakkımızda</a>
    <a href="/iletisim">İletişim</a>
    <a href="https://www.otherdomain.com/kampanya">Dış Link</a>
    <a href="/urunler/kobi">KOBİ Ürünleri</a>
    <a href="/oranlar">Güncel Oranlar</a>
</body>
</html>
"""


class TestIsSameDomain:
    """_is_same_domain fonksiyonu testleri."""

    def test_same_domain(self) -> None:
        """Aynı domain'ler True döner."""
        assert _is_same_domain(
            "https://www.test.com.tr", "https://www.test.com.tr/page"
        )

    def test_www_variant(self) -> None:
        """www olan/olmayan varyantlar aynı kabul edilir."""
        assert _is_same_domain(
            "https://www.test.com.tr", "https://test.com.tr/page"
        )

    def test_different_domain(self) -> None:
        """Farklı domain'ler False döner."""
        assert not _is_same_domain(
            "https://www.test.com.tr", "https://www.other.com.tr/page"
        )


class TestUrlContainsCampaignKeyword:
    """_url_contains_campaign_keyword fonksiyonu testleri."""

    def test_kampanya_in_url(self) -> None:
        """URL'de 'kampanya' varsa True döner."""
        assert _url_contains_campaign_keyword("https://bank.com/kampanyalar")

    def test_no_keyword(self) -> None:
        """Anahtar kelime yoksa False döner."""
        assert not _url_contains_campaign_keyword("https://bank.com/hakkimizda")


class TestLinkTextContainsCampaignKeyword:
    """_link_text_contains_campaign_keyword fonksiyonu testleri."""

    def test_kampanya_in_text(self) -> None:
        """Link metninde 'kampanya' varsa True döner."""
        assert _link_text_contains_campaign_keyword("Güncel Kampanyalar")

    def test_oran_in_text(self) -> None:
        """Link metninde 'oran' varsa True döner."""
        assert _link_text_contains_campaign_keyword("Güncel Oranlar")

    def test_no_keyword_in_text(self) -> None:
        """Anahtar kelime yoksa False döner."""
        assert not _link_text_contains_campaign_keyword("Hakkımızda")


class TestDiscoverLinksFromPage:
    """discover_links_from_page fonksiyonu testleri."""

    def test_finds_campaign_links(self) -> None:
        """Kampanya linklerini doğru bulur."""
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        pages = discover_links_from_page(SAMPLE_BANK, soup)

        urls = [p.page_url for p in pages]
        # Kampanya/finansman/ürün linklerini bulmalı
        assert any("kampanya" in u for u in urls)
        assert any("finansman" in u for u in urls)
        assert any("urunler" in u for u in urls)

    def test_excludes_non_campaign_links(self) -> None:
        """Kampanya olmayan linkleri hariç tutar."""
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        pages = discover_links_from_page(SAMPLE_BANK, soup)

        urls = [p.page_url for p in pages]
        assert not any("hakkimizda" in u for u in urls)
        assert not any("iletisim" in u for u in urls)

    def test_excludes_external_links(self) -> None:
        """Farklı domain'e ait linkleri hariç tutar."""
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        pages = discover_links_from_page(SAMPLE_BANK, soup)

        urls = [p.page_url for p in pages]
        assert not any("otherdomain" in u for u in urls)

    def test_correct_bank_metadata(self) -> None:
        """Keşfedilen sayfalarda doğru banka bilgisi olur."""
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        pages = discover_links_from_page(SAMPLE_BANK, soup)

        for page in pages:
            assert page.bank_id == 1
            assert page.bank_name == "TEST BANKA"
