"""Metinlerden kâr payı, vade, tutar ve kampanya avantajlarını çıkaran modül."""

import re
from typing import Any


def _tr_fold(text: str) -> str:
    """Türkçe-duyarlı küçük harfe çevirme.

    Python'un varsayılan ``str.lower()`` metodu 'İ' harfini 'i' + birleşik
    nokta olarak dönüştürür ('i̇ndirim'), bu da 'indirim' gibi anahtar
    kelime aramalarını sessizce başarısız kılar. ``casefold`` bu sorunu
    çözer; ayrıca 'I' -> 'ı' eşlemesi de yapılır.
    """
    return text.replace("İ", "i").replace("I", "ı").casefold()


# Kâr payı oranı bağlamını doğrulayan / eleyen anahtar kelimeler.
# Katılım bankacılığında "%70 iştirak", "%75 nakit iade", "%80 ekspertiz
# değeri (LTV)", "asgari ödeme %100" gibi ifadeler kâr payı ORANI DEĞİLDİR;
# bu tür yakın bağlamlar elenmelidir.
_PROFIT_RATE_CONTEXT = (
    "kâr payı",
    "kar payi",
    "kâr oranı",
    "kar orani",
    "getiri",
    "oran",  # "oranla", "hoş geldin oranı" vb.
    "yıllık",
    "aylık",
)
# GüçlÜ (sadece kâr payı/getiri) bağlam anahtarları — bir disqualifier'ın
# yanında bile olsa oranı kabul ettirir (ör. "yıllık" tek başına yetmez).
_PROFIT_RATE_STRONG_CONTEXT = (
    "kâr payı", "kar payi", "kâr oranı", "kar orani", "getiri", "oran",
)
_PROFIT_RATE_DISQUALIFIERS = (
    "iade",  # nakit iade / cashback
    "indirim",
    "komisyon",
    "iştirak",  # sermaye iştiraki
    "istirak",
    "asgari ödeme",
    "asgari odeme",
    "ekspertiz",  # ekspertiz değerinin %X'i (LTV)
    "değerine oranı",
    "degerine orani",
    "değerinin",
    "degerinin",
    "değer x",  # "Değer x %70" gibi LTV tabloları
    "deger x",
    "ltv",
    "peşinat",
    "pesinat",
    "vergi",
    "bakiyenin",  # "bakiyenin %50'sine kadar çekim"
    "çekim",
    "cekim",
    "geri alınır",  # kâr payı clawback (ceza), oran değil
    "geri alinir",
    "alışveriş",  # mağaza alışverişinde %X (indirim/iade)
    "alisveris",
    "mağaza",
    "magaza",
    "değere oranı",  # LTV: taşıt/konut değerine oranı
    "degere orani",
    "değer <",  # LTV tablosu "değer < ... %70"
    "deger <",
    "devlet katkı",  # BES/çeyiz devlet katkısı
    "devlet katki",
    "devlet deste",  # "devlet desteği/desteğiyle" (ğ nedeniyle stem)
    "mil kazan",  # mil/uçuş puanı kazanımı
    "stopaj",  # stopaj/vergi oranı
    "kdv",
    "puan",  # altın puan / bonus puan
    "harcama tutarı",  # ödül = harcamanın %X'i
    "harcama tutari",
    "harcamalar",
    "ödül",
    "odul",
)
# Katılım bankası kâr payı oranı için makul üst sınır (bunun üstü büyük
# olasılıkla yanlış atıf: iade/indirim/iştirak yüzdesidir).
_PROFIT_RATE_MAX = 50.0


