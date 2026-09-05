"""
dashboard/theme.py — SPPS Old Money Academic Design System.

Call inject_theme() as the FIRST thing after st.set_page_config() on every page.

Tokens (CSS variables, single source of truth):
    PAPER   #FAF8F3  warm ivory page
    SURFACE #FFFFFF  card vellum
    INK     #1C1917  warm near-black
    OXFORD  #1B2A4A  deep academic navy (hero only)
    FOREST  #234434  primary — High band, CTAs
    BRASS   #9A7B2E  accent — Medium band, rules, seals
    CLAY    #7C2D12  Low band — muted terracotta, never alarm red
    LINE    #E7E0D1  hairline borders

Type: Cormorant Garamond (display serif) + Inter (UI) + IBM Plex Mono (ledger).
Icons: inline Phosphor-style SVG via icon(). No emoji structural icons.
Motion: 200-250ms, prefers-reduced-motion respected, :focus-visible brass ring.
"""

from __future__ import annotations

import html

import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens — single source of truth
# ---------------------------------------------------------------------------
PAPER = "#FAF8F3"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F5F0E6"
INK = "#1C1917"
INK_SEC = "#44403C"
INK_MUTED = "#78716C"
LINE = "#E7E0D1"
LINE_SOFT = "#EFE9DB"
OXFORD = "#1B2A4A"
FOREST = "#234434"
FOREST_DEEP = "#182E24"
BRASS = "#9A7B2E"
BRASS_SOFT = "rgba(154,123,46,0.10)"
CLAY = "#7C2D12"

# Backward-compat aliases (old pages import these names)
ACCENT = FOREST
ACCENT_LIGHT = BRASS_SOFT
BG = PAPER
CHART_GRAY = "#A8A29E"
CHART_DARK = "#44403C"
SIDEBAR_BG = OXFORD
BORDER = LINE

CLASS_COLORS = {
    "H": FOREST,   # High — deep forest
    "M": BRASS,    # Medium — brass
    "L": CLAY,     # Low — muted clay
}
CLASS_LABELS = {"H": "High", "M": "Medium", "L": "Low"}

# Status colours for fairness verdicts (muted, academic — no neon)
VERDICT = {
    "acceptable": FOREST,
    "concern": "#8A6D1B",
    "fail": "#7C2D12",
}

PLOTLY_BASE = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#44403C", size=12),
    legend=dict(orientation="h", y=-0.22, font=dict(size=12)),
    hoverlabel=dict(
        bgcolor="#FFFFFF", bordercolor="#E7E0D1",
        font=dict(family="Inter, sans-serif", size=13),
    ),
)

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

GRID = "#E7E0D1"
ZERO_LINE = "#C9BFA9"

# ---------------------------------------------------------------------------
# Inline SVG icons (Phosphor-style, stroke 1.5) — no emoji
# ---------------------------------------------------------------------------
_ICONS = {
    "cap": '<path d="M12 4 2 9l10 5 10-5-10-5Z"/><path d="M6 11.5V15c0 1.5 2.7 3 6 3s6-1.5 6-3v-3.5"/><path d="M22 9v5"/>',
    "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1" fill="currentColor"/>',
    "ledger": '<path d="M5 4h14v16H5z"/><path d="M9 8h6M9 12h6M9 16h4"/>',
    "flask": '<path d="M9 3h6"/><path d="M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3"/><path d="M7.5 15h9"/>',
    "scales": '<path d="M12 4v16"/><path d="M8 20h8"/><path d="M12 6 6 8m6-2 6 2"/><path d="M3.5 13 6 8l2.5 5a2.6 2.6 0 0 1-5 0Zm12 0L18 8l2.5 5a2.6 2.6 0 0 1-5 0Z"/>',
    "sliders": '<path d="M5 7h9M18 7h1M5 17h3M12 17h7"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19c.6-3 2.8-4.5 5.5-4.5s4.9 1.5 5.5 4.5"/><circle cx="16.5" cy="9" r="2.6"/><path d="M16 14.6c2.3.2 3.9 1.6 4.4 4"/>',
    "seal": '<circle cx="12" cy="10" r="6"/><path d="m9 15-2 6 5-2.5L17 21l-2-6"/>',
    "arrow": '<path d="M4 12h15"/><path d="m13 6 6 6-6 6"/>',
    "book": '<path d="M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5V4.5Z"/><path d="M5 19.5A1.5 1.5 0 0 1 6.5 18H19"/>',
}


