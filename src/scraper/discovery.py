"""Banka sitelerinden kampanya/ürün sayfası URL'lerini keşfeden modül."""

import re
import logging
from urllib.parse import urljoin, urlparse
from typing import Optional

from bs4 import BeautifulSoup

from src.scraper.config import CAMPAIGN_KEYWORDS, MAX_PAGES_PER_BANK
from src.scraper.http_client import fetch_and_parse, fetch_page
from src.scraper.models import BankInfo, CampaignPage

logger = logging.getLogger(__name__)

# robots.txt / sitemap içindeki URL deseni
SITEMAP_URL_PATTERN = re.compile(r"<loc>(https?://[^<]+)</loc>")

# HTML olmayan (parse edilemeyen) ikili dosya uzantıları — keşifte atlanır.
BINARY_EXTENSIONS = (
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".rar", ".7z", ".jpg", ".jpeg", ".png", ".gif",
    ".svg", ".webp", ".mp4", ".mp3", ".exe", ".apk",
)


def _is_binary_url(url: str) -> bool:
    """URL bir ikili/HTML-olmayan dosyaya mı işaret ediyor kontrol eder."""
    path = urlparse(url).path.lower()
    return path.endswith(BINARY_EXTENSIONS)


def _is_same_domain(base_url: str, candidate_url: str) -> bool:
    """İki URL'nin aynı domain'e ait olup olmadığını kontrol eder."""
    base_domain = urlparse(base_url).netloc.replace("www.", "")
    candidate_domain = urlparse(candidate_url).netloc.replace("www.", "")
    return base_domain == candidate_domain


def _url_contains_campaign_keyword(url: str) -> bool:
    """URL yolunda kampanya anahtar kelimesi olup olmadığını kontrol eder."""
    path = urlparse(url).path.lower()
    return any(keyword in path for keyword in CAMPAIGN_KEYWORDS)


def _link_text_contains_campaign_keyword(text: str) -> bool:
    """Link metninde kampanya anahtar kelimesi olup olmadığını kontrol eder."""
    text_lower = text.lower()
    # Türkçe karakter varyasyonları dahil
    turkish_keywords = CAMPAIGN_KEYWORDS + [
        "kampanya", "fırsat", "ürün", "oran",
        "hesap", "kredi", "finansman",
    ]
    return any(kw in text_lower for kw in turkish_keywords)


# Kampanya sayfası bulunamayan (yeni/minimal siteli) bankalar için
# kurumsal/ürün bilgi sayfası anahtar kelimeleri (fallback keşif).
INSTITUTIONAL_KEYWORDS = [
    "hakkimizda",
    "hakkinda",
    "katilim-bankaciligi",
    "katilim-bankacilik",
    "urun",
    "urunler",
    "hizmet",
    "ucret",
    "ucretlendirme",
    "sozlesme",
    "bilgilendirme",
]


def _url_contains_institutional_keyword(url: str) -> bool:
    """URL yolunda kurumsal/ürün bilgi anahtar kelimesi olup olmadığını kontrol eder."""
    path = urlparse(url).path.lower()
    return any(keyword in path for keyword in INSTITUTIONAL_KEYWORDS)


def discover_institutional_pages(
    bank: BankInfo, soup: BeautifulSoup
) -> list[CampaignPage]:
    """Kampanya sayfası bulunamadığında kurumsal/ürün bilgi sayfalarını keşfeder.

    Yeni lisanslı veya minimal içerikli bankaların (ör. ADİL Katılım) sitesinde
    kampanya sayfası olmayabilir; bu durumda her bankanın sistemde temsil
    edilmesi için Hakkımızda/Katılım Bankacılığı/Ürün-Hizmet Ücretleri gibi
    kurumsal sayfalar toplanır.
    """
    found_pages: list[CampaignPage] = []
    seen_urls: set[str] = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(bank.url, href).rstrip("/")
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)
        if not _is_same_domain(bank.url, full_url):
            continue
        if _is_binary_url(full_url):
            continue
        parsed = urlparse(full_url)
        if not parsed.path or parsed.path == "/":
            continue
        if _url_contains_institutional_keyword(full_url):
            found_pages.append(
                CampaignPage(
                    bank_id=bank.id,
                    bank_name=bank.name,
                    page_url=full_url,
                    page_title=a_tag.get_text(strip=True) or None,
                )
            )

    return found_pages


