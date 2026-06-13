"""
TL Shield — Motor Katmanı
==========================
Dört ana yetenek:
  1. kisisel_enflasyon   — π_kişisel = Σ(w_i × π_i)  [ana farklılaştırıcı]
  2. segment_belirle     — K-Means ile kullanıcı kümeleme
  3. likidite_tahmini    — gelecekteki nakit ihtiyacı (savunulabilir model)
  4. yatirim_simulasyonu — atıl TL'yi enflasyona endeksli tahvile yönlendirme

Tasarım kararı (rapordan bilinçli sapma):
  Raporda ARIMA + LSTM vaat edilmişti. Canlı demo bir laptopta çalışacağı ve
  kullanıcı başına uzun geçmiş bulunmadığı için, BİRİNCİL tahminci olarak
  hafif ve savunulabilir bir model kullanıyoruz: tekrarlayan ödeme tespiti +
  kategori bazlı hareketli ortalama (mevsimsel/haftalık desenli). LSTM, veri
  ölçeklendiğinde devreye girecek "büyüme yolu" olarak belgelenir. Bu, "her
  kısıt için doğru aracı seçtik" mühendislik olgunluğunu gösterir.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from .data import (TUIK_AGIRLIKLAR, KATEGORI_ENFLASYON, KATEGORI_ADLARI,
                   TUIK_GENEL_ENFLASYON, PROFILLER, kullanici_agirliklari)


# ---------------------------------------------------------------------------
# 1) KİŞİSEL ENFLASYON  —  π_kişisel = Σ (w_i × π_i)
# ---------------------------------------------------------------------------
def harcama_agirliklari(df: pd.DataFrame) -> dict:
    """Gerçek işlem akışından kullanıcının kategori ağırlıklarını çıkarır."""
    harcama = df[df["tip"].isin(["harcama"])].copy()
    # düzenli ödemeleri de TÜİK kategorilerine bağla (kira->konut vb.)
    toplam = {}
    for kod in TUIK_AGIRLIKLAR:
        toplam[kod] = harcama.loc[harcama["kategori"] == kod, "tutar"].abs().sum()

    # düzenli ödemeleri kategoriye eşle
    duzenli = df[df["tip"] == "duzenli"]
    eslesme = {"Kira": "konut", "Ofis kirası": "konut", "Dükkan kirası": "konut",
               "Okul taksiti": "egitim", "İnternet+telefon": "haberlesme",
               "Aidat": "konut", "Spor salonu": "eglence",
               "Dijital abonelikler": "eglence", "Yazılım abonelikleri": "haberlesme",
               "Personel maaşı": "cesitli", "Tedarikçi ödemesi": "cesitli"}
    for _, r in duzenli.iterrows():
        kod = eslesme.get(r["kategori_ad"], "cesitli")
        toplam[kod] = toplam.get(kod, 0) + abs(r["tutar"])

    s = sum(toplam.values())
    if s == 0:
        return {k: 0 for k in toplam}
    return {k: v / s for k, v in toplam.items()}


def kisisel_enflasyon(agirlik: dict) -> dict:
    """
    Kişisel enflasyon oranını ve kategori katkılarını hesaplar.
    Döndürür: {oran, katkilar[{kategori, agirlik, enflasyon, katki}], fark}
    """
    katkilar = []
    oran = 0.0
    for kod, w in agirlik.items():
        enf = KATEGORI_ENFLASYON[kod]
        katki = w * enf
        oran += katki
        katkilar.append({
            "kod": kod, "kategori": KATEGORI_ADLARI[kod],
            "agirlik": w * 100, "enflasyon": enf, "katki": katki})
    katkilar.sort(key=lambda x: x["katki"], reverse=True)
    return {
        "oran": oran,
        "resmi": TUIK_GENEL_ENFLASYON,
        "fark": oran - TUIK_GENEL_ENFLASYON,
        "katkilar": katkilar,
    }


# ---------------------------------------------------------------------------
# 2) SEGMENTASYON  —  K-Means
# ---------------------------------------------------------------------------
def _profil_ozellik_matrisi() -> tuple[np.ndarray, list, list]:
    """Tüm profillerin kategori ağırlık vektörlerini kümeleme için hazırlar."""
    kodlar = list(TUIK_AGIRLIKLAR.keys())
    isimler, vektorler = [], []
    for ad in PROFILLER:
        w = kullanici_agirliklari(ad)
        vektorler.append([w[k] for k in kodlar])
        isimler.append(ad)
    return np.array(vektorler), isimler, kodlar


def segment_belirle(agirlik: dict, k: int = 4) -> dict:
    """
    Kullanıcıyı, referans profil kümelerinden birine atar.
    Az sayıda profil olduğu için kümeler profillerle hizalanır; gerçek
    sistemde bu binlerce kullanıcı üzerinde çalışır.
    """
    kodlar = list(TUIK_AGIRLIKLAR.keys())
    ref_matris, isimler, _ = _profil_ozellik_matrisi()
    kullanici_vek = np.array([[agirlik[k] for k in kodlar]])

    tum = np.vstack([ref_matris, kullanici_vek])
    olcek = StandardScaler().fit(ref_matris)
    tum_s = olcek.transform(tum)

    n_kume = min(k, len(isimler))
    km = KMeans(n_clusters=n_kume, n_init=10, random_state=42)
    km.fit(tum_s[:-1])  # sadece referanslarla eğit
    kullanici_kume = int(km.predict(tum_s[-1:])[0])

    # bu kümedeki referans profiller
    ref_kumeler = km.labels_
    ayni_kume = [isimler[i] for i in range(len(isimler))
                 if ref_kumeler[i] == kullanici_kume]
    return {
        "kume": kullanici_kume,
        "benzer_profiller": ayni_kume,
        "etiket": ayni_kume[0] if ayni_kume else "Belirsiz",
    }


# ---------------------------------------------------------------------------
# 3) LİKİDİTE TAHMİNİ  —  tekrarlayan ödeme + hareketli ortalama
# ---------------------------------------------------------------------------
def gunluk_harcama_serisi(df: pd.DataFrame) -> pd.Series:
    h = df[df["tutar"] < 0].copy()
    h["tarih"] = pd.to_datetime(h["tarih"])
    seri = h.groupby("tarih")["tutar"].sum().abs()
    idx = pd.date_range(seri.index.min(), seri.index.max(), freq="D")
    return seri.reindex(idx, fill_value=0.0)


def likidite_tahmini(df: pd.DataFrame, ufuk_gun: int = 30) -> dict:
    """
    Önümüzdeki `ufuk_gun` için beklenen toplam nakit ihtiyacını tahmin eder.

    İki bileşen:
      A) Bilinen tekrarlayan ödemeler (kira, taksit) — tarihleri kesin.
      B) Değişken günlük harcama — son 60 günün haftanın-gününe göre
         hareketli ortalaması (haftalık mevsimsellik yakalar).
    """
    # A) tekrarlayan ödemeler
    duzenli = df[df["tip"] == "duzenli"].copy()
    aylik_duzenli = 0.0
    if not duzenli.empty:
        duzenli["tarih"] = pd.to_datetime(duzenli["tarih"])
        son_ay = duzenli[duzenli["tarih"] >=
                         duzenli["tarih"].max() - pd.Timedelta(days=31)]
        aylik_duzenli = son_ay["tutar"].abs().sum()
    duzenli_ufuk = aylik_duzenli * (ufuk_gun / 30.0)

    # B) değişken harcama — haftanın gününe göre ortalama
    h = df[(df["tip"] == "harcama")].copy()
    h["tarih"] = pd.to_datetime(h["tarih"])
    h["dow"] = h["tarih"].dt.dayofweek
    gunluk = h.groupby([h["tarih"].dt.date, "dow"])["tutar"].sum().abs().reset_index()
    dow_ort = gunluk.groupby("dow")["tutar"].mean().to_dict()
    genel_ort = gunluk["tutar"].mean() if not gunluk.empty else 0.0

    son_tarih = pd.to_datetime(df["tarih"]).max()
    degisken_ufuk = 0.0
    gunluk_tahmin = []
    for i in range(1, ufuk_gun + 1):
        t = son_tarih + pd.Timedelta(days=i)
        beklenen = dow_ort.get(t.dayofweek, genel_ort)
        degisken_ufuk += beklenen
        gunluk_tahmin.append({"tarih": t, "beklenen_harcama": beklenen})

    toplam = duzenli_ufuk + degisken_ufuk
    return {
        "ufuk_gun": ufuk_gun,
        "duzenli": duzenli_ufuk,
        "degisken": degisken_ufuk,
        "toplam_ihtiyac": toplam,
        "gunluk_tahmin": pd.DataFrame(gunluk_tahmin),
        "guvenli_tampon": toplam * 1.5,  # rapordaki 1.5x kuralı
    }


# ---------------------------------------------------------------------------
# 4) OTOMATİK YATIRIM SİMÜLASYONU
# ---------------------------------------------------------------------------
def yatirim_simulasyonu(df: pd.DataFrame, tahvil_yillik: float = None,
                        mevduat_yillik: float = 0.0) -> dict:
    """
    Geçmiş bakiyeyi yeniden oynatır ve TL Shield'in atıl bakiyeyi enflasyona
    endeksli tahvile yönlendirmesiyle, hiçbir şey yapmamayı (atıl nakit)
    karşılaştırır.

    tahvil_yillik: enflasyona endeksli tahvil getirisi (varsayılan: kişisel
                   enflasyona yakın; burada genel TÜFE kullanılır).
    """
    if tahvil_yillik is None:
        tahvil_yillik = TUIK_GENEL_ENFLASYON  # enflasyona endeksli ~ TÜFE

    gunluk_tahvil = (1 + tahvil_yillik / 100) ** (1 / 365) - 1
    gunluk_mevduat = (1 + mevduat_yillik / 100) ** (1 / 365) - 1
    gunluk_enf = (1 + TUIK_GENEL_ENFLASYON / 100) ** (1 / 365) - 1

    d = df.copy()
    d["tarih"] = pd.to_datetime(d["tarih"])
    gunluk_net = d.groupby("tarih")["tutar"].sum()
    idx = pd.date_range(gunluk_net.index.min(), gunluk_net.index.max(), freq="D")
    gunluk_net = gunluk_net.reindex(idx, fill_value=0.0)

    # Güvenli tampon: ~1 aylık nakit ihtiyacı (likidite garantisi)
    tampon = likidite_tahmini(df, 30)["toplam_ihtiyac"]

    bakiye_atil = 0.0      # hiçbir şey yapmama (vadesiz, getiri 0)
    bakiye_shield = 0.0    # serbest nakit (her zaman >= tampon hedefi)
    yatirilan = 0.0        # enflasyona endeksli tahvilde
    seri = []
    for t, net in gunluk_net.items():
        # --- ATIL SENARYO: nakit birikir, hiç getiri almaz ---
        bakiye_atil += net

        # --- SHIELD SENARYO ---
        bakiye_shield += net
        # tahvil getirisini uygula (gün sonu)
        yatirilan *= (1 + gunluk_tahvil)
        # tampon üstündeki serbest nakdi otomatik yatır
        if bakiye_shield > tampon:
            fazla = bakiye_shield - tampon
            yatirilan += fazla
            bakiye_shield = tampon
        # tampon altına düşülürse tahvilden çek (likidite koruması)
        elif bakiye_shield < tampon and yatirilan > 0:
            ihtiyac = tampon - bakiye_shield
            cekilen = min(ihtiyac, yatirilan)
            yatirilan -= cekilen
            bakiye_shield += cekilen

        shield_toplam = bakiye_shield + yatirilan
        seri.append({"tarih": t,
                     "atil_nominal": bakiye_atil,
                     "shield_toplam": shield_toplam,
                     "yatirilan": yatirilan})

    seri_df = pd.DataFrame(seri)
    son = seri_df.iloc[-1]
    kazanc = son["shield_toplam"] - son["atil_nominal"]
    return {
        "seri": seri_df,
        "son_atil": son["atil_nominal"],
        "son_shield": son["shield_toplam"],
        "kazanc": kazanc,
        "tahvil_yillik": tahvil_yillik,
        "toplam_yatirilan": son["yatirilan"],
    }
