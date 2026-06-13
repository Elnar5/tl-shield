"""
TL Shield — Canlı Demo Uygulaması  (bank-grade arayüz)
=======================================================
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

st.set_page_config(page_title="TL Shield", page_icon="\U0001F6E1\uFE0F",
                   layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------------------------
# PALET
# ---------------------------------------------------------------------------
INK      = "#0A1F1A"
PANEL    = "#0F2A23"
PANEL_2  = "#143329"
LINE     = "#1F4438"
GOLD     = "#E8B339"
GOLD_DIM = "#B98A22"
GREEN    = "#3FB984"
RED      = "#E06A4E"
TEXT     = "#EAF2EE"
MUTED    = "#7E988D"

PLOTLY_TPL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT, family="Inter, sans-serif", size=13),
    xaxis=dict(gridcolor=LINE, zerolinecolor=LINE, linecolor=LINE),
    yaxis=dict(gridcolor=LINE, zerolinecolor=LINE, linecolor=LINE),
    margin=dict(l=0, r=0, t=20, b=0),
)

st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
  .stApp {{ background:
      radial-gradient(1200px 600px at 80% -10%, #11342A 0%, {INK} 55%) fixed;
      color: {TEXT}; }}
  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
  .block-container {{ padding-top: 2.2rem; max-width: 1180px; }}
  h1,h2,h3,h4 {{ color: {TEXT}; font-family: 'Fraunces', serif;
                 letter-spacing: -0.5px; }}
  .display {{ font-family:'Fraunces',serif; font-weight:600;
              font-size: 3.1rem; line-height:1.05; letter-spacing:-1.5px;
              color:{TEXT}; }}
  .display .hl {{ color:{GOLD}; font-style: italic; }}
  .sub {{ color:{MUTED}; font-size:1.08rem; line-height:1.55; max-width:60ch; }}
  .eyebrow {{ color:{GOLD}; font-weight:600; font-size:0.78rem;
              letter-spacing:2.5px; text-transform:uppercase; }}
  .card {{ background: {PANEL}; border:1px solid {LINE}; border-radius:18px;
           padding:1.5rem 1.6rem; box-shadow: 0 8px 30px rgba(0,0,0,0.18); }}
  .stat-label {{ color:{MUTED}; font-size:0.72rem; letter-spacing:1.8px;
                 text-transform:uppercase; font-weight:600; }}
  .stat-num {{ font-family:'JetBrains Mono', monospace; font-weight:700;
               font-size:3.0rem; line-height:1.05; letter-spacing:-1px; }}
  .stat-foot {{ color:{MUTED}; font-size:0.82rem; margin-top:0.3rem; }}
  .pill {{ display:inline-block; padding:0.35rem 0.95rem; border-radius:999px;
           font-size:0.82rem; font-weight:600; border:1px solid {LINE}; }}
  section[data-testid="stSidebar"] {{ background:{INK};
       border-right:1px solid {LINE}; }}
  section[data-testid="stSidebar"] * {{ color:{TEXT}; }}
  .brand {{ font-family:'Fraunces',serif; font-weight:700; font-size:1.7rem;
            letter-spacing:-0.5px; }}
  .brand .sh {{ color:{GOLD}; }}
  .stTabs [data-baseweb="tab-list"] {{ gap:6px; background:transparent;
       border-bottom:1px solid {LINE}; }}
  .stTabs [data-baseweb="tab"] {{ background:transparent; color:{MUTED};
       border:none; border-radius:10px 10px 0 0; padding:10px 16px;
       font-weight:600; font-size:0.92rem; }}
  .stTabs [aria-selected="true"] {{ color:{GOLD};
       border-bottom:2px solid {GOLD}; background:{PANEL}; }}
  .stButton>button {{ background:{GOLD}; color:{INK}; border:none;
       border-radius:12px; font-weight:700; padding:0.6rem 1rem;
       transition: all .15s ease; }}
  .stButton>button:hover {{ background:{GOLD_DIM}; transform:translateY(-1px); }}
  .stSelectbox div[data-baseweb="select"]>div,
  .stNumberInput input {{ background:{PANEL}; border:1px solid {LINE};
       color:{TEXT}; border-radius:10px; }}
  div[data-baseweb="slider"] [role="slider"] {{ background:{GOLD}; }}
  .stDataFrame {{ border:1px solid {LINE}; border-radius:14px; overflow:hidden; }}
  #MainMenu, footer, header {{ visibility:hidden; }}
  .stDeployButton {{ display:none; }}
  div[data-testid="stMetric"] {{ background:{PANEL}; border:1px solid {LINE};
       border-radius:16px; padding:1rem 1.2rem; }}
  div[data-testid="stMetricValue"] {{ font-family:'JetBrains Mono',monospace; }}
</style>
""", unsafe_allow_html=True)


