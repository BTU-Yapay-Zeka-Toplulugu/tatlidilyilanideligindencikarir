"""data_cleaner modülü için birim testleri."""

import json
import pytest
from pathlib import Path

from src.scraper.data_cleaner import (
    normalize_unicode,
    remove_control_characters,
    collapse_whitespace,
    remove_navigation_noise,
    clean_text,
    clean_record,
    clean_dataset,
)


class TestNormalizeUnicode:
    """Unicode NFC normalizasyonu testleri."""

    def test_turkish_chars_preserved(self):
        """Türkçe karakterler doğru şekilde korunur."""
        text = "Kâr payı oranı şu şekildedir: %2,05"
        result = normalize_unicode(text)
        assert "Kâr" in result
        assert "şu" in result
        assert "%2,05" in result

    def test_nfc_normalization(self):
        """NFC normalizasyonu decomposed karakterleri birleştirir."""
        # ş harfi decomposed formda: s + combining cedilla
        decomposed = "s\u0327"
        result = normalize_unicode(decomposed)
        # NFC formu: ş
        assert result == "\u015f"


class TestRemoveControlCharacters:
    """Kontrol karakteri kaldırma testleri."""

    def test_removes_null_bytes(self):
        """Null byte'lar kaldırılır."""
        assert remove_control_characters("abc\x00def") == "abcdef"

    def test_preserves_newlines_and_tabs(self):
        """Satır sonu ve tab karakterleri korunur."""
        text = "satır1\nsatır2\ttab"
        result = remove_control_characters(text)
        assert "\n" in result
        assert "\t" in result

    def test_removes_various_control_chars(self):
        """Çeşitli kontrol karakterleri kaldırılır."""
        text = "test\x01\x02\x03\x7fdata"
        result = remove_control_characters(text)
        assert result == "testdata"


class TestCollapseWhitespace:
    """Boşluk normalizasyonu testleri."""

    def test_multiple_spaces(self):
        """Ardışık boşluklar tek boşluğa indirgenir."""
        assert collapse_whitespace("çok   fazla    boşluk") == "çok fazla boşluk"

    def test_multiple_newlines(self):
        """3+ ardışık boş satır çift satır sonuna indirgenir."""
        text = "paragraf1\n\n\n\n\nparagraf2"
        result = collapse_whitespace(text)
        assert result == "paragraf1\n\nparagraf2"

    def test_leading_trailing_whitespace(self):
        """Baş ve son boşluklar kaldırılır."""
        assert collapse_whitespace("  test  ") == "test"


class TestRemoveNavigationNoise:
    """Navigasyon gürültüsü temizleme testleri."""

    def test_removes_cookie_notice(self):
        """Çerez uyarıları kaldırılır."""
        text = "İçerik\nÇerez politikası hakkında bilgi\nDevam"
        result = remove_navigation_noise(text)
        assert "Çerez" not in result
        assert "İçerik" in result

    def test_removes_copyright(self):
        """Telif hakkı metinleri kaldırılır."""
        text = "İçerik\nCopyright © 2026 Banka A.Ş.\nDevam"
        result = remove_navigation_noise(text)
        assert "Copyright" not in result

    def test_preserves_normal_text(self):
        """Normal metin değiştirilmeden kalır."""
        text = "Kampanya detayları burada"
        assert remove_navigation_noise(text) == text


class TestCleanText:
    """Entegre metin temizleme testleri."""

    def test_full_pipeline(self):
        """Tüm temizleme adımları sırayla uygulanır."""
        text = "  Kampanya\x00  bilgileri   \n\n\n\n\ndetaylar  "
        result = clean_text(text)
        assert "\x00" not in result
        assert "  " not in result  # Ardışık boşluk yok
        assert result.startswith("Kampanya")
        assert "detaylar" in result


class TestCleanRecord:
    """Kayıt temizleme testleri."""

    def test_valid_record(self):
        """Geçerli kayıt temizlenerek döner."""
        record = {
            "bank_id": 1,
            "bank_name": "Test Bankası",
            "source_url": "https://example.com",
            "page_title": "  Test  Kampanya  ",
            "raw_text": "Bu bir test kampanya metnidir. " * 5,
            "content_length": 150,
        }
        result = clean_record(record)
        assert result is not None
        assert result["page_title"] == "Test Kampanya"
        assert result["content_length"] == len(result["raw_text"])

    def test_empty_text_returns_none(self):
        """Boş metin içeren kayıt None döner."""
        record = {"raw_text": "", "source_url": "test"}
        assert clean_record(record) is None

    def test_short_text_returns_none(self):
        """Çok kısa metin içeren kayıt None döner."""
        record = {"raw_text": "kısa", "source_url": "test"}
        assert clean_record(record) is None


class TestCleanDataset:
    """Veri seti temizleme testleri."""

    def test_clean_dataset_creates_files(self, tmp_path):
        """Temiz veri seti JSON ve CSV olarak kaydedilir."""
        # Ham veri oluştur
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        processed_dir = tmp_path / "processed"

        raw_data = [
            {
                "bank_id": 1,
                "bank_name": "Test Bankası",
                "source_url": "https://example.com/kampanya/1",
                "page_title": "Test Kampanya",
                "raw_text": "Bu bir test kampanya detay metnidir. Çok önemli bilgiler içerir. " * 3,
                "scraped_at": "2026-07-16T12:00:00",
                "content_length": 200,
            },
            {
                "bank_id": 1,
                "bank_name": "Test Bankası",
                "source_url": "https://example.com/kampanya/2",
                "page_title": "Boş Kampanya",
                "raw_text": "",
                "scraped_at": "2026-07-16T12:00:00",
                "content_length": 0,
            },
        ]

        input_path = raw_dir / "campaigns_test.json"
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False)

        # Temizle
        result = clean_dataset(input_path=input_path, output_dir=processed_dir)

        assert result is not None
        assert result.exists()

        # JSON kontrolü
        with open(result, "r", encoding="utf-8") as f:
            cleaned = json.load(f)
        assert len(cleaned) == 1  # Boş kayıt atlanmış olmalı
        assert cleaned[0]["bank_name"] == "Test Bankası"

        # CSV kontrolü
        csv_path = processed_dir / "campaigns_cleaned.csv"
        assert csv_path.exists()

    def test_clean_dataset_no_input(self, tmp_path):
        """Dosya bulunamadığında None döner."""
        result = clean_dataset(
            input_path=tmp_path / "nonexistent.json",
            output_dir=tmp_path / "out",
        )
        assert result is None