def icon(name: str, size: int = 18, color: str = "currentColor") -> str:
    """Inline SVG icon. Never use emoji for structural icons."""
    paths = _ICONS.get(name, _ICONS["ledger"])
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.5" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{paths}</svg>'
    )


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root{
  --paper:#FAF8F3;--surface:#FFFFFF;--surface-alt:#F5F0E6;
  --ink:#1C1917;--ink-sec:#44403C;--ink-muted:#78716C;
  --line:#E7E0D1;--line-soft:#EFE9DB;
  --oxford:#1B2A4A;--forest:#234434;--forest-deep:#182E24;
  --brass:#9A7B2E;--brass-soft:rgba(154,123,46,.10);--clay:#7C2D12;
  --accent:#234434;--accent-sub:rgba(154,123,46,.10);--accent-border:rgba(154,123,46,.35);
  --bg:#FAF8F3;--border:#E7E0D1;
  --radius:10px;--radius-sm:7px;
  --font-display:'Cormorant Garamond',Georgia,serif;
  --font-body:'Inter',system-ui,sans-serif;
  --font-mono:'IBM Plex Mono',ui-monospace,monospace;
  --shadow-card:0 1px 2px rgba(28,25,23,.06);
  --shadow-hover:0 6px 22px rgba(27,42,74,.10);
}
/* base */
html,body,[class*="css"]{font-family:var(--font-body)!important;color:var(--ink);background:var(--paper);}
#MainMenu{visibility:hidden;}footer{visibility:hidden;}
header[data-testid="stHeader"]{display:none!important;height:0!important;}
section[data-testid="stSidebar"]{display:none!important;width:0!important;}
[data-testid="collapsedControl"]{display:none!important;}
[data-testid="stSidebarNav"]{display:none!important;}
button[data-testid="baseButton-headerNoPadding"]{display:none!important;}
.main{background:var(--paper)!important;margin-left:0!important;}
.block-container{max-width:1280px!important;padding:1rem 2.5rem 4rem!important;}
/* focus: visible brass ring, keyboard navigable */
*:focus-visible{outline:2px solid var(--brass)!important;outline-offset:2px;border-radius:4px;}
/* type */
h1,h2,h3,h4,h5,h6,.stMarkdown h1,.stMarkdown h2,.stMarkdown h3{font-family:var(--font-display)!important;color:var(--ink)!important;letter-spacing:0;font-weight:600!important;line-height:1.15;}
.stMarkdown h1{font-size:2.2rem!important;}
.stMarkdown h2{font-size:1.65rem!important;}
.stMarkdown h3{font-size:1.3rem!important;}
p,li,.stMarkdown p{font-family:var(--font-body)!important;font-size:0.9375rem;line-height:1.65;color:var(--ink-sec);}
hr,[data-testid="stDivider"] hr{border:none!important;border-top:1px solid var(--line)!important;margin:2rem 0!important;}
/* top navbar */
[data-testid="stPageLink-NavLink"]{background:var(--surface)!important;border:1px solid var(--line)!important;border-radius:8px!important;padding:0.5rem 0.65rem!important;min-height:44px!important;text-decoration:none!important;font-family:var(--font-body)!important;font-size:0.84rem!important;font-weight:500!important;color:#44403C!important;transition:all .2s ease!important;box-shadow:none!important;text-align:center!important;display:flex!important;align-items:center!important;justify-content:center!important;}
[data-testid="stPageLink-NavLink"]:hover{border-color:var(--brass)!important;color:var(--forest)!important;background:var(--brass-soft)!important;transform:translateY(-1px)!important;box-shadow:var(--shadow-hover)!important;}
[data-testid="stPageLink-NavLink"][aria-current="page"]{border-color:var(--brass)!important;background:var(--brass-soft)!important;color:var(--forest)!important;font-weight:700!important;box-shadow:inset 0 0 0 1px var(--brass)!important;}
/* masthead (replaces gradient hero) */
.spps-masthead{background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--brass);border-radius:12px;padding:2rem 2.25rem;margin-bottom:1.75rem;box-shadow:var(--shadow-card);}
.spps-eyebrow{font-family:var(--font-mono);font-size:0.7rem;font-weight:600;letter-spacing:0.16em;text-transform:uppercase;color:var(--brass);margin:0 0 0.5rem;}
.spps-masthead h1,.spps-mast-title{font-family:var(--font-display)!important;font-size:2.5rem!important;font-weight:600!important;color:var(--ink)!important;margin:0 0 0.5rem!important;line-height:1.1;}
.spps-mast-desc{font-family:var(--font-body);font-size:0.98rem;color:var(--ink-sec);line-height:1.65;max-width:640px;margin:0;}
.spps-mast-rule{border:none;border-top:1px solid var(--line);margin:1.25rem 0 0.9rem;}
.spps-beacon-row{display:flex;flex-wrap:wrap;gap:0.5rem 1.25rem;font-family:var(--font-mono);font-size:0.74rem;color:var(--ink-muted);}
.spps-beacon b{color:var(--forest);font-weight:600;}
/* legacy hero class kept as alias */
.spps-page-hero{background:var(--surface)!important;border:1px solid var(--line)!important;border-top:3px solid var(--brass)!important;border-radius:12px!important;padding:2rem 2.25rem!important;margin-bottom:1.75rem!important;box-shadow:var(--shadow-card)!important;}
.spps-page-hero::after{display:none!important;}
.spps-page-title{font-family:var(--font-display)!important;font-size:2.5rem!important;font-weight:600!important;color:var(--ink)!important;letter-spacing:0!important;margin:0 0 0.5rem!important;}
.spps-page-desc{font-family:var(--font-body)!important;font-size:0.98rem!important;color:var(--ink-sec)!important;max-width:640px!important;margin:0!important;}
/* KPI ledger */
.spps-kpi-row{display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap;}
.spps-kpi-card{flex:1;min-width:170px;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:1.25rem 1.4rem;position:relative;transition:all .2s ease;box-shadow:var(--shadow-card);}
.spps-kpi-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-hover);border-color:var(--accent-border);}
.spps-kpi-card::before{content:'';position:absolute;top:0;left:1.25rem;right:1.25rem;height:2px;background:var(--brass);opacity:.55;border-radius:0 0 2px 2px;}
.spps-kpi-icon{width:2.4rem;height:2.4rem;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:0.8rem;color:var(--forest);background:var(--paper);}
.spps-kpi-value{font-family:var(--font-display);font-size:2.35rem;font-weight:600;color:var(--ink);letter-spacing:0;line-height:1;margin-bottom:0.3rem;}
.spps-kpi-value.blue{color:var(--forest);}
.spps-kpi-label{font-family:var(--font-body);font-size:0.7rem;font-weight:600;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.1em;}
.spps-kpi-trend{font-family:var(--font-mono);font-size:0.74rem;color:var(--ink-muted);margin-top:0.4rem;}
/* section heading with brass rule */
.spps-section-head{margin:2.25rem 0 1rem;padding-left:1rem;border-left:2px solid var(--brass);}
.spps-section-head-title{font-family:var(--font-display);font-size:1.5rem;font-weight:600;color:var(--ink);margin:0;}
.spps-section-head-sub{font-family:var(--font-body);font-size:0.875rem;color:var(--ink-muted);margin:0.25rem 0 0;}
.spps-section-label{font-family:var(--font-body);font-size:0.7rem;font-weight:700;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;display:block;}
.spps-eyebrow-label{font-family:var(--font-mono);font-size:0.7rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:var(--brass);margin-bottom:0.5rem;display:block;}
/* dossier cards, stat cards */
.spps-stat-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:1.2rem 1.4rem;margin-bottom:0.75rem;transition:all .2s ease;box-shadow:var(--shadow-card);}
.spps-stat-card:hover{box-shadow:var(--shadow-hover);border-color:var(--accent-border);transform:translateY(-2px);}
.spps-stat-card-label{font-family:var(--font-body);font-size:0.7rem;font-weight:700;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;display:block;}
.spps-stat-card-value{font-family:var(--font-display);font-size:2rem;font-weight:600;color:var(--ink);line-height:1.1;}
.spps-stat-card-sub{font-size:0.8125rem;color:var(--ink-muted);margin-top:0.25rem;}
.spps-ledger-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:1.1rem 1.3rem;box-shadow:var(--shadow-card);}
.spps-ledger-card + .spps-ledger-card{margin-top:0.75rem;}
/* nav dossier cards */
.spps-navcard-box{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:1.35rem 1.15rem 1.2rem;text-align:left;transition:all .2s ease;box-shadow:var(--shadow-card);margin-bottom:0.6rem;min-height:190px;display:flex;flex-direction:column;justify-content:flex-start;}
.spps-navcard-box:hover{transform:translateY(-2px);box-shadow:var(--shadow-hover);border-color:var(--accent-border);}
.spps-navcard-icon{width:2.4rem;height:2.4rem;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:0.7rem;color:var(--forest);background:var(--paper);}
.spps-navcard-title{font-family:var(--font-display);font-size:1.25rem;font-weight:600;color:var(--ink);margin-bottom:0.3rem;}
.spps-navcard-desc{font-family:var(--font-body);font-size:0.82rem;color:var(--ink-muted);line-height:1.55;}
.spps-navcard-rule{width:2rem;height:2px;background:var(--brass);margin:0.6rem 0 0.5rem;opacity:.7;}
/* result panel — vellum dossier with seal */
.spps-result-panel{background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--brass);border-radius:12px;padding:2rem 2.25rem;box-shadow:var(--shadow-card);position:relative;margin:1rem 0;}
.spps-result-panel::before{display:none;}
.panel-high{border-top-color:var(--forest);}
.panel-medium{border-top-color:var(--brass);}
.panel-low{border-top-color:var(--clay);}
.spps-result-class{font-family:var(--font-display);font-size:3.2rem;font-weight:600;color:var(--ink);letter-spacing:0;line-height:1;margin:0.5rem 0;}
.spps-result-conf{font-family:var(--font-mono);font-size:0.85rem;color:var(--ink-muted);margin-top:0.4rem;}
.spps-conf-badge{display:inline-block;font-family:var(--font-mono);font-size:0.85rem;color:var(--forest);background:var(--brass-soft);border:1px solid var(--accent-border);border-radius:6px;padding:3px 10px;font-weight:600;}
.spps-seal{display:inline-flex;align-items:center;gap:0.5rem;font-family:var(--font-mono);font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--brass);}
/* narrative, suggestions, counterfactuals */
.spps-narrative{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--brass);border-radius:8px;padding:1rem 1.25rem;font-size:0.92rem;color:var(--ink);line-height:1.65;margin-bottom:1.25rem;}
.spps-cf-card{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:1rem 1.25rem;margin:0.6rem 0;display:flex;gap:1rem;align-items:flex-start;transition:all .2s ease;box-shadow:var(--shadow-card);}
.spps-cf-card:hover{border-color:var(--accent-border);box-shadow:var(--shadow-hover);transform:translateX(2px);}
.spps-cf-icon{flex-shrink:0;width:2.4rem;height:2.4rem;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;justify-content:center;color:var(--forest);background:var(--paper);}
.spps-cf-action{font-weight:600;font-size:0.92rem;color:var(--ink);margin:0 0 0.15rem;}
.spps-cf-detail{font-size:0.82rem;color:var(--ink-muted);margin:0;}
.spps-suggestion{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--forest);border-radius:8px;padding:0.85rem 1.1rem;margin:0.5rem 0;font-size:0.9rem;color:var(--ink);transition:all .2s ease;}
.spps-suggestion:hover{background:var(--brass-soft);border-color:var(--accent-border);}
/* delta chips */
.spps-delta{display:inline-flex;align-items:center;gap:4px;font-family:var(--font-mono);font-size:0.8rem;font-weight:600;border-radius:6px;padding:3px 9px;border:1px solid var(--line);}
.spps-delta.up{color:var(--forest);background:var(--brass-soft);border-color:var(--accent-border);}
.spps-delta.down{color:var(--clay);background:rgba(124,45,18,.07);border-color:rgba(124,45,18,.25);}
.spps-delta.neutral{color:var(--ink-muted);background:var(--paper);}
/* probability ledger bars */
.spps-class-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle;}
.spps-prob-wrap{margin:0.9rem 0;}
.spps-prob-label-row{display:flex;justify-content:space-between;font-size:0.82rem;color:var(--ink-sec);margin-bottom:0.35rem;}
.spps-prob-track{width:100%;height:10px;background:var(--surface-alt);border:1px solid var(--line-soft);border-radius:99px;overflow:hidden;}
.spps-prob-fill{height:100%;border-radius:99px;transition:width .25s ease;background:var(--forest);}
.spps-prob-fill.fill-mid{background:var(--brass);}
.spps-prob-fill.fill-low{background:var(--clay);}
/* charts */
.spps-chart-section{margin-bottom:2.5rem;}
.spps-chart-title{font-family:var(--font-display);font-size:1.25rem;font-weight:600;color:var(--ink);margin-bottom:0.2rem;}
.spps-chart-caption{font-size:0.82rem!important;color:var(--ink-muted)!important;line-height:1.55;}
.spps-caption{font-size:0.82rem!important;color:var(--ink-muted)!important;line-height:1.5;}
[data-testid="stPlotlyChart"]{border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow-card);background:var(--surface);}
[data-testid="stDataFrame"]{border:1px solid var(--line)!important;border-radius:var(--radius)!important;overflow:hidden;box-shadow:var(--shadow-card);}
[data-baseweb="tab-list"]{background:var(--surface-alt)!important;border:1px solid var(--line)!important;border-radius:8px!important;padding:4px!important;gap:2px!important;}
[data-baseweb="tab"]{border-radius:6px!important;font-weight:500!important;font-size:0.875rem!important;color:var(--ink-muted)!important;}
[aria-selected="true"][data-baseweb="tab"]{background:var(--surface)!important;color:var(--forest)!important;box-shadow:var(--shadow-card)!important;font-weight:600!important;}
/* buttons — forest primary, no gradient */
.stButton>button[kind="primary"],.stButton>button[data-testid="baseButton-primary"]{background:var(--forest)!important;color:#FAF8F3!important;border:1px solid var(--forest-deep)!important;border-radius:8px!important;font-weight:600!important;font-size:0.9rem!important;padding:0.65rem 1.75rem!important;min-height:44px!important;box-shadow:var(--shadow-card)!important;transition:all .2s ease!important;}
.stButton>button[kind="primary"]:hover{background:var(--forest-deep)!important;box-shadow:var(--shadow-hover)!important;transform:translateY(-1px)!important;}
.stButton>button[kind="secondary"],.stButton>button[data-testid="baseButton-secondary"]{background:transparent!important;color:var(--ink)!important;border:1px solid var(--line)!important;border-radius:8px!important;font-size:0.875rem!important;font-weight:500!important;min-height:44px!important;transition:all .2s ease;}
.stButton>button[kind="secondary"]:hover{border-color:var(--brass)!important;color:var(--forest)!important;background:var(--brass-soft)!important;}
/* inputs */
[data-testid="stSlider"] label{font-size:0.875rem!important;color:var(--ink-sec)!important;font-weight:500!important;}
[data-testid="stSlider"]>div>div>div>div{background:var(--forest)!important;}
[data-testid="stSlider"] [role="slider"]{background:var(--surface)!important;border:2px solid var(--forest)!important;box-shadow:0 0 0 4px var(--brass-soft)!important;min-width:22px!important;min-height:22px!important;}
[data-testid="stSelectbox"] label,[data-testid="stNumberInput"] label,[data-testid="stRadio"] label{font-size:0.875rem!important;color:var(--ink-sec)!important;font-weight:500!important;}
[data-testid="stSelectbox"]>div>div{border-color:var(--line)!important;border-radius:8px!important;background:var(--surface)!important;}
[data-testid="stAlert"]{border-radius:8px!important;border:1px solid var(--line)!important;background:var(--surface-alt)!important;color:var(--ink-sec)!important;font-size:0.875rem!important;}
details>summary{font-size:0.875rem!important;color:var(--ink-sec)!important;font-weight:500!important;min-height:44px!important;}
.stDownloadButton>button{min-height:44px!important;}
/* tables */
.spps-class-stat{display:flex;align-items:center;gap:0.75rem;padding:0.65rem 0;border-bottom:1px solid var(--line);font-size:0.875rem;}
.spps-class-stat:last-child{border-bottom:none;}
.spps-class-stat-label{min-width:65px;color:var(--ink);font-weight:600;}
.spps-class-stat-bar-wrap{flex:1;height:6px;background:var(--surface-alt);border:1px solid var(--line-soft);border-radius:99px;overflow:hidden;}
.spps-class-stat-bar{height:100%;border-radius:99px;}
.spps-class-stat-pct{min-width:42px;text-align:right;color:var(--ink-muted);font-family:var(--font-mono);font-size:0.78rem;}
.spps-hero{text-align:center;padding:2.25rem 1rem;background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--brass);border-radius:12px;margin-bottom:1.5rem;}
.spps-hero-number{font-family:var(--font-display);font-size:4.5rem;font-weight:600;color:var(--forest);line-height:1;}
.spps-hero-label{font-size:0.7rem;font-weight:700;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;}
.spps-hero-note{font-size:0.9rem;color:var(--ink-sec);margin-top:0.6rem;}
.spps-footnote{margin-top:3rem;font-family:var(--font-mono);font-size:0.72rem;color:var(--ink-muted);text-align:center;}
/* motion: restrained 200-250ms */
@keyframes fadeInUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.anim-fade-up{animation:fadeInUp .25s ease both;}
.anim-fade{animation:fadeIn .25s ease both;}
.anim-scale-in{animation:fadeInUp .25s ease both;}
.anim-slide-right{animation:fadeInUp .25s ease both;}
.anim-glow{animation:none;}
.anim-fade-up-1{animation-delay:0.03s;}.anim-fade-up-2{animation-delay:0.06s;}.anim-fade-up-3{animation-delay:0.09s;}.anim-fade-up-4{animation-delay:0.12s;}.anim-fade-up-5{animation-delay:0.15s;}
.main .block-container>div:nth-child(1){animation:fadeInUp .25s ease both;}
.main .block-container>div:nth-child(2){animation:fadeInUp .25s .03s ease both;}
.main .block-container>div:nth-child(3){animation:fadeInUp .25s .06s ease both;}
.main .block-container>div:nth-child(4){animation:fadeInUp .25s .09s ease both;}
.main .block-container>div:nth-child(5){animation:fadeInUp .25s .12s ease both;}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation:none!important;transition:none!important;}}
@media (max-width: 768px){.block-container{padding:1rem 1rem 3rem!important;}.spps-masthead h1,.spps-mast-title,.spps-page-title{font-size:1.9rem!important;}.spps-result-class{font-size:2.4rem!important;}.spps-kpi-row{flex-direction:column;}}
</style>
"""

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def inject_theme(active_page: str = "home") -> None:
    """Inject CSS + top navbar. Call immediately after set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)

    with st.container():
        c_brand, c_home, c_over, c_pred, c_whatif, c_cohort, c_models = st.columns(
            [1.5, 0.9, 1.1, 1.1, 1.0, 1.1, 1.3],
            vertical_alignment="center",
        )
        with c_brand:
            st.markdown(
                '<div style="display:flex;align-items:center;gap:8px;padding-left:2px;">'
                f'<span style="width:26px;height:26px;border:1px solid var(--brass);border-radius:50%;'
                'display:inline-flex;align-items:center;justify-content:center;'
                'background:var(--forest);color:#FAF8F3;font-family:var(--font-display);'
                'font-size:0.8rem;font-weight:700;">S</span>'
                '<span style="font-family:var(--font-display);font-weight:600;'
                'font-size:1.3rem;color:var(--ink);">SPPS</span>'
                '<span style="font-family:var(--font-mono);font-size:0.6rem;color:var(--brass);'
                'font-weight:600;border:1px solid var(--line);padding:2px 6px;border-radius:4px;'
                'text-transform:uppercase;letter-spacing:0.1em;">Est. MMXXVI</span>'
                "</div>",
                unsafe_allow_html=True,
            )
        with c_home:
            st.page_link("app.py", label="Home", use_container_width=True)
        with c_over:
            st.page_link("pages/1_Overview.py", label="Overview", use_container_width=True)
        with c_pred:
            st.page_link("pages/2_Individual_Predictor.py", label="Predictor", use_container_width=True)
        with c_whatif:
            st.page_link("pages/3_What_If_Simulator.py", label="What-If", use_container_width=True)
        with c_cohort:
            st.page_link("pages/4_Cohort_Simulator.py", label="Cohort Sim", use_container_width=True)
        with c_models:
            st.page_link("pages/5_Model_and_Fairness.py", label="Model & Fairness", use_container_width=True)

    st.markdown(
        '<hr style="margin:0.25rem 0 1.25rem 0;border:none;border-top:1px solid var(--line);">',
        unsafe_allow_html=True,
    )


