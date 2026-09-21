"""
dashboard/theme.py — Student Success · Academic Intelligence Platform
Design System v2.0

Call inject_theme() as the FIRST thing after st.set_page_config() on every page.

Color Tokens (CSS variables):
    BG         #F8FAFC  near-white page
    SURFACE    #FFFFFF  card white
    INK        #1E293B  deep slate (primary text)
    INK_SEC    #475569  slate (secondary)
    INK_MUTED  #94A3B8  light slate (muted)
    ACCENT     #2563EB  calm academic blue (primary)
    TEAL       #0891B2  secondary teal
    PURPLE     #7C3AED  secondary purple
    GREEN      #059669  HIGH performance (soft green)
    AMBER      #D97706  MEDIUM performance (soft amber)
    CORAL      #DC2626  LOW performance (soft coral)
    LINE       #E2E8F0  hairline borders

Typography: Inter — clear hierarchy without decorative serifs.
Icons: inline Lucide-style SVG via icon(). No emoji for structural icons.
Motion: 200ms ease, prefers-reduced-motion respected.
"""

from __future__ import annotations

import html

import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens — single source of truth
# ---------------------------------------------------------------------------
BG          = "#F8FAFC"
SURFACE     = "#FFFFFF"
SURFACE_ALT = "#F1F5F9"
INK         = "#1E293B"
INK_SEC     = "#475569"
INK_MUTED   = "#94A3B8"
ACCENT      = "#2563EB"
ACCENT_SOFT = "rgba(37,99,235,0.08)"
ACCENT_BDR  = "rgba(37,99,235,0.20)"
TEAL        = "#0891B2"
TEAL_SOFT   = "rgba(8,145,178,0.08)"
PURPLE      = "#7C3AED"
PURPLE_SOFT = "rgba(124,58,237,0.08)"
GREEN       = "#059669"
GREEN_SOFT  = "rgba(5,150,105,0.10)"
AMBER       = "#D97706"
AMBER_SOFT  = "rgba(217,119,6,0.10)"
CORAL       = "#DC2626"
CORAL_SOFT  = "rgba(220,38,38,0.10)"
LINE        = "#E2E8F0"
LINE_SOFT   = "#F1F5F9"

# Backward-compat aliases (old pages import these names)
PAPER       = BG
OXFORD      = "#1E293B"
FOREST      = ACCENT
FOREST_DEEP = "#1D4ED8"
BRASS       = AMBER
BRASS_SOFT  = AMBER_SOFT
CLAY        = CORAL
CHART_GRAY  = INK_MUTED
CHART_DARK  = INK_SEC
SIDEBAR_BG  = SURFACE
BORDER      = LINE

CLASS_COLORS = {
    "H": GREEN,   # High — soft green
    "M": AMBER,   # Medium — soft amber
    "L": CORAL,   # Low — soft coral
}
CLASS_LABELS = {"H": "High", "M": "Medium", "L": "Low"}

VERDICT = {
    "acceptable": GREEN,
    "concern":    AMBER,
    "fail":       CORAL,
}

PLOTLY_BASE = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color=INK_SEC, size=12),
    hoverlabel=dict(
        bgcolor=SURFACE, bordercolor=LINE,
        font=dict(family="Inter, system-ui, sans-serif", size=13),
    ),
)

PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo":    False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "toImageButtonOptions": {"format": "png", "filename": "student_success_chart", "scale": 2},
}

GRID      = LINE
ZERO_LINE = "#CBD5E1"

# ---------------------------------------------------------------------------
# Inline SVG icons (Lucide-style, stroke 1.5) — no emoji
# ---------------------------------------------------------------------------
_ICONS: dict[str, str] = {
    # Navigation
    "home":       '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "user":       '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "trending":   '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "users":      '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "shield":     '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "info":       '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    # Content
    "cap":        '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
    "target":     '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "chart":      '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    "activity":   '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "check":      '<polyline points="20 6 9 17 4 12"/>',
    "check-circle":'<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "arrow":      '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    "star":       '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "book":       '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "bulb":       '<line x1="9" y1="18" x2="15" y2="18"/><line x1="10" y1="22" x2="14" y2="22"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>',
    "sliders":    '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
    "flask":      '<path d="M9 3h6"/><path d="M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3"/><path d="M7.5 15h9"/>',
    "scales":     '<path d="M12 4v16"/><path d="M8 20h8"/><path d="M12 6 6 8m6-2 6 2"/><path d="M3.5 13 6 8l2.5 5a2.6 2.6 0 0 1-5 0Zm12 0L18 8l2.5 5a2.6 2.6 0 0 1-5 0Z"/>',
    "calendar":   '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "bell":       '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    "sparkle":    '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z"/>',
    "play":       '<polygon points="5 3 19 12 5 21 5 3"/>',
    "refresh":    '<polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>',
    "settings":   '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    # Legacy keys for backward compat
    "ledger":     '<rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="8" x2="16" y2="8"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="8" y1="16" x2="12" y2="16"/>',
    "seal":       '<circle cx="12" cy="10" r="6"/><path d="m9 15-2 6 5-2.5L17 21l-2-6"/>',
    "navigation": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
}


def icon(name: str, size: int = 18, color: str = "currentColor") -> str:
    """Inline SVG icon. Never use emoji for structural icons."""
    paths = _ICONS.get(name, _ICONS["ledger"])
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.75" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{paths}</svg>'
    )


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Design tokens ───────────────────────────────────────────────────── */
:root{
  --bg:#F8FAFC; --surface:#FFFFFF; --surface-alt:#F1F5F9;
  --ink:#1E293B; --ink-sec:#475569; --ink-muted:#94A3B8;
  --line:#E2E8F0; --line-soft:#F1F5F9;
  --accent:#2563EB; --accent-soft:rgba(37,99,235,.08); --accent-bdr:rgba(37,99,235,.20);
  --teal:#0891B2; --teal-soft:rgba(8,145,178,.08);
  --purple:#7C3AED; --purple-soft:rgba(124,58,237,.08);
  --green:#059669; --green-soft:rgba(5,150,105,.10);
  --amber:#D97706; --amber-soft:rgba(217,119,6,.10);
  --coral:#DC2626; --coral-soft:rgba(220,38,38,.10);
  --radius:12px; --radius-sm:8px; --radius-xs:6px;
  --shadow:0 1px 3px rgba(0,0,0,.08),0 1px 2px rgba(0,0,0,.04);
  --shadow-md:0 4px 6px rgba(0,0,0,.07),0 2px 4px rgba(0,0,0,.06);
  --shadow-lg:0 10px 15px rgba(0,0,0,.1),0 4px 6px rgba(0,0,0,.05);
  --font-body:'Inter',system-ui,-apple-system,sans-serif;
  --font-mono:ui-monospace,'SFMono-Regular','Cascadia Code',monospace;
  /* backward compat aliases */
  --paper:var(--bg); --oxford:var(--ink); --forest:var(--accent);
  --forest-deep:#1D4ED8; --brass:var(--amber); --brass-soft:var(--amber-soft);
  --clay:var(--coral); --border:var(--line);
  --font-display:var(--font-body);
}

/* ── Base reset ──────────────────────────────────────────────────────── */
html,body,[class*="css"]{font-family:var(--font-body)!important;color:var(--ink);background:var(--bg);}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent!important;z-index:90!important;}
header[data-testid="stHeader"] button{visibility:visible!important;}
[data-testid="stSidebarCollapsedControl"]{
  display:flex!important;
  visibility:visible!important;
  z-index:99!important;
  color:var(--ink)!important;
  background:var(--surface)!important;
  border:1px solid var(--line)!important;
  border-radius:var(--radius-sm)!important;
  padding:4px!important;
  margin:10px!important;
}
.main{background:var(--bg)!important;}
.block-container{max-width:1260px!important;padding:1rem 2rem 4rem!important;margin-top:0!important;}

