"""Metinlerden kâr payı, vade, tutar ve kampanya avantajlarını çıkaran modül."""

import re
from typing import Any


def extract_profit_share_rate(text: str) -> float | None:
    """Metinden kâr payı oranını (%) bularak float değer olarak döner."""
    if not text:
        return None

    patterns = [
        r"(?:%|yüzde)\s*(\d+(?:[\.,]\d+)?)",
        r"(\d+(?:[\.,]\d+)?)\s*(?:%|yüzde)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val_str = match.group(1).replace(",", ".")
            try:
                return float(val_str)
            except ValueError:
                continue
    return None


def extract_term_months(text: str) -> int | None:
    """Metinden vade bilgisini bularak ay cinsinden tam sayı olarak döner."""
    if not text:
        return None

    patterns = [
        r"(\d+(?:[\.,]\d+)?)\s*yıl(?:a|ı|ın)?\s*(?:varan|vade|boyunca|lık)?",
        r"(\d+)\s*ay(?:a|ı|ın)?\s*(?:varan|vade|boyunca|lık)?",
        r"(\d+)\s*gün(?:e|lük)?\s*(?:varan|vade|boyunca|lük)?",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1).replace(",", "."))
            token = match.group(0).lower()
            if "yıl" in token:
                return max(1, round(value * 12))
            if "gün" in token:
                return max(1, round(value / 30))
            return int(value)
    return None


def extract_amounts(text: str) -> tuple[float | None, float | None]:
    """Metinden asgari ve azami tutarları (TL cinsinden) bularak döner."""
    if not text:
        return None, None

    multipliers = {
        "bin": 1000,
        "milyon": 1000000,
        "milyar": 1000000000,
    }

    amount_pattern = r"(\d+(?:[\.,]\d+)?)\s*(bin|milyon|milyar)?\s*(?:TL|TRY|₺|dolar|usd|\$|euro|eur|€)?"

    range_patterns = [
        r"(\d+(?:[\.,]\d+)?\s*(?:bin|milyon)?)\s*(?:TL|TRY|₺)?\s*(?:ile|-|veya)\s*(\d+(?:[\.,]\d+)?\s*(?:bin|milyon)?)\s*(?:TL|TRY|₺)?\s*(?:arasında|arası|aralığında)",
        r"(\d+(?:[\.,]\d+)?\s*(?:bin|milyon)?)\s*(?:TL|TRY|₺)?\s*-\s*(\d+(?:[\.,]\d+)?\s*(?:bin|milyon)?)\s*(?:TL|TRY|₺)?",
    ]

    def parse_value(num_str: str, mult_str: str) -> float:
        """Sayı dizesini ve çarpanını float değere çevirir."""
        val = float(num_str.replace(".", "").replace(",", "."))
        if mult_str:
            val *= multipliers.get(mult_str.lower(), 1)
        return val

    for pattern in range_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            m1 = re.search(r"(\d+(?:[\.,]\d+)?)\s*(bin|milyon|milyar)?", match.group(1), re.IGNORECASE)
            m2 = re.search(r"(\d+(?:[\.,]\d+)?)\s*(bin|milyon|milyar)?", match.group(2), re.IGNORECASE)
            if m1 and m2:
                v1 = parse_value(m1.group(1), m1.group(2))
                v2 = parse_value(m2.group(1), m2.group(2))
                return min(v1, v2), max(v1, v2)

    min_patterns = [
        r"(?:en az|asgari|minimum|alt limit)\s*(?:olan)?\s*(\d+(?:[\.,]\d+)?\s*(?:bin|milyon)?)",
        r"(\d+(?:[\.,]\d+)?\s*(?:bin|milyon)?)\s*(?:TL|TRY|₺)?\s*(?:ve üzeri|ve üstü|üzerindeki|başlayan)",
    ]
    max_patterns = [
        r"(?:en fazla|azami|maksimum|üst limit|kadar)\s*(?:olan)?\s*(\d+(?:[\.,]\d+)?\s*(?:bin|milyon)?)",
        r"(\d+(?:[\.,]\d+)?\s*(?:bin|milyon)?)\s*(?:TL|TRY|₺)?\s*(?:geçmeyen|aşmayan|kadar)",
    ]

    min_val = None
    for pattern in min_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            m = re.search(r"(\d+(?:[\.,]\d+)?)\s*(bin|milyon|milyar)?", match.group(1), re.IGNORECASE)
            if m:
                min_val = parse_value(m.group(1), m.group(2))
                break

    max_val = None
    for pattern in max_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            m = re.search(r"(\d+(?:[\.,]\d+)?)\s*(bin|milyon|milyar)?", match.group(1), re.IGNORECASE)
            if m:
                max_val = parse_value(m.group(1), m.group(2))
                break

    if min_val is None and max_val is None:
        matches = re.findall(amount_pattern, text, re.IGNORECASE)
        if matches:
            vals = [parse_value(m[0], m[1]) for m in matches]
            valid_vals = [v for v in vals if v >= 100]
            if valid_vals:
                min_val = min(valid_vals)

    return min_val, max_val


