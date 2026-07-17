"""Tam dinamik & recursive kampanya keşfi (HTML + PDF birlikte).

ADR-012: Statik path/liste bağımlılığı KALDIRDI. Tek merkezi fonksiyon
bankanın ana URL'inden BFS ile başlar, sayfadaki TÜM bağları toplar,
anahtar kelime ile filtreler ve hem HTML kampanya sayfalarını hem de
PDF bağlarını (havuz) döndürür.

Güvenlik/performans:
- Her HTTP isteği timeout'lu + retry'li (config.CRAWL_PER_PAGE_TIMEOUT).
- max_depth (derinlik) ve max_pages (sayfa sayısı) KATI limitli.
- Aynı domain dışına çıkılmaz; ziyaret edilen URL'ler set'te tutulur
  (sonsuz döngü imkânsız).
- Her sayfa ziyaretinde ilerleme logu basılır (takılma görünür).
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from src.scraper.config import (
    DEFAULT_HEADERS,
    DISCOVERY_KEYWORDS,
    MAX_CRAWL_DEPTH,
    MAX_CRAWL_PAGES,
    MAX_RETRIES,
    CRAWL_PER_PAGE_TIMEOUT,
)
from src.scraper.http_client import _resolve_encoding
from src.scraper.models import BankInfo, CampaignPage

logger = logging.getLogger(__name__)


# PDF olarak kabul edilecek uzantı
PDF_EXTENSION = ".pdf"

# İçerik çıkarımında atlanacak kök sayfalar (ananas menü, ana sayfa vs.)
ROOT_ONLY_PATHS = ("", "/")


def _is_same_domain(base_url: str, candidate_url: str) -> bool:
    base_domain = urlparse(base_url).netloc.replace("www.", "")
    candidate_domain = urlparse(candidate_url).netloc.replace("www.", "")
    return base_domain == candidate_domain


def _is_pdf_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    return path.endswith(PDF_EXTENSION)


def _tr_fold(text: str) -> str:
    """Türkçe-duyarlı küçük harfe çevirme."""
    return text.replace("İ", "i").replace("I", "ı").casefold()


def _keyword_hit(url: str, link_text: str) -> bool:
    """URL veya link metninde keşif anahtar kelimesi var mı (Türkçe-duyarlı)."""
    haystack = _tr_fold(f"{url} {link_text}")
    return any(kw in haystack for kw in DISCOVERY_KEYWORDS)


@dataclass
class DiscoveryResult:
    """Bir banka için keşif sonucu: HTML sayfaları + PDF havuzu."""

    html_pages: list[CampaignPage] = field(default_factory=list)
    pdf_urls: list[str] = field(default_factory=list)
    pages_visited: int = 0


class RecursiveDiscoverer:
    """Banka sitesinde BFS ile recursive keşif yapan sınıf.

    Hem HTML kampanya sayfalarını hem de PDF bağlarını toplar.
    """

    def __init__(
        self,
        bank: BankInfo,
        max_depth: int = MAX_CRAWL_DEPTH,
        max_pages: int = MAX_CRAWL_PAGES,
        request_delay: float = 1.0,
        timeout: int = CRAWL_PER_PAGE_TIMEOUT,
    ) -> None:
        self.bank = bank
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.request_delay = request_delay
        self.timeout = timeout
        self._visited: set[str] = set()
        self._html_found: set[str] = set()
        self._pdf_found: set[str] = set()
        self._session = requests.Session()
        self._session.headers.update(DEFAULT_HEADERS)

    # -- HTTP -----------------------------------------------------------

    def _get(self, url: str) -> Optional[requests.Response]:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self._session.get(
                    url, timeout=self.timeout, allow_redirects=True,
                )
                resp.raise_for_status()
                return resp
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 404:
                    return None
                logger.warning("HTTP [%d/%d]: %s — %s",
                               attempt, MAX_RETRIES, url, e)
            except requests.exceptions.RequestException as e:
                logger.warning("İstek [%d/%d]: %s — %s",
                               attempt, MAX_RETRIES, url, e)
            if attempt < MAX_RETRIES:
                time.sleep(self.request_delay * attempt)
        return None

    # -- Link toplama ---------------------------------------------------

    def _collect_links(self, html: str, base_url: str
                       ) -> tuple[list[str], list[str]]:
        soup = BeautifulSoup(html, "html.parser")
        html_links: list[str] = []
        pdf_links: list[str] = []

        for tag in soup.find_all(["a", "iframe", "embed", "object"]):
            href = tag.get("href") or tag.get("src")
            if not href:
                continue
            href = href.strip()
            if not href or href.startswith(("javascript:", "mailto:",
                                            "tel:", "#")):
                continue
            full = urljoin(base_url, href).rstrip("/")
            if not _is_same_domain(self.bank.url, full):
                continue
            if _is_pdf_url(full):
                pdf_links.append(full)
            else:
                parsed = urlparse(full)
                if parsed.path and parsed.path not in ROOT_ONLY_PATHS:
                    html_links.append(full)
        return html_links, pdf_links

    # -- Çekirdek -------------------------------------------------------

    def discover(self, seed_urls: Optional[list[str]] = None) -> DiscoveryResult:
        queue: deque[tuple[str, int]] = deque()
        seeds = seed_urls or [self.bank.url]
        for s in seeds:
            if _is_same_domain(self.bank.url, s):
                queue.append((s.rstrip("/"), 0))

        result = DiscoveryResult()
        pages_visited = 0

        while queue and pages_visited < self.max_pages:
            url, depth = queue.popleft()
            if url in self._visited:
                continue
            self._visited.add(url)

            if depth > self.max_depth:
                continue

            if pages_visited > 0:
                time.sleep(self.request_delay)

            logger.info("visiting: %s (depth=%d, pages=%d/%d)",
                        url, depth, pages_visited + 1, self.max_pages)
            resp = self._get(url)
            pages_visited += 1
            result.pages_visited = pages_visited

            if resp is None:
                continue

            # PDF olarak servis edilen bir sayfaya denk gelirsek havuzla
            ctype = resp.headers.get("Content-Type", "").lower()
            if "application/pdf" in ctype or _is_pdf_url(resp.url):
                self._add_pdf(resp.url, result)
                continue

            try:
                resp.encoding = _resolve_encoding(resp)
                html = resp.text
            except Exception as e:
                logger.warning("encode hatası %s: %s", url, e)
                continue

            html_links, pdf_links = self._collect_links(html, url)
            for pdf_url in pdf_links:
                self._add_pdf(pdf_url, result)

            # HTML kampanya sayfalarını (anahtar kelimeyle eşleşen) kaydet
            for a_tag in BeautifulSoup(html, "html.parser").find_all("a", href=True):
                href = a_tag["href"].strip()
                if not href or href.startswith(("javascript:", "mailto:",
                                                "tel:", "#")):
                    continue
                full = urljoin(url, href).rstrip("/")
                link_text = a_tag.get_text(strip=True)
                parsed = urlparse(full)
                if (parsed.path and parsed.path not in ROOT_ONLY_PATHS
                        and _is_same_domain(self.bank.url, full)
                        and not _is_pdf_url(full)
                        and _keyword_hit(full, link_text)):
                    page = CampaignPage(
                        bank_id=self.bank.id,
                        bank_name=self.bank.name,
                        page_url=full,
                        page_title=link_text or None,
                    )
                    self._add_html(page, result)

            if depth < self.max_depth:
                for link in html_links:
                    if link not in self._visited:
                        queue.append((link, depth + 1))

        logger.info(
            "%s: recursive keşif bitti. %d sayfa tarandı, %d HTML + %d PDF bulundu.",
            self.bank.name, pages_visited,
            len(result.html_pages), len(result.pdf_urls),
        )
        return result

    def _add_pdf(self, pdf_url: str, result: DiscoveryResult) -> None:
        if pdf_url in self._pdf_found:
            return
        self._pdf_found.add(pdf_url)
        result.pdf_urls.append(pdf_url)

    def _add_html(self, page: CampaignPage, result: DiscoveryResult) -> None:
        if page.page_url in self._html_found:
            return
        self._html_found.add(page.page_url)
        result.html_pages.append(page)


def discover_pages_recursive(
    bank: BankInfo, seed_urls: Optional[list[str]] = None,
    max_depth: int = MAX_CRAWL_DEPTH, max_pages: int = MAX_CRAWL_PAGES,
    request_delay: float = 1.0,
) -> DiscoveryResult:
    """Bir banka için recursive keşif yapar (HTML + PDF).

    Döner: DiscoveryResult (html_pages + pdf_urls).
    """
    discoverer = RecursiveDiscoverer(
        bank, max_depth=max_depth, max_pages=max_pages,
        request_delay=request_delay,
    )
    return discoverer.discover(seed_urls)
