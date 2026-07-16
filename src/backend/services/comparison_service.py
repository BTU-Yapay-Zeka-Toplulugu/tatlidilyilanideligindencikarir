"""Bankalar arası karşılaştırma iş mantığı (Service Layer Pattern)."""

from typing import Any

from src.backend.repositories.campaign_repository import CampaignRepository
from src.backend.services.campaign_service import CampaignService
from src.nlp.normalizer import (
    normalize_amount,
    normalize_profit_share_rate,
    normalize_term,
)
from src.database.models import Campaign

COMPARABLE_CAMPAIGN_TYPE = "Katılma Hesabı / Mevduat"


class ComparisonService:
    """Kâr payı oranına göre kampanya karşılaştırması yapan servis."""

    def __init__(self, campaign_service: CampaignService, repository: CampaignRepository) -> None:
        """Karşılaştırma servisine bağımlılıklarını enjekte eder."""
        self.campaign_service = campaign_service
        self.repository = repository

    def compare(
        self,
        term_months: int | None = None,
        amount: float | None = None,
    ) -> list[dict[str, Any]]:
        """Filtrelere uyan mevduat kampanyalarını orana göre sıralayıp döner."""
        campaigns = self.campaign_service.list_campaigns()
        results: list[dict[str, Any]] = []

        for campaign in campaigns:
            detail = self.campaign_service.ensure_nlp_processed(campaign)
            if detail.campaign_type != COMPARABLE_CAMPAIGN_TYPE:
                continue
            if term_months is not None and detail.term_months is not None:
                if detail.term_months != term_months:
                    continue
            if amount is not None and detail.min_amount is not None:
                if amount < detail.min_amount:
                    continue

            bank_name = self.repository.get_bank_name(campaign.bank_id)
            results.append(
                {
                    "bank_name": bank_name,
                    "campaign_title": campaign.page_title,
                    "profit_share_rate": detail.profit_share_rate,
                    "term_months": detail.term_months,
                    "min_amount": detail.min_amount,
                    "advantage_description": detail.advantage_description,
                    "target_audience": detail.target_audience,
                    "source_url": campaign.source_url,
                    "normalized_rate": normalize_profit_share_rate(detail.profit_share_rate),
                    "normalized_amount": normalize_amount(detail.min_amount),
                    "normalized_term": normalize_term(detail.term_months),
                }
            )

        results.sort(key=lambda x: x["profit_share_rate"] or 0.0, reverse=True)
        return results