def tl(x):
    return f"\u20BA{x:,.0f}".replace(",", ".")


def stat_card(label, value, color, foot=""):
    return (f"<div class='card'><div class='stat-label'>{label}</div>"
            f"<div class='stat-num' style='color:{color}'>{value}</div>"
            f"<div class='stat-foot'>{foot}</div></div>")


# ===========================================================================
# SIDEBAR
# ===========================================================================
with st.sidebar:
    st.markdown("<div class='brand'>\U0001F6E1\uFE0F TL <span class='sh'>Shield</span></div>",
                unsafe_allow_html=True)
    st.markdown(f"<div style='color:{MUTED};font-size:0.9rem;margin:.3rem 0 1rem'>"
                f"Enflasyona kar\u015f\u0131 otomatik tasarruf korumas\u0131</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='eyebrow'>1 \u00b7 Hesab\u0131n\u0131 ba\u011fla</div>",
                unsafe_allow_html=True)
    profil = st.selectbox("Profil", list(PROFILLER.keys()),
                          label_visibility="collapsed")
    st.markdown(f"<div style='color:{MUTED};font-size:0.84rem'>"
                f"{PROFILLER[profil]['aciklama']}</div>", unsafe_allow_html=True)
    st.write("")
    ay = st.slider("Ge\u00e7mi\u015f veri (ay)", 6, 18, 12)
    tohum = st.number_input("Tekrarlanabilirlik tohumu", 1, 9999, 42)
    st.write("")
    baglan = st.button("\U0001F517  Hesab\u0131 ba\u011fla ve analiz et",
                       type="primary", use_container_width=True)
    st.write("")
    with st.expander("Veri kayna\u011f\u0131 (\u015feffafl\u0131k)"):
        st.markdown(
            f"<div style='font-size:0.84rem;color:{MUTED};line-height:1.5'>"
            "<b style='color:#EAF2EE'>Enflasyon: GER\u00c7EK</b> \u2014 T\u00dc\u0130K Aral\u0131k 2025 "
            "T\u00dcFE (kategori a\u011f\u0131rl\u0131klar\u0131 + y\u0131ll\u0131k oranlar).<br><br>"
            "<b style='color:#EAF2EE'>\u0130\u015flemler: SENTET\u0130K</b> \u2014 a\u00e7\u0131k banka "
            "verisi olmad\u0131\u011f\u0131ndan, ger\u00e7ek T\u00dc\u0130K a\u011f\u0131rl\u0131klar\u0131yla \u00fcretilir. "
            "Ger\u00e7ek da\u011f\u0131t\u0131mda a\u00e7\u0131k-bankac\u0131l\u0131k API'si ile ba\u011flan\u0131r.</div>",
            unsafe_allow_html=True)

if baglan:
    st.session_state["df"] = islem_uret(profil, ay * 30, int(tohum))
    st.session_state["profil"] = profil
    st.session_state["ay"] = ay


