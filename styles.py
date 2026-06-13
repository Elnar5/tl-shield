"""TL Shield arayüz teması — renkler, Plotly şablonu ve CSS tek yerde."""

PAPER   = "#FBFAF8"
CARD    = "#FFFFFF"
INK     = "#16263B"
SLATE   = "#1E3A5F"
SLATE_2 = "#2C4E7A"
AMBER   = "#D4953A"
TEAL    = "#2E8B7A"
CLAY    = "#C16B52"
LINE    = "#ECE7DF"
MUTED   = "#6E7C8C"

PLOTLY_TPL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=INK, family="Inter, sans-serif", size=13),
    xaxis=dict(gridcolor=LINE, zerolinecolor=LINE, linecolor=LINE),
    yaxis=dict(gridcolor=LINE, zerolinecolor=LINE, linecolor=LINE),
    margin=dict(l=0, r=0, t=20, b=0),
)


def css() -> str:
    """Tema CSS'ini döndürür (st.markdown ile enjekte edilir)."""
    return """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">
<style>
  .stApp { background:#FBFAF8; color:#16263B; }
  html, body, [class*="css"] { font-family:'Inter',sans-serif; }
  .block-container { padding:1.5rem 1rem 4rem; max-width:860px; }

  section[data-testid="stSidebar"] { display:none; }
  [data-testid="collapsedControl"] { display:none; }
  #MainMenu, footer, header { visibility:hidden; }
  .stDeployButton { display:none; }

  h1,h2,h3 { font-family:'Sora',sans-serif; color:#16263B; letter-spacing:-0.5px; }
  .display { font-family:'Sora',sans-serif; font-weight:700;
             font-size:clamp(1.9rem,6vw,3rem); line-height:1.08;
             letter-spacing:-1px; color:#16263B; }
  .display .hl { color:#D4953A; }
  .sub { color:#6E7C8C; font-size:clamp(0.98rem,2.5vw,1.1rem); line-height:1.55; }
  .eyebrow { color:#D4953A; font-weight:700; font-size:0.74rem;
             letter-spacing:2px; text-transform:uppercase; }

  .card { background:#FFFFFF; border:1px solid #ECE7DF; border-radius:16px;
          padding:1.3rem 1.4rem; box-shadow:0 2px 12px rgba(22,38,59,0.05);
          margin-bottom:.4rem; }
  .brandbar { display:flex; align-items:center; gap:.6rem; margin-bottom:1.4rem; }
  .brandbar .logo { font-size:1.5rem; }
  .brandbar .name { font-family:'Sora',sans-serif; font-weight:700;
                    font-size:1.25rem; color:#16263B; }
  .brandbar .name .sh { color:#D4953A; }

  .stat-label { color:#6E7C8C; font-size:0.7rem; letter-spacing:1.4px;
                text-transform:uppercase; font-weight:700; }
  .stat-num { font-family:'JetBrains Mono',monospace; font-weight:700;
              font-size:clamp(1.8rem,6vw,2.6rem); line-height:1.1;
              letter-spacing:-1px; }
  .stat-foot { color:#6E7C8C; font-size:0.8rem; margin-top:.25rem; }

  .pill { display:inline-block; padding:.4rem 1rem; border-radius:999px;
          font-size:0.9rem; font-weight:700; }
  .step { display:inline-flex; align-items:center; justify-content:center;
          width:1.5rem; height:1.5rem; border-radius:50%; background:#1E3A5F;
          color:white; font-size:0.8rem; font-weight:700; margin-right:.5rem; }

  .stTabs [data-baseweb="tab-list"] { gap:4px; overflow-x:auto;
       border-bottom:1px solid #ECE7DF; flex-wrap:nowrap; }
  .stTabs [data-baseweb="tab"] { background:transparent; color:#6E7C8C;
       border:none; padding:9px 13px; font-weight:600; font-size:0.88rem;
       white-space:nowrap; }
  .stTabs [aria-selected="true"] { color:#1E3A5F;
       border-bottom:2.5px solid #D4953A; }

  .stButton>button { background:#1E3A5F; color:white; border:none;
       border-radius:12px; font-weight:700; padding:.7rem 1rem;
       font-size:1rem; transition:all .15s; }
  .stButton>button:hover { background:#2C4E7A; transform:translateY(-1px); }

  .stSelectbox div[data-baseweb="select"]>div { background:#FFFFFF;
       border:1px solid #ECE7DF; color:#16263B; border-radius:10px; }
  .stNumberInput input { background:#FFFFFF; border:1px solid #ECE7DF;
       color:#16263B; border-radius:10px; }
  label, .stMarkdown p { color:#16263B; }
  div[data-testid="stMetricValue"] { font-family:'JetBrains Mono',monospace; }
</style>
"""
