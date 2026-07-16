"""İnce (thin) kampanya ve banka API uç noktaları."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.backend.core.database import get_db
from src.backend.repositories.campaign_repository import CampaignRepository
from src.backend.schemas import BankResponse, CampaignDetailResponse
from src.backend.services.campaign_service import CampaignService

router = APIRouter(prefix="/api", tags=["campaigns"])


def _campaign_service(db: Session = Depends(get_db)) -> CampaignService:
    """CampaignService örneğini repository ile enjekte eder (DI)."""
    return CampaignService(CampaignRepository(db))


@router.get("/banks", response_model=list[BankResponse])
def get_banks(service: CampaignService = Depends(_campaign_service)):
    """Veritabanında kayıtlı tüm bankaları listeler."""
    return service.list_banks()


@router.get("/campaigns", response_model=list[CampaignDetailResponse])
def get_campaigns(
    bank_id: int | None = Query(None, description="Belli bir bankaya göre filtreleme"),
    campaign_type: str | None = Query(None, description="Kampanya türüne göre filtreleme"),
    service: CampaignService = Depends(_campaign_service),
):
    """Kampanyaları listeler ve NLP detaylarını iliştirir."""
    campaigns = service.list_campaigns(bank_id=bank_id)
    results = []
    for campaign in campaigns:
        campaign.extracted_detail = service.ensure_nlp_processed(campaign)
        if campaign_type and campaign.extracted_detail.campaign_type != campaign_type:
            continue
        results.append(campaign)
    return results


@router.get("/campaigns/{campaign_id}", response_model=CampaignDetailResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    service: CampaignService = Depends(_campaign_service),
):
    """Belirtilen ID'ye sahip kampanyanın detaylarını döner."""
    campaign = service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Kampanya bulunamadı")
    campaign.extracted_detail = service.ensure_nlp_processed(campaign)
    return campaign
