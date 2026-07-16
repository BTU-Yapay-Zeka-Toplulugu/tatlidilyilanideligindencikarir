"""Scraper modülü sabitleri ve yapılandırma değerleri."""

from pathlib import Path

# Proje kök dizini
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Veri dizinleri
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Banka site listesi
BANK_SITES_FILE = DATA_DIR / "bank_sites.txt"

# HTTP ayarları
REQUEST_TIMEOUT = 30  # saniye
REQUEST_DELAY = 2  # istekler arası bekleme (saniye), sitelere yük bindirmemek için
MAX_RETRIES = 3

# User-Agent başlığı (botlardan farklı görünmek için)
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# HTTP başlıkları
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Kampanya sayfası keşfi için anahtar kelimeler
CAMPAIGN_KEYWORDS = [
    "kampanya",
    "kampanyalar",
    "firsat",
    "firsatlar",
    "duyuru",
    "duyurular",
    "kar-payi",
    "kar_payi",
    "oranlar",
    "oran",
]

# Kampanya metin çıkarımı için minimum karakter sayısı
MIN_CONTENT_LENGTH = 50

# Banka başına maksimum taranacak kampanya sayfa sayısı
MAX_PAGES_PER_BANK = 15