# ===========================================================================
# A\u00c7ILI\u015e EKRANI
# ===========================================================================
if "df" not in st.session_state:
    st.markdown("<div class='eyebrow'>Ak\u0131ll\u0131 tasarruf korumas\u0131</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='display'>Resm\u00ee enflasyon herkes i\u00e7in ayn\u0131.<br>"
                "<span class='hl'>Sizinki de\u011fil.</span></div>",
                unsafe_allow_html=True)
    st.write("")
    st.markdown("<div class='sub'>TL Shield harcama sepetinizi analiz ederek "
                "size \u00f6zel enflasyonu hesaplar, gelecekteki nakit ihtiyac\u0131n\u0131z\u0131 "
                "tahmin eder ve at\u0131l T\u00fcrk Liras\u0131 bakiyenizi otomatik olarak "
                "enflasyona endeksli tahvile y\u00f6nlendirir \u2014 siz hi\u00e7bir \u015fey "
                "yapmadan.</div>", unsafe_allow_html=True)
    st.write("")
    st.markdown(f"<div style='color:{GOLD};font-weight:600'>"
                f"\u2190 Soldan bir profil se\u00e7ip <b>Hesab\u0131 ba\u011fla</b>'ya bas\u0131n</div>",
                unsafe_allow_html=True)
    st.write(""); st.write("")
    st.markdown("<div class='eyebrow'>Ger\u00e7ek veri temeli \u00b7 T\u00dc\u0130K 2025 "
                "enflasyon sepeti</div>", unsafe_allow_html=True)
    st.write("")
    kt = kategori_tablosu().sort_values("Y\u0131ll\u0131k Enflasyon (%)")
    fig = go.Figure(go.Bar(
        x=kt["Y\u0131ll\u0131k Enflasyon (%)"], y=kt["Kategori"], orientation="h",
        marker=dict(color=kt["Y\u0131ll\u0131k Enflasyon (%)"],
                    colorscale=[[0, GREEN], [1, RED]], showscale=False),
        text=kt["Y\u0131ll\u0131k Enflasyon (%)"].map(lambda v: f"%{v:.1f}"),
        textposition="outside", textfont=dict(color=TEXT)))
    fig.add_vline(x=TUIK_GENEL_ENFLASYON, line_dash="dash", line_color=GOLD,
                  annotation_text=f"Resm\u00ee genel %{TUIK_GENEL_ENFLASYON}",
                  annotation_font_color=GOLD)
    fig.update_layout(height=460, **PLOTLY_TPL)
    st.plotly_chart(fig, use_container_width=True)
    st.stop()


# ===========================================================================
# ANAL\u0130Z EKRANI
# ===========================================================================
df = st.session_state["df"]
profil = st.session_state["profil"]
ay = st.session_state.get("ay", 12)

w = harcama_agirliklari(df)
ke = kisisel_enflasyon(w)
seg = segment_belirle(w)

st.markdown(f"<div class='eyebrow'>Analiz haz\u0131r</div>", unsafe_allow_html=True)
st.markdown(f"<div class='display' style='font-size:2.3rem'>{profil}</div>",
            unsafe_allow_html=True)
st.markdown(f"<div style='color:{MUTED};margin-bottom:.6rem'>"
            f"{len(df):,} i\u015flem \u00b7 {ay} ayl\u0131k ge\u00e7mi\u015f analiz edildi</div>",
            unsafe_allow_html=True)

tabs = st.tabs(["  Ki\u015fisel Enflasyon  ", "  Harcama DNA's\u0131  ",
                "  Likidite Tahmini  ", "  Otomatik Yat\u0131r\u0131m  ",
                "  \u0130\u015flemler  "])

# TAB 1
with tabs[0]:
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown(stat_card("Resm\u00ee enflasyon \u00b7 T\u00dc\u0130K", f"%{ke['resmi']:.1f}",
                          MUTED, "Herkese uygulanan tek oran"), unsafe_allow_html=True)
    renk = RED if ke["fark"] > 0 else GREEN
    c2.markdown(stat_card("Sizin enflasyonunuz", f"%{ke['oran']:.1f}",
                          renk, "Harcama sepetinize g\u00f6re"), unsafe_allow_html=True)
    isaret = "puan daha y\u00fcksek" if ke["fark"] > 0 else "puan daha d\u00fc\u015f\u00fck"
    c3.markdown(stat_card("Fark", f"{ke['fark']:+.1f}", GOLD, isaret),
                unsafe_allow_html=True)
    st.write("")
    if ke["fark"] > 0:
        st.markdown(
            f"<div class='card' style='border-left:3px solid {RED}'>"
            f"<b style='color:{TEXT}'>Resm\u00ee orana g\u00f6re yat\u0131r\u0131m yapsayd\u0131n\u0131z, "
            f"paran\u0131z yine erirdi.</b><br><span style='color:{MUTED}'>"
            f"Ger\u00e7ek enflasyon y\u00fck\u00fcn\u00fcz resm\u00ee orandan "
            f"<b style='color:{RED}'>{ke['fark']:.1f} puan</b> y\u00fcksek. "
            f"TL Shield, hedef getiriyi sizin oran\u0131n\u0131za g\u00f6re belirler.</span>"
            f"</div>", unsafe_allow_html=True)
    st.write(""); st.write("")
    st.markdown("<div class='eyebrow'>Ki\u015fisel enflasyonunuz nereden geliyor</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div style='color:{MUTED};font-family:JetBrains Mono;"
                f"font-size:0.9rem;margin:.4rem 0 1rem'>"
                f"\u03c0_ki\u015fisel = \u03a3 (w\u1d62 \u00d7 \u03c0\u1d62)</div>", unsafe_allow_html=True)
    kdf = pd.DataFrame(ke["katkilar"]).head(8).sort_values("katki")
    fig = go.Figure(go.Bar(
        x=kdf["katki"], y=kdf["kategori"], orientation="h",
        marker=dict(color=kdf["katki"], colorscale=[[0, GREEN], [1, RED]],
                    showscale=False),
        text=kdf["katki"].map(lambda v: f"{v:.2f}"),
        textposition="outside", textfont=dict(color=TEXT)))
    fig.update_layout(height=360, xaxis_title="Enflasyona katk\u0131 (puan)", **PLOTLY_TPL)
    st.plotly_chart(fig, use_container_width=True)