/* ── Sidebar ─────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"]{
  background:var(--surface)!important;
  border-right:1px solid var(--line)!important;
  min-width:240px!important;
  max-width:280px!important;
  display:block!important;
  visibility:visible!important;
}
[data-testid="stSidebarNav"]{
  padding:0 8px 8px!important;
}
[data-testid="stSidebarNav"] ul{
  padding:0!important;
  list-style:none!important;
}
[data-testid="stSidebarNav"] [data-testid="stSidebarNavSeparator"]{
  padding-top:10px!important;
  margin-top:6px!important;
  border-top:1px solid var(--line)!important;
}
[data-testid="stSidebarNav"] [data-testid="stSidebarNavSeparator"] span{
  font-size:0.68rem!important;
  font-weight:600!important;
  text-transform:uppercase!important;
  letter-spacing:0.1em!important;
  color:var(--ink-muted)!important;
}
[data-testid="stSidebarNav"] a{
  border-radius:var(--radius-sm)!important;
  padding:8px 12px!important;
  font-family:var(--font-body)!important;
  font-size:0.875rem!important;
  font-weight:500!important;
  color:var(--ink-sec)!important;
  transition:all .15s ease!important;
  margin:1px 0!important;
}
[data-testid="stSidebarNav"] a:hover{
  background:var(--surface-alt)!important;
  color:var(--accent)!important;
}
[data-testid="stSidebarNav"] a[aria-current="page"]{
  background:var(--accent-soft)!important;
  color:var(--accent)!important;
  font-weight:600!important;
}
section[data-testid="stSidebar"] > div:first-child{padding:0!important;}
[data-testid="stSidebarUserContent"]{padding:0!important;}
/* Sidebar page links */
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]{
  background:transparent!important;
  border:none!important;
  border-radius:var(--radius-sm)!important;
  padding:9px 12px!important;
  font-family:var(--font-body)!important;
  font-size:0.875rem!important;
  font-weight:500!important;
  color:var(--ink-sec)!important;
  text-align:left!important;
  justify-content:flex-start!important;
  width:calc(100% - 16px)!important;
  margin:1px 8px!important;
  box-shadow:none!important;
  min-height:40px!important;
  transition:all .15s ease!important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover{
  background:var(--surface-alt)!important;
  color:var(--accent)!important;
  transform:none!important;
  box-shadow:none!important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"]{
  background:var(--accent-soft)!important;
  color:var(--accent)!important;
  font-weight:600!important;
  border:none!important;
  box-shadow:none!important;
}
/* Sidebar brand block */
.ss-sidebar-brand{
  display:flex;align-items:center;gap:10px;
  padding:20px 16px 16px;border-bottom:1px solid var(--line);margin-bottom:8px;
}
.ss-brand-logo{
  width:36px;height:36px;border-radius:8px;
  background:var(--accent);color:#fff;
  display:flex;align-items:center;justify-content:center;
  font-size:1rem;font-weight:700;flex-shrink:0;
}
.ss-brand-name{font-size:0.9rem;font-weight:700;color:var(--ink);line-height:1.2;}
.ss-brand-tagline{font-size:0.7rem;color:var(--ink-muted);margin-top:1px;}
/* Sidebar section label */
.ss-nav-label{
  font-size:0.68rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;
  color:var(--ink-muted);padding:4px 16px 4px;margin-top:4px;
}
.ss-nav-divider{border:none;border-top:1px solid var(--line);margin:8px 16px;}
/* System status card */
.ss-status-card{
  margin:8px;border:1px solid var(--line);border-radius:var(--radius-sm);
  padding:12px;background:var(--surface-alt);
}
.ss-status-row{display:flex;align-items:center;gap:6px;margin-bottom:4px;}
.ss-status-dot{width:8px;height:8px;border-radius:50%;background:#10B981;flex-shrink:0;}
.ss-status-label{font-size:0.8rem;font-weight:600;color:var(--ink);}
.ss-status-meta{font-size:0.73rem;color:var(--ink-muted);line-height:1.7;}
.ss-sidebar-quote{
  padding:12px 16px;font-size:0.78rem;font-style:italic;
  color:var(--ink-muted);line-height:1.55;
}

/* ── Top header bar ──────────────────────────────────────────────────── */
.ss-top-bar{
  display:flex;align-items:center;justify-content:space-between;
  padding:12px 0 12px;border-bottom:1px solid var(--line);margin-bottom:24px;
  position:sticky;top:0;background:var(--bg);z-index:100;
}
.ss-search-wrap{
  display:flex;align-items:center;gap:8px;
  background:var(--surface);border:1px solid var(--line);
  border-radius:var(--radius-sm);padding:8px 14px;
  width:280px;transition:border-color .15s;
}
.ss-search-wrap:focus-within{border-color:var(--accent);}
.ss-search-input{
  border:none;outline:none;background:transparent;
  font-family:var(--font-body);font-size:0.875rem;color:var(--ink-sec);
  width:100%;
}
.ss-search-input::placeholder{color:var(--ink-muted);}
.ss-header-right{display:flex;align-items:center;gap:12px;}
.ss-bell-btn{
  width:36px;height:36px;border-radius:var(--radius-sm);background:var(--surface);
  border:1px solid var(--line);display:flex;align-items:center;justify-content:center;
  cursor:pointer;position:relative;transition:border-color .15s;
}
.ss-bell-btn:hover{border-color:var(--accent);}
.ss-bell-badge{
  position:absolute;top:6px;right:6px;width:8px;height:8px;
  border-radius:50%;background:var(--coral);border:2px solid var(--bg);
}
.ss-user-wrap{display:flex;align-items:center;gap:8px;}
.ss-avatar{
  width:36px;height:36px;border-radius:50%;background:var(--accent);
  color:#fff;display:flex;align-items:center;justify-content:center;
  font-size:0.8rem;font-weight:700;flex-shrink:0;
}
.ss-user-name{font-size:0.875rem;font-weight:600;color:var(--ink);}
.ss-user-role{font-size:0.73rem;color:var(--ink-muted);}

/* ── Page header ─────────────────────────────────────────────────────── */
.ss-page-header{margin-bottom:24px;}
.ss-page-label{
  font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;
  color:var(--accent);margin-bottom:4px;
}
.ss-page-title{
  font-family:var(--font-body);font-size:2rem;font-weight:700;
  color:var(--ink);line-height:1.2;margin:0 0 6px;
}
.ss-page-subtitle{font-size:0.9375rem;color:var(--ink-sec);line-height:1.6;margin:0;}

/* ── Hero banner (page header with illustration area) ─────────────────── */
.ss-hero-banner{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:24px 28px;margin-bottom:24px;box-shadow:var(--shadow);
  display:flex;align-items:flex-start;justify-content:space-between;gap:16px;
}
.ss-hero-left{flex:1;}
.ss-hero-label{font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:var(--accent);margin-bottom:4px;}
.ss-hero-title{font-size:1.9rem;font-weight:700;color:var(--ink);line-height:1.2;margin:0 0 6px;}
.ss-hero-sub{font-size:0.9375rem;color:var(--ink-sec);line-height:1.6;margin:0;}
.ss-hero-right{
  flex-shrink:0;width:220px;min-height:90px;border-radius:var(--radius-sm);
  background:linear-gradient(135deg,var(--accent-soft) 0%,var(--teal-soft) 100%);
  display:flex;align-items:center;justify-content:center;
  font-size:0.8rem;color:var(--accent);text-align:center;padding:12px;
  font-style:italic;line-height:1.5;
}

/* ── Metric / KPI cards ──────────────────────────────────────────────── */
.ss-kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px;}
@media(max-width:900px){.ss-kpi-grid{grid-template-columns:repeat(2,1fr);}}
@media(max-width:600px){.ss-kpi-grid{grid-template-columns:1fr;}}
.ss-kpi-card{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:20px;box-shadow:var(--shadow);transition:all .2s ease;
}
.ss-kpi-card:hover{box-shadow:var(--shadow-md);border-color:var(--accent-bdr);transform:translateY(-1px);}
.ss-kpi-icon-wrap{
  width:40px;height:40px;border-radius:var(--radius-sm);display:flex;
  align-items:center;justify-content:center;margin-bottom:12px;
}
.ss-kpi-value{font-size:2rem;font-weight:700;color:var(--ink);line-height:1;margin-bottom:2px;}
.ss-kpi-label{font-size:0.8rem;font-weight:500;color:var(--ink-sec);margin-bottom:6px;}
.ss-kpi-sub{font-size:0.75rem;color:var(--ink-muted);margin-bottom:4px;}
.ss-kpi-trend{display:flex;align-items:center;gap:4px;font-size:0.78rem;font-weight:500;}
.ss-trend-up{color:#10B981;}.ss-trend-down{color:var(--coral);}
.ss-trend-neutral{color:var(--ink-muted);}

/* ── Status badges ───────────────────────────────────────────────────── */
.ss-badge{
  display:inline-flex;align-items:center;gap:5px;padding:4px 10px;
  border-radius:99px;font-size:0.75rem;font-weight:600;
}
.ss-badge-high{background:var(--green-soft);color:var(--green);}
.ss-badge-medium{background:var(--amber-soft);color:var(--amber);}
.ss-badge-low{background:var(--coral-soft);color:var(--coral);}
.ss-badge-blue{background:var(--accent-soft);color:var(--accent);}
.ss-badge-teal{background:var(--teal-soft);color:var(--teal);}
.ss-badge-purple{background:var(--purple-soft);color:var(--purple);}

/* ── Content cards ───────────────────────────────────────────────────── */
.ss-card{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:20px;box-shadow:var(--shadow);margin-bottom:16px;
}
.ss-card-title{font-size:1rem;font-weight:600;color:var(--ink);margin-bottom:4px;display:flex;align-items:center;gap:8px;}
.ss-card-subtitle{font-size:0.8125rem;color:var(--ink-muted);margin-bottom:16px;}
.ss-card-label{font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-muted);margin-bottom:8px;}

/* ── Insight cards ───────────────────────────────────────────────────── */
.ss-insight-list{display:flex;flex-direction:column;gap:12px;}
.ss-insight-item{
  display:flex;align-items:flex-start;gap:12px;padding:12px 14px;
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-sm);
  cursor:default;transition:all .15s ease;
}
.ss-insight-item:hover{border-color:var(--accent-bdr);box-shadow:var(--shadow);}
.ss-insight-icon{
  width:36px;height:36px;border-radius:var(--radius-sm);flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
}
.ss-insight-body{flex:1;min-width:0;}
.ss-insight-title{font-size:0.875rem;font-weight:600;color:var(--ink);margin-bottom:2px;}
.ss-insight-desc{font-size:0.8rem;color:var(--ink-sec);line-height:1.5;}
.ss-insight-arrow{color:var(--ink-muted);flex-shrink:0;align-self:center;}

