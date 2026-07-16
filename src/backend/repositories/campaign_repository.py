"""Kampanya verisine veritabanı erişimini soyutan repository (Repository Pattern)."""

from sqlalchemy.orm import Session

from src.database.models import Bank, Campaign, ExtractedCampaignDetail


class CampaignRepository:
    """Kampanya ve ilişkili varitlere DB erişimini soyutlayan repository."""

    def __init__(self, db: Session) -> None:
        """Repository'nin kullanacağı veritabanı oturumunu alır."""
        self.db = db

    def list_banks(self) -> list[Bank]:
        """Veritabanında kayıtlı tüm bankaları döner."""
        return self.db.query(Bank).all()

    def list_campaigns(self, bank_id: int | None = None) -> list[Campaign]:
        """Kampanyaları bankaya göre filtreleyerek listeler."""
        query = self.db.query(Campaign)
        if bank_id is not None:
            query = query.filter(Campaign.bank_id == bank_id)
        return query.all()

    def get_campaign(self, campaign_id: int) -> Campaign | None:
        """ID'ye göre tek bir kampanyayı döner, yoksa None."""
        return self.db.query(Campaign).filter(Campaign.id == campaign_id).first()

    def get_extracted_detail(self, campaign_id: int) -> ExtractedCampaignDetail | None:
        """Bir kampanyaya ait NLP detayını döner, yoksa None."""
        return (
            self.db.query(ExtractedCampaignDetail)
            .filter_by(campaign_id=campaign_id)
            .first()
        )

    def save_extracted_detail(self, detail: ExtractedCampaignDetail) -> ExtractedCampaignDetail:
        """NLP ile çıkarılan detayı veritabanına kaydeder ve döner."""
        self.db.add(detail)
        self.db.commit()
        self.db.refresh(detail)
        return detail

    def get_bank_name(self, bank_id: int) -> str:
        """Banka ID'sine karşılık gelen banka adını döner."""
        bank = self.db.query(Bank).filter(Bank.id == bank_id).first()
        return bank.name if bank else "Bilinmeyen Banka"
