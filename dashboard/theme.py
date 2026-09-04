"""
dashboard/theme.py — SPPS Premium Design System.

Call inject_theme() as the FIRST thing after st.set_page_config() on every page.

Design tokens:
    ACCENT      = "#2563EB"   electric blue
    BG          = "#FFFFFF"   white
    INK         = "#0D0D0D"   near-black
    INK_SEC     = "#374151"   secondary
    INK_MUTED   = "#6B7280"   muted
    BORDER      = "#E5E7EB"   light gray border
    SIDEBAR_BG  = "#0A0F1E"   dark navy
"""

from __future__ import annotations
import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
ACCENT       = "#2563EB"
ACCENT_LIGHT = "rgba(37,99,235,0.08)"
BG           = "#FFFFFF"
SURFACE      = "#FFFFFF"
SURFACE_ALT  = "#F9FAFB"
INK          = "#0D0D0D"
INK_SEC      = "#374151"
INK_MUTED    = "#6B7280"
BORDER       = "#E5E7EB"
CHART_GRAY   = "#9CA3AF"
CHART_DARK   = "#1F2937"
SIDEBAR_BG   = "#0A0F1E"

CLASS_COLORS = {
    "H": "#2563EB",
    "M": "#6B7280",
    "L": "#1F2937",
}
CLASS_LABELS = {"H": "High", "M": "Medium", "L": "Low"}

PLOTLY_BASE = dict(
    plot_bgcolor  = "rgba(0,0,0,0)",
    paper_bgcolor = "rgba(0,0,0,0)",
    font          = dict(family="Inter, sans-serif", color="#374151", size=12),
    legend        = dict(orientation="h", y=-0.22, font=dict(size=12)),
    hoverlabel    = dict(bgcolor="#fff", bordercolor="#E5E7EB",
                         font=dict(family="Inter, sans-serif", size=13)),
)

# Passed to every st.plotly_chart(..., config=PLOTLY_CONFIG). Enables a clean
# modebar whose download button exports a high-resolution PNG entirely in the
# browser (Plotly's client-side toImage) — no kaleido / server dependency.
PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "spps_chart",
        "scale": 2,
    },
}

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{
  --accent:#2563EB;--accent-sub:rgba(37,99,235,0.08);--accent-border:rgba(37,99,235,0.2);
  --bg:#FFFFFF;--surface:#FFFFFF;--surface-alt:#F9FAFB;
  --ink:#0D0D0D;--ink-sec:#374151;--ink-muted:#6B7280;--border:#E5E7EB;
  --radius:12px;--radius-sm:8px;
  --font-display:'Space Grotesk',system-ui,sans-serif;
  --font-body:'Inter',system-ui,sans-serif;
  --font-mono:'IBM Plex Mono',monospace;
  --shadow-card:0 2px 12px rgba(0,0,0,0.06);--shadow-hover:0 12px 40px rgba(37,99,235,0.12);
  --navbar-h:56px;
}
html,body,[class*="css"]{font-family:var(--font-body)!important;color:var(--ink);background:var(--bg);}
#MainMenu{visibility:hidden;}footer{visibility:hidden;}
header[data-testid="stHeader"]{display:none!important;height:0!important;}

/* ── HIDE SIDEBAR COMPLETELY ── */
section[data-testid="stSidebar"]{display:none!important;width:0!important;}
[data-testid="collapsedControl"]{display:none!important;}
[data-testid="stSidebarNav"]{display:none!important;}
button[data-testid="baseButton-headerNoPadding"]{display:none!important;}

.main{background:#FFFFFF!important;margin-left:0!important;}
.block-container{max-width:1300px!important;padding:1rem 2.5rem 4rem!important;}

/* ── TOP NAVBAR STYLING VIA ST.PAGE_LINK ── */
[data-testid="stPageLink-NavLink"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 9px !important;
    padding: 0.42rem 0.65rem !important;
    text-decoration: none !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #4B5563 !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
    text-align: center !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stPageLink-NavLink"]:hover {
    border-color: #2563EB !important;
    color: #2563EB !important;
    background: rgba(37,99,235,0.05) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.12) !important;
}
[data-testid="stPageLink-NavLink"][aria-current="page"] {
    border-color: #2563EB !important;
    background: rgba(37,99,235,0.09) !important;
    color: #2563EB !important;
    font-weight: 700 !important;
    box-shadow: 0 0 0 1px #2563EB !important;
}