/* ── Activity / recent analysis cards ───────────────────────────────── */
.ss-activity-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px;}
@media(max-width:900px){.ss-activity-grid{grid-template-columns:repeat(2,1fr);}}
.ss-activity-card{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-sm);
  padding:14px;box-shadow:var(--shadow);
}
.ss-activity-icon-wrap{width:32px;height:32px;border-radius:6px;display:flex;align-items:center;justify-content:center;margin-bottom:10px;}
.ss-activity-title{font-size:0.8rem;font-weight:600;color:var(--ink);margin-bottom:2px;}
.ss-activity-val{font-size:0.75rem;color:var(--ink-sec);}
.ss-activity-time{font-size:0.7rem;color:var(--ink-muted);margin-top:4px;}

/* ── Prediction / result card ────────────────────────────────────────── */
.ss-prediction-card{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:20px;box-shadow:var(--shadow);text-align:center;
}
.ss-pred-icon-wrap{
  width:56px;height:56px;border-radius:50%;display:flex;
  align-items:center;justify-content:center;margin:0 auto 10px;font-size:1.5rem;
}
.ss-pred-label-small{font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-muted);margin-bottom:4px;}
.ss-pred-class-high{font-size:2.4rem;font-weight:800;color:var(--green);line-height:1;}
.ss-pred-class-medium{font-size:2.4rem;font-weight:800;color:var(--amber);line-height:1;}
.ss-pred-class-low{font-size:2.4rem;font-weight:800;color:var(--coral);line-height:1;}
.ss-pred-conf{font-size:0.8125rem;color:var(--ink-muted);margin-top:4px;}
/* Prob mini-grid */
.ss-prob-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px;}
.ss-prob-cell{
  padding:10px 6px;border-radius:var(--radius-sm);text-align:center;
  border:1px solid var(--line);
}
.ss-prob-cell-val{font-size:1.1rem;font-weight:700;margin-bottom:1px;}
.ss-prob-cell-label{font-size:0.7rem;color:var(--ink-muted);}
.ss-prob-cell-low{background:var(--coral-soft);border-color:rgba(220,38,38,.15);}
.ss-prob-cell-low .ss-prob-cell-val{color:var(--coral);}
.ss-prob-cell-med{background:var(--amber-soft);border-color:rgba(217,119,6,.15);}
.ss-prob-cell-med .ss-prob-cell-val{color:var(--amber);}
.ss-prob-cell-high{background:var(--green-soft);border-color:rgba(5,150,105,.15);}
.ss-prob-cell-high .ss-prob-cell-val{color:var(--green);}

/* ── Profile bars (Academic Profile) ────────────────────────────────── */
.ss-profile-list{display:flex;flex-direction:column;gap:10px;}
.ss-profile-row{display:flex;align-items:center;gap:10px;}
.ss-profile-icon{width:20px;height:20px;flex-shrink:0;}
.ss-profile-label{font-size:0.8125rem;color:var(--ink-sec);min-width:130px;flex-shrink:0;}
.ss-profile-track{flex:1;height:6px;background:var(--surface-alt);border-radius:99px;overflow:hidden;}
.ss-profile-fill{height:100%;border-radius:99px;}
.ss-profile-value{font-size:0.8125rem;font-weight:600;color:var(--ink);min-width:36px;text-align:right;}

/* ── Recommendation cards ────────────────────────────────────────────── */
.ss-rec-list{display:flex;flex-direction:column;gap:8px;}
.ss-rec-item{
  display:flex;align-items:flex-start;gap:10px;padding:12px 14px;
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-sm);
  transition:all .15s ease;
}
.ss-rec-item:hover{border-color:var(--accent-bdr);box-shadow:var(--shadow);}
.ss-rec-icon-wrap{
  width:28px;height:28px;border-radius:6px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
}
.ss-rec-title{font-size:0.875rem;font-weight:600;color:var(--ink);margin-bottom:1px;}
.ss-rec-desc{font-size:0.78rem;color:var(--ink-muted);}
.ss-rec-arrow{color:var(--ink-muted);flex-shrink:0;align-self:center;margin-left:auto;}

/* ── SHAP / factor bars ──────────────────────────────────────────────── */
.ss-shap-section{display:flex;flex-direction:column;gap:6px;}
.ss-shap-tabs{display:flex;gap:8px;margin-bottom:12px;}
.ss-shap-tab{
  padding:6px 14px;border-radius:99px;font-size:0.8rem;font-weight:600;
  border:1.5px solid var(--line);background:var(--surface);cursor:pointer;
}
.ss-shap-tab-pos{border-color:var(--green);background:var(--green-soft);color:var(--green);}
.ss-shap-tab-neg{border-color:var(--coral);background:var(--coral-soft);color:var(--coral);}
.ss-shap-row{display:flex;align-items:center;gap:10px;margin-bottom:6px;}
.ss-shap-icon-wrap{width:28px;height:28px;border-radius:6px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.ss-shap-label{font-size:0.8125rem;color:var(--ink);min-width:150px;}
.ss-shap-track{flex:1;height:8px;background:var(--surface-alt);border-radius:99px;overflow:hidden;}
.ss-shap-fill-pos{height:100%;border-radius:99px;background:var(--green);}
.ss-shap-fill-neg{height:100%;border-radius:99px;background:var(--coral);}
.ss-shap-val{font-size:0.78rem;font-weight:600;font-family:var(--font-mono);min-width:42px;text-align:right;}

/* ── "What this means" card ──────────────────────────────────────────── */
.ss-means-card{
  background:var(--accent-soft);border:1px solid var(--accent-bdr);
  border-radius:var(--radius-sm);padding:14px;
}
.ss-means-icon{width:32px;height:32px;border-radius:8px;background:var(--accent);display:flex;align-items:center;justify-content:center;margin-bottom:8px;}
.ss-means-title{font-size:0.875rem;font-weight:600;color:var(--accent);margin-bottom:4px;}
.ss-means-text{font-size:0.8125rem;color:var(--ink-sec);line-height:1.55;}

/* ── Counterfactual / scenario path cards ────────────────────────────── */
.ss-cf-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}
@media(max-width:900px){.ss-cf-grid{grid-template-columns:1fr;}}
.ss-cf-card{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:16px;box-shadow:var(--shadow);
}
.ss-cf-path-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;}
.ss-cf-path-badge{font-size:0.7rem;font-weight:600;padding:3px 8px;border-radius:99px;}
.ss-cf-type-improve{background:var(--green-soft);color:var(--green);}
.ss-cf-type-maintain{background:var(--purple-soft);color:var(--purple);}
.ss-cf-card-title{font-size:0.875rem;font-weight:600;color:var(--ink);margin-bottom:4px;}
.ss-cf-card-desc{font-size:0.78rem;color:var(--ink-sec);line-height:1.5;margin-bottom:12px;}
.ss-cf-range{
  display:flex;align-items:center;gap:6px;
  font-size:1.1rem;font-weight:700;color:var(--ink);margin-bottom:10px;
}
.ss-cf-range-arrow{color:var(--ink-muted);}
.ss-cf-explore-btn{
  display:block;width:100%;padding:8px 0;text-align:center;
  background:transparent;border:1px solid var(--line);border-radius:var(--radius-xs);
  font-size:0.8rem;font-weight:600;color:var(--ink-sec);cursor:pointer;
  transition:all .15s ease;
}
.ss-cf-explore-btn:hover{border-color:var(--accent);color:var(--accent);}

/* ── What-If / Explore Improvements ─────────────────────────────────── */
.ss-slider-section{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:20px;box-shadow:var(--shadow);margin-bottom:16px;
}
.ss-slider-row{display:flex;align-items:center;gap:12px;margin-bottom:16px;}
.ss-slider-icon-wrap{
  width:36px;height:36px;border-radius:var(--radius-sm);flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
}
.ss-slider-label{font-size:0.875rem;font-weight:500;color:var(--ink);min-width:180px;}
.ss-slider-sublabel{font-size:0.73rem;color:var(--ink-muted);}

/* ── Current vs Scenario comparison ────────────────────────────────── */
.ss-compare-grid{display:grid;grid-template-columns:1fr 40px 1fr;gap:8px;align-items:center;margin-bottom:16px;}
.ss-compare-card{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-sm);
  padding:16px;box-shadow:var(--shadow);text-align:center;
}
.ss-compare-label{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-muted);margin-bottom:4px;}
.ss-compare-sublabel{font-size:0.7rem;color:var(--ink-muted);margin-bottom:8px;}
.ss-compare-arrow{text-align:center;font-size:1.5rem;color:var(--accent);}
.ss-positive-change{
  display:flex;align-items:flex-start;gap:10px;
  background:var(--green-soft);border:1px solid rgba(5,150,105,.15);
  border-radius:var(--radius-sm);padding:12px;margin-bottom:16px;
}
.ss-positive-change-text{font-size:0.8125rem;color:var(--ink-sec);line-height:1.5;}
.ss-positive-change-text strong{color:var(--green);}

