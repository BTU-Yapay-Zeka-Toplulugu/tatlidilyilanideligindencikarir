"""Veritabanı tabloları ve SQLAlchemy modelleri."""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """SQLAlchemy modelleri için taban sınıf."""


class Bank(Base):
    """Katılım bankaları bilgilerini saklayan tablo."""

    __tablename__ = "banks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    url = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # İlişkiler
    campaigns = relationship("Campaign", back_populates="bank", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Banka modelinin okunabilir temsilini döner."""
        return f"<Bank(name='{self.name}', url='{self.url}')>"


class Campaign(Base):
    """Taranan ve temizlenen kampanya metinlerini saklayan tablo."""

    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_id = Column(Integer, ForeignKey("banks.id", ondelete="CASCADE"), nullable=False)
    source_url = Column(String(1024), unique=True, nullable=False)
    page_title = Column(String(512), nullable=True)
    raw_text = Column(Text, nullable=False)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    content_length = Column(Integer, nullable=False)

    # İlişkiler
    bank = relationship("Bank", back_populates="campaigns")
    extracted_detail = relationship(
        "ExtractedCampaignDetail",
        back_populates="campaign",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Kampanya modelinin okunabilir temsilini döner."""
        return f"<Campaign(title='{self.page_title}', url='{self.source_url}')>"


class ExtractedCampaignDetail(Base):
    """NLP modülü tarafından çıkarılan yapılandırılmış kampanya detayları."""

    __tablename__ = "extracted_campaign_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    profit_share_rate = Column(Float, nullable=True)  # kâr payı oranı
    term_months = Column(Integer, nullable=True)  # vade (ay olarak)
    min_amount = Column(Float, nullable=True)  # asgari tutar
    max_amount = Column(Float, nullable=True)  # azami tutar
    advantage_description = Column(Text, nullable=True)  # kampanya avantajı
    target_audience = Column(String(255), nullable=True)  # hedef kitle
    campaign_type = Column(String(100), nullable=True)  # kampanya türü (sınıflandırma)
    is_processed = Column(Boolean, default=False, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    # İlişkiler
    campaign = relationship("Campaign", back_populates="extracted_detail")

    def __repr__(self) -> str:
        """Detay modelinin okunabilir temsilini döner."""
        return f"<ExtractedCampaignDetail(campaign_id={self.campaign_id}, type='{self.campaign_type}')>"