def extract_target_audience(text: str) -> str | None:
    """Metinden campaigns hedef kitlesini tespit eder."""
    if not text:
        return None

    keywords = {
        "esnaf": ["esnaf", "kobi", "işletme", "ticari", "serbest meslek"],
        "emekli": ["emekli", "emekliler", "emeklilik"],
        "genç": ["genç", "öğrenci", "üniversite", "gençler"],
        "yeni müşteri": ["yeni müşteri", "ilk defa", "ilk kez", "müşterimiz olan"],
        "çiftçi": ["çiftçi", "tarım", "üretici"],
    }

    detected = []
    for audience, words in keywords.items():
        for word in words:
            if re.search(rf"\b{word}", text, re.IGNORECASE):
                detected.append(audience)
                break

    return ", ".join(detected) if detected else "Herkes"


def split_sentences(text: str) -> list[str]:
    """Metni cümlelere böler, sayılar içindeki noktaları göz ardı eder."""
    # Nokta, ünlem, soru işaretlerinden sonra gelen büyük harf veya metin sonu ile böl
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜa-zçğıöşü])", text)
    return [s.strip() for s in sentences if s.strip()]


def extract_advantage(text: str) -> str | None:
    """Metinden kampanya avantajını/fırsatını çıkaran kural tabanlı fonksiyon."""
    if not text:
        return None

    sentences = split_sentences(text)

    # Güçlü avantaj anahtar kelimeleri
    strong_keywords = [
        "ücretsiz",
        "masrafsız",
        "komisyonsuz",
        "indirimli",
        "hediye",
        "iade",
        "puan",
        "promosyon",
        "kart aidatı yok",
        "faizsiz",
        "katkı payı",
    ]

    # Zayıf avantaj anahtar kelimeleri
    weak_keywords = [
        "fırsat",
        "avantaj",
        "ayrıcalık",
        "özel",
    ]

    # Önce güçlü anahtar kelimeleri ara
    for sentence in sentences:
        if any(kw in sentence.lower() for kw in strong_keywords):
            return sentence

    # Güçlü yoksa zayıf olanları ara
    for sentence in sentences:
        if any(kw in sentence.lower() for kw in weak_keywords):
            return sentence

    # Eşleşen cümle bulunamadıysa ilk cümleyi dön
    if sentences:
        return sentences[0]

    return "Avantaj belirtilmemiş"


def classify_campaign_type(text: str) -> str:
    """Metin içeriğine göre kampanyanın türünü sınıflandırır."""
    if not text:
        return "Diğer"

    text_lower = text.lower()
    categories = {
        # Kredi kartı gibi ödeme araçları taksit vb içerebildiğinden finansmandan önce taranmalıdır
        "Kart / Ödeme": [
            "kredi kartı",
            "kredi kart",
            "kartı",
            "kartla",
            "kartın",
            "aidat",
            "bonus",
            "puan",
            " chip ",
            "temassız",
            "ödeme",
            "fatura",
        ],
        "Katılma Hesabı / Mevduat": [
            "katılma hesabı",
            "katılma hesap",
            "kâr payı",
            "kar payi",
            "tasarruf",
            "mevduat",
            "yatırım hesabı",
            "hoş geldin",
        ],
        "Sigorta / Emeklilik": [
            "sigorta",
            "bes",
            "bireysel emeklilik",
            "kasko",
        ],
        "Finansman / Kredi": [
            "finansman",
            "kredi",
            "taksit",
            "konut",
            "taşıt",
            "ihtiyaç",
            "leasing",
            "borç",
        ],
    }

    for category, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            return category

    return "Diğer"


def extract_all_campaign_details(text: str) -> dict[str, Any]:
    """Metinden tüm kampanya detaylarını çıkararak bir sözlük olarak döner."""
    min_amt, max_amt = extract_amounts(text)
    return {
        "profit_share_rate": extract_profit_share_rate(text),
        "term_months": extract_term_months(text),
        "min_amount": min_amt,
        "max_amount": max_amt,
        "advantage_description": extract_advantage(text),
        "target_audience": extract_target_audience(text),
        "campaign_type": classify_campaign_type(text),
    }
