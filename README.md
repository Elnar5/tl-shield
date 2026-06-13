# 🛡️ TL Shield — MVP Demo

Yüksek enflasyona karşı Türk Lirası tasarruflarını **otomatik** koruyan akıllı
finansal asistan. Bu depo, TEKNOFEST final sunumunda **canlı** gösterilecek
çalışan MVP'dir.

---

## Hızlı başlangıç (laptopta)

```bash
# 1. Sanal ortam (önerilir)
uv venv
source .venv/bin/activate

# 2. Bağımlılıklar
uv pip install -r requirements.txt

# 3. Çalıştır
uv run streamlit run app.py
```

Tarayıcıda otomatik açılır (`http://localhost:8501`). Açılmazsa terminaldeki
linke tıklayın.

> **Demo öncesi:** Bir kez `streamlit run app.py` çalıştırıp ekranların
> yüklendiğinden emin olun. Sunumda internet **gerekmez** — tüm veri yereldir.

---

## Ne gösteriyor (4 modül)

| Modül | Ne yapar | Demo'daki etki |
|---|---|---|
| **Kişisel Enflasyon** | π_kişisel = Σ(wᵢ × πᵢ) — sizin sepetinize göre gerçek enflasyon | "Resmî %30,9 ama SİZİN %42,6" — ana farklılaştırıcı |
| **Segment** | K-Means ile harcama davranışı kümeleme | "Siz 'Şehirli Kiracı Aile' grubundasınız" |
| **Likidite Tahmini** | Tekrarlayan ödeme tespiti + haftalık desenli tahmin | 30/60/90 gün nakit ihtiyacı + güvenli tampon |
| **Otomatik Yatırım** | Atıl nakdi enflasyona endeksli tahvile yönlendirme simülasyonu | "TL Shield size ₺X kazandırdı" sayacı |

---

## Veri şeffaflığı (jüri bunu sorar — hazır olun)

- **Enflasyon verisi GERÇEKTİR.** TÜİK Aralık 2025 TÜFE bülteni: kategori
  ağırlıkları (gıda %24,96, konut %15,21, ulaştırma %15,34...) ve yıllık
  kategori enflasyonları (konut %49,45, gıda %28,31, ulaştırma %28,44...).
  Genel manşet: %30,89.
- **Kişisel işlemler SENTETİKTİR.** Türkiye'de temiz, kamuya açık bireysel
  banka işlem verisi bulunmaz. İşlemleri, **gerçek TÜİK harcama
  ağırlıklarıyla tohumlanmış** bir üreticiyle üretiyoruz. Gerçek dağıtımda
  bu veri, açık-bankacılık API'si ile gelir.

Bu duruşu savunun: "Enflasyon temelimiz resmî ve doğrulanabilir; sadece
demo için bireysel işlemleri sentetik ürettik çünkü gerçek banka verisi
BDDK lisansı gerektirir."

---

## Mimari

```
tlshield/
  data.py     → GERÇEK TÜİK sabitleri + sentetik işlem üreticisi
  engine.py   → 4 yetenek: kişisel enflasyon, segment, likidite, yatırım
app.py        → Streamlit canlı demo arayüzü
```

---

## Önemli mühendislik kararı (rapordan bilinçli sapma)

Ön değerlendirme raporunda **ARIMA + LSTM** vaat edilmişti. Canlı demo bir
laptopta çalışacağı ve kullanıcı başına uzun geçmiş bulunmadığı için,
**birincil tahminci olarak hafif ve açıklanabilir bir model** seçtik
(tekrarlayan ödeme tespiti + haftanın gününe göre hareketli ortalama).
LSTM, veri ölçeklendiğinde devreye girecek **belgelenmiş büyüme yolu**
olarak konumlandırıldı.

**Neden bu güçlü bir hikâye:** Jüri "neden bu model?" diye sorar.
"Her kısıt için doğru aracı seçtik; tahminlerimiz açıklanabilir ve anında
çalışır, LSTM'e geçiş yolu da hazır" cevabı, mühendislik olgunluğu gösterir.
Bu, ön değerlendirmede en çok puan kaybeden **Yöntem** bölümünü güçlendirir.

---

## Sunum akışı önerisi (3 dakika)

1. **Aç:** "Resmî enflasyon herkes için aynı. Sizinki değil." (açılış ekranı)
2. **Bağla:** "Şehirli Kiracı Aile" profilini seç → Hesabı bağla.
3. **Vur:** Kişisel Enflasyon sekmesi — "%30,9 değil, SİZİN %42,6'nız."
   Farkın nereden geldiğini (konut, gıda) tabloda göster.
4. **Bağla:** Segment → "Sistem sizi otomatik tanıdı."
5. **Güven:** Likidite Tahmini → "Paranızı bağlarken nakitsiz kalmazsınız."
6. **Kapat:** Otomatik Yatırım → kazanç sayacını göster. "Sıfır işlemle."

---

## Sorun giderme

- `streamlit: command not found` → `uv pip install -r requirements.txt` tekrar.
- Port meşgul → `streamlit run app.py --server.port 8502`.
- Grafik görünmüyor → tarayıcıyı yenile (F5).
