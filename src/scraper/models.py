"""Scraper modülü veri modelleri (dataclass'lar)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class BankInfo:
    """Bir katılım bankasının temel bilgilerini tutar."""

    id: int
    name: str
    url: str

    def __str__(self) -> str:
        """Banka bilgisini okunabilir formatta döndürür."""
        return f"{self.id}. {self.name} - {self.url}"


@dataclass
class CampaignPage:
    """Bir bankanın kampanya sayfasının URL ve meta bilgisini tutar."""

    bank_id: int
    bank_name: str
    page_url: str
    page_title: Optional[str] = None
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CampaignData:
    """Bir kampanya sayfasından çıkarılan ham metin verisini tutar."""

    bank_id: int
    bank_name: str
    source_url: str
    page_title: str
    raw_text: str
    source_type: str = "html"
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())
    content_length: int = 0

    def __post_init__(self) -> None:
        """İçerik uzunluğunu otomatik hesaplar."""
        self.content_length = len(self.raw_text)