/* ── Key insight banner ──────────────────────────────────────────────── */
.ss-key-insight{
  background:var(--green-soft);border:1px solid rgba(5,150,105,.15);
  border-radius:var(--radius-sm);padding:14px 16px;margin-bottom:16px;
  display:flex;align-items:flex-start;gap:10px;
}
.ss-key-insight-text{font-size:0.875rem;color:var(--ink);line-height:1.55;}
.ss-key-insight-text strong{color:var(--green);}

/* ── Detailed results table ──────────────────────────────────────────── */
.ss-results-table{width:100%;border-collapse:collapse;}
.ss-results-table th{
  font-size:0.73rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;
  color:var(--ink-muted);padding:8px 12px;border-bottom:1px solid var(--line);
  text-align:left;
}
.ss-results-table td{
  font-size:0.875rem;color:var(--ink-sec);padding:10px 12px;
  border-bottom:1px solid var(--line-soft);
}
.ss-results-table tr:last-child td{border-bottom:none;}
.ss-results-table .ss-change-pos{color:var(--green);font-weight:600;}
.ss-results-table .ss-change-neg{color:var(--coral);font-weight:600;}
.ss-results-table .ss-change-neu{color:var(--ink-muted);}

/* ── Scenario preset cards ───────────────────────────────────────────── */
.ss-scenario-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}
@media(max-width:900px){.ss-scenario-grid{grid-template-columns:repeat(2,1fr);}}
.ss-scenario-card{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:16px;box-shadow:var(--shadow);transition:all .15s ease;cursor:pointer;
}
.ss-scenario-card:hover{border-color:var(--accent-bdr);box-shadow:var(--shadow-md);}
.ss-scenario-icon-wrap{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:10px;}
.ss-scenario-title{font-size:0.875rem;font-weight:600;color:var(--ink);margin-bottom:4px;}
.ss-scenario-detail{font-size:0.78rem;color:var(--ink-muted);line-height:1.5;}
.ss-scenario-arrow{color:var(--ink-muted);margin-top:8px;font-size:0.8rem;}

/* ── Model confidence card ───────────────────────────────────────────── */
.ss-confidence-card{
  background:var(--accent-soft);border:1px solid var(--accent-bdr);
  border-radius:var(--radius);padding:20px;text-align:center;
}
.ss-confidence-val{font-size:2rem;font-weight:700;color:var(--accent);margin-bottom:4px;}
.ss-confidence-label{font-size:0.8125rem;color:var(--ink-sec);}

/* ── Info / warning banners ──────────────────────────────────────────── */
.ss-info-banner{
  display:flex;align-items:flex-start;gap:10px;padding:10px 14px;
  background:var(--accent-soft);border:1px solid var(--accent-bdr);
  border-radius:var(--radius-sm);margin-top:8px;
}
.ss-info-banner-text{font-size:0.8rem;color:var(--accent);line-height:1.5;}
.ss-warning-banner{
  display:flex;align-items:flex-start;gap:10px;padding:10px 14px;
  background:var(--amber-soft);border:1px solid rgba(217,119,6,.2);
  border-radius:var(--radius-sm);margin-top:8px;
}
.ss-warning-banner-text{font-size:0.8rem;color:var(--amber);line-height:1.5;}

/* ── Next steps list ─────────────────────────────────────────────────── */
.ss-next-steps{display:flex;flex-direction:column;gap:8px;}
.ss-next-step{display:flex;align-items:flex-start;gap:10px;padding:8px 0;}
.ss-next-step-num{
  width:24px;height:24px;border-radius:50%;background:var(--accent);
  color:#fff;font-size:0.75rem;font-weight:700;display:flex;align-items:center;
  justify-content:center;flex-shrink:0;
}
.ss-next-step-text{font-size:0.875rem;color:var(--ink-sec);line-height:1.5;}

/* ── Section heading ─────────────────────────────────────────────────── */
.spps-section-head{margin:24px 0 14px;display:flex;align-items:baseline;gap:10px;}
.spps-section-head-title{font-size:1.1rem;font-weight:700;color:var(--ink);margin:0;}
.spps-section-head-sub{font-size:0.8125rem;color:var(--ink-muted);margin:0 0 0 4px;}
.spps-section-label{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:var(--ink-muted);display:block;margin-bottom:8px;}
.spps-eyebrow-label{font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.12em;color:var(--accent);display:block;margin-bottom:6px;}

/* ── Probability bars (legacy + updated) ─────────────────────────────── */
.spps-prob-wrap{margin:8px 0;}
.spps-prob-label-row{display:flex;justify-content:space-between;font-size:0.8rem;color:var(--ink-sec);margin-bottom:4px;}
.spps-prob-track{width:100%;height:8px;background:var(--surface-alt);border-radius:99px;overflow:hidden;}
.spps-prob-fill{height:100%;border-radius:99px;background:var(--green);}
.spps-prob-fill.fill-mid{background:var(--amber);}
.spps-prob-fill.fill-low{background:var(--coral);}
.spps-class-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle;}

/* ── Result panel (legacy) ───────────────────────────────────────────── */
.spps-result-panel{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:20px;box-shadow:var(--shadow);position:relative;
}
.panel-high{border-top:3px solid var(--green);}
.panel-medium{border-top:3px solid var(--amber);}
.panel-low{border-top:3px solid var(--coral);}
.spps-result-class{font-size:2.5rem;font-weight:800;line-height:1;margin:6px 0 4px;}
.spps-result-conf{font-size:0.8125rem;color:var(--ink-muted);margin-top:4px;}
.spps-conf-badge{
  display:inline-block;font-size:0.8rem;color:var(--accent);
  background:var(--accent-soft);border:1px solid var(--accent-bdr);
  border-radius:var(--radius-xs);padding:2px 8px;font-weight:600;
}
.spps-seal{display:inline-flex;align-items:center;gap:4px;font-size:0.7rem;color:var(--ink-muted);}

/* ── Narrative / suggestions (legacy) ────────────────────────────────── */
.spps-narrative{
  background:var(--accent-soft);border:1px solid var(--accent-bdr);border-left:3px solid var(--accent);
  border-radius:var(--radius-sm);padding:12px 14px;font-size:0.875rem;color:var(--ink);
  line-height:1.6;margin-bottom:14px;
}
.spps-cf-card{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-sm);
  padding:12px 14px;margin:6px 0;display:flex;gap:10px;align-items:flex-start;
  transition:all .15s ease;box-shadow:var(--shadow);
}
.spps-cf-card:hover{border-color:var(--accent-bdr);box-shadow:var(--shadow-md);}
.spps-cf-icon{flex-shrink:0;width:32px;height:32px;border-radius:6px;display:flex;align-items:center;justify-content:center;color:var(--accent);background:var(--accent-soft);}
.spps-cf-action{font-weight:600;font-size:0.875rem;color:var(--ink);margin:0 0 2px;}
.spps-cf-detail{font-size:0.8rem;color:var(--ink-muted);margin:0;}
.spps-suggestion{
  background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:var(--radius-sm);padding:10px 14px;margin:5px 0;font-size:0.875rem;color:var(--ink);
  transition:all .15s ease;
}
.spps-suggestion:hover{background:var(--accent-soft);border-color:var(--accent-bdr);}

/* ── Delta chips (legacy) ────────────────────────────────────────────── */
.spps-delta{display:inline-flex;align-items:center;gap:4px;font-size:0.78rem;font-weight:600;border-radius:99px;padding:2px 8px;border:1px solid var(--line);}
.spps-delta.up{color:var(--green);background:var(--green-soft);border-color:rgba(5,150,105,.2);}
.spps-delta.down{color:var(--coral);background:var(--coral-soft);border-color:rgba(220,38,38,.2);}
.spps-delta.neutral{color:var(--ink-muted);background:var(--surface-alt);}

/* ── Chart containers ────────────────────────────────────────────────── */
[data-testid="stPlotlyChart"]{
  border:1px solid var(--line);border-radius:var(--radius);
  overflow:hidden;box-shadow:var(--shadow);background:var(--surface);
}
.spps-chart-caption,.spps-caption{font-size:0.8rem!important;color:var(--ink-muted)!important;line-height:1.55;margin-top:6px!important;}
.spps-chart-title{font-size:1rem;font-weight:600;color:var(--ink);margin-bottom:2px;}