def masthead(eyebrow: str, title: str, description: str, beacons: list[str] | None = None) -> str:
    """Old-money masthead: eyebrow + serif title + rule + beacon ledger."""
    beacons = beacons or []
    beacon_html = ""
    if beacons:
        beacon_html = '<div class="spps-beacon-row">' + "".join(
            f"<span>{html.escape(b)}</span>" for b in beacons
        ) + "</div>"
    return f"""
<div class="spps-masthead anim-fade-up">
  <p class="spps-eyebrow">{html.escape(eyebrow)}</p>
  <h1 class="spps-mast-title">{html.escape(title)}</h1>
  <p class="spps-mast-desc">{html.escape(description)}</p>
  <hr class="spps-mast-rule" />
  {beacon_html}
</div>
"""


def page_hero(title: str, description: str) -> str:
    """Backward-compat alias → masthead styling."""
    return f"""
<div class="spps-page-hero anim-fade-up">
  <p class="spps-eyebrow">Student Performance Intelligence</p>
  <p class="spps-page-title">{html.escape(title)}</p>
  <p class="spps-page-desc">{html.escape(description)}</p>
</div>
"""


def hero_stat(value: str, label: str, note: str = "") -> str:
    """Large centered ledger number block."""
    note_html = f'<p class="spps-hero-note">{html.escape(note)}</p>' if note else ""
    return f"""
<div class="spps-hero anim-fade-up">
  <p class="spps-hero-label">{html.escape(label)}</p>
  <p class="spps-hero-number">{html.escape(value)}</p>
  {note_html}
</div>
"""


