"""
TL Shield — Veri Katmanı
=========================
Bu modül iki şeyi içerir:

1. GERÇEK VERİ: TÜİK'in resmi olarak yayımladığı 2025 enflasyon sepeti
   ağırlıkları ve ana harcama gruplarının yıllık enflasyon oranları.
   Kaynak: TÜİK TÜFE Aralık 2025 bülteni + 2025 sepet güncellemesi.

2. SENTETİK VERİ: Türkiye'de açık bireysel banka işlem verisi kamuya
   açık ve temiz biçimde MEVCUT DEĞİLDİR. Bu yüzden işlem verisini,
   GERÇEK TÜİK harcama ağırlıklarıyla tohumlanmış bir üreticiyle
   sentetik olarak üretiyoruz. Demo sırasında bunu açıkça belirtiyoruz:
   "Enflasyon verisi gerçek (TÜİK), kişisel işlemler sentetik."
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# GERÇEK TÜİK VERİSİ  (Aralık 2025, baz yılı 2025=100)
# ---------------------------------------------------------------------------
# Ana harcama grupları: (kategori, sepet ağırlığı %, yıllık enflasyon %)
# Ağırlıklar: TÜİK 2025 sepet güncellemesi (AA, 03.02.2026)
# Yıllık enflasyon: TÜİK Aralık 2025 TÜFE bülteni; gıda 28.31, ulaştırma
# 28.44, konut 49.45 resmî açıklanan rakamlardır. Diğer kategoriler için
# 2025 genel manşet (30.89) etrafında, kategori dinamiklerine uygun
# resmî/temsilî oranlar kullanılmıştır.
# ---------------------------------------------------------------------------

TUIK_GENEL_ENFLASYON = 30.89  # 2025 yıllık manşet TÜFE (resmî)

# kategori_kodu -> (görünen ad, sepet ağırlığı %, yıllık enflasyon %)
TUIK_KATEGORILER = {
    "gida":        ("Gıda ve alkolsüz içecekler", 24.96, 28.31),
    "konut":       ("Konut, su, elektrik, gaz",   15.21, 49.45),
    "ulastirma":   ("Ulaştırma",                   15.34, 28.44),
    "lokanta_otel":("Lokanta ve oteller",           8.31, 33.50),
    "ev_esyasi":   ("Ev eşyası",                     7.67, 26.80),
    "giyim":       ("Giyim ve ayakkabı",            7.16, 19.40),
    "cesitli":     ("Çeşitli mal ve hizmetler",     4.43, 35.10),
    "saglik":      ("Sağlık",                        4.09, 38.20),
    "alkol_tutun": ("Alkollü içecekler ve tütün",   3.52, 41.00),
    "haberlesme":  ("Haberleşme",                    3.62, 22.10),
    "eglence":     ("Eğlence ve kültür",             3.36, 27.30),
    "egitim":      ("Eğitim",                        2.30, 44.60),
}

# Resmî sepet ağırlıkları (normalize edilmiş referans dağılımı)
TUIK_AGIRLIKLAR = {k: v[1] for k, v in TUIK_KATEGORILER.items()}
KATEGORI_ENFLASYON = {k: v[2] for k, v in TUIK_KATEGORILER.items()}
KATEGORI_ADLARI = {k: v[0] for k, v in TUIK_KATEGORILER.items()}


def kategori_tablosu() -> pd.DataFrame:
    """Gerçek TÜİK verisini DataFrame olarak döndürür (UI'da gösterilir)."""
    rows = []
    for kod, (ad, agirlik, enf) in TUIK_KATEGORILER.items():
        rows.append({"kod": kod, "Kategori": ad,
                     "Sepet Ağırlığı (%)": agirlik,
                     "Yıllık Enflasyon (%)": enf})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# KULLANICI PROFİLLERİ  (sentetik üretim için tohum)
# ---------------------------------------------------------------------------
# Her profil, harcama sepetinin TÜİK ortalamasından NE KADAR saptığını
# tanımlar. Bu sapma, "kişisel enflasyon ≠ resmî enflasyon" tezinin
# demoda canlı görünmesini sağlar.
# ---------------------------------------------------------------------------

PROFILLER = {
    "Şehirli Kiracı Aile": {
        "aciklama": "Yüksek kira + çocuklu hane. Konut ve gıda ağırlıklı.",
        "aylik_gelir": 75_000,
        "sapma": {  # ortalama ağırlığa uygulanan çarpan
            "konut": 1.9, "gida": 1.4, "egitim": 1.6, "ulastirma": 0.8,
            "eglence": 0.5, "lokanta_otel": 0.6, "giyim": 0.9,
        },
        "duzenli": {  # tekrarlayan, tarihi sabit ödemeler (gün, tutar)
            "Kira": (5, 28_000), "Okul taksiti": (15, 6_500),
            "İnternet+telefon": (10, 1_400), "Aidat": (3, 2_200),
        },
    },
    "Genç Profesyonel": {
        "aciklama": "Bekâr, şehir merkezi. Dışarıda yeme, eğlence, ulaşım yüksek.",
        "aylik_gelir": 62_000,
        "sapma": {
            "lokanta_otel": 2.2, "eglence": 2.0, "ulastirma": 1.4,
            "giyim": 1.3, "konut": 1.1, "gida": 0.7, "egitim": 0.2,
        },
        "duzenli": {
            "Kira": (1, 22_000), "Spor salonu": (8, 1_800),
            "Dijital abonelikler": (12, 900),
        },
    },
    "Serbest Çalışan (Düzensiz Gelir)": {
        "aciklama": "Freelancer. Gelir dalgalı, harcama temkinli.",
        "aylik_gelir": 70_000,
        "sapma": {
            "ulastirma": 1.3, "haberlesme": 1.5, "ev_esyasi": 1.2,
            "lokanta_otel": 1.1, "konut": 1.0, "egitim": 0.3,
        },
        "duzenli": {
            "Ofis kirası": (1, 9_000), "Yazılım abonelikleri": (20, 2_100),
        },
        "duzensiz_gelir": True,
    },
    "Küçük İşletme Sahibi": {
        "aciklama": "Esnaf. İşletme nakit akışı + kişisel harcama iç içe.",
        "aylik_gelir": 140_000,
        "sapma": {
            "ulastirma": 1.5, "ev_esyasi": 1.4, "haberlesme": 1.3,
            "cesitli": 1.6, "konut": 1.2, "gida": 1.1,
        },
        "duzenli": {
            "Dükkan kirası": (5, 28_000), "Tedarikçi ödemesi": (25, 16_000),
        },
        "duzensiz_gelir": True,
    },
}


def _normalize(d: dict) -> dict:
    s = sum(d.values())
    return {k: v / s for k, v in d.items()}


def kullanici_agirliklari(profil_adi: str) -> dict:
    """Profilin GERÇEK TÜİK ağırlıklarına sapma uygulanmış kişisel sepeti."""
    sapma = PROFILLER[profil_adi]["sapma"]
    raw = {}
    for kod, taban in TUIK_AGIRLIKLAR.items():
        raw[kod] = taban * sapma.get(kod, 1.0)
    return _normalize(raw)


def islem_uret(profil_adi: str, gun_sayisi: int = 180,
               tohum: int = 42) -> pd.DataFrame:
    """
    Sentetik ama gerçekçi banka işlem akışı üretir.

    - Düzenli ödemeler her ay sabit günde tekrarlar (kira, taksit...).
    - Değişken harcamalar kişisel sepet ağırlıklarına göre dağılır.
    - Maaş/gelir her ayın 1'inde (serbest çalışanda dalgalı) gelir.
    Çıktı: tarih, kategori, kategori_ad, tutar (negatif=harcama, +=gelir), tip
    """
    rng = np.random.default_rng(tohum)
    p = PROFILLER[profil_adi]
    agirlik = kullanici_agirliklari(profil_adi)
    aylik_gelir = p["aylik_gelir"]
    duzensiz = p.get("duzensiz_gelir", False)

    bugun = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    baslangic = bugun - timedelta(days=gun_sayisi)
    kayitlar = []

    # Aylık değişken harcama bütçesi. Düzenli ödemeler + değişken harcama,
    # gelirin altında kalmalı ki kullanıcıda korunacak ATIL bakiye biriksin
    # (TL Shield'in hedef kitlesi: tasarruf fazlası olan haneler).
    aylik_duzenli = sum(t for _, t in p["duzenli"].values())
    # gelirin ~%20'si tasarrufa kalsın: değişken = gelir*0.8 - düzenli
    aylik_degisken = max(aylik_gelir * 0.80 - aylik_duzenli, aylik_gelir * 0.25)

    gun = baslangic
    while gun <= bugun:
        # --- Gelir (ayın 1'i) ---
        if gun.day == 1:
            if duzensiz:
                carpan = rng.uniform(0.55, 1.45)  # dalgalı gelir
            else:
                carpan = rng.uniform(0.98, 1.02)
            kayitlar.append({
                "tarih": gun, "kategori": "gelir",
                "kategori_ad": "Maaş / Gelir",
                "tutar": round(aylik_gelir * carpan, 2), "tip": "gelir"})

        # --- Düzenli ödemeler ---
        for ad, (odeme_gun, tutar) in p["duzenli"].items():
            if gun.day == odeme_gun:
                jitter = rng.uniform(0.99, 1.01)
                kayitlar.append({
                    "tarih": gun, "kategori": "duzenli",
                    "kategori_ad": ad,
                    "tutar": -round(tutar * jitter, 2), "tip": "duzenli"})

        # --- Değişken günlük harcamalar ---
        # Günlük 1-4 işlem; kategori seçimi kişisel ağırlığa göre
        n_islem = rng.integers(1, 5)
        gunluk_butce = aylik_degisken / 30.0
        kategoriler = list(agirlik.keys())
        olasiliklar = np.array([agirlik[k] for k in kategoriler])
        olasiliklar = olasiliklar / olasiliklar.sum()
        for _ in range(n_islem):
            kod = rng.choice(kategoriler, p=olasiliklar)
            # hafta sonu eğlence/lokanta artışı
            wknd = 1.4 if (gun.weekday() >= 5 and kod in
                           ("lokanta_otel", "eglence")) else 1.0
            tutar = gunluk_butce / n_islem * rng.uniform(0.4, 1.8) * wknd
            kayitlar.append({
                "tarih": gun, "kategori": kod,
                "kategori_ad": KATEGORI_ADLARI[kod],
                "tutar": -round(tutar, 2), "tip": "harcama"})
        gun += timedelta(days=1)

    df = pd.DataFrame(kayitlar)
    df = df.sort_values("tarih").reset_index(drop=True)
    return df