/* ── HOME NAV CARDS ── */
.spps-navcard-box{
    background:#fff;
    border:1px solid var(--border);
    border-radius:14px;
    padding:1.4rem 1.15rem 1.25rem;
    text-align:center;
    transition:all 0.22s ease;
    box-shadow:var(--shadow-card);
    margin-bottom:0.6rem;
    height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.spps-navcard-box:hover{transform:translateY(-3px);box-shadow:var(--shadow-hover);border-color:var(--accent-border);}
.spps-navcard-icon{font-size:2.2rem;margin-bottom:0.5rem;}
.spps-navcard-title{font-family:var(--font-display);font-size:1.02rem;font-weight:700;color:var(--ink);margin-bottom:0.35rem;letter-spacing:-0.02em;}
.spps-navcard-desc{font-family:var(--font-body);font-size:0.8rem;color:var(--ink-muted);line-height:1.4;}

h1,h2,h3,h4,h5,h6,.stMarkdown h1,.stMarkdown h2,.stMarkdown h3{font-family:var(--font-display)!important;color:var(--ink)!important;letter-spacing:-0.02em;line-height:1.2;}
.stMarkdown h1{font-size:2.4rem!important;font-weight:800!important;}
.stMarkdown h2{font-size:1.7rem!important;font-weight:700!important;}
.stMarkdown h3{font-size:1.25rem!important;font-weight:600!important;}
p,li,.stMarkdown p{font-family:var(--font-body)!important;font-size:0.9375rem;line-height:1.65;color:var(--ink-sec);}
hr,[data-testid="stDivider"] hr{border:none!important;border-top:1px solid var(--border)!important;margin:2rem 0!important;}

.stButton>button[kind="primary"],.stButton>button[data-testid="baseButton-primary"]{
  background:linear-gradient(135deg,#2563EB,#1D4ED8)!important;color:#fff!important;border:none!important;
  border-radius:10px!important;font-family:var(--font-body)!important;font-weight:600!important;
  font-size:0.9rem!important;padding:0.65rem 1.75rem!important;
  box-shadow:0 4px 12px rgba(37,99,235,0.3)!important;transition:all 0.2s ease!important;
}
.stButton>button[kind="primary"]:hover{box-shadow:0 8px 28px rgba(37,99,235,0.45)!important;transform:translateY(-2px)!important;}
.stButton>button[kind="secondary"],.stButton>button[data-testid="baseButton-secondary"]{
  background:transparent!important;color:var(--ink)!important;border:1px solid var(--border)!important;
  border-radius:10px!important;font-family:var(--font-body)!important;font-size:0.875rem!important;font-weight:500!important;transition:all 0.2s ease;
}
.stButton>button[kind="secondary"]:hover{border-color:var(--accent)!important;color:var(--accent)!important;background:var(--accent-sub)!important;}

[data-testid="stSlider"] label{font-family:var(--font-body)!important;font-size:0.875rem!important;color:var(--ink-sec)!important;font-weight:500!important;}
[data-testid="stSlider"]>div>div>div>div{background:linear-gradient(90deg,#2563EB,#60A5FA)!important;}
[data-testid="stSlider"] [role="slider"]{background:#2563EB!important;box-shadow:0 0 0 4px rgba(37,99,235,0.2)!important;border:2px solid #fff!important;}
[data-testid="stSelectbox"] label,[data-testid="stNumberInput"] label,[data-testid="stRadio"] label{font-size:0.875rem!important;color:var(--ink-sec)!important;font-weight:500!important;}
[data-testid="stSelectbox"]>div>div{border-color:var(--border)!important;border-radius:10px!important;font-family:var(--font-body)!important;}
[data-testid="stAlert"]{border-radius:10px!important;border:1px solid #BFDBFE!important;background:#EFF6FF!important;color:#1E40AF!important;font-size:0.875rem!important;}
details>summary{font-family:var(--font-body)!important;font-size:0.875rem!important;color:var(--ink-sec)!important;font-weight:500!important;}
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:var(--radius)!important;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.04);}
[data-testid="stPlotlyChart"]{border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow-card);}
[data-baseweb="tab-list"]{background:#F3F4F6!important;border-radius:10px!important;padding:4px!important;gap:2px!important;border:none!important;}
[data-baseweb="tab"]{border-radius:8px!important;font-family:var(--font-body)!important;font-weight:500!important;font-size:0.875rem!important;color:var(--ink-muted)!important;}
[aria-selected="true"][data-baseweb="tab"]{background:#fff!important;color:var(--accent)!important;box-shadow:0 2px 8px rgba(0,0,0,0.08)!important;font-weight:600!important;}

.spps-kpi-row{display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap;}
.spps-kpi-card{flex:1;min-width:160px;background:#fff;border:1px solid var(--border);border-radius:14px;padding:1.35rem 1.5rem;position:relative;overflow:hidden;transition:all 0.25s cubic-bezier(0.4,0,0.2,1);cursor:default;box-shadow:var(--shadow-card);}
.spps-kpi-card:hover{transform:translateY(-4px);box-shadow:var(--shadow-hover);border-color:var(--accent-border);}
.spps-kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#2563EB,#60A5FA);border-radius:14px 14px 0 0;}
.spps-kpi-icon{font-size:1.3rem;width:2.6rem;height:2.6rem;background:rgba(37,99,235,0.08);border-radius:10px;display:flex;align-items:center;justify-content:center;margin-bottom:0.85rem;}
.spps-kpi-value{font-family:var(--font-display);font-size:2.4rem;font-weight:800;color:var(--ink);letter-spacing:-0.04em;line-height:1;margin-bottom:0.3rem;}
.spps-kpi-value.blue{color:var(--accent);}
.spps-kpi-label{font-family:var(--font-body);font-size:0.72rem;font-weight:600;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.09em;}
.spps-kpi-trend{font-family:var(--font-mono);font-size:0.75rem;color:#9CA3AF;margin-top:0.4rem;}

.spps-section-head{margin:2.5rem 0 1rem;padding-left:1rem;border-left:3px solid var(--accent);}
.spps-section-head-title{font-family:var(--font-display);font-size:1.35rem;font-weight:700;color:var(--ink);letter-spacing:-0.025em;margin:0;}
.spps-section-head-sub{font-family:var(--font-body);font-size:0.875rem;color:var(--ink-muted);margin:0.25rem 0 0;}

.spps-page-hero{background:linear-gradient(135deg,#0A0F1E 0%,#1E3A8A 80%,#1D4ED8 100%);border-radius:16px;padding:2.5rem 2.75rem;margin-bottom:2rem;position:relative;overflow:hidden;}
.spps-page-hero::after{content:'';position:absolute;top:-60%;right:-5%;width:450px;height:450px;background:radial-gradient(circle,rgba(96,165,250,0.18) 0%,transparent 65%);pointer-events:none;}
.spps-page-title{font-family:var(--font-display);font-size:2.6rem;font-weight:800;color:#FFFFFF;letter-spacing:-0.04em;margin:0 0 0.5rem;line-height:1.1;position:relative;z-index:1;}
.spps-page-desc{font-family:var(--font-body);font-size:1rem;color:rgba(255,255,255,0.72);line-height:1.65;max-width:600px;margin:0;position:relative;z-index:1;}

.spps-hero{text-align:center;padding:2.5rem 1rem;background:linear-gradient(135deg,#EFF6FF,#DBEAFE);border-radius:14px;border:1px solid #BFDBFE;margin-bottom:1.5rem;}
.spps-hero-number{font-family:var(--font-display);font-size:5rem;font-weight:800;color:var(--accent);letter-spacing:-0.05em;line-height:1;}
.spps-hero-label{font-family:var(--font-body);font-size:0.72rem;font-weight:700;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;}
.spps-hero-note{font-family:var(--font-body);font-size:0.9rem;color:var(--ink-sec);margin-top:0.6rem;}

.spps-stat-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem 1.5rem;margin-bottom:0.75rem;transition:all 0.22s cubic-bezier(0.4,0,0.2,1);box-shadow:var(--shadow-card);}
.spps-stat-card:hover{box-shadow:var(--shadow-hover);border-color:var(--accent-border);transform:translateY(-2px);}
.spps-stat-card-label{font-family:var(--font-body);font-size:0.7rem;font-weight:700;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;display:block;}
.spps-stat-card-value{font-family:var(--font-display);font-size:2rem;font-weight:800;color:var(--ink);letter-spacing:-0.03em;line-height:1.1;}
.spps-stat-card-sub{font-size:0.8125rem;color:var(--ink-muted);margin-top:0.25rem;}

.spps-result-panel{background:#fff;border:1px solid var(--border);border-radius:16px;padding:2rem 2.25rem;box-shadow:0 4px 24px rgba(0,0,0,0.07);position:relative;overflow:hidden;margin:1rem 0;}
.spps-result-panel::before{content:'';position:absolute;top:0;left:0;right:0;height:4px;}
.panel-high::before{background:linear-gradient(90deg,#2563EB,#60A5FA);}
.panel-medium::before{background:linear-gradient(90deg,#6B7280,#D1D5DB);}
.panel-low::before{background:linear-gradient(90deg,#1F2937,#4B5563);}
.spps-result-class{font-family:var(--font-display);font-size:3.5rem;font-weight:800;color:var(--ink);letter-spacing:-0.04em;line-height:1;margin:0.5rem 0;}
.spps-result-conf{font-family:var(--font-mono);font-size:0.875rem;color:var(--ink-muted);margin-top:0.4rem;}
.spps-conf-badge{display:inline-block;font-family:var(--font-mono);font-size:0.85rem;color:var(--accent);background:rgba(37,99,235,0.08);border:1px solid rgba(37,99,235,0.2);border-radius:6px;padding:3px 10px;font-weight:600;}

.spps-narrative{background:linear-gradient(135deg,rgba(37,99,235,0.03),rgba(96,165,250,0.06));border:1px solid rgba(37,99,235,0.15);border-left:4px solid var(--accent);border-radius:10px;padding:1rem 1.25rem;font-size:0.9375rem;color:var(--ink);line-height:1.6;margin-bottom:1.25rem;}

.spps-cf-card{background:#fff;border:1px solid var(--border);border-radius:10px;padding:1rem 1.25rem;margin:0.6rem 0;display:flex;gap:1rem;align-items:flex-start;transition:all 0.22s ease;box-shadow:0 1px 4px rgba(0,0,0,0.04);}
.spps-cf-card:hover{border-color:rgba(37,99,235,0.3);box-shadow:0 6px 20px rgba(37,99,235,0.1);transform:translateX(3px);}
.spps-cf-icon{font-size:1.2rem;flex-shrink:0;width:2.5rem;height:2.5rem;background:rgba(37,99,235,0.08);border-radius:8px;display:flex;align-items:center;justify-content:center;}
.spps-cf-action{font-weight:700;font-size:0.9375rem;color:var(--ink);margin:0 0 0.15rem;}
.spps-cf-detail{font-size:0.8125rem;color:var(--ink-muted);margin:0;}

.spps-suggestion{background:linear-gradient(135deg,rgba(37,99,235,0.03),rgba(96,165,250,0.05));border:1px solid rgba(37,99,235,0.15);border-left:4px solid var(--accent);border-radius:10px;padding:0.85rem 1.1rem;margin:0.5rem 0;font-family:var(--font-body);font-size:0.9rem;color:var(--ink);transition:all 0.2s ease;}
.spps-suggestion:hover{background:rgba(37,99,235,0.06);border-color:rgba(37,99,235,0.3);}

.spps-delta{display:inline-flex;align-items:center;gap:4px;font-family:var(--font-mono);font-size:0.8rem;font-weight:600;border-radius:6px;padding:3px 9px;}
.spps-delta.up{color:#2563EB;background:rgba(37,99,235,0.09);}
.spps-delta.down{color:#6B7280;background:#F3F4F6;}
.spps-delta.neutral{color:#9CA3AF;background:#F3F4F6;}

.spps-class-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle;}
.spps-prob-wrap{margin:1rem 0;}
.spps-prob-label-row{display:flex;justify-content:space-between;font-family:var(--font-body);font-size:0.8125rem;color:var(--ink-sec);margin-bottom:0.35rem;}
.spps-prob-track{width:100%;height:10px;background:#F3F4F6;border-radius:99px;overflow:hidden;}
.spps-prob-fill{height:100%;border-radius:99px;transition:width 0.5s cubic-bezier(0.4,0,0.2,1);background:linear-gradient(90deg,#2563EB,#60A5FA);}
.spps-prob-fill.fill-mid{background:linear-gradient(90deg,#6B7280,#9CA3AF);}
.spps-prob-fill.fill-low{background:linear-gradient(90deg,#1F2937,#4B5563);}

.spps-section-label{font-family:var(--font-body);font-size:0.7rem;font-weight:700;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;display:block;}
.spps-chart-section{margin-bottom:2.5rem;}
.spps-chart-title{font-family:var(--font-display);font-size:1.1rem;font-weight:700;color:var(--ink);letter-spacing:-0.01em;margin-bottom:0.2rem;}
.spps-chart-caption{font-family:var(--font-body);font-size:0.8125rem;color:var(--ink-muted);line-height:1.5;margin-top:0.5rem;}

.spps-class-stat{display:flex;align-items:center;gap:0.75rem;padding:0.65rem 0;border-bottom:1px solid var(--border);font-family:var(--font-body);font-size:0.875rem;}
.spps-class-stat:last-child{border-bottom:none;}
.spps-class-stat-label{min-width:65px;color:var(--ink);font-weight:600;}
.spps-class-stat-bar-wrap{flex:1;height:6px;background:#F3F4F6;border-radius:99px;overflow:hidden;}
.spps-class-stat-bar{height:100%;border-radius:99px;}
.spps-class-stat-pct{min-width:42px;text-align:right;color:var(--ink-muted);font-family:var(--font-mono);font-size:0.78rem;}

@keyframes fadeInUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}
@keyframes scaleIn{from{opacity:0;transform:scale(0.94)}to{opacity:1;transform:scale(1)}}
@keyframes slideRight{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:translateX(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes glow{0%,100%{box-shadow:0 0 8px rgba(37,99,235,0.3)}50%{box-shadow:0 0 28px rgba(37,99,235,0.7)}}
.anim-fade-up{animation:fadeInUp 0.5s cubic-bezier(0.22,0.61,0.36,1) both;}
.anim-scale-in{animation:scaleIn 0.45s cubic-bezier(0.22,0.61,0.36,1) both;}
.anim-slide-right{animation:slideRight 0.4s cubic-bezier(0.22,0.61,0.36,1) both;}
.anim-fade{animation:fadeIn 0.4s ease both;}
.anim-glow{animation:glow 2.5s ease-in-out infinite;}
.anim-fade-up-1{animation-delay:0.05s;}.anim-fade-up-2{animation-delay:0.12s;}.anim-fade-up-3{animation-delay:0.20s;}.anim-fade-up-4{animation-delay:0.28s;}.anim-fade-up-5{animation-delay:0.36s;}
.main .block-container>div:nth-child(1){animation:fadeInUp 0.5s 0.02s cubic-bezier(0.22,0.61,0.36,1) both;}
.main .block-container>div:nth-child(2){animation:fadeInUp 0.5s 0.08s cubic-bezier(0.22,0.61,0.36,1) both;}
.main .block-container>div:nth-child(3){animation:fadeInUp 0.5s 0.14s cubic-bezier(0.22,0.61,0.36,1) both;}
.main .block-container>div:nth-child(4){animation:fadeInUp 0.5s 0.20s cubic-bezier(0.22,0.61,0.36,1) both;}
.main .block-container>div:nth-child(5){animation:fadeInUp 0.5s 0.26s cubic-bezier(0.22,0.61,0.36,1) both;}
.main .block-container>div:nth-child(n+6){animation:fadeInUp 0.5s 0.31s cubic-bezier(0.22,0.61,0.36,1) both;}
.stMarkdown small,[data-testid="stCaptionContainer"] p,.spps-caption{font-size:0.8125rem!important;color:var(--ink-muted)!important;line-height:1.5;}
</style>
"""

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def inject_theme(active_page: str = "home") -> None:
    """Inject CSS + native top navbar. Call immediately after set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)

    with st.container():
        c_brand, c_home, c_over, c_pred, c_whatif, c_cohort, c_models = st.columns(
            [1.5, 0.9, 1.1, 1.1, 1.0, 1.1, 1.3],
            vertical_alignment="center",
        )
        with c_brand:
            st.markdown(
                '<div style="display:flex;align-items:center;gap:7px;padding-left:2px;">'
                '<span style="width:10px;height:10px;border-radius:50%;background:#2563EB;display:inline-block;box-shadow:0 0 8px #2563EB;"></span>'
                '<span style="font-family:\'Space Grotesk\',sans-serif;font-weight:800;font-size:1.12rem;color:#0D0D0D;letter-spacing:-0.02em;">SPPS</span>'
                '<span style="font-family:\'Inter\',sans-serif;font-size:0.62rem;color:#6B7280;font-weight:600;background:#F3F4F6;padding:2px 5px;border-radius:4px;text-transform:uppercase;">ML</span>'
                '</div>',
                unsafe_allow_html=True,
            )
        with c_home:
            st.page_link("app.py", label="Home", icon="📊", use_container_width=True)
        with c_over:
            st.page_link("pages/1_Overview.py", label="Overview", icon="🔬", use_container_width=True)
        with c_pred:
            st.page_link("pages/2_Individual_Predictor.py", label="Predictor", icon="🎯", use_container_width=True)
        with c_whatif:
            st.page_link("pages/3_What_If_Simulator.py", label="What-If", icon="⚙️", use_container_width=True)
        with c_cohort:
            st.page_link("pages/4_Cohort_Simulator.py", label="Cohort Sim", icon="🏫", use_container_width=True)
        with c_models:
            st.page_link("pages/5_Model_and_Fairness.py", label="Model & Fairness", icon="⚖️", use_container_width=True)

    st.markdown('<hr style="margin:0.25rem 0 1.25rem 0;border:none;border-top:1px solid #E5E7EB;">', unsafe_allow_html=True)


def delta_chip(value, direction: str | None = None,
               prefix: str = "", suffix: str = "") -> str:
    """Inline delta chip, e.g. ``\u2191 +15%`` / ``\u2193 -30%`` / ``\u2192 0``.

    Parameters
    ----------
    value : int | float | str
        The magnitude to show. If numeric and ``direction`` is None, the sign
        of the number decides the arrow (positive \u2192 up, negative \u2192 down,
        zero \u2192 neutral) and the number is rendered with an explicit sign.
    direction : {'up', 'down', 'neutral'} | None
        Force the arrow/colour. When None and ``value`` is numeric it is
        inferred from the sign; when None and ``value`` is a string it defaults
        to neutral.
    prefix, suffix : str
        Wrap the displayed value, e.g. ``suffix="%"`` \u2192 ``\u2191 +15%``.
    """
    is_number = isinstance(value, (int, float)) and not isinstance(value, bool)

    if is_number:
        if direction is None:
            direction = "up" if value > 0 else ("down" if value < 0 else "neutral")
        num = "0" if value == 0 else f"{value:+g}"
        display = f"{prefix}{num}{suffix}"
    else:
        direction = direction or "neutral"
        display = f"{prefix}{value}{suffix}"

    arrow = {"up": "\u2191", "down": "\u2193", "neutral": "\u2192"}.get(direction, "\u2192")
    return f'<span class="spps-delta {direction}">{arrow} {display}</span>'


def page_hero(title: str, description: str) -> str:
    """Dark gradient hero banner — top of every page."""
    return f"""
<div class="spps-page-hero anim-fade-up">
  <p class="spps-page-title">{title}</p>
  <p class="spps-page-desc">{description}</p>
</div>
"""


def hero_stat(value: str, label: str, note: str = "") -> str:
    """Large centered KPI number block."""
    note_html = f'<p class="spps-hero-note">{note}</p>' if note else ""
    return f"""
<div class="spps-hero anim-fade-up">
  <p class="spps-hero-label">{label}</p>
  <p class="spps-hero-number">{value}</p>
  {note_html}
</div>
"""


def stat_card(title: str, value: str, subtitle: str = "", delay: int = 0) -> str:
    """Secondary metric card."""
    delay_class = f"anim-fade-up-{delay}" if 1 <= delay <= 5 else ""
    sub_html = f'<p class="spps-stat-card-sub">{subtitle}</p>' if subtitle else ""
    return f"""
<div class="spps-stat-card anim-fade-up {delay_class}">
  <p class="spps-stat-card-label">{title}</p>
  <p class="spps-stat-card-value">{value}</p>
  {sub_html}
</div>
"""


def kpi_hero_row(stats: list[dict]) -> str:
    """
    Horizontal row of KPI cards.
    Each dict: {"icon": str, "value": str, "label": str, "trend": str (optional), "blue": bool}
    """
    cards = ""
    for i, s in enumerate(stats):
        delay = min(i + 1, 5)
        blue_cls = "blue" if s.get("blue") else ""
        trend_html = f'<div class="spps-kpi-trend">{s["trend"]}</div>' if s.get("trend") else ""
        cards += f"""
<div class="spps-kpi-card anim-fade-up anim-fade-up-{delay}">
  <span class="spps-kpi-icon">{s.get('icon', '📊')}</span>
  <div class="spps-kpi-value {blue_cls}">{s['value']}</div>
  <div class="spps-kpi-label">{s['label']}</div>
  {trend_html}
</div>"""
    return f'<div class="spps-kpi-row">{cards}</div>'


def section_heading(title: str, subtitle: str = "") -> str:
    """Styled section heading with blue left border."""
    sub = f'<p class="spps-section-head-sub">{subtitle}</p>' if subtitle else ''
    return f'<div class="spps-section-head anim-slide-right"><p class="spps-section-head-title">{title}</p>{sub}</div>'


def result_panel(predicted_class: str, label: str, confidence: float,
                runner_up: str = "", runner_prob: float = 0.0,
                is_borderline: bool = False) -> str:
    """Prediction result panel with gradient top bar."""
    panel_map = {"H": "panel-high", "M": "panel-medium", "L": "panel-low"}
    panel_cls = panel_map.get(predicted_class, "panel-medium")
    conf_pct = f"{confidence:.0%}"

    borderline_note = ""
    if is_borderline:
        borderline_note = (
            '<p class="spps-result-conf" style="margin-top:0.5rem;">'
            '⚠ Borderline — this student is close to the class boundary.'
            '</p>'
        )

    runner_html = ""
    if runner_up and runner_up != "—":
        runner_label = CLASS_LABELS.get(runner_up, runner_up)
        runner_html = (
            f'<p class="spps-result-conf">Runner-up: {runner_label} '
            f'({runner_prob:.0%})</p>'
        )

    return f"""
<div class="spps-result-panel {panel_cls} anim-fade-up">
  <p class="spps-stat-card-label">Predicted Performance Band</p>
  <p class="spps-result-class">{label}</p>
  <p class="spps-result-conf">Confidence <span class="spps-conf-badge anim-glow">{conf_pct}</span></p>
  {runner_html}
  {borderline_note}
</div>
"""


def shap_narrative(top_features: list[str], direction: str = "toward") -> str:
    """Plain-English SHAP summary sentence."""
    if not top_features:
        return ""
    if len(top_features) == 1:
        feature_str = top_features[0]
    elif len(top_features) == 2:
        feature_str = f"{top_features[0]} and {top_features[1]}"
    else:
        feature_str = f"{', '.join(top_features[:-1])}, and {top_features[-1]}"

    if direction == "toward":
        sentence = (
            f"{feature_str} "
            f"{'are' if len(top_features) > 1 else 'is'} the strongest "
            f"factor{'s' if len(top_features) > 1 else ''} driving this prediction upward."
        )
    else:
        sentence = (
            f"{feature_str} "
            f"{'are' if len(top_features) > 1 else 'is'} the strongest "
            f"factor{'s' if len(top_features) > 1 else ''} pulling this prediction down."
        )
    return f'<div class="spps-narrative anim-fade-up">📌 {sentence}</div>'


def cf_card(icon: str, action_line: str, detail: str = "") -> str:
    """Counterfactual / recommendation card."""
    detail_html = f'<p class="spps-cf-detail">{detail}</p>' if detail else ""
    return f"""
<div class="spps-cf-card anim-fade-up">
  <span class="spps-cf-icon">{icon}</span>
  <div class="spps-cf-body">
    <p class="spps-cf-action">{action_line}</p>
    {detail_html}
  </div>
</div>
"""


def suggestion_card(text: str) -> str:
    """Improvement suggestion card."""
    return f'<div class="spps-suggestion anim-fade-up">{text}</div>'


def probability_bar(probs: dict[str, float], predicted_class: str) -> str:
    """Segmented probability bars for H/M/L."""
    fill_cls = {"H": "", "M": "fill-mid", "L": "fill-low"}
    bars_html = ""
    for cls, label in [("H", "High"), ("M", "Medium"), ("L", "Low")]:
        prob = probs.get(cls, 0)
        pct = prob * 100
        fc = fill_cls[cls]
        bold = " font-weight:700; color:var(--ink);" if cls == predicted_class else ""
        bars_html += f"""
<div class="spps-prob-wrap">
  <div class="spps-prob-label-row">
    <span style="{bold}">{label}</span>
    <span style="font-family:var(--font-mono);font-size:0.8rem;{bold}">{prob:.0%}</span>
  </div>
  <div class="spps-prob-track">
    <div class="spps-prob-fill {fc}" style="width:{pct:.1f}%;"></div>
  </div>
</div>"""
    return bars_html
