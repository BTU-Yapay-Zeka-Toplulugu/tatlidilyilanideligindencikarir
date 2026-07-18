"""Dinamik & recursive PDF crawler — banka sitelerindeki PDF'leri otonom keşfeder.

TASARIM İLKELERİ (ADR-011):
- STATİK MAPPING YOK: Banka başına sabit PDF URL'si/selector'ü tanımlanmaz.
- Recursive crawl: seed sayfalarından başlayarak yalnızca aynı domain içinde
  linkler takip edilir, PDF bağları bir havuzda toplanır.
- Collect & Filter: İndirilen her PDF, içeriğindeki kampanya/oran anahtar
  kelimesine göre skorlanır; ilgisiz PDF'ler (aydınlatma, sözleşme vb.)
  elenir.
- Extraction: Kalan PDF'ler pdfplumber ile metne çevrilir ve HTML kaynaklı
  veriyle AYNI temizleme/NLP hattından geçer.

Kütüphane: pdfplumber (açık kaynak). Taranmış görüntü PDF tespit edilirse
loglanır; OCR (pytesseract) yalnızca gerçekten gerektiğinde eklenir.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from src.scraper.config import (
    DEFAULT_HEADERS,
    MAX_PAGES_PER_BANK,
    MAX_RETRIES,
    REQUEST_DELAY,
    REQUEST_TIMEOUT,
)
from src.scraper.http_client import _resolve_encoding
from src.scraper.models import BankInfo, CampaignData

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------

# PDF olarak kabul edilecek dosya uzantısı
PDF_EXTENSION = ".pdf"

# Kampanya/oran içeriğini işaret eden GÜÇLÜ anahtar kelimeler (Türkçe-duyarlı fold ile).
# Tek başına "oran"/"kâr"/"taksit" gibi zayıf kelimeler KVKK/gizlilik/fee formlarında
# da geçtiğinden kampanya PDF'i sayılmaz; yalnızca GÜÇLÜ sinyaller kabul edilir.
CAMPAIGN_PDF_KEYWORDS = (
    "kâr payı", "kar payi", "kâr payi",
    "finansman oranı", "finansman orani", "finansman",
    "kampanya", "kampanyalar", "fırsat", "firsa",
    "katılma hesabı", "katilma hesabi", "katılma fonu", "katilim fonu",
    "kâr payı oranı", "kar payi orani",
    "profit rate", "profit share",
    "hoş geldin", "hos geldin",
    "taksitli finansman", "konut finansman", "taşıt finansman", "tasit finansman",
)

# İlgisiz (eleme) PDF işaretleri — bu kelimeler baskın ise belge kampanya değildir
# (aydınlatma metni, gizlilik, sözleşme, KVKK, ücret tarifesi/fee disclosure vb.)
IRRELEVANT_PDF_KEYWORDS = (
    "aydınlatma", "aydinlatma", "kvkk", "gizlilik politikası", "gizlilik politikasi",
    "sözleşme", "sozlesme", "bilgilendirme formu",
    "bilgilendirme metni", "rıza", "riza", "feragat",
    "uygulama esasları", "wolfsberg", "kişisel verilerin korunması",
    "kisisel verilerin korunmasi", "ücret tarifesi", "ucret tarifesi",
    "menkul kıymet", "menkul kiymet", "faaliyet raporu", "bilanço",
)

# Filtreleme eşiği: ilk N sayfada kaç GÜÇLÜ kampanya anahtar kelimesi görülmeli
CAMPAIGN_KEYWORD_MIN_HITS = 1

# Recursive crawl için maksimum derinlik
DEFAULT_CRAWL_DEPTH = 3

# Bir PDF'in filtreleme için incelenecek ilk sayfa sayısı
PDF_SCAN_PAGES = 3

# Bir PDF'in boyut üst sınırı (byte) — aşırı büyük dosyaları atla
MAX_PDF_BYTES = 25 * 1024 * 1024

# İndirme zaman aşımı (saniye)
PDF_DOWNLOAD_TIMEOUT = 45

# Parse zaman aşımı (saniye) — pdfplumber tek bir sayfada TAKILABİLİR;
# bu guard olmadan tüm crawl donar (ADR-011 donma riski). Parse bu süreyi
# aşarsa PDF atlanır, crawl devam eder.
PDF_PARSE_TIMEOUT = 30

# İndirmeye bile gitmeden ELENEN PDF ad/resmi döküman işaretçileri
# (sözleşme, form, tarife vb. — kampanya içeriği taşımaz).
IRRELEVANT_PDF_FILENAME = (
    "sozlesme", "sözleşme", "form", "tarife", "bilgilendirme",
    "aydınlatma", "aydinlatma", "kvkk", "gizlilik", "bilanço",
    "faaliyet raporu", "wolfsberg", "izahname", "prospektus",
    "prospectus", "hesap ozeti", "hesap özeti", "ekstre",
)


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------

def _tr_fold(text: str) -> str:
    """Türkçe-duyarlı küçük harfe çevirme (extractor ile uyumlu)."""
    return text.replace("İ", "i").replace("I", "ı").casefold()


def _is_same_domain(base_url: str, candidate_url: str) -> bool:
    """İki URL aynı domain'de mi (www. farkı yok)."""
    base_domain = urlparse(base_url).netloc.replace("www.", "")
    candidate_domain = urlparse(candidate_url).netloc.replace("www.", "")
    return base_domain == candidate_domain


