"""FastAPI için Pydantic veri şemaları (request/response modelleri)."""

from datetime import datetime
from pydantic import BaseModel


class BankBase(BaseModel):
    """Banka için temel Pydantic şeması."""

    name: str
    url: str


class BankCreate(BankBase):
    """Yeni banka oluşturma isteği için Pydantic şeması."""


class BankResponse(BankBase):
    """Banka API yanıtları için Pydantic şeması."""

    id: int

    class Config:
        """Pydantic ORM modunu etkinleştirir."""

        from_attributes = True


class CampaignBase(BaseModel):
    """Kampanya için temel Pydantic şeması."""

    bank_id: int
    source_url: str
    page_title: str
    raw_text: str


class CampaignCreate(CampaignBase):
    """Yeni kampanya oluşturma isteği için Pydantic şeması."""


class CampaignUpdate(BaseModel):
    """Kampanya güncelleme isteği için Pydantic şeması (kısmi alanlar)."""

    bank_id: int | None = None
    source_url: str | None = None
    page_title: str | None = None
    raw_text: str | None = None


class CampaignResponse(BaseModel):
    """Kampanya API yanıtları için Pydantic şeması."""

    id: int
    bank_id: int
    source_url: str
    page_title: str
    content_length: int
    scraped_at: datetime

    class Config:
        """Pydantic ORM modunu etkinleştirir."""

        from_attributes = True


class ExtractedDetailResponse(BaseModel):
    """NLP ile çıkarılan kampanya detayları API yanıtı için Pydantic şeması."""

    id: int
    campaign_id: int
    profit_share_rate: float | None = None
    term_months: int | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    advantage_description: str | None = None
    target_audience: str | None = None
    campaign_type: str | None = None
    is_processed: bool
    processed_at: datetime | None = None

    class Config:
        """Pydantic ORM modunu etkinleştirir."""

        from_attributes = True


class CampaignDetailResponse(CampaignResponse):
    """Tüm NLP detayları ile birlikte kampanya API yanıtı şeması."""

    extracted_detail: ExtractedDetailResponse | None = None


class FinansmanKalemi(BaseModel):
    """Frontend'in beklediği finansman özet kalemi (Türkçe alan adları)."""

    id: str
    bankaAdi: str
    urunAdi: str
    tutar: float
    karOrani: float
    vade: str
    tarih: str


class KarsilastirmaKalemi(BaseModel):
    """Frontend'in beklediği karşılaştırma satırı (banka başına ürünler)."""

    bankaId: str
    bankaAdi: str
    urunler: list[FinansmanKalemi]


class BankaKalemi(BaseModel):
    """Frontend'in beklediği banka listesi kalemi."""

    id: str
    ad: str
    logo: str | None = None


class Atif(BaseModel):
    """RAG kaynakçası (chatbot citation)."""

    bankaAdi: str
    urunAdi: str
    url: str | None = None


class Mesaj(BaseModel):
    """Chatbot mesajı (frontend sözleşmesi)."""

    id: str
    rol: str
    icerik: str
    atiflar: list[Atif] = []
    zaman: str
    akisDevam: bool = False


class ChatYaniti(BaseModel):
    """POST /chat/mesaj yanıtı."""

    oturumId: str
    mesaj: Mesaj


class CompareResponse(BaseModel):
    """Karşılaştırma API yanıtı için Pydantic şeması."""

    bank_name: str
    campaign_title: str
    profit_share_rate: float | None = None
    term_months: int | None = None
    min_amount: float | None = None
    advantage_description: str | None = None
    target_audience: str | None = None
    source_url: str
    normalized_rate: str
    normalized_amount: str
    normalized_term: str
