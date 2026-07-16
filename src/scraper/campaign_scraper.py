"""Kampanya sayfalarından ham metin içeriğini çıkaran modül."""

import logging
import time
from typing import Optional

from bs4 import BeautifulSoup, Tag

from src.scraper.config import MIN_CONTENT_LENGTH, REQUEST_DELAY
from src.scraper.http_client import fetch_and_parse
from src.scraper.models import BankInfo, CampaignData, CampaignPage

logger = logging.getLogger(__name__)

# İçerik çıkarımında atlanacak HTML etiketleri
SKIP_TAGS = {"script", "style", "nav", "footer", "header", "noscript", "svg", "iframe"}

# İçerik çıkarımı için öncelikli CSS seçiciler (sırayla denenir)
CONTENT_SELECTORS = [
    "article",
    "main",
    ".campaign-detail",
    ".kampanya-detay",
    ".content",
    ".page-content",
    "#content",
    "#main-content",
    ".entry-content",
    "[role='main']",
]


def _clean_text(text: str) -> str:
    """HTML'den çıkarılan ham metni temizler (fazla boşluklar, boş satırlar)."""
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(stripped)
    return "\n".join(cleaned_lines)


def _extract_text_from_element(element: Tag) -> str:
    """Bir HTML elementinden metin çıkarır, gereksiz etiketleri atlayarak."""
    for tag in element.find_all(SKIP_TAGS):
        tag.decompose()
    return _clean_text(element.get_text(separator="\n"))


def extract_page_title(soup: BeautifulSoup) -> str:
    """Sayfanın başlığını çıkarır (title etiketi veya h1)."""
    # Önce <title> dene
    if soup.title and soup.title.string:
        return soup.title.string.strip()

    # Sonra <h1> dene
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    return "Başlık Bulunamadı"


def extract_main_content(soup: BeautifulSoup) -> str:
    """Sayfadan ana içerik metnini çıkarır, öncelikli seçicileri sırayla dener."""
    # Öncelikli CSS seçicileri ile hedef alanı bul
    for selector in CONTENT_SELECTORS:
        element = soup.select_one(selector)
        if element:
            text = _extract_text_from_element(element)
            if len(text) >= MIN_CONTENT_LENGTH:
                return text

    # Hiçbir seçici çalışmadıysa body'den çıkar
    body = soup.find("body")
    if body:
        return _extract_text_from_element(body)

    return ""


def scrape_campaign_page(
    bank: BankInfo, campaign_page: CampaignPage
) -> Optional[CampaignData]:
    """Tek bir kampanya sayfasından ham metin verisini çıkarır."""
    soup = fetch_and_parse(campaign_page.page_url)
    if soup is None:
        logger.warning(
            "Sayfa çekilemedi: %s (%s)", campaign_page.page_url, bank.name
        )
        return None

    title = extract_page_title(soup)
    content = extract_main_content(soup)

    if len(content) < MIN_CONTENT_LENGTH:
        logger.warning(
            "Yetersiz içerik (%d karakter): %s",
            len(content), campaign_page.page_url,
        )
        return None

    return CampaignData(
        bank_id=bank.id,
        bank_name=bank.name,
        source_url=campaign_page.page_url,
        page_title=title,
        raw_text=content,
    )


def scrape_all_campaign_pages(
    bank: BankInfo, campaign_pages: list[CampaignPage]
) -> list[CampaignData]:
    """Bir bankaya ait tüm kampanya sayfalarını tarar ve metin çıkarır."""
    results: list[CampaignData] = []

    for i, page in enumerate(campaign_pages, 1):
        logger.info(
            "[%d/%d] Taranıyor: %s", i, len(campaign_pages), page.page_url
        )

        data = scrape_campaign_page(bank, page)
        if data:
            results.append(data)

        # Siteye yük bindirmemek için bekleme
        if i < len(campaign_pages):
            time.sleep(REQUEST_DELAY)

    logger.info(
        "%s: %d/%d sayfadan içerik çıkarıldı.",
        bank.name, len(results), len(campaign_pages),
    )
    return results
