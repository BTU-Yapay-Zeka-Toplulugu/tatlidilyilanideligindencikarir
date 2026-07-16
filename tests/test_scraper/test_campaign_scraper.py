"""campaign_scraper modülü birim testleri."""

from bs4 import BeautifulSoup

from src.scraper.campaign_scraper import (
    _clean_text,
    extract_page_title,
    extract_main_content,
)


SAMPLE_HTML_WITH_ARTICLE = """
<html>
<head><title>Kampanya Detayı - Test Banka</title></head>
<body>
    <nav>Menü burada</nav>
    <article>
        <h1>Konut Finansmanı Kampanyası</h1>
        <p>Aylık %1,29 kâr payı oranıyla konut finansmanı fırsatı!</p>
        <p>36 ay vade ile 500.000 TL'ye kadar finansman imkanı sunulmaktadır.</p>
        <p>Başvuru tarihi: 01.07.2026 - 31.08.2026</p>
    </article>
    <footer>Footer burada</footer>
    <script>var x = 1;</script>
</body>
</html>
"""

SAMPLE_HTML_BODY_ONLY = """
<html>
<body>
    <div>
        <h1>Genel Sayfa</h1>
        <p>Bu sayfada herhangi bir article veya main etiketi bulunmamaktadır.
        Ancak yeterli miktarda içerik bulunmaktadır ve body'den çıkarılmalıdır.
        Kampanya oranları burada listelenmiştir.</p>
    </div>
</body>
</html>
"""

SAMPLE_HTML_H1_TITLE = """
<html>
<head><title></title></head>
<body>
    <h1>H1 Başlık</h1>
    <main>
        <p>Ana içerik metni burada yer almaktadır. Yeterli karakter sayısına ulaşmak
        için biraz daha uzun bir metin gerekiyor.</p>
    </main>
</body>
</html>
"""


class TestCleanText:
    """_clean_text fonksiyonu testleri."""

    def test_removes_extra_whitespace(self) -> None:
        """Fazla boşluk ve boş satırları temizler."""
        text = "  Satır 1  \n\n\n  Satır 2  \n  \n  Satır 3  "
        result = _clean_text(text)
        assert result == "Satır 1\nSatır 2\nSatır 3"

    def test_empty_string(self) -> None:
        """Boş string boş döner."""
        assert _clean_text("") == ""


class TestExtractPageTitle:
    """extract_page_title fonksiyonu testleri."""

    def test_title_from_tag(self) -> None:
        """<title> etiketinden başlık çıkarır."""
        soup = BeautifulSoup(SAMPLE_HTML_WITH_ARTICLE, "html.parser")
        title = extract_page_title(soup)
        assert "Kampanya Detayı" in title

    def test_title_from_h1_fallback(self) -> None:
        """<title> boşsa <h1>'den başlık çıkarır."""
        soup = BeautifulSoup(SAMPLE_HTML_H1_TITLE, "html.parser")
        title = extract_page_title(soup)
        assert title == "H1 Başlık"


class TestExtractMainContent:
    """extract_main_content fonksiyonu testleri."""

    def test_extracts_from_article(self) -> None:
        """<article> etiketinden içerik çıkarır."""
        soup = BeautifulSoup(SAMPLE_HTML_WITH_ARTICLE, "html.parser")
        content = extract_main_content(soup)
        assert "kâr payı" in content
        assert "500.000 TL" in content

    def test_excludes_nav_footer_script(self) -> None:
        """Nav, footer ve script içeriklerini hariç tutar."""
        soup = BeautifulSoup(SAMPLE_HTML_WITH_ARTICLE, "html.parser")
        content = extract_main_content(soup)
        assert "Menü burada" not in content
        assert "Footer burada" not in content
        assert "var x" not in content

    def test_fallback_to_body(self) -> None:
        """Article/main yoksa body'den çıkarır."""
        soup = BeautifulSoup(SAMPLE_HTML_BODY_ONLY, "html.parser")
        content = extract_main_content(soup)
        assert "Kampanya oranları" in content

    def test_extracts_from_main(self) -> None:
        """<main> etiketinden içerik çıkarır."""
        soup = BeautifulSoup(SAMPLE_HTML_H1_TITLE, "html.parser")
        content = extract_main_content(soup)
        assert "Ana içerik metni" in content