def stat_card(title: str, value: str, subtitle: str = "", delay: int = 0) -> str:
    """Secondary metric card."""
    delay_class = f"anim-fade-up-{delay}" if 1 <= delay <= 5 else ""
    sub_html = f'<p class="spps-stat-card-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    return f"""
<div class="spps-stat-card anim-fade-up {delay_class}">
  <p class="spps-stat-card-label">{html.escape(title)}</p>
  <p class="spps-stat-card-value">{html.escape(value)}</p>
  {sub_html}
</div>
"""


def kpi_hero_row(stats: list[dict]) -> str:
    """Ledger row of KPI cards. Each dict: icon (svg key), value, label, trend, blue."""
    cards = ""
    for i, s in enumerate(stats):
        delay = min(i + 1, 5)
        blue_cls = "blue" if s.get("blue") else ""
        trend_html = (
            f'<div class="spps-kpi-trend">{html.escape(str(s["trend"]))}</div>'
            if s.get("trend") else ""
        )
        raw_icon = str(s.get("icon", "ledger"))
        # Map legacy emoji → svg keys
        emoji_map = {
            "🎓": "cap", "🎯": "target", "📐": "ledger", "🔬": "flask",
            "🌟": "seal", "📈": "ledger", "⚠️": "ledger", "🏆": "seal",
            "⚖️": "scales", "🏫": "users", "⚙️": "sliders", "🔮": "ledger",
        }
        key = emoji_map.get(raw_icon, raw_icon if raw_icon in _ICONS else "ledger")
        cards += f"""
