"""Veritabanı yükleyici, kalite kontrol ve periyodik çalıştırıcı için birim testleri."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Bank, Campaign
from src.database.loader import load_cleaned_data_to_db
from src.scraper.check_data_quality import analyze_data_quality, analyze_db_quality
from src.scraper.periodic_runner import run_full_cycle


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


def test_load_cleaned_data_to_db(tmp_path, db_session):
    """Temizlenmiş JSON verileri veritabanına başarıyla yüklenir ve güncellenir."""
    # Test JSON dosyası oluştur
    test_data = [
        {
            "bank_name": "Test Katılım Bankası",
            "bank_url": "https://testkatilim.com.tr",
            "source_url": "https://testkatilim.com.tr/kampanya-1",
            "page_title": "Test Kampanya 1",
            "raw_text": "Bu bir test kampanya metnidir. En az yüz karakter içermelidir ki kalite testini geçsin ve veritabanına sorunsuz şekilde eklensin.",
        }
    ]
    json_file = tmp_path / "test_cleaned.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f)

    # Verileri yükle
    loaded = load_cleaned_data_to_db(json_file, db=db_session)
    assert loaded == 1

    # Banka ve kampanyayı doğrula
    bank = db_session.query(Bank).filter_by(name="Test Katılım Bankası").first()
    assert bank is not None
    assert bank.url == "https://testkatilim.com.tr"

    campaign = db_session.query(Campaign).filter_by(bank_id=bank.id).first()
    assert campaign is not None
    assert campaign.page_title == "Test Kampanya 1"
    assert campaign.content_length > 100


def test_analyze_data_quality(tmp_path):
    """Veri kalitesi analiz fonksiyonu eksik ve tam verileri doğru raporlar."""
    # Kaliteli veri seti
    good_data = [
        {
            "bank_name": "Test Bank",
            "source_url": "https://test.com/1",
            "page_title": "Title 1",
            "raw_text": "Yeterince uzun metin. " * 10,
        }
    ] * 60  # Raporun geçmesi için 50'den fazla kayıt gerekir
    good_json = tmp_path / "good.json"
    with open(good_json, "w", encoding="utf-8") as f:
        json.dump(good_data, f)

    assert analyze_data_quality(good_json) is True

    # Kalitesiz/Boş veri seti
    bad_data = [
        {
            "bank_name": "Test Bank",
            "source_url": "https://test.com/2",
            "page_title": "",
            "raw_text": "",
        }
    ]
    bad_json = tmp_path / "bad.json"
    with open(bad_json, "w", encoding="utf-8") as f:
        json.dump(bad_data, f)

    assert analyze_data_quality(bad_json) is False


def test_analyze_db_quality(db_session):
    """Veritabanı kalite analizi boş ve dolu tabloları doğru şekilde analiz eder."""
    # Henüz veri yokken kontrol
    assert analyze_db_quality(db=db_session) is False

    # Kaliteli veri ekle
    bank = Bank(name="Kaliteli Banka", url="https://kalite.com.tr")
    db_session.add(bank)
    db_session.flush()

    for i in range(60):  # 50'den fazla kayıt gerekir
        campaign = Campaign(
            bank_id=bank.id,
            source_url=f"https://kalite.com.tr/kampanya-{i}",
            page_title=f"Kampanya {i}",
            raw_text="Uzun metin " * 20,
            content_length=len("Uzun metin " * 20),
        )
        db_session.add(campaign)
    db_session.commit()

    assert analyze_db_quality(db=db_session) is True


@patch("src.scraper.periodic_runner.init_db")
@patch("src.scraper.periodic_runner.run_pipeline")
@patch("src.scraper.periodic_runner.clean_dataset")
@patch("src.scraper.periodic_runner.load_cleaned_data_to_db")
@patch("src.scraper.periodic_runner.analyze_data_quality")
@patch("src.scraper.periodic_runner.analyze_db_quality")
def test_run_full_cycle(
    mock_db_quality,
    mock_data_quality,
    mock_loader,
    mock_cleaner,
    mock_pipeline,
    mock_init_db,
):
    """Tam tarama döngüsü tüm alt adımları sırayla çalıştırır."""
    mock_cleaner.return_value = ("/path/to/cleaned.json", "/path/to/cleaned.csv")
    mock_data_quality.return_value = True
    mock_db_quality.return_value = True

    success = run_full_cycle()
    assert success is True
    mock_init_db.assert_called_once()
    mock_pipeline.assert_called_once()
    mock_cleaner.assert_called_once()
    mock_loader.assert_called_once()
    mock_data_quality.assert_called_once_with(Path("/path/to/cleaned.json"))
    mock_db_quality.assert_called_once()