/* ── Buttons ─────────────────────────────────────────────────────────── */
.stButton>button[kind="primary"]{
  background:var(--accent)!important;color:#FFFFFF!important;
  border:none!important;border-radius:var(--radius-sm)!important;
  font-weight:600!important;font-size:0.9rem!important;
  padding:0.65rem 1.75rem!important;min-height:44px!important;
  box-shadow:var(--shadow)!important;transition:all .2s ease!important;
}
.stButton>button[kind="primary"]:hover{background:#1D4ED8!important;box-shadow:var(--shadow-md)!important;transform:translateY(-1px)!important;}
.stButton>button[kind="secondary"]{
  background:var(--surface)!important;color:var(--ink)!important;
  border:1px solid var(--line)!important;border-radius:var(--radius-sm)!important;
  font-size:0.875rem!important;font-weight:500!important;min-height:44px!important;
  transition:all .2s ease;
}
.stButton>button[kind="secondary"]:hover{border-color:var(--accent)!important;color:var(--accent)!important;background:var(--accent-soft)!important;}

/* ── Inputs ──────────────────────────────────────────────────────────── */
[data-testid="stSlider"] label{font-size:0.875rem!important;color:var(--ink-sec)!important;font-weight:500!important;}
[data-testid="stSlider"]>div>div>div>div{background:var(--accent)!important;}
[data-testid="stSlider"] [role="slider"]{background:var(--surface)!important;border:2px solid var(--accent)!important;box-shadow:0 0 0 4px var(--accent-soft)!important;min-width:20px!important;min-height:20px!important;}
[data-testid="stSelectbox"] label,[data-testid="stNumberInput"] label{font-size:0.875rem!important;color:var(--ink-sec)!important;font-weight:500!important;}
[data-testid="stSelectbox"]>div>div{border-color:var(--line)!important;border-radius:var(--radius-sm)!important;background:var(--surface)!important;}
[data-testid="stAlert"]{border-radius:var(--radius-sm)!important;border:1px solid var(--line)!important;background:var(--surface-alt)!important;}

/* ── Tabs ────────────────────────────────────────────────────────────── */
[data-baseweb="tab-list"]{background:var(--surface-alt)!important;border:1px solid var(--line)!important;border-radius:var(--radius-sm)!important;padding:4px!important;gap:2px!important;}
[data-baseweb="tab"]{border-radius:6px!important;font-weight:500!important;font-size:0.875rem!important;color:var(--ink-muted)!important;}
[aria-selected="true"][data-baseweb="tab"]{background:var(--surface)!important;color:var(--accent)!important;box-shadow:var(--shadow)!important;font-weight:600!important;}

/* ── Dataframes ──────────────────────────────────────────────────────── */
[data-testid="stDataFrame"]{border:1px solid var(--line)!important;border-radius:var(--radius)!important;overflow:hidden;box-shadow:var(--shadow);}

/* ── Typography ──────────────────────────────────────────────────────── */
h1,h2,h3,h4,h5,h6,.stMarkdown h1,.stMarkdown h2,.stMarkdown h3{
  font-family:var(--font-body)!important;color:var(--ink)!important;
  font-weight:700!important;line-height:1.2;letter-spacing:-0.01em;
}
.stMarkdown h1{font-size:1.9rem!important;}
.stMarkdown h2{font-size:1.4rem!important;}
.stMarkdown h3{font-size:1.1rem!important;}
p,li,.stMarkdown p{font-family:var(--font-body)!important;font-size:0.9375rem;line-height:1.65;color:var(--ink-sec);}
hr,[data-testid="stDivider"] hr{border:none!important;border-top:1px solid var(--line)!important;margin:20px 0!important;}

/* ── KPI row (legacy kpi_hero_row) ───────────────────────────────────── */
.spps-kpi-row{display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap;}
.spps-kpi-card{
  flex:1;min-width:170px;background:var(--surface);border:1px solid var(--line);
  border-radius:var(--radius);padding:18px;transition:all .2s ease;box-shadow:var(--shadow);
}
.spps-kpi-card:hover{transform:translateY(-1px);box-shadow:var(--shadow-md);border-color:var(--accent-bdr);}
.spps-kpi-icon{width:36px;height:36px;border-radius:var(--radius-sm);display:flex;align-items:center;justify-content:center;margin-bottom:10px;background:var(--accent-soft);color:var(--accent);}
.spps-kpi-value{font-size:1.9rem;font-weight:700;color:var(--ink);line-height:1;margin-bottom:2px;}
.spps-kpi-value.blue{color:var(--accent);}
.spps-kpi-label{font-size:0.75rem;font-weight:600;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.08em;}
.spps-kpi-trend{font-size:0.75rem;color:var(--ink-muted);margin-top:6px;}

/* ── Legacy cards ─────────────────────────────────────────────────────── */
.spps-stat-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;margin-bottom:10px;box-shadow:var(--shadow);}
.spps-stat-card:hover{box-shadow:var(--shadow-md);border-color:var(--accent-bdr);}
.spps-stat-card-label{font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-muted);margin-bottom:4px;display:block;}
.spps-stat-card-value{font-size:1.8rem;font-weight:700;color:var(--ink);}
.spps-stat-card-sub{font-size:0.8rem;color:var(--ink-muted);margin-top:2px;}
.spps-ledger-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px;box-shadow:var(--shadow);}
.spps-hero{text-align:center;padding:24px 16px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);margin-bottom:16px;}
.spps-hero-number{font-size:3.5rem;font-weight:800;color:var(--accent);line-height:1;}
.spps-hero-label{font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-muted);margin-bottom:6px;}
.spps-hero-note{font-size:0.9rem;color:var(--ink-sec);margin-top:6px;}

/* ── Masthead / hero (legacy) ────────────────────────────────────────── */
.spps-masthead,.spps-page-hero{
  background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--accent);
  border-radius:var(--radius);padding:24px 28px;margin-bottom:24px;box-shadow:var(--shadow);
}
.spps-eyebrow,.spps-eyebrow-label-top{font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.14em;color:var(--accent);margin:0 0 4px;}
.spps-mast-title,.spps-page-title{font-size:2rem!important;font-weight:700!important;color:var(--ink)!important;margin:0 0 6px!important;}
.spps-mast-desc,.spps-page-desc{font-size:0.9375rem!important;color:var(--ink-sec)!important;max-width:640px!important;margin:0!important;}
.spps-mast-rule{border:none;border-top:1px solid var(--line);margin:14px 0 10px;}
.spps-beacon-row{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:0.75rem;color:var(--ink-muted);}

/* ── Footnote ─────────────────────────────────────────────────────────── */
.spps-footnote{margin-top:40px;font-size:0.72rem;color:var(--ink-muted);text-align:center;font-family:var(--font-mono);}

/* ── Verdict banner (fairness) ───────────────────────────────────────── */
.spps-class-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle;}
.spps-class-stat{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--line);font-size:0.875rem;}
.spps-class-stat:last-child{border-bottom:none;}
.spps-class-stat-label{min-width:65px;color:var(--ink);font-weight:600;}
.spps-class-stat-bar-wrap{flex:1;height:6px;background:var(--surface-alt);border-radius:99px;overflow:hidden;}
.spps-class-stat-bar{height:100%;border-radius:99px;}
.spps-class-stat-pct{min-width:42px;text-align:right;color:var(--ink-muted);font-size:0.78rem;}

/* ── Focus ring ──────────────────────────────────────────────────────── */
*:focus-visible{outline:2px solid var(--accent)!important;outline-offset:2px;border-radius:4px;}

/* ── Animations ──────────────────────────────────────────────────────── */
@keyframes fadeInUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.anim-fade-up{animation:fadeInUp .22s ease both;}
.anim-fade{animation:fadeIn .22s ease both;}
.anim-fade-up-1{animation-delay:0.03s;}.anim-fade-up-2{animation-delay:0.06s;}
.anim-fade-up-3{animation-delay:0.09s;}.anim-fade-up-4{animation-delay:0.12s;}
.anim-fade-up-5{animation-delay:0.15s;}
.anim-scale-in{animation:fadeInUp .22s ease both;}
.anim-slide-right{animation:fadeInUp .22s ease both;}
.anim-glow{animation:none;}
.main .block-container>div:nth-child(1){animation:fadeInUp .22s ease both;}
.main .block-container>div:nth-child(2){animation:fadeInUp .22s .04s ease both;}
.main .block-container>div:nth-child(3){animation:fadeInUp .22s .07s ease both;}
.main .block-container>div:nth-child(4){animation:fadeInUp .22s .10s ease both;}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;}}

/* ── Responsive ──────────────────────────────────────────────────────── */
@media(max-width:768px){
  .block-container{padding:0 1rem 3rem!important;}
  .ss-kpi-grid{grid-template-columns:repeat(2,1fr);}
  .ss-activity-grid{grid-template-columns:repeat(2,1fr);}
  .ss-cf-grid{grid-template-columns:1fr;}
  .ss-scenario-grid{grid-template-columns:repeat(2,1fr);}
  .ss-compare-grid{grid-template-columns:1fr;gap:6px;}
  .ss-compare-arrow{transform:rotate(90deg);}
  .spps-mast-title,.spps-page-title{font-size:1.6rem!important;}
  .spps-kpi-row{flex-direction:column;}
}
</style>
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def inject_theme(active_page: str = "home") -> None:
    """Inject CSS + left sidebar navigation. Call immediately after set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────────────────
    with st.sidebar:
        # Brand
        st.markdown("""