def _is_pdf_url(url: str) -> bool:
    """URL bir PDF dosyasına mı işaret ediyor (uzantıya göre)."""
    path = urlparse(url).path.lower()
    return path.endswith(PDF_EXTENSION)


def _looks_like_pdf(response: "requests.Response") -> bool:
    """Yanıtın Content-Type'ı PDF mi (uzantı olmasa da)."""
    content_type = response.headers.get("Content-Type", "").lower()
    if "application/pdf" in content_type:
        return True
    return _is_pdf_url(response.url)


# ---------------------------------------------------------------------------
# Veri modelleri
# ---------------------------------------------------------------------------

@dataclass
class PdfCandidate:
    """Havuzda toplanan bir PDF adayı."""

    bank_id: int
    bank_name: str
    pdf_url: str
    found_on: str = ""  # hangi sayfadan keşfedildiği
    depth: int = 0


# ---------------------------------------------------------------------------
# Recursive Crawler
# ---------------------------------------------------------------------------

class RecursivePdfCrawler:
    """Bir bankanın sitesinde recursive olarak PDF'leri toplayan tarayıcı.

    Statik mapping yapmaz; seed URL'lerinden başlayarak aynı domain içinde
    linkleri takip eder ve PDF bağlarını havuzda toplar.
    """

    def __init__(
        self,
        bank: BankInfo,
        max_depth: int = DEFAULT_CRAWL_DEPTH,
        max_pages: int = MAX_PAGES_PER_BANK * 2,
        request_delay: float = REQUEST_DELAY,
    ) -> None:
        self.bank = bank
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.request_delay = request_delay
        self.pdf_pool: list[PdfCandidate] = []
        self._visited_html: set[str] = set()
        self._visited_pdf: set[str] = set()
        self._session = requests.Session()
        self._session.headers.update(DEFAULT_HEADERS)

    # -- HTTP yardımcıları ------------------------------------------------

    def _get(self, url: str, timeout: int = REQUEST_TIMEOUT,
             stream: bool = False) -> Optional[requests.Response]:
        """Retry'li GET isteği."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self._session.get(
                    url, timeout=timeout, stream=stream,
                    allow_redirects=True,
                )
                resp.raise_for_status()
                return resp
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 404:
                    logger.debug("404: %s", url)
                    return None
                logger.warning(
                    "HTTP hata [%d/%d]: %s — %s", attempt, MAX_RETRIES, url, e
                )
            except requests.exceptions.RequestException as e:
                logger.warning(
                    "İstek hatası [%d/%d]: %s — %s", attempt, MAX_RETRIES, url, e
                )
            if attempt < MAX_RETRIES:
                import time
                time.sleep(self.request_delay * attempt)
        return None

    # -- Link toplama -----------------------------------------------------

    def _collect_links(self, html: str, base_url: str
                       ) -> tuple[list[str], list[str]]:
        """Bir HTML sayfasındaki tüm bağları ayırır: (html_linkler, pdf_linkler)."""
        soup = BeautifulSoup(html, "html.parser")
        html_links: list[str] = []
        pdf_links: list[str] = []

        # <a href> bağları
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("javascript:", "mailto:", "tel:")):
                continue
            full = urljoin(base_url, href).rstrip("/")
            if not _is_same_domain(self.bank.url, full):
                continue
            if _is_pdf_url(full):
                pdf_links.append(full)
            else:
                parsed = urlparse(full)
                if parsed.path and parsed.path != "/":
                    html_links.append(full)

        # <iframe>/<embed>/<object> src bağları (PDF gömülü olabilir)
        for tag in soup.find_all(["iframe", "embed", "object"], src=True):
            src = tag["src"].strip()
            if not src:
                continue
            full = urljoin(base_url, src).rstrip("/")
            if not _is_same_domain(self.bank.url, full):
                continue
            if _is_pdf_url(full):
                pdf_links.append(full)

        return html_links, pdf_links

    # -- Recursive çekirdek ------------------------------------------------

    def crawl(self, seed_urls: list[str]) -> list[PdfCandidate]:
        """Seed URL'lerden başlayarak recursive PDF keşfi yapar."""
        from collections import deque

        queue: deque[tuple[str, int]] = deque()
        for seed in seed_urls:
            if _is_same_domain(self.bank.url, seed):
                queue.append((seed.rstrip("/"), 0))

        pages_visited = 0
        while queue and pages_visited < self.max_pages:
            url, depth = queue.popleft()
            if url in self._visited_html:
                continue
            self._visited_html.add(url)

            if depth > self.max_depth:
                continue

            import time
            if pages_visited > 0:
                time.sleep(self.request_delay)

            resp = self._get(url)
            if resp is None:
                continue

            # PDF olarak servis edilen bir sayfaya denk gelirsek havuzla
            if _looks_like_pdf(resp):
                self._add_pdf(url, url, depth)
                continue

            try:
                resp.encoding = _resolve_encoding(resp)
                html = resp.text
            except Exception as e:  # pragma: no cover - aşırı nadir
                logger.warning("Encode hatası %s: %s", url, e)
                continue

            html_links, pdf_links = self._collect_links(html, url)

            for pdf_url in pdf_links:
                self._add_pdf(pdf_url, url, depth)

            # Sonraki derinliğe yalnızca henüz görülmemiş HTML bağlarını ekle
            if depth < self.max_depth:
                for link in html_links:
                    if link not in self._visited_html:
                        queue.append((link, depth + 1))

            pages_visited += 1

        logger.info(
            "%s: recursive crawl tamamlandı. %d sayfa tarandı, %d PDF adayı.",
            self.bank.name, pages_visited, len(self.pdf_pool),
        )
        # Aynı URL'den birden fazla aday olabilir; benzersizle
        return self._dedupe_pool()

    def _add_pdf(self, pdf_url: str, found_on: str, depth: int) -> None:
        if pdf_url in self._visited_pdf:
            return
        self._visited_pdf.add(pdf_url)
        self.pdf_pool.append(
            PdfCandidate(
                bank_id=self.bank.id,
                bank_name=self.bank.name,
                pdf_url=pdf_url,
                found_on=found_on,
                depth=depth,
            )
        )

    def _dedupe_pool(self) -> list[PdfCandidate]:
        seen: set[str] = set()
        unique: list[PdfCandidate] = []
        for c in self.pdf_pool:
            if c.pdf_url in seen:
                continue
            seen.add(c.pdf_url)
            unique.append(c)
        return unique