<div class="spps-kpi-card anim-fade-up anim-fade-up-{delay}">
  <span class="spps-kpi-icon">{icon(key, 18, FOREST)}</span>
  <div class="spps-kpi-value {blue_cls}">{html.escape(str(s['value']))}</div>
  <div class="spps-kpi-label">{html.escape(str(s['label']))}</div>
  {trend_html}
</div>"""
    return f'<div class="spps-kpi-row">{cards}</div>'


def section_heading(title: str, subtitle: str = "") -> str:
    """Section heading with brass left rule."""
    sub = f'<p class="spps-section-head-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    return (
        f'<div class="spps-section-head"><p class="spps-section-head-title">'
        f"{html.escape(title)}</p>{sub}</div>"
    )


def dossier_header(eyebrow: str, title: str, subtitle: str = "") -> str:
    """Alias for section_heading with eyebrow styling."""
    return section_heading(title, subtitle)


def result_panel(
    predicted_class: str,
    label: str,
    confidence: float,
    runner_up: str = "",
    runner_prob: float = 0.0,
    is_borderline: bool = False,
) -> str:
    """Vellum prediction dossier with seal."""
    panel_map = {"H": "panel-high", "M": "panel-medium", "L": "panel-low"}
    panel_cls = panel_map.get(predicted_class, "panel-medium")
    conf_pct = f"{confidence:.0%}"

    borderline_note = ""
    if is_borderline:
        borderline_note = (
            '<p class="spps-result-conf" style="margin-top:0.5rem;">'
            "Borderline — this student sits close to the class boundary."
            "</p>"
        )

    runner_html = ""
    if runner_up and runner_up != "—":
        runner_label = CLASS_LABELS.get(runner_up, runner_up)
        runner_html = (
            f"<p class=\"spps-result-conf\">Runner-up: {html.escape(runner_label)} "
            f"({runner_prob:.0%})</p>"
        )

    return f"""
