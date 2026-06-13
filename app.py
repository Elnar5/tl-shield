"""
TL Shield — Canlı Demo  (mobil + masaüstü uyumlu)
Çalıştırma:  uv run streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from tlshield.data import (islem_uret, kategori_tablosu, PROFILLER,
                           TUIK_GENEL_ENFLASYON, TUIK_AGIRLIKLAR, KATEGORI_ADLARI)
from tlshield.engine import (harcama_agirliklari, kisisel_enflasyon,
                             segment_belirle, likidite_tahmini,
                             yatirim_simulasyonu)
from tlshield.styles import (css, PLOTLY_TPL, PAPER, CARD, INK, SLATE, SLATE_2,
                             AMBER, TEAL, CLAY, LINE, MUTED)

st.set_page_config(page_title="TL Shield", page_icon="\U0001F6E1\uFE0F",
                   layout="centered", initial_sidebar_state="collapsed")
st.markdown(css(), unsafe_allow_html=True)


def tl(x):
    return f"\u20BA{x:,.0f}".replace(",", ".")


def stat_card(label, value, color, foot=""):
    return (f"<div class='card'><div class='stat-label'>{label}</div>"
            f"<div class='stat-num' style='color:{color}'>{value}</div>"
            f"<div class='stat-foot'>{foot}</div></div>")


# ===== MARKA =====
st.markdown("<div class='brandbar'><span class='logo'>\U0001F6E1\uFE0F</span>"
            "<span class='name'>TL <span class='sh'>Shield</span></span></div>",
            unsafe_allow_html=True)

# ===== HERO + KURULUM =====
if "df" not in st.session_state:
    st.markdown("<div class='eyebrow'>Ak\u0131ll\u0131 tasarruf korumas\u0131</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='display'>Resm\u00ee enflasyon herkes i\u00e7in ayn\u0131. "
                "<span class='hl'>Sizinki de\u011fil.</span></div>",
                unsafe_allow_html=True)
    st.write("")
    st.markdown("<div class='sub'>TL Shield harcama sepetinizi analiz ederek "
                "size \u00f6zel enflasyonu hesaplar, gelecekteki nakit ihtiyac\u0131n\u0131z\u0131 "
                "tahmin eder ve at\u0131l Liran\u0131z\u0131 otomatik olarak enflasyona endeksli "
                "tahvile y\u00f6nlendirir.</div>", unsafe_allow_html=True)
    st.write("")

    st.markdown(f"<div class='card'>"
                f"<div style='margin-bottom:.8rem'><span class='step'>1</span>"
                f"<b>Bir profil se\u00e7in ve ba\u015flay\u0131n</b></div>",
                unsafe_allow_html=True)
    profil = st.selectbox("Profil", list(PROFILLER.keys()),
                          label_visibility="collapsed")
    st.markdown(f"<div style='color:{MUTED};font-size:0.88rem;"
                f"margin:-.3rem 0 .8rem'>{PROFILLER[profil]['aciklama']}</div>",
                unsafe_allow_html=True)
    cset1, cset2 = st.columns(2)
    with cset1:
        ay = st.slider("Ge\u00e7mi\u015f veri (ay)", 6, 18, 12)
    with cset2:
        tohum = st.number_input("Tohum (tekrar i\u00e7in)", 1, 9999, 42)
    if st.button("\U0001F517  Hesab\u0131 ba\u011fla ve analiz et",
                 use_container_width=True):
        st.session_state["df"] = islem_uret(profil, ay * 30, int(tohum))
        st.session_state["profil"] = profil
        st.session_state["ay"] = ay
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    with st.expander("Veri kayna\u011f\u0131 \u2014 neyin ger\u00e7ek, neyin sim\u00fcle oldu\u011fu"):
        st.markdown(
            f"<div style='color:{MUTED};font-size:0.9rem;line-height:1.55'>"
            f"<b style='color:{INK}'>Enflasyon: GER\u00c7EK.</b> T\u00dc\u0130K Aral\u0131k 2025 "
            f"T\u00dcFE \u2014 kategori a\u011f\u0131rl\u0131klar\u0131 ve y\u0131ll\u0131k oranlar.<br><br>"
            f"<b style='color:{INK}'>\u0130\u015flemler: SENTET\u0130K.</b> T\u00fcrkiye'de a\u00e7\u0131k "
            f"bireysel banka verisi olmad\u0131\u011f\u0131ndan, ger\u00e7ek T\u00dc\u0130K a\u011f\u0131rl\u0131klar\u0131yla "
            f"\u00fcretilir. Ger\u00e7ek \u00fcr\u00fcnde a\u00e7\u0131k-bankac\u0131l\u0131k API'si kullan\u0131l\u0131r.</div>",
            unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='eyebrow'>Ger\u00e7ek veri temeli \u00b7 T\u00dc\u0130K 2025</div>",
                unsafe_allow_html=True)
    kt = kategori_tablosu().sort_values("Y\u0131ll\u0131k Enflasyon (%)")
    fig = go.Figure(go.Bar(
        x=kt["Y\u0131ll\u0131k Enflasyon (%)"], y=kt["Kategori"], orientation="h",
        marker=dict(color=kt["Y\u0131ll\u0131k Enflasyon (%)"],
                    colorscale=[[0, TEAL], [1, CLAY]], showscale=False),
        text=kt["Y\u0131ll\u0131k Enflasyon (%)"].map(lambda v: f"%{v:.1f}"),
        textposition="outside", textfont=dict(color=INK, size=11)))
    fig.add_vline(x=TUIK_GENEL_ENFLASYON, line_dash="dash", line_color=AMBER,
                  annotation_text=f"Genel %{TUIK_GENEL_ENFLASYON}",
                  annotation_font_color=AMBER)
    fig.update_layout(height=430, **PLOTLY_TPL)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.stop()


# ===== ANALİZ =====
df = st.session_state["df"]
profil = st.session_state["profil"]
ay = st.session_state.get("ay", 12)
w = harcama_agirliklari(df)
ke = kisisel_enflasyon(w)
seg = segment_belirle(w)

top1, top2 = st.columns([3, 1])
with top1:
    st.markdown(f"<div class='eyebrow'>Analiz haz\u0131r</div>"
                f"<div class='display' style='font-size:clamp(1.5rem,5vw,2.1rem)'>"
                f"{profil}</div>"
                f"<div style='color:{MUTED};font-size:0.9rem'>{len(df):,} i\u015flem "
                f"\u00b7 {ay} ayl\u0131k ge\u00e7mi\u015f</div>", unsafe_allow_html=True)
with top2:
    st.write("")
    if st.button("\u21bb Yeni profil", use_container_width=True):
        for k in ("df", "profil", "ay"):
            st.session_state.pop(k, None)
        st.rerun()

st.write("")
tabs = st.tabs(["Ki\u015fisel Enflasyon", "Harcama DNA's\u0131",
                "Likidite", "Otomatik Yat\u0131r\u0131m", "\u0130\u015flemler"])

with tabs[0]:
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown(stat_card("Resm\u00ee \u00b7 T\u00dc\u0130K", f"%{ke['resmi']:.1f}",
                          MUTED, "Tek oran"), unsafe_allow_html=True)
    renk = CLAY if ke["fark"] > 0 else TEAL
    c2.markdown(stat_card("Sizin oran\u0131n\u0131z", f"%{ke['oran']:.1f}",
                          renk, "Sepetinize g\u00f6re"), unsafe_allow_html=True)
    isaret = "puan y\u00fcksek" if ke["fark"] > 0 else "puan d\u00fc\u015f\u00fck"
    c3.markdown(stat_card("Fark", f"{ke['fark']:+.1f}", AMBER, isaret),
                unsafe_allow_html=True)
    st.write("")
    if ke["fark"] > 0:
        st.markdown(
            f"<div class='card' style='border-left:4px solid {CLAY}'>"
            f"<b>Resm\u00ee orana g\u00f6re yat\u0131r\u0131m yapsayd\u0131n\u0131z, paran\u0131z yine erirdi.</b>"
            f"<br><span style='color:{MUTED}'>Ger\u00e7ek enflasyon y\u00fck\u00fcn\u00fcz resm\u00ee "
            f"orandan <b style='color:{CLAY}'>{ke['fark']:.1f} puan</b> y\u00fcksek. "
            f"TL Shield hedef getiriyi sizin oran\u0131n\u0131za g\u00f6re belirler.</span></div>",
            unsafe_allow_html=True)
    st.write("")
    st.markdown("<div class='eyebrow'>Enflasyonunuz nereden geliyor</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div style='color:{MUTED};font-family:JetBrains Mono;"
                f"font-size:0.88rem;margin:.3rem 0 .8rem'>\u03c0 = \u03a3 (w\u1d62 \u00d7 \u03c0\u1d62)"
                f"</div>", unsafe_allow_html=True)
    kdf = pd.DataFrame(ke["katkilar"]).head(8).sort_values("katki")
    fig = go.Figure(go.Bar(x=kdf["katki"], y=kdf["kategori"], orientation="h",
        marker=dict(color=kdf["katki"], colorscale=[[0, TEAL], [1, CLAY]],
                    showscale=False),
        text=kdf["katki"].map(lambda v: f"{v:.2f}"),
        textposition="outside", textfont=dict(color=INK, size=11)))
    fig.update_layout(height=350, xaxis_title="Katk\u0131 (puan)", **PLOTLY_TPL)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with tabs[1]:
    st.write("")
    st.markdown(f"<div style='color:{MUTED}'>K-Means k\u00fcmeleme sizi \u015fu gruba "
                f"yerle\u015ftirdi:</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin:.6rem 0 1rem'><span class='pill' "
                f"style='background:{AMBER};color:white'>{seg['etiket']}</span>"
                f"</div>", unsafe_allow_html=True)
    kodlar = list(TUIK_AGIRLIKLAR.keys())
    tt = sum(TUIK_AGIRLIKLAR.values())
    kategoriler = [KATEGORI_ADLARI[k] for k in kodlar]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[TUIK_AGIRLIKLAR[k]/tt*100 for k in kodlar],
                  theta=kategoriler, fill='toself', name="T\u00dc\u0130K ort.",
                  line_color=MUTED, opacity=0.5))
    fig.add_trace(go.Scatterpolar(r=[w[k]*100 for k in kodlar],
                  theta=kategoriler, fill='toself', name="Siz",
                  line_color=SLATE, fillcolor="rgba(30,58,95,0.15)"))
    fig.update_layout(height=460, paper_bgcolor="rgba(0,0,0,0)",
                  font=dict(color=INK, family="Inter", size=12),
                  margin=dict(l=30, r=30, t=20, b=40),
                  polar=dict(bgcolor="rgba(30,58,95,0.02)",
                             radialaxis=dict(gridcolor=LINE, color=MUTED),
                             angularaxis=dict(gridcolor=LINE, color=INK)),
                  legend=dict(orientation="h", y=-0.12))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with tabs[2]:
    st.write("")
    ufuk = st.radio("Ufuk", [30, 60, 90], horizontal=True,
                    format_func=lambda x: f"{x} g\u00fcn", label_visibility="collapsed")
    lik = likidite_tahmini(df, ufuk)
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown(stat_card(f"{ufuk}g harcama", tl(lik["toplam_ihtiyac"]), INK),
                unsafe_allow_html=True)
    c2.markdown(stat_card("Tekrarlayan", tl(lik["duzenli"]), MUTED, "Kira, taksit"),
                unsafe_allow_html=True)
    c3.markdown(stat_card("G\u00fcvenli tampon", tl(lik["guvenli_tampon"]), AMBER,
                          "1,5\u00d7"), unsafe_allow_html=True)
    st.write("")
    gt = lik["gunluk_tahmin"]
    fig = go.Figure(go.Scatter(x=gt["tarih"], y=gt["beklenen_harcama"],
                  fill="tozeroy", line=dict(color=SLATE, width=2),
                  fillcolor="rgba(30,58,95,0.08)"))
    fig.update_layout(height=300, yaxis_title="G\u00fcnl\u00fck (\u20BA)", **PLOTLY_TPL)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(f"<div class='card' style='border-left:4px solid {AMBER}'>"
        f"<b>Model se\u00e7imi \u2014 savunulabilir m\u00fchendislik.</b><br>"
        f"<span style='color:{MUTED}'>Birincil tahminci: tekrarlayan \u00f6deme "
        f"tespiti + haftan\u0131n g\u00fcn\u00fcne g\u00f6re hareketli ortalama. An\u0131nda \u00e7al\u0131\u015f\u0131r, "
        f"a\u00e7\u0131klanabilir. LSTM, veri \u00f6l\u00e7eklendi\u011finde devreye girer.</span></div>",
        unsafe_allow_html=True)

with tabs[3]:
    st.write("")
    tahvil = st.slider("Tahvil y\u0131ll\u0131k getirisi (%)", 20, 55,
                       int(TUIK_GENEL_ENFLASYON), 1)
    sim = yatirim_simulasyonu(df, tahvil_yillik=float(tahvil))
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown(stat_card("At\u0131l nakit", tl(sim["son_atil"]), MUTED, "Getiri yok"),
                unsafe_allow_html=True)
    c2.markdown(stat_card("TL Shield ile", tl(sim["son_shield"]), TEAL,
                          f"+{tl(sim['kazanc'])}"), unsafe_allow_html=True)
    c3.markdown(stat_card("Yat\u0131r\u0131lan", tl(sim["toplam_yatirilan"]), AMBER,
                          "Otomatik"), unsafe_allow_html=True)
    if sim["kazanc"] > 0:
        st.write("")
        st.markdown(f"<div class='card' style='text-align:center;"
            f"background:linear-gradient(135deg,#F4FAF8,#FFFFFF);"
            f"border:1px solid {TEAL}'>"
            f"<div class='stat-label'>Bu d\u00f6nemde kazand\u0131rd\u0131</div>"
            f"<div class='stat-num' style='color:{TEAL};"
            f"font-size:clamp(2.2rem,8vw,3.2rem)'>{tl(sim['kazanc'])}</div>"
            f"<div class='stat-foot'>Hi\u00e7bir i\u015flem yapmadan.</div></div>",
            unsafe_allow_html=True)
    st.write("")
    s = sim["seri"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s["tarih"], y=s["atil_nominal"],
                  name="At\u0131l nakit", line=dict(color=CLAY, width=2)))
    fig.add_trace(go.Scatter(x=s["tarih"], y=s["shield_toplam"],
                  name="TL Shield", line=dict(color=TEAL, width=2.5),
                  fill="tonexty", fillcolor="rgba(46,139,122,0.10)"))
    fig.update_layout(height=340, yaxis_title="Bakiye (\u20BA)",
                  legend=dict(orientation="h", y=-0.15), **PLOTLY_TPL)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with tabs[4]:
    st.write("")
    show = df.copy()
    show["tarih"] = pd.to_datetime(show["tarih"]).dt.strftime("%Y-%m-%d")
    show["tutar"] = show["tutar"].round(0)
    show = show.rename(columns={"tarih": "Tarih", "kategori_ad": "A\u00e7\u0131klama",
                                "tutar": "Tutar (\u20BA)", "tip": "Tip"})
    st.dataframe(show[["Tarih", "A\u00e7\u0131klama", "Tutar (\u20BA)", "Tip"]]
                 .sort_values("Tarih", ascending=False),
                 use_container_width=True, hide_index=True, height=460)