# ---------------------------------------------------------------------------
# PDF İndirme & Akıllı Filtreleme
# ---------------------------------------------------------------------------

def download_pdf(candidate: PdfCandidate) -> Optional[bytes]:
    """PDF'i indirir, başarısızlıkta (zaman aşımı/DNS takılması dahil) None döner."""
    def _fetch() -> Optional[bytes]:
        resp = requests.get(
            candidate.pdf_url,
            headers=DEFAULT_HEADERS,
            timeout=PDF_DOWNLOAD_TIMEOUT,
            stream=True,
            allow_redirects=True,
        )
        resp.raise_for_status()
        if not _looks_like_pdf(resp):
            logger.debug("PDF değil (%s): %s",
                         resp.headers.get("Content-Type"), candidate.pdf_url)
            return None
        data = resp.content
        if len(data) == 0:
            logger.warning("Boş PDF: %s", candidate.pdf_url)
            return None
        if len(data) > MAX_PDF_BYTES:
            logger.warning("PDF çok büyük (%.1f MB): %s",
                           len(data) / 1024 / 1024, candidate.pdf_url)
            return None
        return data

    # DNS çözümü / bağlantı takılmaları requests timeout'ını bazen aşabildiğinden
    # ayrı thread + duvar saati guard ile korunur (ADR-011 donma riski).
    return _run_with_timeout(_fetch, PDF_DOWNLOAD_TIMEOUT + 10, label="indirme")