# TAB 2
with tabs[1]:
    st.write("")
    st.markdown(f"<div style='color:{MUTED}'>K-Means k\u00fcmeleme sizi \u015fu "
                f"davran\u0131\u015f grubuna yerle\u015ftirdi:</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin:.6rem 0 1rem'><span class='pill' "
                f"style='background:{GOLD};color:{INK};border-color:{GOLD};"
                f"font-size:1rem;padding:.5rem 1.2rem'>{seg['etiket']}</span>"
                f"</div>", unsafe_allow_html=True)
    kodlar = list(TUIK_AGIRLIKLAR.keys())
    toplam_tuik = sum(TUIK_AGIRLIKLAR.values())
    kategoriler = [KATEGORI_ADLARI[k] for k in kodlar]
    user_vals = [w[k] * 100 for k in kodlar]
    tuik_vals = [TUIK_AGIRLIKLAR[k] / toplam_tuik * 100 for k in kodlar]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=tuik_vals, theta=kategoriler, fill='toself',
                                  name="T\u00dc\u0130K ortalamas\u0131",
                                  line_color=MUTED, opacity=0.55))
    fig.add_trace(go.Scatterpolar(r=user_vals, theta=kategoriler, fill='toself',
                                  name="Sizin sepetiniz", line_color=GOLD,
                                  fillcolor="rgba(232,179,57,0.18)"))
    fig.update_layout(height=500,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=TEXT, family="Inter, sans-serif", size=13),
                      margin=dict(l=20, r=20, t=20, b=20),
                      polar=dict(bgcolor="rgba(255,255,255,0.02)",
                                 radialaxis=dict(gridcolor=LINE, color=MUTED),
                                 angularaxis=dict(gridcolor=LINE, color=TEXT)),
                      legend=dict(orientation="h", y=-0.08))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"<div style='color:{MUTED};font-size:0.9rem'>Sepetinizin "
                f"T\u00dc\u0130K ortalamas\u0131ndan sapt\u0131\u011f\u0131 yerler, ki\u015fisel enflasyonunuzun "
                f"neden farkl\u0131 oldu\u011funu a\u00e7\u0131klar.</div>", unsafe_allow_html=True)

# TAB 3
with tabs[2]:
    st.write("")
    ufuk = st.radio("Tahmin ufku", [30, 60, 90], horizontal=True,
                    format_func=lambda x: f"{x} g\u00fcn", label_visibility="collapsed")
    lik = likidite_tahmini(df, ufuk)
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown(stat_card(f"{ufuk} g\u00fcnl\u00fck beklenen harcama",
                          tl(lik["toplam_ihtiyac"]), TEXT), unsafe_allow_html=True)
    c2.markdown(stat_card("Tekrarlayan \u00f6demeler", tl(lik["duzenli"]), MUTED,
                          "Kira, taksit, abonelik"), unsafe_allow_html=True)
    c3.markdown(stat_card("G\u00fcvenli likidite tamponu", tl(lik["guvenli_tampon"]),
                          GOLD, "1,5\u00d7 ihtiya\u00e7"), unsafe_allow_html=True)
    st.write(""); st.write("")
    st.markdown("<div class='eyebrow'>G\u00fcnl\u00fck nakit ihtiyac\u0131 tahmini</div>",
                unsafe_allow_html=True)
    gt = lik["gunluk_tahmin"]
    fig = go.Figure(go.Scatter(x=gt["tarih"], y=gt["beklenen_harcama"],
                               fill="tozeroy", line=dict(color=GOLD, width=2),
                               fillcolor="rgba(232,179,57,0.10)"))
    fig.update_layout(height=320, yaxis_title="Beklenen g\u00fcnl\u00fck harcama (\u20BA)",
                      **PLOTLY_TPL)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"<div class='card' style='border-left:3px solid {GOLD}'>"
        f"<b style='color:{TEXT}'>Model se\u00e7imi \u2014 savunulabilir m\u00fchendislik.</b>"
        f"<br><span style='color:{MUTED}'>Birincil tahminci: tekrarlayan \u00f6deme "
        f"tespiti + haftan\u0131n g\u00fcn\u00fcne g\u00f6re hareketli ortalama. Laptopta an\u0131nda "
        f"\u00e7al\u0131\u015f\u0131r, az veri ister, her tahmin a\u00e7\u0131klanabilir. <b>LSTM</b>, veri "
        f"\u00f6l\u00e7eklendi\u011finde devreye girecek belgelenmi\u015f b\u00fcy\u00fcme yoludur.</span>"
        f"</div>", unsafe_allow_html=True)

