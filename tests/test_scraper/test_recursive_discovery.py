"""Yeni tam dinamik/recursive keşif modülü birim testleri (ADR-012).

Eski statik discovery (sitemap-only, sabit CAMPAIGN_KEYWORDS path) kaldırıldı;
yerine recursive_discovery kullanılır. Bu testler: domain sınırı, derinlik/
sayfa limiti, PDF+HTML ayrımı ve anahtar kelime filtresini doğrular.
"""

from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from src.scraper.models import BankInfo
from src.scraper.recursive_discovery import (
    DISCOVERY_KEYWORDS,
    _is_pdf_url,
    _is_same_domain,
    _keyword_hit,
    _tr_fold,
    RecursiveDiscoverer,
    discover_pages_recursive,
)


SAMPLE_BANK = BankInfo(id=1, name="TEST BANKA", url="https://www.testbanka.com.tr")

SAMPLE_HTML = """
<html><body>
  <a href="/kampanyalar">Kampanyalar</a>
  <a href="/kendim-icin/finansmanlar/arac-finansmanlari">Araç Finansmanları</a>
  <a href="/hakkimizda">Hakkımızda</a>
  <a href="/urun-ve-hizmet-ucretleri.pdf">Ücret Tablosu (PDF)</a>
  <a href="https://www.otherdomain.com/kampanya">Dış Link</a>
  <a href="/iletisim">İletişim</a>
</body></html>
"""


def test_is_same_domain_www_variant():
    assert _is_same_domain("https://www.test.com.tr", "https://test.com.tr/x")
    assert not _is_same_domain("https://www.test.com.tr", "https://other.com/x")


def test_is_pdf_url():
    assert _is_pdf_url("https://x.com/a/brosur.pdf")
    assert not _is_pdf_url("https://x.com/kampanyalar")


def test_tr_fold_turkish():
    assert _tr_fold("KÂR PAYI İNDİRİM") == "kâr payı indirim"
    assert "finansman" in _tr_fold("Araç Finansmanları")


def test_keyword_hit_in_url_and_text():
    assert _keyword_hit("/kampanyalar/kendim-icin", "")
    assert _keyword_hit("/x", "Araç Finansmanları")
    assert not _keyword_hit("/hakkimizda", "Hakkımızda")
    assert not _keyword_hit("/iletisim", "İletişim")


def test_discover_records_html_and_pdf():
    """Recursive keşif HTML kampanya sayfalarını ve PDF'leri ayırır bulmalı."""
    bank = SAMPLE_BANK
    disc = RecursiveDiscoverer(bank, max_depth=1, max_pages=5, request_delay=0)

    def fake_get(url):
        resp = MagicMock()
        resp.headers = {"Content-Type": "text/html"}
        resp.url = url
        resp.text = SAMPLE_HTML
        return resp

    with patch.object(disc, "_get", side_effect=fake_get):
        result = disc.discover([bank.url])

    html_urls = {p.page_url for p in result.html_pages}
    assert "https://www.testbanka.com.tr/kampanyalar" in html_urls
    assert any("finansman" in u for u in html_urls)
    # PDF ayrı havuzda, HTML listesinde değil
    assert "https://www.testbanka.com.tr/urun-ve-hizmet-ucretleri.pdf" not in html_urls
    assert "https://www.testbanka.com.tr/urun-ve-hizmet-ucretleri.pdf" in result.pdf_urls
    # Dış domain ve alakasız sayfalar hariç
    assert not any("otherdomain" in u for u in html_urls)
    assert not any("hakkimizda" in u for u in html_urls)
    assert not any("iletisim" in u for u in html_urls)


def test_discover_respects_page_limit():
    """max_pages sınırı aşılmamalı (sonsuz crawl engeli)."""
    bank = SAMPLE_BANK
    disc = RecursiveDiscoverer(bank, max_depth=3, max_pages=3, request_delay=0)

    counter = {"n": 0}

    def fake_get(url):
        counter["n"] += 1
        resp = MagicMock()
        resp.headers = {"Content-Type": "text/html"}
        resp.url = url
        resp.text = SAMPLE_HTML
        return resp

    with patch.object(disc, "_get", side_effect=fake_get):
        result = disc.discover([bank.url])

    assert counter["n"] <= 3
    assert result.pages_visited <= 3


def test_discover_no_external_domain():
    """Keşif aynı domain dışına çıkmaz."""
    bank = SAMPLE_BANK
    disc = RecursiveDiscoverer(bank, max_depth=2, max_pages=10, request_delay=0)

    def fake_get(url):
        resp = MagicMock()
        resp.headers = {"Content-Type": "text/html"}
        resp.url = url
        resp.text = SAMPLE_HTML
        return resp

    with patch.object(disc, "_get", side_effect=fake_get):
        result = disc.discover([bank.url])

    for p in result.html_pages:
        assert _is_same_domain(bank.url, p.page_url)
    for u in result.pdf_urls:
        assert _is_same_domain(bank.url, u)


def test_keywords_config_driven():
    """Keşif anahtar kelimeleri config'te tutulmalı (kod gömülü değil)."""
    assert "kampanya" in DISCOVERY_KEYWORDS
    assert "finansman" in DISCOVERY_KEYWORDS
    assert "kâr" in DISCOVERY_KEYWORDS
