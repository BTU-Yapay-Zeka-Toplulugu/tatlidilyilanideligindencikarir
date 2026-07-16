"""bank_parser modülü birim testleri."""

import tempfile
from pathlib import Path

from src.scraper.bank_parser import parse_bank_line, load_bank_list
from src.scraper.models import BankInfo


class TestParseBankLine:
    """parse_bank_line fonksiyonu testleri."""

    def test_valid_line(self) -> None:
        """Geçerli bir satırı doğru parse eder."""
        line = "1. ADİL KATILIM BANKASI A.Ş. - https://www.adilkatilim.com.tr/"
        result = parse_bank_line(line)
        assert result is not None
        assert result.id == 1
        assert result.name == "ADİL KATILIM BANKASI A.Ş."
        assert result.url == "https://www.adilkatilim.com.tr"

    def test_valid_line_with_path(self) -> None:
        """URL'de path bulunan satırı doğru parse eder."""
        line = "2. ALBARAKA TÜRK KATILIM BANKASI A.Ş. - https://www.albaraka.com.tr/tr"
        result = parse_bank_line(line)
        assert result is not None
        assert result.id == 2
        assert result.url == "https://www.albaraka.com.tr/tr"

    def test_empty_line(self) -> None:
        """Boş satırda None döndürür."""
        assert parse_bank_line("") is None
        assert parse_bank_line("   ") is None

    def test_invalid_format(self) -> None:
        """Geçersiz formatlı satırda None döndürür."""
        assert parse_bank_line("Bu geçersiz bir satır") is None

    def test_trailing_slash_stripped(self) -> None:
        """URL sonundaki / karakteri temizlenir."""
        line = "5. TEST BANKASI A.Ş. - https://www.test.com.tr/"
        result = parse_bank_line(line)
        assert result is not None
        assert not result.url.endswith("/")


class TestLoadBankList:
    """load_bank_list fonksiyonu testleri."""

    def test_load_actual_file(self) -> None:
        """Gerçek bank_sites.txt dosyasını yükler."""
        banks = load_bank_list()
        assert len(banks) == 10
        assert all(isinstance(b, BankInfo) for b in banks)

    def test_load_custom_file(self) -> None:
        """Özel dosya yolundan yükler."""
        content = (
            "1. TEST BANKA A.Ş. - https://www.test1.com.tr/\n"
            "2. TEST BANKA 2 A.Ş. - https://www.test2.com.tr/\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = Path(f.name)

        banks = load_bank_list(temp_path)
        assert len(banks) == 2
        temp_path.unlink()

    def test_missing_file(self) -> None:
        """Dosya bulunamazsa boş liste döner."""
        banks = load_bank_list(Path("/nonexistent/file.txt"))
        assert banks == []
