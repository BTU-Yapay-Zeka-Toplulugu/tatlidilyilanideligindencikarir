"""Kampanya iş mantığı katmanı (Service Layer Pattern)."""

from datetime import datetime, timezone
from typing import Any

from src.backend.repositories.campaign_repository import CampaignRepository
from src.database.models import Bank, Campaign, ExtractedCampaignDetail
from src.nlp.pipeline import run_extraction_pipeline


class CampaignService:
    """Kampanya okuma ve NLP detayı çıkarma iş mantığını yürüten servis."""

    def __init__(self, repository: CampaignRepository) -> None:
        """Servisin kullanacağı repository'yi enjekte eder."""
        self.repository = repository

    def ensure_nlp_processed(self, campaign: Campaign) -> ExtractedCampaignDetail:
        """Kampanya için NLP detayının çıkarılmış olduğunu garanti eder."""
        existing = self.repository.get_extracted_detail(campaign.id)
        if existing:
            return existing
        extracted = run_extraction_pipeline(campaign.raw_text)
        detail = ExtractedCampaignDetail(
            campaign_id=campaign.id,
            profit_share_rate=extracted["profit_share_rate_raw"],
            term_months=extracted["term_months_raw"],
            min_amount=extracted["min_amount_raw"],
            max_amount=extracted["max_amount_raw"],
            start_date=extracted["start_date"],
            end_date=extracted["end_date"],
            advantage_description=extracted["advantage_description"],
            target_audience=extracted["target_audience"],
            campaign_type=extracted["campaign_type"],
            is_processed=True,
            processed_at=datetime.now(timezone.utc),
        )
        return self.repository.save_extracted_detail(detail)

    def list_banks(self) -> list[Any]:
        """Tüm bankaları repository üzerinden döner."""
        return self.repository.list_banks()

    def get_bank(self, bank_id: int) -> Bank | None:
        """ID'ye göre bankayı döner."""
        return self.repository.get_bank(bank_id)

    def list_campaigns(self, bank_id: int | None = None) -> list[Campaign]:
        """Tüm kampanyaları (repository filtresiyle) döner."""
        return self.repository.list_campaigns(bank_id=bank_id)

    def get_campaign(self, campaign_id: int) -> Campaign | None:
        """ID'ye göre kampanyayı döner."""
        return self.repository.get_campaign(campaign_id)

    def create_bank(self, name: str, url: str) -> Bank:
        """Yeni banka oluşturur."""
        return self.repository.create_bank(name=name, url=url)

    def create_campaign(self, bank_id: int, source_url: str, page_title: str, raw_text: str) -> Campaign:
        """Yeni kampanya oluşturur."""
        return self.repository.create_campaign(
            bank_id=bank_id, source_url=source_url, page_title=page_title, raw_text=raw_text
        )

    def update_campaign(self, campaign: Campaign, **fields: object) -> Campaign:
        """Kampanyayı günceller."""
        return self.repository.update_campaign(campaign, **fields)

    def delete_campaign(self, campaign: Campaign) -> None:
        """Kampanyayı siler."""
        self.repository.delete_campaign(campaign)

    def delete_bank(self, bank: Bank) -> None:
        """Bankayı siler."""
        self.repository.delete_bank(bank)