<div class="spps-result-panel {panel_cls} anim-fade-up">
  <span class="spps-seal">{icon('seal', 14, BRASS)} Faculty dossier · sealed</span>
  <p class="spps-stat-card-label" style="margin-top:0.6rem;">Predicted Performance Band</p>
  <p class="spps-result-class">{html.escape(label)}</p>
  <p class="spps-result-conf">Confidence <span class="spps-conf-badge">{conf_pct}</span></p>
  {runner_html}
  {borderline_note}
</div>
"""


def shap_narrative(top_features: list[str], direction: str = "toward") -> str:
    """Plain-English SHAP summary sentence."""
    if not top_features:
        return ""
    safe = [html.escape(t) for t in top_features]
    if len(safe) == 1:
        feature_str = safe[0]
    elif len(safe) == 2:
        feature_str = f"{safe[0]} and {safe[1]}"
    else:
        feature_str = f"{', '.join(safe[:-1])}, and {safe[-1]}"

    verb = "are" if len(safe) > 1 else "is"
    plural = "s" if len(safe) > 1 else ""
    if direction == "toward":
        sentence = (
            f"{feature_str} {verb} the strongest factor{plural} "
            "driving this prediction upward."
        )
    else:
        sentence = (
            f"{feature_str} {verb} the strongest factor{plural} "
            "pulling this prediction down."
        )
    return f'<div class="spps-narrative anim-fade-up"><strong>Reading:</strong> {sentence}</div>'


def cf_card(icon_name: str, action_line: str, detail: str = "") -> str:
    """Counterfactual / recommendation card. icon_name is an SVG key."""
    key = icon_name if icon_name in _ICONS else "arrow"
    detail_html = f'<p class="spps-cf-detail">{html.escape(detail)}</p>' if detail else ""
    return f"""
