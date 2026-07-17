"""Tüm kampanyalar için NLP çıkarımını yeniden çalıştırıp DB'yi günceller.

Çıkarım kurallarında (ör. kâr payı oranı bağlam-duyarlı hâle getirildiğinde)
değişiklik yapıldığında, DB'de saklanan eski (yanlış) ``ExtractedCampaignDetail``
kayıtlarının yeniden üretilmesi gerekir. Bu betik bunu yapar.

Kullanım:
    conda activate katilim-nlp
    python -m src.database.reprocess
"""

from datetime import datetime, timezone

from dotenv import load_dotenv

from src.database.connection import SessionLocal, init_db
from src.database.models import Campaign, ExtractedCampaignDetail
from src.nlp.extractor import extract_all_campaign_details


def reprocess() -> dict[str, int]:
    """Tüm kampanyaların çıkarılmış detaylarını yeniden hesaplar ve kaydeder."""
    load_dotenv()
    init_db()
    db = SessionLocal()
    updated = 0
    created = 0
    try:
        campaigns = db.query(Campaign).all()
        for campaign in campaigns:
            extracted = extract_all_campaign_details(campaign.raw_text)
            detail = (
                db.query(ExtractedCampaignDetail)
                .filter_by(campaign_id=campaign.id)
                .first()
            )
            if detail is None:
                detail = ExtractedCampaignDetail(campaign_id=campaign.id)
                db.add(detail)
                created += 1
            else:
                updated += 1
            detail.profit_share_rate = extracted["profit_share_rate"]
            detail.term_months = extracted["term_months"]
            detail.min_amount = extracted["min_amount"]
            detail.max_amount = extracted["max_amount"]
            detail.advantage_description = extracted["advantage_description"]
            detail.target_audience = extracted["target_audience"]
            detail.campaign_type = extracted["campaign_type"]
            detail.is_processed = True
            detail.processed_at = datetime.now(timezone.utc)
        db.commit()
        return {"total": len(campaigns), "updated": updated, "created": created}
    finally:
        db.close()


if __name__ == "__main__":
    result = reprocess()
    print(
        f"Yeniden işleme tamamlandı: {result['total']} kampanya "
        f"({result['updated']} güncellendi, {result['created']} oluşturuldu)."
    )
