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

    def get_bank(self, bank_id: int) -> Bank | None:
        """ID'ye göre tek bir bankayı döner, yoksa None."""
        return self.db.query(Bank).filter(Bank.id == bank_id).first()

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

    def create_bank(self, name: str, url: str) -> Bank:
        """Yeni bir banka kaydı oluşturur ve döner."""
        bank = Bank(name=name, url=url)
        self.db.add(bank)
        self.db.commit()
        self.db.refresh(bank)
        return bank

    def create_campaign(self, bank_id: int, source_url: str, page_title: str, raw_text: str) -> Campaign:
        """Yeni bir kampanya kaydı oluşturur ve döner."""
        campaign = Campaign(
            bank_id=bank_id,
            source_url=source_url,
            page_title=page_title,
            raw_text=raw_text,
            content_length=len(raw_text),
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def update_campaign(self, campaign: Campaign, **fields: object) -> Campaign:
        """Kampanya kaydının belirtilen alanlarını günceller ve döner."""
        for key, value in fields.items():
            if value is not None:
                setattr(campaign, key, value)
        if "raw_text" in fields and fields["raw_text"] is not None:
            campaign.content_length = len(fields["raw_text"])
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def delete_campaign(self, campaign: Campaign) -> None:
        """Kampanya kaydını veritabanından siler."""
        self.db.delete(campaign)
        self.db.commit()

    def delete_bank(self, bank: Bank) -> None:
        """Banka kaydını (ve ilişkili kampanyaları) veritabanından siler."""
        self.db.delete(bank)
        self.db.commit()