def _run_with_timeout(func, timeout: int, label: str = "işlem"):
    """Bir fonksiyonu ayrı thread'de çalıştırır; süre aşımında None döner.

    pdfplumber tek bir sayfada TAKILABİLDİĞİNDEN (C seviyesinde blok) VEYA
    ``requests.get`` DNS çözümünde takılabildiğinden bu guard olmadan tüm
    crawl donar. Süre aşımı güvenliği için zorunludur (ADR-011 donma riski).
    """
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(func)
        try:
            return future.result(timeout=timeout)
        except Exception as e:  # zaman aşımı veya hatası
            logger.warning("PDF %s zaman aşımı/hatası (%ss): %s", label, timeout, e)
            return None


def _extract_first_pages_text(pdf_bytes: bytes, pages: int = PDF_SCAN_PAGES
                              ) -> tuple[str, bool]:
    """PDF'in ilk N sayfasının metnini çıkarır.

    Döner: (metin, taranmış_mı). Metin boşsa ve sayfada görüntü varsa
    taranmış (scanned) olarak işaretlenir.
    """
    import io

    import pdfplumber

    def _parse() -> tuple[str, bool]:
        text_parts: list[str] = []
        scanned_suspected = False
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                if i >= pages:
                    break
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
                # Görüntü var ama metin yok → taranmış olabilir
                if not page_text.strip() and (page.images or page.chars is None):
                    scanned_suspected = True
        return "\n".join(text_parts), scanned_suspected

    result = _run_with_timeout(_parse, PDF_PARSE_TIMEOUT)
    if result is None:
        return "", False
    return result


def is_campaign_pdf(pdf_bytes: bytes) -> tuple[bool, str]:
    """PDF'in kampanya/oran içeriği taşıyıp taşımadığına karar verir.

    Döner: (ilgili_mi, sebep). İlk sayfalardaki metne göre skorlama yapar.
    """
    first_text, scanned = _extract_first_pages_text(pdf_bytes)
    folded = _tr_fold(first_text)

    # İlk sayfalarda metin yoksa tüm PDF'e bak (küçük dosya varsayımı)
    if not first_text.strip():
        if scanned:
            logger.info("Taranmış PDF tespit edildi (OCR gerekebilir) — şimdilik atlanıyor.")
            return False, "scanned_no_ocr"
        return False, "empty_text"

    # GÜÇLÜ kampanya sinyali sayısı
    hits = sum(1 for kw in CAMPAIGN_PDF_KEYWORDS if _tr_fold(kw) in folded)

    # İlgisiz (eleme) anahtar kelimesi varsa belge kampanya dışı bir
    # resmi döküman (KVKK/gizlilik/sözleşme/ücret tarifesi) olabilir.
    # Bu durumda yalnızca zayıf "oran/kâr" eşleşmesi YETERLİ DEĞİLDİR;
    # en az 2 GÜÇLÜ kampanya sinyali gerekir (fee disclosure formları elenir).
    irrelevant_hit = next(
        (kw for kw in IRRELEVANT_PDF_KEYWORDS if _tr_fold(kw) in folded),
        None,
    )
    if irrelevant_hit and hits < 2:
        return False, f"irrelevant:{irrelevant_hit}"

    if hits >= CAMPAIGN_KEYWORD_MIN_HITS:
        return True, f"campaign_hits:{hits}"

    return False, f"no_campaign_keywords:hits={hits}"


# ---------------------------------------------------------------------------
# Tam Extraction
# ---------------------------------------------------------------------------

def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Bir PDF'in TÜM sayfalarının metnini çıkarır (ham, temizlenmemiş)."""
    import io

    import pdfplumber

    def _parse() -> str:
        parts: list[str] = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    parts.append(page_text)
        return "\n".join(parts)

    result = _run_with_timeout(_parse, PDF_PARSE_TIMEOUT)
    if result is None:
        logger.error("PDF tam metin çıkarımı zaman aşımında atlandı.")
        return ""
    return result


