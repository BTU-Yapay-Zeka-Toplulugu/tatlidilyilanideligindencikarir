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


def _resolve_encoding(response: "requests.Response") -> str:
    """Yanıt için doğru karakter kodlamasını belirler.

    ``requests.apparent_encoding`` (chardet), charset başlığı olmayan Türkçe
    sitelerde bazen yanlış tahmin edip mojibake ('Hakk─▒m─▒zda') üretir.
    Bu nedenle sırayla: (1) HTTP başlığındaki charset, (2) HTML meta
    charset, (3) UTF-8 (kayıpsız çözülüyorsa), (4) apparent_encoding denenir.
    """
    # 1) HTTP Content-Type başlığında charset açıkça belirtilmişse ona güven.
    content_type = response.headers.get("Content-Type", "").lower()
    if "charset=" in content_type:
        declared = content_type.split("charset=")[-1].split(";")[0].strip()
        if declared:
            return declared

    raw = response.content

    # 2) HTML içindeki <meta charset=...> bildirimi.
    head = raw[:2048].lower()
    for marker in (b'charset="', b"charset='", b"charset="):
        idx = head.find(marker)
        if idx != -1:
            start = idx + len(marker)
            rest = head[start:start + 40]
            declared = b""
            for ch in rest:
                c = bytes([ch])
                if c in (b'"', b"'", b" ", b"/", b">", b";", b"\r", b"\n", b"\t"):
                    break
                declared += c
            declared_str = declared.decode("ascii", "ignore").strip()
            if declared_str:
                return declared_str

    # 3) Charset bildirilmemişse UTF-8'i dene (Türkçe siteler çoğunlukla UTF-8).
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass

    # 4) Son çare: chardet tahmini.
    return response.apparent_encoding or "utf-8"


def fetch_page(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
    """Verilen URL'den HTML içeriğini çeker, başarısızlıkta None döner."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                url, headers=DEFAULT_HEADERS, timeout=timeout
            )
            response.raise_for_status()
            response.encoding = _resolve_encoding(response)
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