<div class="spps-cf-card anim-fade-up">
  <span class="spps-cf-icon">{icon(key, 18, FOREST)}</span>
  <div class="spps-cf-body">
    <p class="spps-cf-action">{html.escape(action_line)}</p>
    {detail_html}
  </div>
</div>
"""


def suggestion_card(text: str) -> str:
    """Improvement suggestion card."""
    return f'<div class="spps-suggestion anim-fade-up">{html.escape(text)}</div>'


def probability_bar(probs: dict[str, float], predicted_class: str) -> str:
    """Ledger probability bars for H/M/L."""
    fill_cls = {"H": "", "M": "fill-mid", "L": "fill-low"}
    dot = {"H": FOREST, "M": BRASS, "L": CLAY}
    bars_html = ""
    for cls, label in [("H", "High"), ("M", "Medium"), ("L", "Low")]:
        prob = probs.get(cls, 0)
        pct = prob * 100
        fc = fill_cls[cls]
        bold = " font-weight:700; color:var(--ink);" if cls == predicted_class else ""
        bars_html += f"""
<div class="spps-prob-wrap">
  <div class="spps-prob-label-row">
    <span style="{bold}"><span class="spps-class-dot" style="background:{dot[cls]};"></span>{label}</span>
    <span style="font-family:var(--font-mono);font-size:0.8rem;{bold}">{prob:.0%}</span>
  </div>
  <div class="spps-prob-track">
    <div class="spps-prob-fill {fc}" style="width:{pct:.1f}%;"></div>
  </div>
