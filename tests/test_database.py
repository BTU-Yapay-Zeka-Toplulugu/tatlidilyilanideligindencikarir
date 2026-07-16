"""Veritabanı modelleri ve bağlantı yönetimi için birim testleri."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Bank, Campaign, ExtractedCampaignDetail


@pytest.fixture(name="db_session")
def fixture_db_session():
    """Testler için bellek içi SQLite veritabanı oturumu oluşturur."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_bank_creation(db_session):
    """Banka kaydı başarıyla oluşturulur ve sorgulanır."""
    bank = Bank(name="Adil Katılım Bankası", url="https://www.adilkatilim.com.tr")
    db_session.add(bank)
    db_session.commit()

    saved_bank = db_session.query(Bank).filter_by(name="Adil Katılım Bankası").first()
    assert saved_bank is not None
    assert saved_bank.url == "https://www.adilkatilim.com.tr"
    assert saved_bank.id is not None


def test_campaign_creation(db_session):
    """Kampanya kaydı banka ilişkisiyle başarıyla oluşturulur."""
    bank = Bank(name="Türkiye Finans", url="https://www.turkiyefinans.com.tr")
    db_session.add(bank)
    db_session.commit()

    campaign = Campaign(
        bank_id=bank.id,
        source_url="https://www.turkiyefinans.com.tr/kampanya1",
        page_title="Tasarruf Kampanyası",
        raw_text="Bu bir tasarruf hesabı kampanyasıdır.",
        content_length=len("Bu bir tasarruf hesabı kampanyasıdır."),
    )
    db_session.add(campaign)
    db_session.commit()

    saved_campaign = db_session.query(Campaign).first()
    assert saved_campaign is not None
    assert saved_campaign.bank.name == "Türkiye Finans"
    assert saved_campaign.page_title == "Tasarruf Kampanyası"


def test_extracted_details_creation(db_session):
    """Kampanyanın çıkarılan NLP detayları başarıyla kaydedilir."""
    bank = Bank(name="Albaraka Türk", url="https://www.albaraka.com.tr")
    db_session.add(bank)
    db_session.commit()

    campaign = Campaign(
        bank_id=bank.id,
        source_url="https://www.albaraka.com.tr/kampanya",
        page_title="Kar Payı Kampanyası",
        raw_text="Kar payı oranı %2.5 vade 12 ay.",
        content_length=len("Kar payı oranı %2.5 vade 12 ay."),
    )
    db_session.add(campaign)
    db_session.commit()

    detail = ExtractedCampaignDetail(
        campaign_id=campaign.id,
        profit_share_rate=2.5,
        term_months=12,
        campaign_type="Mevduat",
        is_processed=True,
    )
    db_session.add(detail)
    db_session.commit()

    saved_detail = db_session.query(ExtractedCampaignDetail).first()
    assert saved_detail is not None
    assert saved_detail.profit_share_rate == 2.5
    assert saved_detail.term_months == 12
    assert saved_detail.campaign.page_title == "Kar Payı Kampanyası"


def test_cascade_delete(db_session):
    """Banka silindiğinde ilişkili tüm kampanyalar otomatik olarak silinir."""
    bank = Bank(name="Vakıf Katılım", url="https://www.vakifkatilim.com.tr")
    db_session.add(bank)
    db_session.commit()

    campaign = Campaign(
        bank_id=bank.id,
        source_url="https://www.vakifkatilim.com.tr/kampanya",
        page_title="Vakıf Kampanya",
        raw_text="Vakıf katılım kampanya metni.",
        content_length=len("Vakıf katılım kampanya metni."),
    )
    db_session.add(campaign)
    db_session.commit()

    # Bankayı sil
    db_session.delete(bank)
    db_session.commit()

    # Kampanyanın silindiğini doğrula
    assert db_session.query(Campaign).count() == 0
