"""NLP bilgi çıkarımı modülü için birim testleri."""

import pytest
from src.nlp.extractor import (
    classify_campaign_type,
    extract_all_campaign_details,
    extract_amounts,
    extract_profit_share_rate,
    extract_term_months,
)


def test_extract_profit_share_rate():
    """Metin içindeki kâr payı oranlarını başarıyla çıkarır."""
    assert extract_profit_share_rate("Kâr payı oranımız %2.05 olarak belirlenmiştir.") == 2.05
    assert extract_profit_share_rate("Yıllık yüzde 3.5 kâr payı fırsatı.") == 3.5
    assert extract_profit_share_rate("Kazanmaya % 12,50 oranla başlayın.") == 12.5
    assert extract_profit_share_rate("Hoş geldin oranı 5%!") == 5.0
    assert extract_profit_share_rate("Hiçbir oran belirtilmemiş metin.") is None


def test_extract_profit_share_rate_format_varyasyonlari():
    """Farklı format varyasyonları (virgül/nokta, %/yüzde) doğru parse edilir."""
    assert extract_profit_share_rate("Kâr payı oranı %2,05") == 2.05
    assert extract_profit_share_rate("Getiri oranı yüzde 3") == 3.0
    assert extract_profit_share_rate("kâr oranı 4,5%") == 4.5


def test_extract_profit_share_rate_yanlis_atiflari_eler():
    """İlgisiz yüzdeler (iade, indirim, iştirak, LTV, devlet katkısı, vergi)
    yanlışlıkla kâr payı oranı olarak çıkarılmamalıdır (precision)."""
    # Nakit iade / cashback — kâr payı oranı değil
    assert extract_profit_share_rate("Biz Kart ile Dijital Üyeliklerde %75 Nakit İade Fırsatı!") is None
    # İndirim (büyük İ ile — Türkçe casefold hatası regresyon testi)
    assert extract_profit_share_rate("TROY Yıllık Paketinde %50 İndirim!") is None
    # Sermaye iştiraki
    assert extract_profit_share_rate("Sermayesine %70 oranında iştirak edilen bağlı ortaklık") is None
    # LTV / ekspertiz değeri
    assert extract_profit_share_rate("konutun ekspertiz değerinin %80'ine kadar finansman") is None
    # Devlet katkısı / desteği
    assert extract_profit_share_rate("Çeyiz Hesabı ile %25 devlet katkısından yararlanın") is None
    # Asgari ödeme
    assert extract_profit_share_rate("Asgari ödeme tutarı %100 olarak yansıtılır.") is None
    # Makul olmayan yüksek oran (>%50) elenir
    assert extract_profit_share_rate("oran %95 kâr payı") is None
    # Binlik ayraçlı sayı bir oran değildir (% 10.000 -> tutar)
    assert extract_profit_share_rate("Getiri Oranı % 10.000-20.000 arası bakiye") is None


def test_extract_term_months():
    """Metin içindeki vade sürelerini ay bazında başarıyla çıkarır."""
    assert extract_term_months("12 ay vade ile ödeme kolaylığı.") == 12
    assert extract_term_months("Tasarrufunuz 90 gün boyunca değerlensin.") == 3
    assert extract_term_months("3 aya varan kâr payı ödemeli hesap.") == 3
    assert extract_term_months("180 günlük katılma hesabı.") == 6
    assert extract_term_months("Vade bilgisi içermeyen metin.") is None
    # Edge-case: yıl ifadesi ay'a çevrilir
    assert extract_term_months("2 yıla varan vadeli katılma hesabı.") == 24
    assert extract_term_months("1.5 yıl vade") == 18


def test_extract_amounts():
    """Metin içindeki asgari, azami ve aralık tutarlarını başarıyla çıkarır."""
    # Tekil asgari tutar
    assert extract_amounts("En az 10.000 TL bakiye gerekmektedir.") == (10000.0, None)
    assert extract_amounts("100.000 TL ve üzeri mevduatlara özel.") == (100000.0, None)

    # Aralık tutarlar
    assert extract_amounts("50.000 TL ile 100.000 TL arasında bakiye.") == (50000.0, 100000.0)
    assert extract_amounts("10.000 - 50.000 TL arası limit.") == (10000.0, 50000.0)

    # Bin/Milyon çarpanlı tutarlar
    assert extract_amounts("En az 50 bin TL yatırılmalıdır.") == (50000.0, None)
    assert extract_amounts("Üst limit 1 milyon TL'dir.") == (None, 1000000.0)


def test_classify_campaign_type():
    """Metin içeriğine göre kampanya kategorisini doğru sınıflandırır."""
    assert classify_campaign_type("Katılma hesabı açarak kâr payı kazanın.") == "Katılma Hesabı / Mevduat"
    assert classify_campaign_type("İhtiyaç finansmanı 12 taksit fırsatıyla.") == "Finansman / Kredi"
    assert classify_campaign_type("Kredi kartı ile fatura ödemelerine bonus.") == "Kart / Ödeme"
    assert classify_campaign_type("Bireysel emeklilik sistemi ile birikim.") == "Sigorta / Emeklilik"
    assert classify_campaign_type("Alışveriş kampanyası detayları.") == "Diğer"


def test_extract_all_campaign_details():
    """Uçtan uca tüm kampanya detaylarını sözlük halinde çıkarır."""
    text = "Yeni müşterilerimize özel, en az 10.000 TL bakiye ile 32 gün vadeli %22.5 kâr payı fırsatı! Ücretsiz havale yapın."
    details = extract_all_campaign_details(text)

    assert details["profit_share_rate"] == 22.5
    assert details["term_months"] == 1
    assert details["min_amount"] == 10000.0
    assert details["target_audience"] == "yeni müşteri"
    assert "ücretsiz havale" in details["advantage_description"].lower()
    assert details["campaign_type"] == "Katılma Hesabı / Mevduat"