# ---------------------------------------------------------------------------
# Üst Seviye: Tüm pipeline adımı
# ---------------------------------------------------------------------------

def crawl_and_extract_pdfs(
    bank: BankInfo, seed_urls: list[str]
) -> list[CampaignData]:
    """Bir banka için recursive PDF crawl + filtre + extraction yapar.

    Dönen ``CampaignData`` kayıtları ``source_type="pdf"`` ile işaretlenir ve
    HTML kaynaklı kayıtlarla aynı temizleme/NLP hattından geçer.
    """
    crawler = RecursivePdfCrawler(bank)
    candidates = crawler.crawl(seed_urls)

    if not candidates:
        logger.info("%s: recursive crawl'de PDF bulunamadı.", bank.name)
        return []

    return _process_pdf_candidates(bank, candidates)


def extract_pdfs_from_urls(
    bank: BankInfo, pdf_urls: list[str], max_pdfs: int = 20
) -> list[CampaignData]:
    """Önceden keşfedilmiş PDF URL'lerinden filtre + extraction yapar.

    ``recursive_discovery`` ile bulunmuş PDF havuzunu doğrudan işler
    (çift crawl yapmaz). Dönen kayıtlar ``source_type="pdf"`` ile işaretlenir.

    ``max_pdfs``: bir bankada indirilip filtrelenecek MAKSİMUM PDF sayısı
    (havuz çok büyükse — örn. 171 aday — tümünü indirmek yerine ilk N
    aday işlenir; bu hem hız hem ağ yükü için gereklidir).
    """
    if not pdf_urls:
        logger.info("%s: keşifte PDF bulunamadı.", bank.name)
        return []
    if len(pdf_urls) > max_pdfs:
        logger.info(
            "%s: %d PDF adayı var, ilk %d tanesi işlenecek (max_pdfs).",
            bank.name, len(pdf_urls), max_pdfs,
        )
    selected = pdf_urls[:max_pdfs]
    candidates = [
        PdfCandidate(bank_id=bank.id, bank_name=bank.name, pdf_url=u)
        for u in selected
    ]
    return _process_pdf_candidates(bank, candidates)


def _process_pdf_candidates(
    bank: BankInfo, candidates: list[PdfCandidate]
) -> list[CampaignData]:
    """PDF adaylarını indirir, filtreler, metne çevirir → CampaignData listesi."""
    results: list[CampaignData] = []
    for i, cand in enumerate(candidates, 1):
        # Dosya adıyla ELENEN resmi dökümanlar (sözleşme/form/tarife vb.) —
        # indirmeye bile gerek kalmadan atlanır (zaman/ağ tasarrufu).
        fname = cand.pdf_url.rsplit("/", 1)[-1].lower()
        if any(bad in _tr_fold(fname) for bad in IRRELEVANT_PDF_FILENAME):
            logger.info("  → Resmi döküman (atlandı): %s", cand.pdf_url)
            continue

        logger.info(
            "[%d/%d] PDF inceleniyor: %s", i, len(candidates), cand.pdf_url
        )
        pdf_bytes = download_pdf(cand)
        if pdf_bytes is None:
            continue  # hata loglandı, atla, devam et

        relevant, reason = is_campaign_pdf(pdf_bytes)
        if not relevant:
            logger.info("  → İlgisiz PDF (atlandı): %s [%s]", cand.pdf_url, reason)
            continue

        logger.info("  → Kampanya PDF'i (işleniyor): %s [%s]", cand.pdf_url, reason)
        raw_text = extract_pdf_text(pdf_bytes)
        if len(raw_text) < 50:
            logger.warning("  → PDF metni çok kısa, atlanıyor: %s", cand.pdf_url)
            continue

        results.append(
            CampaignData(
                bank_id=bank.id,
                bank_name=bank.name,
                source_url=cand.pdf_url,
                page_title=f"PDF: {cand.pdf_url.rsplit('/', 1)[-1]}",
                raw_text=raw_text,
                source_type="pdf",
            )
        )

    logger.info(
        "%s: %d/%d PDF adayı kampanya PDF'i olarak işlendi.",
        bank.name, len(results), len(candidates),
    )
    return results
