"""Kampanya iş mantığı katmanı (Service Layer Pattern)."""

from datetime import datetime, timezone
from typing import Any

from src.backend.repositories.campaign_repository import CampaignRepository
from src.database.models import Campaign, ExtractedCampaignDetail
from src.nlp.extractor import extract_all_campaign_details


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
        extracted = extract_all_campaign_details(campaign.raw_text)
        detail = ExtractedCampaignDetail(
            campaign_id=campaign.id,
            profit_share_rate=extracted["profit_share_rate"],
            term_months=extracted["term_months"],
            min_amount=extracted["min_amount"],
            max_amount=extracted["max_amount"],
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

    def list_campaigns(self, bank_id: int | None = None) -> list[Campaign]:
        """Tüm kampanyaları (repository filtresiyle) döner."""
        return self.repository.list_campaigns(bank_id=bank_id)

    def get_campaign(self, campaign_id: int) -> Campaign | None:
        """ID'ye göre kampanyayı döner."""
        return self.repository.get_campaign(campaign_id)