def discover_links_from_page(
    bank: BankInfo, soup: BeautifulSoup
) -> list[CampaignPage]:
    """Bir sayfadaki tüm linkleri tarayıp kampanya sayfalarını filtreler."""
    found_pages: list[CampaignPage] = []
    seen_urls: set[str] = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(bank.url, href).rstrip("/")

        # Aynı URL'yi tekrar ekleme
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        # Farklı domain'e ait linkleri atla
        if not _is_same_domain(bank.url, full_url):
            continue

        # İkili (PDF/görsel vb.) dosyaları atla — HTML olarak parse edilemez.
        if _is_binary_url(full_url):
            continue

        # Fragment ve query-only linkleri atla
        parsed = urlparse(full_url)
        if not parsed.path or parsed.path == "/":
            continue

        # URL veya link metninde kampanya anahtar kelimesi aranır
        link_text = a_tag.get_text(strip=True)
        if _url_contains_campaign_keyword(full_url) or _link_text_contains_campaign_keyword(link_text):
            page = CampaignPage(
                bank_id=bank.id,
                bank_name=bank.name,
                page_url=full_url,
                page_title=link_text or None,
            )
            found_pages.append(page)

    return found_pages


def try_sitemap(bank: BankInfo) -> list[CampaignPage]:
    """Bankanın sitemap.xml dosyasından kampanya URL'lerini çıkarmayı dener."""
    sitemap_urls = [
        f"{bank.url}/sitemap.xml",
        f"{bank.url}/sitemap_index.xml",
    ]

    found_pages: list[CampaignPage] = []

    for sitemap_url in sitemap_urls:
        xml_content = fetch_page(sitemap_url, timeout=15)
        if xml_content is None:
            continue

        urls = SITEMAP_URL_PATTERN.findall(xml_content)
        for url in urls:
            if _url_contains_campaign_keyword(url):
                page = CampaignPage(
                    bank_id=bank.id,
                    bank_name=bank.name,
                    page_url=url.rstrip("/"),
                    page_title=None,
                )
                found_pages.append(page)

        if found_pages:
            logger.info(
                "Sitemap'ten %d kampanya URL'si bulundu: %s",
                len(found_pages), bank.name,
            )
            break

    return found_pages


def discover_campaign_pages(bank: BankInfo) -> list[CampaignPage]:
    """Bir banka için tüm kampanya sayfalarını keşfeder (sitemap + ana sayfa taraması)."""
    all_pages: list[CampaignPage] = []
    seen_urls: set[str] = set()

    # 1. Sitemap denemesi
    sitemap_pages = try_sitemap(bank)
    for page in sitemap_pages:
        if page.page_url not in seen_urls:
            seen_urls.add(page.page_url)
            all_pages.append(page)

    # 2. Ana sayfa link taraması
    soup = fetch_and_parse(bank.url)
    if soup:
        link_pages = discover_links_from_page(bank, soup)
        for page in link_pages:
            if page.page_url not in seen_urls:
                seen_urls.add(page.page_url)
                all_pages.append(page)

        # 3. Fallback: hiç kampanya sayfası bulunamadıysa kurumsal/ürün
        # bilgi sayfalarını keşfet (her bankanın sistemde temsil edilmesi için).
        if not all_pages:
            institutional = discover_institutional_pages(bank, soup)
            for page in institutional:
                if page.page_url not in seen_urls:
                    seen_urls.add(page.page_url)
                    all_pages.append(page)
            if institutional:
                logger.info(
                    "%s: kampanya sayfası yok; %d kurumsal sayfa (fallback) bulundu.",
                    bank.name, len(institutional),
                )

    logger.info(
        "%s: toplam %d kampanya sayfası keşfedildi. Sınır: %d.",
        bank.name, len(all_pages), MAX_PAGES_PER_BANK
    )
    return all_pages[:MAX_PAGES_PER_BANK]