<div class="ss-sidebar-brand">
  <div class="ss-brand-logo">🎓</div>
  <div>
    <div class="ss-brand-name">Student Success</div>
    <div class="ss-brand-tagline">Academic Intelligence Platform</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # System status
        st.markdown("""
<div style="height:16px"></div>
<div class="ss-status-card">
  <div class="ss-status-row">
    <div class="ss-status-dot"></div>
    <span class="ss-status-label">System Operational</span>
  </div>
  <div class="ss-status-meta">
    Model v1.0 · RF (82.3% Acc)<br>API: Online &middot; Sub-10ms<br>Fairness: Parity 0.982
  </div>
</div>
""", unsafe_allow_html=True)

        # Quote
        st.markdown("""
<div class="ss-sidebar-quote">
  "Better insights<br>for brighter futures."
</div>
""", unsafe_allow_html=True)

    # ── Top header bar ────────────────────────────────────────────────────
    st.markdown("""
<div class="ss-top-bar">
  <div class="ss-search-wrap">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94A3B8"
         stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
    <input class="ss-search-input" type="text" placeholder="Search for a student (e.g. A1042)...">
  </div>
  <div class="ss-header-right">
    <div class="ss-bell-btn">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#475569"
           stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
      <div class="ss-bell-badge"></div>
    </div>
    <div class="ss-user-wrap">
      <div class="ss-avatar">SS</div>
      <div>
        <div class="ss-user-name">Satyam Shrivastav</div>
        <div class="ss-user-role">Educator View</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Component helpers — new design system
# ---------------------------------------------------------------------------

def page_header(label: str, title: str, subtitle: str = "", hero_text: str = "") -> str:
    """Premium SaaS page header with optional hero banner on the right."""
    sub_html = f'<p class="ss-hero-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    hero_html = (
        f'<div class="ss-hero-right">{html.escape(hero_text)}</div>'
        if hero_text else ""
    )
    return f"""
<div class="ss-hero-banner anim-fade-up">
  <div class="ss-hero-left">
    <div class="ss-hero-label">{html.escape(label)}</div>
    <h1 class="ss-hero-title">{html.escape(title)}</h1>
    {sub_html}
  </div>
  {hero_html}
</div>
"""


def metric_card(
    icon_name: str,
    value: str,
    label: str,
    sub: str = "",
    trend_value: str = "",
    trend_dir: str = "neutral",
    bg_color: str = "",
    icon_color: str = "",
) -> str:
    """Premium KPI metric card."""
    bg = bg_color or ACCENT_SOFT
    ic = icon_color or ACCENT
    sub_html = f'<div class="ss-kpi-sub">{html.escape(sub)}</div>' if sub else ""
    trend_cls = {"up": "ss-trend-up", "down": "ss-trend-down"}.get(trend_dir, "ss-trend-neutral")
    trend_arrow = {"up": "↑ ", "down": "↓ "}.get(trend_dir, "")
    trend_html = (
        f'<div class="ss-kpi-trend {trend_cls}">{trend_arrow}{html.escape(trend_value)}</div>'
        if trend_value else ""
    )
    ic_svg = icon(icon_name, 20, ic)
    return f"""
<div class="ss-kpi-card anim-fade-up">
  <div class="ss-kpi-icon-wrap" style="background:{bg};">{ic_svg}</div>
  <div class="ss-kpi-value">{html.escape(value)}</div>
  <div class="ss-kpi-label">{html.escape(label)}</div>
  {sub_html}
  {trend_html}
</div>
"""


def status_badge(level: str) -> str:
    """HIGH / MEDIUM / LOW status badge."""
    cls_map = {"H": ("ss-badge-high", "High"), "M": ("ss-badge-medium", "Medium"), "L": ("ss-badge-low", "Low")}
    badge_cls, text = cls_map.get(level, ("ss-badge-blue", level))
    dot = {"H": GREEN, "M": AMBER, "L": CORAL}.get(level, ACCENT)
    return f'<span class="ss-badge {badge_cls}"><span style="width:6px;height:6px;border-radius:50%;background:{dot};display:inline-block;"></span>{text}</span>'


def insight_card(icon_name: str, title: str, body: str, icon_bg: str = "", icon_color: str = "") -> str:
    """Key insight item card."""
    bg = icon_bg or ACCENT_SOFT
    ic = icon_color or ACCENT
    return f"""
<div class="ss-insight-item anim-fade-up">
  <div class="ss-insight-icon" style="background:{bg};">{icon(icon_name, 18, ic)}</div>
  <div class="ss-insight-body">
    <div class="ss-insight-title">{html.escape(title)}</div>
    <div class="ss-insight-desc">{html.escape(body)}</div>
  </div>
  <div class="ss-insight-arrow">›</div>
</div>
"""


def activity_card(icon_name: str, title: str, value: str, time_str: str, icon_bg: str = "", icon_color: str = "") -> str:
    """Recent activity/analysis card."""
    bg = icon_bg or ACCENT_SOFT
    ic = icon_color or ACCENT
    return f"""
<div class="ss-activity-card anim-fade-up">
  <div class="ss-activity-icon-wrap" style="background:{bg};">{icon(icon_name, 16, ic)}</div>
  <div class="ss-activity-title">{html.escape(title)}</div>
  <div class="ss-activity-val">{html.escape(value)}</div>
  <div class="ss-activity-time">{html.escape(time_str)}</div>
</div>
"""


def prediction_card_html(
    predicted_class: str,
    predicted_label: str,
    confidence: float,
    probs: dict[str, float],
) -> str:
    """Prediction result card with probability mini-grid."""
    cls_css = {"H": "ss-pred-class-high", "M": "ss-pred-class-medium", "L": "ss-pred-class-low"}.get(predicted_class, "ss-pred-class-medium")
    bg_color = {"H": GREEN_SOFT, "M": AMBER_SOFT, "L": CORAL_SOFT}.get(predicted_class, ACCENT_SOFT)
    emoji = {"H": "🎓", "M": "📘", "L": "📋"}.get(predicted_class, "📊")
    conf_pct = f"{confidence:.0%}"
    ph = probs.get("H", 0)
    pm = probs.get("M", 0)
    pl = probs.get("L", 0)
    return f"""
<div class="ss-prediction-card anim-fade-up">
  <div class="ss-pred-icon-wrap" style="background:{bg_color};">{emoji}</div>
  <div class="ss-pred-label-small">Predicted Performance Band</div>
  <div class="{cls_css}">{html.escape(predicted_label)}</div>
  <div class="ss-pred-conf">{conf_pct} confidence</div>
  <div class="ss-prob-grid">
    <div class="ss-prob-cell ss-prob-cell-low">
      <div class="ss-prob-cell-val">{pl:.0%}</div>
      <div class="ss-prob-cell-label">Low</div>
    </div>
    <div class="ss-prob-cell ss-prob-cell-med">
      <div class="ss-prob-cell-val">{pm:.0%}</div>
      <div class="ss-prob-cell-label">Medium</div>
    </div>
    <div class="ss-prob-cell ss-prob-cell-high">
      <div class="ss-prob-cell-val">{ph:.0%}</div>
      <div class="ss-prob-cell-label">High</div>
    </div>
  </div>
</div>
"""


def profile_bar(label: str, value: float, max_val: float = 100.0, bar_color: str = "") -> str:
    """Academic profile progress bar row."""
    color = bar_color or ACCENT
    pct = min(100, max(0, value / max_val * 100)) if max_val > 0 else 0
    return f"""
<div class="ss-profile-row">
  <div class="ss-profile-label">{html.escape(label)}</div>
  <div class="ss-profile-track"><div class="ss-profile-fill" style="width:{pct:.1f}%;background:{color};"></div></div>
  <div class="ss-profile-value">{int(value)}%</div>
</div>
"""


def recommendation_card_html(title: str, body: str, icon_name: str = "check-circle", icon_color: str = "") -> str:
    """Personalized recommendation list item."""
    ic = icon_color or GREEN
    bg = {"#059669": GREEN_SOFT, "#2563EB": ACCENT_SOFT, "#0891B2": TEAL_SOFT, "#7C3AED": PURPLE_SOFT}.get(ic, GREEN_SOFT)
    return f"""
<div class="ss-rec-item anim-fade-up">
  <div class="ss-rec-icon-wrap" style="background:{bg};">{icon(icon_name, 16, ic)}</div>
  <div style="flex:1">
    <div class="ss-rec-title">{html.escape(title)}</div>
    <div class="ss-rec-desc">{html.escape(body)}</div>
  </div>
  <div class="ss-rec-arrow">›</div>
</div>
"""


def scenario_card_html(
    path_num: int,
    type_label: str,
    title: str,
    desc: str,
    from_val: str,
    to_val: str,
    card_color: str = "",
) -> str:
    """Counterfactual path card."""
    type_css = "ss-cf-type-improve" if "improve" in type_label.lower() or "potential" in type_label.lower() else "ss-cf-type-maintain"
    color = card_color or ACCENT
    return f"""
<div class="ss-cf-card anim-fade-up">
  <div class="ss-cf-path-row">
    <span class="ss-cf-path-badge {type_css}">Path {path_num} · {html.escape(type_label)}</span>
  </div>
  <div class="ss-cf-card-title">{html.escape(title)}</div>
  <div class="ss-cf-card-desc">{html.escape(desc)}</div>
  <div class="ss-cf-range">
    <span style="color:var(--ink-muted)">{html.escape(from_val)}</span>
    <span class="ss-cf-range-arrow">→</span>
    <span style="color:{color}">{html.escape(to_val)}</span>
  </div>
  <div class="ss-cf-explore-btn">Explore This Path →</div>
</div>
"""


def info_banner(text: str, warning: bool = False) -> str:
    """Info or warning informational banner."""
    css = "ss-warning-banner" if warning else "ss-info-banner"
    text_css = "ss-warning-banner-text" if warning else "ss-info-banner-text"
    ic = icon("sparkle", 14, AMBER if warning else ACCENT)
    return f"""
<div class="{css}">
  {ic}
  <span class="{text_css}">{html.escape(text)}</span>
</div>
"""


def section_header_html(title: str, subtitle: str = "", icon_name: str = "") -> str:
    """Section header with optional icon."""
    ic_html = f'<span style="margin-right:8px;">{icon(icon_name, 18, ACCENT)}</span>' if icon_name else ""
    sub_html = f'<div class="ss-card-subtitle">{html.escape(subtitle)}</div>' if subtitle else ""
    return f"""
<div style="margin:24px 0 12px">
  <div class="ss-card-title">{ic_html}{html.escape(title)}</div>
  {sub_html}
</div>
"""


def next_steps_html(steps: list[str]) -> str:
    """Numbered next steps list."""
    items = "".join(
        f'<div class="ss-next-step"><div class="ss-next-step-num">{i+1}</div>'
        f'<div class="ss-next-step-text">{html.escape(s)}</div></div>'
        for i, s in enumerate(steps)
    )
    return f'<div class="ss-next-steps">{items}</div>'


# ---------------------------------------------------------------------------
# UI State & Analytics components
# ---------------------------------------------------------------------------

def ui_info_banner(text: str) -> str:
    """Informational banner with accent styling."""
    return f"""
<div class="ss-info-banner anim-fade-up" style="display:flex;align-items:flex-start;gap:10px;padding:12px 16px;background:var(--accent-soft);border:1px solid var(--accent-bdr);border-radius:var(--radius-sm);margin:8px 0;">
  <span style="font-size:1.05rem;line-height:1.2;">ℹ️</span>
  <span style="font-size:0.875rem;color:var(--ink);line-height:1.5;">{html.escape(text)}</span>
</div>
"""


def ui_warning_banner(text: str) -> str:
    """Warning banner with amber styling."""
    return f"""
<div class="ss-warning-banner anim-fade-up" style="display:flex;align-items:flex-start;gap:10px;padding:12px 16px;background:var(--amber-soft);border:1px solid rgba(217,119,6,.2);border-radius:var(--radius-sm);margin:8px 0;">
  <span style="font-size:1.05rem;line-height:1.2;">⚠️</span>
  <span style="font-size:0.875rem;color:var(--amber);line-height:1.5;">{html.escape(text)}</span>
</div>
"""


def ui_error_state(title: str, message: str, action: str = "") -> str:
    """Prominent error state card."""
    act_html = (
        f'<p style="margin-top:0.65rem;font-size:0.8125rem;font-family:var(--font-mono);background:var(--surface-alt);padding:6px 12px;border-radius:4px;display:inline-block;color:var(--ink);">'
        f'{html.escape(action)}</p>'
        if action else ""
    )
    return f"""
<div class="anim-fade-up" style="background:var(--coral-soft);border:1px solid rgba(220,38,38,.25);border-radius:var(--radius);padding:24px 20px;margin:16px 0;text-align:center;">
  <div style="font-size:2rem;margin-bottom:8px;">⚠️</div>
  <h3 style="color:var(--coral);margin:0 0 6px 0;font-size:1.15rem;font-weight:700;">{html.escape(title)}</h3>
  <p style="color:var(--ink-sec);font-size:0.875rem;margin:0 auto;max-width:540px;line-height:1.55;">{html.escape(message)}</p>
  {act_html}
</div>
"""


def ui_success_state(title: str, message: str) -> str:
    """Success confirmation banner."""
    return f"""
<div class="anim-fade-up" style="background:var(--green-soft);border:1px solid rgba(5,150,105,.25);border-radius:var(--radius);padding:16px 18px;margin:12px 0;display:flex;align-items:flex-start;gap:12px;">
  <div style="font-size:1.3rem;line-height:1;">✅</div>
  <div>
    <h4 style="color:var(--green);margin:0 0 3px 0;font-size:0.95rem;font-weight:700;">{html.escape(title)}</h4>
    <p style="color:var(--ink-sec);font-size:0.85rem;margin:0;line-height:1.5;">{html.escape(message)}</p>
  </div>
</div>
"""


def ui_empty_state(title: str, message: str) -> str:
    """Empty state placeholder card."""
    return f"""
<div class="anim-fade-up" style="background:var(--surface);border:1px dashed var(--line);border-radius:var(--radius);padding:36px 20px;margin:16px 0;text-align:center;">
  <div style="font-size:2.2rem;margin-bottom:8px;opacity:0.85;">📋</div>
  <h3 style="color:var(--ink);margin:0 0 6px 0;font-size:1.1rem;font-weight:600;">{html.escape(title)}</h3>
  <p style="color:var(--ink-muted);font-size:0.875rem;margin:0 auto;max-width:480px;line-height:1.6;">{html.escape(message)}</p>
</div>
"""


def ui_loading_card(message: str) -> str:
    """Loading card placeholder."""
    return f"""
<div class="anim-fade-up" style="background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:24px;margin:14px 0;text-align:center;">
  <div style="font-size:1.8rem;margin-bottom:8px;">⏳</div>
  <p style="color:var(--ink-sec);font-size:0.875rem;margin:0;font-weight:500;">{html.escape(message)}</p>
</div>
"""


def analytics_card_header(title: str, description: str = "") -> str:
    """Header for analytics charts with title and subtitle."""
    desc_html = f'<p class="spps-chart-caption" style="margin:0 0 10px 0;font-size:0.82rem;color:var(--ink-muted);">{html.escape(description)}</p>' if description else ""
    return f"""
<div style="margin:16px 0 8px;">
  <h3 style="font-size:1.05rem;font-weight:700;color:var(--ink);margin:0 0 4px 0;">{html.escape(title)}</h3>
  {desc_html}
</div>
"""


def analytics_card_takeaway(text: str) -> str:
    """Key takeaway pill below an analytics chart."""
    return f"""
<div style="background:var(--surface-alt);border-left:3px solid var(--accent);border-radius:var(--radius-xs);padding:8px 12px;margin:8px 0 16px;">
  <p style="font-size:0.8rem;color:var(--ink-sec);margin:0;line-height:1.5;">
    <strong style="color:var(--accent);">Key Takeaway:</strong> {html.escape(text)}
  </p>
</div>
"""


def takeaway_box(title: str, points: list[str]) -> str:
    """Structured takeaway card with bullet points."""
    items = "".join(f'<li style="margin:4px 0;font-size:0.875rem;color:var(--ink-sec);">{html.escape(p)}</li>' for p in points)
    return f"""
<div class="anim-fade-up" style="background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:var(--radius);padding:16px 20px;margin:16px 0;box-shadow:var(--shadow);">
  <h4 style="color:var(--ink);font-size:0.95rem;font-weight:700;margin:0 0 8px 0;">{html.escape(title)}</h4>
  <ul style="margin:0;padding-left:20px;">{items}</ul>
</div>
"""


def mcnemar_evidence_card(
    model_a: str = "Model A",
    model_b: str = "Model B",
    both_correct: int = 0,
    only_a: int = 0,
    only_b: int = 0,
    both_wrong: int = 0,
    stat: float = 0.0,
    p_value: float = 1.0,
    significant: bool = False,
    interpretation: str = "",
    odds_ratio: float = 0.0,
) -> str:
    """Statistical evidence card for McNemar's test with contingency table."""
    sig_text = "Statistically Significant (p < 0.05)" if (significant or p_value < 0.05) else "Not Statistically Significant (p ≥ 0.05)"
    badge_bg = "rgba(220,38,38,0.1)" if (significant or p_value < 0.05) else "rgba(5,150,105,0.1)"
    badge_color = "var(--coral)" if (significant or p_value < 0.05) else "var(--green)"
    
    table_html = f"""
    <table style="width:100%;font-size:0.82rem;border-collapse:collapse;margin:10px 0;text-align:center;">
      <thead>
        <tr style="color:var(--ink-muted);border-bottom:1px solid var(--line);">
          <th style="padding:6px;text-align:left;">Contingency</th>
          <th style="padding:6px;">{html.escape(model_b)} Correct</th>
          <th style="padding:6px;">{html.escape(model_b)} Incorrect</th>
        </tr>
      </thead>
      <tbody>
        <tr style="border-bottom:1px solid var(--line-soft);">
          <td style="padding:6px;text-align:left;font-weight:600;color:var(--ink);">{html.escape(model_a)} Correct</td>
          <td style="padding:6px;font-family:var(--font-mono);">{both_correct}</td>
          <td style="padding:6px;font-family:var(--font-mono);color:var(--accent);font-weight:600;">{only_a}</td>
        </tr>
        <tr>
          <td style="padding:6px;text-align:left;font-weight:600;color:var(--ink);">{html.escape(model_a)} Incorrect</td>
          <td style="padding:6px;font-family:var(--font-mono);color:var(--coral);font-weight:600;">{only_b}</td>
          <td style="padding:6px;font-family:var(--font-mono);">{both_wrong}</td>
        </tr>
      </tbody>
    </table>
    """ if (both_correct or only_a or only_b or both_wrong) else ""
    
    interp = interpretation or ("The models perform comparably on discordant pairs." if p_value >= 0.05 else "The models perform significantly differently on discordant pairs.")
    return f"""
<div class="anim-fade-up" style="background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:18px 22px;margin:12px 0;box-shadow:var(--shadow);">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:6px;">
    <span style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--ink-muted);">McNemar Test · Discordant Pairs</span>
    <span style="font-size:0.75rem;font-weight:600;padding:3px 10px;border-radius:99px;background:{badge_bg};color:{badge_color};">{sig_text}</span>
  </div>
  <p style="font-family:var(--font-mono);font-size:1.05rem;font-weight:700;color:var(--ink);margin:0 0 4px 0;">
    χ² = {stat:.3f} · p = {p_value:.4f} <span style="font-size:0.8rem;color:var(--ink-muted);font-weight:normal;">(α = 0.05)</span>
  </p>
  {table_html}
  <p style="font-size:0.84rem;color:var(--ink-sec);margin:6px 0 0;line-height:1.5;">{html.escape(interp)}</p>
</div>
"""


def protected_attr_badge(attr: str) -> str:
    """Inline badge identifying a protected attribute audited for fairness."""
    return f"""
<span style="display:inline-flex;align-items:center;gap:4px;background:var(--surface-alt);border:1px solid var(--line);border-radius:99px;padding:3px 10px;font-size:0.75rem;color:var(--ink-sec);margin-right:6px;">
  <span style="width:6px;height:6px;border-radius:50%;background:var(--accent);"></span>
  <span>{html.escape(attr)}</span>
</span>
"""


# ---------------------------------------------------------------------------
# Legacy component functions — kept for backward compatibility
# (all pages still import these; they now render in the new visual style)
# ---------------------------------------------------------------------------

def masthead(eyebrow: str, title: str, description: str, beacons: list[str] | None = None) -> str:
    """Legacy masthead → now renders as hero banner."""
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
  <hr class="spps-mast-rule">
  {beacon_html}
</div>
"""


def page_hero(title: str, description: str) -> str:
    """Legacy page hero → renders in new style."""
    return f"""
<div class="spps-page-hero anim-fade-up">
  <p class="spps-eyebrow">Student Success · Academic Intelligence Platform</p>
  <p class="spps-page-title">{html.escape(title)}</p>
  <p class="spps-page-desc">{html.escape(description)}</p>
</div>
"""


def hero_stat(value: str, label: str, note: str = "") -> str:
    """Large centered number block."""
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
    sub_html = f'<p class="spps-stat-card-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    return f"""
<div class="spps-stat-card anim-fade-up">
  <p class="spps-stat-card-label">{html.escape(title)}</p>
  <p class="spps-stat-card-value">{html.escape(value)}</p>
  {sub_html}
</div>
"""


def kpi_hero_row(stats: list[dict]) -> str:
    """KPI card row. Each dict: icon, value, label, trend, blue."""
    cards = ""
    for i, s in enumerate(stats):
        blue_cls = "blue" if s.get("blue") else ""
        trend_html = (
            f'<div class="spps-kpi-trend">{html.escape(str(s["trend"]))}</div>'
            if s.get("trend") else ""
        )
        raw_icon = str(s.get("icon", "ledger"))
        emoji_map = {
            "🎓": "cap", "🎯": "target", "📐": "ledger", "🔬": "flask",
            "🌟": "seal", "📈": "chart", "⚠️": "ledger", "🏆": "star",
            "⚖️": "scales", "🏫": "users", "⚙️": "settings", "🔮": "ledger",
        }
        key = emoji_map.get(raw_icon, raw_icon if raw_icon in _ICONS else "ledger")
        cards += f"""
<div class="spps-kpi-card anim-fade-up anim-fade-up-{min(i+1,5)}">
  <div class="spps-kpi-icon">{icon(key, 18, ACCENT)}</div>
  <div class="spps-kpi-value {blue_cls}">{html.escape(str(s['value']))}</div>
  <div class="spps-kpi-label">{html.escape(str(s['label']))}</div>
  {trend_html}
</div>"""
    return f'<div class="spps-kpi-row">{cards}</div>'


def section_heading(title: str, subtitle: str = "") -> str:
    """Section heading."""
    sub = f'<span class="spps-section-head-sub">{html.escape(subtitle)}</span>' if subtitle else ""
    return (
        f'<div class="spps-section-head"><p class="spps-section-head-title">'
        f'{html.escape(title)}</p>{sub}</div>'
    )


def dossier_header(eyebrow: str, title: str, subtitle: str = "") -> str:
    """Alias for section_heading."""
    return section_heading(title, subtitle)


def result_panel(
    predicted_class: str,
    label: str,
    confidence: float,
    runner_up: str = "",
    runner_prob: float = 0.0,
    is_borderline: bool = False,
) -> str:
    """Prediction result panel."""
    panel_map = {"H": "panel-high", "M": "panel-medium", "L": "panel-low"}
    panel_cls = panel_map.get(predicted_class, "panel-medium")
    conf_pct = f"{confidence:.0%}"
    borderline_note = ""
    if is_borderline:
        borderline_note = (
            '<p class="spps-result-conf" style="margin-top:6px;">'
            "Borderline — this student sits close to the class boundary.</p>"
        )
    runner_html = ""
    if runner_up and runner_up != "—":
        runner_label = CLASS_LABELS.get(runner_up, runner_up)
        runner_html = (
            f'<p class="spps-result-conf">Runner-up: {html.escape(runner_label)} '
            f"({runner_prob:.0%})</p>"
        )
    return f"""
<div class="spps-result-panel {panel_cls} anim-fade-up">
  <p class="spps-stat-card-label">Predicted Performance Band</p>
  <p class="spps-result-class" style="color:{CLASS_COLORS.get(predicted_class, INK)}">{html.escape(label)}</p>
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
    feature_str = (
        safe[0] if len(safe) == 1
        else f"{safe[0]} and {safe[1]}" if len(safe) == 2
        else f"{', '.join(safe[:-1])}, and {safe[-1]}"
    )
    verb = "are" if len(safe) > 1 else "is"
    plural = "s" if len(safe) > 1 else ""
    sentence = (
        f"{feature_str} {verb} the strongest factor{plural} driving this prediction upward."
        if direction == "toward"
        else f"{feature_str} {verb} the strongest factor{plural} pulling this prediction down."
    )
    return f'<div class="spps-narrative anim-fade-up"><strong>Why this prediction:</strong> {sentence}</div>'


def cf_card(icon_name: str, action_line: str, detail: str = "") -> str:
    """Counterfactual / recommendation card."""
    key = icon_name if icon_name in _ICONS else "arrow"
    detail_html = f'<p class="spps-cf-detail">{html.escape(detail)}</p>' if detail else ""
    return f"""
<div class="spps-cf-card anim-fade-up">
  <span class="spps-cf-icon">{icon(key, 18, ACCENT)}</span>
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
    """Probability bars for H/M/L."""
    fill_cls = {"H": "", "M": "fill-mid", "L": "fill-low"}
    dot = {"H": GREEN, "M": AMBER, "L": CORAL}
    bars_html = ""
    for cls, label in [("H", "High"), ("M", "Medium"), ("L", "Low")]:
        prob = probs.get(cls, 0)
        pct = prob * 100
        fc = fill_cls[cls]
        bold = "font-weight:700;color:var(--ink);" if cls == predicted_class else ""
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
    """Inline delta chip."""
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
    """Fairness verdict banner."""
    color = VERDICT.get(verdict, INK_MUTED)
    return (
        f'<div style="background:var(--surface);border:1px solid var(--line);'
        f'border-left:3px solid {color};border-radius:var(--radius);'
        f'padding:14px 18px;margin-bottom:14px;">'
        f'<p style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;'
        f'color:{color};margin:0 0 4px;font-weight:700;">Overall verdict — '
        f'{html.escape(verdict)}</p>'
        f'<p style="font-size:0.9rem;color:var(--ink);margin:0;line-height:1.6;">'
        f"{html.escape(headline)}</p></div>"
    )


def footnote(text: str) -> str:
    """Centered footnote."""
    return f"<div class='spps-footnote'>{html.escape(text)}</div>"
