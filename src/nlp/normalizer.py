"""Oran, tutar ve vade gibi farklı formatlardaki değerleri standart gösterimlere dönüştüren normalizasyon modülü."""

import re


def normalize_profit_share_rate(rate: float | None) -> str:
    """Float kâr payı oranını standart %X.XX gösterimine normalize eder."""
    if rate is None:
        return "Belirtilmemiş"
    return f"%{rate:.2f}"


def normalize_amount(amount: float | None) -> str:
    """Float tutar değerini standart binlik ayraçlı ve TL simgeli gösterime normalize eder."""
    if amount is None:
        return "Belirtilmemiş"
    return f"{amount:,.0f} TL".replace(",", ".")


def normalize_term(months: int | None) -> str:
    """Vade değerini ay cinsinden standart gösterime normalize eder."""
    if months is None:
        return "Belirtilmemiş"
    return f"{months} Ay"


def normalize_text_numbers(text: str) -> str:
    """Metin içindeki Türkçe sayı ve oran yazımlarını standart biçime dönüştürür (örn: yüzde 5 -> %5)."""
    if not text:
        return ""

    # 'yüzde X' -> '%X'
    text = re.sub(r"yüzde\s*(\d+)", r"%\1", text, flags=re.IGNORECASE)

    # 'X TL' / 'X ₺' / 'X TRY' -> 'X TL'
    text = re.sub(r"(\d+)\s*(?:TRY|₺)", r"\1 TL", text, flags=re.IGNORECASE)

    return text
