"""Recursive PDF crawler modülü için birim testleri.

Ağ erişimi gerektirmeyen testler: Türkçe casefold, PDF URL tespiti,
recursive link toplama ve kampanya filtresi doğrulanır.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.scraper.models import BankInfo, CampaignPage  # noqa: E402
from src.scraper.pdf_crawler import (  # noqa: E402
    CAMPAIGN_PDF_KEYWORDS,
    IRRELEVANT_PDF_KEYWORDS,
    RecursivePdfCrawler,
    _is_pdf_url,
    _is_same_domain,
    _tr_fold,
    is_campaign_pdf,
)


def test_tr_fold_turkish_specific():
    """Türkçe büyük-İ doğru çözülmeli (casefold uyumu)."""
    assert _tr_fold("KÂR PAYI İNDİRİM") == "kâr payı indirim"
    assert "indirim" in _tr_fold("FİNANSMAN İNDİRİMİ")
    assert _tr_fold("İHTİYAÇ FİNANSMANI") == "ihtiyaç finansmanı"


def test_is_pdf_url_variants():
    assert _is_pdf_url("https://bank.com/brosur.pdf")
    assert _is_pdf_url("https://bank.com/dir/KAMPANYA.PDF")
    assert not _is_pdf_url("https://bank.com/kampanya")
    assert not _is_pdf_url("https://bank.com/page.html")


def test_is_same_domain_ignores_www():
    base = "https://www.kuveytturk.com.tr/"
    assert _is_same_domain(base, "https://kuveytturk.com.tr/kampanya.pdf")
    assert not _is_same_domain(base, "https://other.com/x.pdf")


def test_is_campaign_pdf_relevant_keywords():
    """Kampanya anahtar kelimeleri içeren metin 'ilgili' döndürmeli."""
    text = (
        "Taşıt Finansmanı Kâr Payı Oranları\n"
        "Vade 36 ay, kâr oranı %2,05 olarak uygulanır.\n"
        "Kampanya kapsamında finansman avantajı sunulur."
    )
    from src.scraper import pdf_crawler

    with patch.object(pdf_crawler, "_extract_first_pages_text",
                      return_value=(text, False)):
        relevant, reason = is_campaign_pdf(b"dummy")
    assert relevant is True
    assert reason.startswith("campaign_hits:")


def test_is_campaign_pdf_irrelevant():
    """Aydınlatma/sözleşme metni kampanya kelimesi yoksa elenmeli."""
    text = (
        "Kişisel Verilerin Korunması Hakkında Aydınlatma Metni\n"
        "KVKK kapsamında bilgilendirme formu. Gizlilik ilkeleri."
    )
    from src.scraper import pdf_crawler

    with patch.object(pdf_crawler, "_extract_first_pages_text",
                      return_value=(text, False)):
        relevant, reason = is_campaign_pdf(b"dummy")
    assert relevant is False
    assert "irrelevant" in reason


def test_recursive_crawler_collects_pdf_links():
    """Recursive crawler aynı domain'deki PDF bağlarını havuzda toplamalı."""
    bank = BankInfo(id=1, name="TEST BANK", url="https://test.com/")

    html_page1 = """
    <html><body>
      <a href="/kampanya">Kampanya</a>
      <a href="/brosur.pdf">Brosur PDF</a>
      <a href="https://external.com/x.pdf">External PDF</a>
      <a href="/sayfa2">Sayfa 2</a>
    </body></html>
    """
    html_page2 = """
    <html><body>
      <a href="/derin/brosur2.pdf">PDF 2</a>
      <a href="https://test.com/loop">Loop</a>
    </body></html>
    """

    crawler = RecursivePdfCrawler(bank, max_depth=2, max_pages=10)

    def fake_get(url, timeout=None, stream=False):
        resp = MagicMock()
        resp.headers = {"Content-Type": "text/html"}
        resp.url = url
        if url.rstrip("/") == "https://test.com":
            resp.text = html_page1
        elif url.rstrip("/") == "https://test.com/sayfa2":
            resp.text = html_page2
        else:
            resp.text = "<html></html>"
        return resp

    with patch.object(crawler, "_get", side_effect=fake_get):
        candidates = crawler.crawl(["https://test.com/"])

    pdf_urls = {c.pdf_url for c in candidates}
    assert "https://test.com/brosur.pdf" in pdf_urls
    assert "https://test.com/derin/brosur2.pdf" in pdf_urls
    # External domain dışı kalmalı
    assert "https://external.com/x.pdf" not in pdf_urls
    # Tekrar (loop) sayfası sonsuz döngüye yol açmamalı
    assert len(candidates) >= 2


def test_extract_pdfs_from_urls_filters_irrelevant():
    """Keşfedilen PDF URL'lerinden ilgisiz olanlar (ücret tablosu vb.)
    filtrelenip yalnızca kampanya içerikliler işlenmeli."""
    from src.scraper.pdf_crawler import (
        PdfCandidate,
        extract_pdfs_from_urls,
    )

    bank = BankInfo(id=5, name="BANK5", url="https://b5.com/")

    # İlgisiz PDF (ücret tablosu) — indirme başarısız sayılır ki filtre
    # zaten metin üzerinden çalışır; burada download'ı mock'layıp filtreyi
    # doğruluyoruz.
    from src.scraper import pdf_crawler

    def fake_download(cand):
        # İçerik "ücret tablosu" → kampanya kelimesi yok → elenir
        return b"%PDF-1.4\n Urun ve Hizmet Ucret Tablosu \n KVKK aydinlatma"

    with patch.object(pdf_crawler, "download_pdf", side_effect=fake_download):
        data = extract_pdfs_from_urls(
            bank, ["https://b5.com/ucret.pdf"]
        )
    assert data == []