# TAB 4
with tabs[3]:
    st.write("")
    tahvil = st.slider("Enflasyona endeksli tahvil y\u0131ll\u0131k getirisi (%)",
                       20, 55, int(TUIK_GENEL_ENFLASYON), 1)
    sim = yatirim_simulasyonu(df, tahvil_yillik=float(tahvil))
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown(stat_card("Hi\u00e7bir \u015fey yapmasayd\u0131n\u0131z", tl(sim["son_atil"]),
                          MUTED, "At\u0131l nakit \u00b7 getiri yok"), unsafe_allow_html=True)
    c2.markdown(stat_card("TL Shield ile", tl(sim["son_shield"]), GREEN,
                          f"+{tl(sim['kazanc'])} kazan\u00e7"), unsafe_allow_html=True)
    c3.markdown(stat_card("Otomatik yat\u0131r\u0131lan", tl(sim["toplam_yatirilan"]),
                          GOLD, "S\u0131f\u0131r manuel i\u015flem"), unsafe_allow_html=True)
    if sim["kazanc"] > 0:
        st.write("")
        st.markdown(
            f"<div class='card' style='text-align:center;background:"
            f"linear-gradient(135deg,{PANEL},{PANEL_2});border-color:{GREEN}'>"
            f"<div class='stat-label'>Bu d\u00f6nemde kazand\u0131rd\u0131</div>"
            f"<div class='stat-num' style='color:{GREEN};font-size:3.6rem'>"
            f"{tl(sim['kazanc'])}</div>"
            f"<div class='stat-foot'>Hi\u00e7bir i\u015flem yapmadan, otomatik.</div>"
            f"</div>", unsafe_allow_html=True)
    st.write(""); st.write("")
    st.markdown("<div class='eyebrow'>At\u0131l nakit \u00b7 TL Shield bakiye seyri</div>",
                unsafe_allow_html=True)
    s = sim["seri"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s["tarih"], y=s["atil_nominal"],
                             name="At\u0131l nakit (getiri yok)",
                             line=dict(color=RED, width=2)))
    fig.add_trace(go.Scatter(x=s["tarih"], y=s["shield_toplam"],
                             name="TL Shield (otomatik yat\u0131r\u0131m)",
                             line=dict(color=GREEN, width=2.5),
                             fill="tonexty", fillcolor="rgba(63,185,132,0.10)"))
    fig.update_layout(height=360, yaxis_title="Bakiye (\u20BA)",
                      legend=dict(orientation="h", y=-0.12), **PLOTLY_TPL)
    st.plotly_chart(fig, use_container_width=True)

# TAB 5
with tabs[4]:
    st.write("")
    show = df.copy()
    show["tarih"] = pd.to_datetime(show["tarih"]).dt.strftime("%Y-%m-%d")
    show["tutar"] = show["tutar"].round(0)
    show = show.rename(columns={"tarih": "Tarih", "kategori_ad": "A\u00e7\u0131klama",
                                "tutar": "Tutar (\u20BA)", "tip": "Tip"})
    st.dataframe(show[["Tarih", "A\u00e7\u0131klama", "Tutar (\u20BA)", "Tip"]]
                 .sort_values("Tarih", ascending=False),
                 use_container_width=True, hide_index=True, height=520)