</div>"""
    return bars_html


def delta_chip(
    value,
    direction: str | None = None,
    prefix: str = "",
    suffix: str = "",
) -> str:
    """Inline delta chip, e.g. ↑ +15% / ↓ -30% / → 0."""
    is_number = isinstance(value, (int, float)) and not isinstance(value, bool)

    if is_number:
        if direction is None:
            direction = "up" if value > 0 else ("down" if value < 0 else "neutral")
        num = "0" if value == 0 else f"{value:+g}"
        display = f"{prefix}{num}{suffix}"
    else:
        direction = direction or "neutral"
        display = f"{prefix}{value}{suffix}"

    arrow = {"up": "↑", "down": "↓", "neutral": "→"}.get(direction, "→")
    return f'<span class="spps-delta {direction}">{arrow} {html.escape(display)}</span>'


def verdict_banner(verdict: str, headline: str) -> str:
    """Fairness verdict banner in muted academic tones."""
    color = VERDICT.get(verdict, INK_MUTED)
    return (
        f'<div style="background:var(--surface);border:1px solid var(--line);'
        f'border-left:3px solid {color};border-radius:var(--radius);'
        f'padding:1.1rem 1.35rem;margin-bottom:1rem;">'
        f'<p style="font-family:var(--font-mono);font-size:0.72rem;text-transform:uppercase;'
        f'letter-spacing:0.1em;color:{color};margin:0 0 0.3rem;">Overall verdict — '
        f"{html.escape(verdict)}</p>"
        f'<p style="font-size:0.95rem;color:var(--ink);margin:0;line-height:1.6;">'
        f"{html.escape(headline)}</p></div>"
    )


def footnote(text: str) -> str:
    """Centered mono footnote."""
    return f"<div class='spps-footnote'>{html.escape(text)}</div>"
