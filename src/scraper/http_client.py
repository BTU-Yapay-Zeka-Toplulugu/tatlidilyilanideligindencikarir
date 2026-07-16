"""Merkezi HTTP istemcisi — retry, delay, hata yönetimi ile web sayfası çekme."""

import time
import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup

from src.scraper.config import (
    DEFAULT_HEADERS,
    MAX_RETRIES,
    REQUEST_DELAY,
    REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)


def fetch_page(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
    """Verilen URL'den HTML içeriğini çeker, başarısızlıkta None döner."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                url, headers=DEFAULT_HEADERS, timeout=timeout
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding or "utf-8"
            logger.info("Sayfa çekildi [%d/%d]: %s", attempt, MAX_RETRIES, url)
            return response.text

        except requests.exceptions.Timeout:
            logger.warning(
                "Zaman aşımı [%d/%d]: %s", attempt, MAX_RETRIES, url
            )
        except requests.exceptions.HTTPError as e:
            logger.warning(
                "HTTP hatası [%d/%d]: %s — %s", attempt, MAX_RETRIES, url, e
            )
            if e.response is not None and e.response.status_code == 404:
                logger.info("404 Hatası tespit edildi, tekrar denenmiyor.")
                break
        except requests.exceptions.ConnectionError as e:
            logger.warning(
                "Bağlantı hatası [%d/%d]: %s — %s", attempt, MAX_RETRIES, url, e
            )
        except requests.exceptions.RequestException as e:
            logger.error(
                "Beklenmeyen istek hatası [%d/%d]: %s — %s",
                attempt, MAX_RETRIES, url, e,
            )

        if attempt < MAX_RETRIES:
            wait = REQUEST_DELAY * attempt
            logger.info("%.1f saniye bekleniyor...", wait)
            time.sleep(wait)

    logger.error("Sayfa çekilemedi (tüm denemeler tükendi): %s", url)
    return None


def parse_html(html: str) -> BeautifulSoup:
    """HTML string'ini BeautifulSoup nesnesine dönüştürür."""
    return BeautifulSoup(html, "html.parser")


def fetch_and_parse(url: str) -> Optional[BeautifulSoup]:
    """URL'den HTML çekip parse eder, başarısızlıkta None döner."""
    html = fetch_page(url)
    if html is None:
        return None
    return parse_html(html)