def extract_profit_share_rate(text: str) -> float | None:
    """Metinden kâr payı oranını (%) bağlam-duyarlı biçimde çıkarır.

    Yalnızca kâr payı/getiri/oran bağlamına yakın ve makul (<= %50) yüzdeler
    kabul edilir; nakit iade, indirim, iştirak, ekspertiz/LTV, asgari ödeme
    gibi ilgisiz yüzdeler elenir. Böylece "%75 nakit iade" veya
    "%70 iştirak" gibi ifadeler yanlışlıkla kâr payı oranı sayılmaz.
    """
    if not text:
        return None

    # Metindeki tüm yüzde ifadelerini konumlarıyla birlikte bul.
    percent_pattern = re.compile(
        r"(?:%|yüzde)\s*(\d+(?:[\.,]\d+)?)|(\d+(?:[\.,]\d+)?)\s*(?:%|yüzde)",
        re.IGNORECASE,
    )

    for match in percent_pattern.finditer(text):
        raw_num = match.group(1) or match.group(2) or ""
        # Binlik ayraçlı sayı (ör. "10.000") bir ORAN değil, tutardır: ele.
        if re.fullmatch(r"\d{1,3}\.\d{3}", raw_num):
            continue
        val_str = raw_num.replace(",", ".")
        try:
            value = float(val_str)
        except ValueError:
            continue

        # Makul olmayan (çok yüksek) yüzdeleri ele.
        if value <= 0 or value > _PROFIT_RATE_MAX:
            continue

        # Kâr payı bağlamını DAR pencerede ara — oran, anahtar kelimeye
        # bitişik olmalı (LTV/vergi tablolarındaki uzak yüzdelerden kaçınmak
        # için pencere sıkı tutulur).
        ctx_window = _tr_fold(text[max(0, match.start() - 28):min(len(text), match.end() + 20)])
        has_context = any(ctx in ctx_window for ctx in _PROFIT_RATE_CONTEXT)
        has_strong_context = any(ctx in ctx_window for ctx in _PROFIT_RATE_STRONG_CONTEXT)

        # İlgisiz bağlamı GENİŞ pencerede tara (indirim/iade/LTV/clawback/
        # devlet katkısı/stopaj/kdv ifadeleri yüzdeden biraz uzakta olabilir).
        # Zayıf bağlam ("yıllık"/"aylık") varsa ve bir disqualifier yakındaysa
        # oranı ele. Yalnızca GÜÇLÜ bağlam (kâr payı/getiri/oran) bitişikse,
        # bu disqualifier başka bir oranın gürültüsü olabilir — kabul et
        # (ADR-013 edge-case: aynı cümlede birden fazla oran).
        if not has_strong_context:
            disq_window = _tr_fold(text[max(0, match.start() - 90):min(len(text), match.end() + 70)])
            if any(bad in disq_window for bad in _PROFIT_RATE_DISQUALIFIERS):
                continue

        if has_context:
            return value

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

    folded = _tr_fold(text)
    detected = []
    for audience, words in keywords.items():
        for word in words:
            if re.search(rf"\b{re.escape(_tr_fold(word))}", folded):
                detected.append(audience)
                break

    return ", ".join(detected) if detected else "Herkes"


def extract_dates(text: str) -> tuple[str | None, str | None]:
    """Metinden başlangıç/bitiş tarihlerini (ISO YYYY-MM-DD) bularak döner.

    Türkçe tarih formatlarını (GG.AA.YYYY, GG/AA/YYYY, "1 Ocak 2026",
    "31 Aralık 2026 tarihine kadar") ve yıl-only ifadeleri destekler.
    """
    if not text:
        return None, None

    month_map = {
        "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4,
        "mayıs": 5, "mayis": 5, "haziran": 6, "temmuz": 7, "ağustos": 8,
        "agustos": 8, "eylül": 9, "eylul": 9, "ekim": 10, "kasım": 11,
        "kasim": 11, "aralık": 12, "aralik": 12,
    }

    found: list[str] = []

    # 1) GG.AA.YYYY veya GG/AA/YYYY
    for m in re.finditer(r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b", text):
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            found.append(f"{y:04d}-{mo:02d}-{d:02d}")

    # 2) "DD Ay YYYY" veya "DD Ay YYYY tarihine kadar"
    for m in re.finditer(
        r"\b(\d{1,2})\s+([a-zçğıöşü]+)\s+(\d{4})\b", text, re.IGNORECASE
    ):
        gm = month_map.get(_tr_fold(m.group(2)))
        if gm:
            found.append(f"{int(m.group(3)):04d}-{gm:02d}-{int(m.group(1)):02d}")

    if not found:
        return None, None
    # Tekrarları kaldır, korunmuş sırada
    seen: set[str] = set()
    uniq = [x for x in found if not (x in seen or seen.add(x))]
    return uniq[0], uniq[-1] if len(uniq) > 1 else None


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
        folded = _tr_fold(sentence)
        if any(_tr_fold(kw) in folded for kw in strong_keywords):
            return sentence

    # Güçlü yoksa zayıf olanları ara
    for sentence in sentences:
        folded = _tr_fold(sentence)
        if any(_tr_fold(kw) in folded for kw in weak_keywords):
            return sentence

    # Eşleşen cümle bulunamadıysa ilk cümleyi dön
    if sentences:
        return sentences[0]

    return "Avantaj belirtilmemiş"


def classify_campaign_type(text: str) -> str:
    """Metin içeriğine göre kampanyanın türünü sınıflandırır."""
    if not text:
        return "Diğer"

    text_lower = _tr_fold(text)
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
        if any(_tr_fold(kw) in text_lower for kw in keywords):
            return category

    return "Diğer"


def extract_all_campaign_details(text: str) -> dict[str, Any]:
    """Metinden tüm kampanya detaylarını çıkararak bir sözlük olarak döner.

    Bu fonksiyon yalnızca KURAL TABANLI (regex) katmanı içerir; birleşik
    regex+model hattı için ``src.nlp.pipeline.run_extraction_pipeline``
    kullanılmalıdır (ADR-013).
    """
    min_amt, max_amt = extract_amounts(text)
    start_date, end_date = extract_dates(text)
    return {
        "profit_share_rate": extract_profit_share_rate(text),
        "term_months": extract_term_months(text),
        "min_amount": min_amt,
        "max_amount": max_amt,
        "start_date": start_date,
        "end_date": end_date,
        "advantage_description": extract_advantage(text),
        "target_audience": extract_target_audience(text),
        "campaign_type": classify_campaign_type(text),
    }
