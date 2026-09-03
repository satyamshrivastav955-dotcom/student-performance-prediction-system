"""
dashboard/theme.py — SPPS shared design system.

Call inject_theme() as the FIRST thing after st.set_page_config() on every page.
All CSS custom properties live here; change a value once and it propagates everywhere.

HTML builder helpers return raw HTML strings for use with
    st.markdown(html, unsafe_allow_html=True)

Design tokens (for reference in Python too):
    ACCENT      = "#2C52A0"   cobalt-ink blue
    BG          = "#F7F7F5"   warm off-white
    INK         = "#141414"   near-black
    INK_SEC     = "#525252"   secondary text
    BORDER      = "#E3E3E1"   hairline border
    CHART_GRAY  = "#C8C8C6"   non-highlighted chart series
    CLASS_HIGH  = "#2C52A0"   accent blue  (High)
    CLASS_MID   = "#8C8C8C"   mid gray     (Medium)
    CLASS_LOW   = "#3D3D3D"   dark charcoal (Low)
"""

from __future__ import annotations
import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens (also used in Python for Plotly chart calls)
# ---------------------------------------------------------------------------
ACCENT       = "#2C52A0"
ACCENT_LIGHT = "rgba(44,82,160,0.08)"
BG           = "#F7F7F5"
SURFACE      = "#FFFFFF"
SURFACE_ALT  = "#EFEFED"
INK          = "#141414"
INK_SEC      = "#525252"
INK_MUTED    = "#8C8C8C"
BORDER       = "#E3E3E1"
CHART_GRAY   = "#C8C8C6"
CHART_DARK   = "#3D3D3D"

# Per-class colors replacing the original traffic-light palette
CLASS_COLORS = {
    "H": ACCENT,       # cobalt-ink blue — High is the positive outcome
    "M": "#8C8C8C",    # mid gray — Medium
    "L": "#3D3D3D",    # dark charcoal — Low (no alarm-red)
}
CLASS_LABELS = {"H": "High", "M": "Medium", "L": "Low"}

# Plotly layout defaults (apply via fig.update_layout(**PLOTLY_BASE))
# NOTE: margin, xaxis, yaxis are intentionally omitted — each chart passes
# its own values, and Python raises "multiple values for keyword argument"
# if a key appears in both **PLOTLY_BASE and an explicit kwarg.
PLOTLY_BASE = dict(
    plot_bgcolor  = "rgba(0,0,0,0)",
    paper_bgcolor = "rgba(0,0,0,0)",
    font          = dict(family="Inter, sans-serif", color=INK_SEC, size=12),
    legend        = dict(orientation="h", y=-0.18, font=dict(size=12)),
    hoverlabel    = dict(bgcolor=SURFACE, bordercolor=BORDER,
                         font=dict(family="Inter, sans-serif", size=13)),
)

# ---------------------------------------------------------------------------
# Core CSS
# ---------------------------------------------------------------------------
_CSS = """
<style>
/* ═══════════════════════════════════════════════════════════════════
   0. Google Fonts
═══════════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ═══════════════════════════════════════════════════════════════════
   1. Design tokens
═══════════════════════════════════════════════════════════════════ */
:root {
  --accent:         #2C52A0;
  --accent-subtle:  rgba(44,82,160,0.08);
  --accent-border:  rgba(44,82,160,0.25);
  --bg:             #F7F7F5;
  --surface:        #FFFFFF;
  --surface-alt:    #EFEFED;
  --ink:            #141414;
  --ink-sec:        #525252;
  --ink-muted:      #8C8C8C;
  --border:         #E3E3E1;
  --radius:         8px;
  --radius-sm:      4px;
  --font-display:   'Space Grotesk', system-ui, sans-serif;
  --font-body:      'Inter', system-ui, sans-serif;
  --font-mono:      'IBM Plex Mono', monospace;
}

/* ═══════════════════════════════════════════════════════════════════
   2. Global resets
═══════════════════════════════════════════════════════════════════ */
html, body, [class*="css"] {
  font-family: var(--font-body) !important;
  color: var(--ink);
  background-color: var(--bg);
}

/* Remove Streamlit branding */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* Block container breathing room */
.block-container {
  padding-top: 2.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 1200px;
}

/* ═══════════════════════════════════════════════════════════════════
   3. Typography overrides
═══════════════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: var(--font-display) !important;
  color: var(--ink) !important;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

/* Streamlit's st.title() */
.stMarkdown h1 { font-size: 2.2rem !important; font-weight: 700 !important; }
.stMarkdown h2 { font-size: 1.6rem !important; font-weight: 600 !important; }
.stMarkdown h3 { font-size: 1.25rem !important; font-weight: 600 !important; }

p, li, .stMarkdown p {
  font-family: var(--font-body) !important;
  font-size: 0.9375rem;
  line-height: 1.65;
  color: var(--ink);
}

/* captions */
.stMarkdown small,
[data-testid="stCaptionContainer"] p,
.spps-caption {
  font-size: 0.8125rem !important;
  color: var(--ink-muted) !important;
  line-height: 1.5;
}

/* ═══════════════════════════════════════════════════════════════════
   4. Sidebar — minimal nav rail
═══════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
  background-color: var(--surface) !important;
  border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] .block-container {
  padding-top: 2rem !important;
}

/* Nav link items: accent underline on active, not filled button */
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
  font-family: var(--font-body) !important;
  font-size: 0.875rem !important;
  color: var(--ink-sec) !important;
  border-radius: 0 !important;
  border-left: 3px solid transparent;
  padding-left: 12px !important;
  transition: color 0.15s ease, border-color 0.15s ease;
}

section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
  color: var(--ink) !important;
  background: transparent !important;
  border-left-color: var(--border);
}

section[data-testid="stSidebar"] [aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"] {
  color: var(--accent) !important;
  background: var(--accent-subtle) !important;
  border-left: 3px solid var(--accent) !important;
  font-weight: 500 !important;
}

/* Sidebar title */
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ink-muted) !important;
  margin-bottom: 0.5rem;
}

/* ═══════════════════════════════════════════════════════════════════
   5. Dividers
═══════════════════════════════════════════════════════════════════ */
hr, [data-testid="stDivider"] hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 2rem 0 !important;
}

/* ═══════════════════════════════════════════════════════════════════
   6. Native Streamlit widgets
═══════════════════════════════════════════════════════════════════ */

/* Radio buttons */
[data-testid="stRadio"] label {
  font-size: 0.9rem !important;
  color: var(--ink-sec) !important;
}

/* Sliders */
[data-testid="stSlider"] label {
  font-family: var(--font-body) !important;
  font-size: 0.875rem !important;
  color: var(--ink-sec) !important;
}

/* Selectboxes */
[data-testid="stSelectbox"] label {
  font-size: 0.875rem !important;
  color: var(--ink-sec) !important;
}

/* Number input */
[data-testid="stNumberInput"] label {
  font-size: 0.875rem !important;
  color: var(--ink-sec) !important;
}

/* Primary button */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
  background: var(--accent) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius) !important;
  font-family: var(--font-body) !important;
  font-size: 0.9375rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.01em;
  padding: 0.65rem 1.5rem !important;
  transition: opacity 0.15s ease, transform 0.1s ease;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
  opacity: 0.88;
  transform: translateY(-1px);
}

/* Secondary button */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"] {
  background: transparent !important;
  color: var(--ink) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  font-family: var(--font-body) !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.stButton > button[kind="secondary"]:hover {
  border-color: var(--ink-sec) !important;
  background: var(--surface-alt) !important;
}

/* st.info / st.warning / st.success / st.error — neutralize default colors */
[data-testid="stAlert"] {
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
  background: var(--surface) !important;
  font-size: 0.875rem !important;
}

/* Expander */
details > summary {
  font-family: var(--font-body) !important;
  font-size: 0.875rem !important;
  color: var(--ink-sec) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  overflow: hidden;
}

/* ═══════════════════════════════════════════════════════════════════
   7. Custom component classes
═══════════════════════════════════════════════════════════════════ */

/* --- Hero stat (large editorial number) --- */
.spps-hero {
  padding: 2.5rem 0 2rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
}
.spps-hero-number {
  font-family: var(--font-display);
  font-size: 5rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.04em;
  line-height: 1;
  margin: 0;
}
.spps-hero-label {
  font-family: var(--font-body);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.35rem;
}
.spps-hero-note {
  font-family: var(--font-body);
  font-size: 0.9375rem;
  color: var(--ink-sec);
  margin-top: 0.5rem;
  max-width: 480px;
}

/* --- Stat card (secondary metric) --- */
.spps-stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.1rem 1.35rem;
  margin-bottom: 0.75rem;
}
.spps-stat-card-label {
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 0.3rem;
}
.spps-stat-card-value {
  font-family: var(--font-display);
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.02em;
  line-height: 1.1;
}
.spps-stat-card-sub {
  font-family: var(--font-body);
  font-size: 0.8125rem;
  color: var(--ink-muted);
  margin-top: 0.2rem;
}

/* --- Section heading --- */
.spps-section-label {
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
}

/* --- Result panel (prediction outcome) --- */
.spps-result-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left-width: 4px;
  border-radius: var(--radius);
  padding: 1.5rem 1.75rem;
  margin: 1rem 0;
}
.spps-result-panel.panel-high  { border-left-color: #2C52A0; }
.spps-result-panel.panel-medium{ border-left-color: #8C8C8C; }
.spps-result-panel.panel-low   { border-left-color: #3D3D3D; }

.spps-result-class {
  font-family: var(--font-display);
  font-size: 2.8rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.03em;
  line-height: 1;
  margin: 0.25rem 0;
}
.spps-result-conf {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--ink-sec);
  margin-top: 0.4rem;
}

/* --- Confidence inline badge --- */
.spps-conf-badge {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  color: var(--accent);
  background: var(--accent-subtle);
  border-radius: var(--radius-sm);
  padding: 2px 8px;
  font-weight: 500;
}

/* --- Probability bar (CSS segmented) --- */
.spps-prob-wrap {
  margin: 1.25rem 0;
}
.spps-prob-label-row {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-body);
  font-size: 0.8125rem;
  color: var(--ink-sec);
  margin-bottom: 0.35rem;
}
.spps-prob-track {
  width: 100%;
  height: 8px;
  background: var(--surface-alt);
  border-radius: 99px;
  overflow: hidden;
  position: relative;
}
.spps-prob-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 99px;
  transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.spps-prob-fill.fill-mid { background: #8C8C8C; }
.spps-prob-fill.fill-low { background: #3D3D3D; }

/* --- SHAP narrative sentence --- */
.spps-narrative {
  background: var(--surface-alt);
  border-radius: var(--radius);
  padding: 0.85rem 1.1rem;
  font-family: var(--font-body);
  font-size: 0.9375rem;
  color: var(--ink);
  line-height: 1.55;
  margin-bottom: 1rem;
  border-left: 3px solid var(--accent);
}

/* --- Counterfactual / recommendation card --- */
.spps-cf-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin: 0.6rem 0;
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
}
.spps-cf-icon {
  font-size: 1.15rem;
  line-height: 1;
  margin-top: 2px;
  flex-shrink: 0;
}
.spps-cf-body {}
.spps-cf-action {
  font-family: var(--font-body);
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.2rem 0;
}
.spps-cf-detail {
  font-family: var(--font-body);
  font-size: 0.8125rem;
  color: var(--ink-sec);
  margin: 0;
}

/* --- Suggestion card (improvement suggestions) --- */
.spps-suggestion {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: var(--radius);
  padding: 0.85rem 1.1rem;
  margin: 0.5rem 0;
  font-family: var(--font-body);
  font-size: 0.9rem;
  color: var(--ink);
}

/* --- Delta chip --- */
.spps-delta {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}
.spps-delta.up   { color: var(--accent); background: var(--accent-subtle); }
.spps-delta.down { color: #525252; background: #EFEFED; }
.spps-delta.neutral { color: #8C8C8C; background: #EFEFED; }

/* --- Class dot / label --- */
.spps-class-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
}

/* --- Page hero title block --- */
.spps-page-hero {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}
.spps-page-title {
  font-family: var(--font-display);
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.03em;
  margin: 0 0 0.4rem 0;
}
.spps-page-desc {
  font-family: var(--font-body);
  font-size: 1rem;
  color: var(--ink-sec);
  line-height: 1.55;
  max-width: 640px;
  margin: 0;
}

/* --- Chart section wrapper --- */
.spps-chart-section {
  margin-bottom: 2.5rem;
}
.spps-chart-title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.01em;
  margin-bottom: 0.25rem;
}
.spps-chart-caption {
  font-family: var(--font-body);
  font-size: 0.8125rem;
  color: var(--ink-muted);
  line-height: 1.5;
  margin-top: 0.5rem;
}

/* --- Class stat bar (horizontal proportion bar) --- */
.spps-class-stat {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
  font-family: var(--font-body);
  font-size: 0.875rem;
}
.spps-class-stat:last-child { border-bottom: none; }
.spps-class-stat-label { min-width: 60px; color: var(--ink); font-weight: 500; }
.spps-class-stat-bar-wrap {
  flex: 1;
  height: 5px;
  background: var(--surface-alt);
  border-radius: 99px;
  overflow: hidden;
}
.spps-class-stat-bar { height: 100%; border-radius: 99px; }
.spps-class-stat-pct {
  min-width: 40px;
  text-align: right;
  color: var(--ink-muted);
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

/* ═══════════════════════════════════════════════════════════════════
   8. Entrance animations
═══════════════════════════════════════════════════════════════════ */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

.anim-fade-up {
  animation: fadeInUp 0.45s cubic-bezier(0.22,0.61,0.36,1) both;
}
.anim-fade-up-1 { animation-delay: 0.04s; }
.anim-fade-up-2 { animation-delay: 0.10s; }
.anim-fade-up-3 { animation-delay: 0.17s; }
.anim-fade-up-4 { animation-delay: 0.24s; }
.anim-fade-up-5 { animation-delay: 0.32s; }

.anim-fade {
  animation: fadeIn 0.4s ease both;
}

/* Apply to top-level streamlit element children automatically */
.main .block-container > div:nth-child(1)  { animation: fadeInUp 0.45s 0.02s cubic-bezier(0.22,0.61,0.36,1) both; }
.main .block-container > div:nth-child(2)  { animation: fadeInUp 0.45s 0.07s cubic-bezier(0.22,0.61,0.36,1) both; }
.main .block-container > div:nth-child(3)  { animation: fadeInUp 0.45s 0.13s cubic-bezier(0.22,0.61,0.36,1) both; }
.main .block-container > div:nth-child(4)  { animation: fadeInUp 0.45s 0.19s cubic-bezier(0.22,0.61,0.36,1) both; }
.main .block-container > div:nth-child(5)  { animation: fadeInUp 0.45s 0.24s cubic-bezier(0.22,0.61,0.36,1) both; }
.main .block-container > div:nth-child(6)  { animation: fadeInUp 0.45s 0.28s cubic-bezier(0.22,0.61,0.36,1) both; }
.main .block-container > div:nth-child(n+7){ animation: fadeInUp 0.45s 0.32s cubic-bezier(0.22,0.61,0.36,1) both; }

/* ═══════════════════════════════════════════════════════════════════
   9. Plotly chart container
═══════════════════════════════════════════════════════════════════ */
[data-testid="stPlotlyChart"] {
  border-radius: var(--radius);
  overflow: hidden;
}
</style>
"""

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def inject_theme() -> None:
    """Inject the full SPPS design system CSS into the current page."""
    st.markdown(_CSS, unsafe_allow_html=True)


# ── HTML builders ─────────────────────────────────────────────────────────

def page_hero(title: str, description: str) -> str:
    """
    Top-of-page hero block: large display title + one-line description.
    Returns HTML string.
    """
    return f"""
<div class="spps-page-hero anim-fade-up">
  <p class="spps-page-title">{title}</p>
  <p class="spps-page-desc">{description}</p>
</div>
"""


def hero_stat(value: str, label: str, note: str = "") -> str:
    """
    Large editorial number with a label above and optional note below.
    Use for the primary KPI on a page.
    """
    note_html = f'<p class="spps-hero-note">{note}</p>' if note else ""
    return f"""
<div class="spps-hero anim-fade-up">
  <p class="spps-hero-label">{label}</p>
  <p class="spps-hero-number">{value}</p>
  {note_html}
</div>
"""


def stat_card(title: str, value: str, subtitle: str = "", delay: int = 0) -> str:
    """
    Secondary metric card: hairline border, no shadow.
    delay: 0–5 for staggered entrance animation.
    """
    delay_class = f"anim-fade-up-{delay}" if 1 <= delay <= 5 else ""
    sub_html = f'<p class="spps-stat-card-sub">{subtitle}</p>' if subtitle else ""
    return f"""
<div class="spps-stat-card anim-fade-up {delay_class}">
  <p class="spps-stat-card-label">{title}</p>
  <p class="spps-stat-card-value">{value}</p>
  {sub_html}
</div>
"""


def result_panel(predicted_class: str, label: str, confidence: float,
                 runner_up: str = "", runner_prob: float = 0.0,
                 is_borderline: bool = False) -> str:
    """
    Calm prediction result panel with accent-colored left border.
    Uses tone/weight variation of single accent + neutral grays.
    No traffic-light colors.
    """
    panel_map = {"H": "panel-high", "M": "panel-medium", "L": "panel-low"}
    panel_cls = panel_map.get(predicted_class, "panel-medium")
    conf_pct = f"{confidence:.0%}"

    borderline_note = ""
    if is_borderline:
        borderline_note = (
            '<p class="spps-result-conf" style="margin-top:0.5rem;">'
            '⚠ Borderline — this student is close to the boundary between bands.'
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
  <p class="spps-stat-card-label">Predicted Performance</p>
  <p class="spps-result-class">{label}</p>
  <p class="spps-result-conf">Confidence <span class="spps-conf-badge">{conf_pct}</span></p>
  {runner_html}
  {borderline_note}
</div>
"""


def shap_narrative(top_features: list[str], direction: str = "toward") -> str:
    """
    One-sentence plain-English SHAP summary above the bar chart.
    top_features: list of 2-3 friendly feature names.
    direction: "toward" (pulling up) | "against" (pulling down)
    """
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
    """
    Counterfactual / recommendation card: icon + bold action + detail text.
    """
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
    """Styled improvement suggestion with accent left-border."""
    return f'<div class="spps-suggestion anim-fade-up">{text}</div>'


def probability_bar(probs: dict[str, float], predicted_class: str) -> str:
    """
    Segmented horizontal probability bars for H/M/L.
    probs: {"H": 0.7, "M": 0.2, "L": 0.1}
    """
    fill_cls = {"H": "", "M": "fill-mid", "L": "fill-low"}
    bars_html = ""
    for cls, label in [("H", "High"), ("M", "Medium"), ("L", "Low")]:
        prob = probs.get(cls, 0)
        pct = prob * 100
        fc = fill_cls[cls]
        bold = " font-weight:600; color:var(--ink);" if cls == predicted_class else ""
        bars_html += f"""
<div class="spps-prob-wrap">
  <div class="spps-prob-label-row">
    <span style="{bold}">{label}</span>
    <span style="font-family:var(--font-mono);{bold}">{prob:.0%}</span>
  </div>
  <div class="spps-prob-track">
    <div class="spps-prob-fill {fc}" style="width:{pct:.1f}%"></div>
  </div>
</div>
"""
    return bars_html


def class_breakdown_bars(class_counts: dict[str, int], total: int) -> str:
    """
    Compact horizontal proportion bars for class distribution panel.
    """
    color_map = {"H": ACCENT, "M": "#8C8C8C", "L": "#3D3D3D"}
    label_map = {"H": "High", "M": "Medium", "L": "Low"}
    html = '<div style="margin-top:0.5rem;">'
    for cls in ["H", "M", "L"]:
        count = class_counts.get(cls, 0)
        pct = (count / total * 100) if total else 0
        color = color_map[cls]
        label = label_map[cls]
        html += f"""
<div class="spps-class-stat">
  <span class="spps-class-stat-label">
    <span class="spps-class-dot" style="background:{color}"></span>{label}
  </span>
  <div class="spps-class-stat-bar-wrap">
    <div class="spps-class-stat-bar" style="width:{pct:.1f}%;background:{color}"></div>
  </div>
  <span class="spps-class-stat-pct">{pct:.1f}%</span>
</div>
"""
    html += "</div>"
    return html


def section_heading(title: str) -> str:
    """Display heading as styled section label."""
    return (
        f'<p class="spps-section-label anim-fade-up">'
        f'<span style="font-family:var(--font-display);font-size:1.15rem;'
        f'font-weight:600;color:var(--ink);text-transform:none;letter-spacing:-0.01em;">'
        f'{title}</span></p>'
    )


def delta_chip(value: float | str, prefix: str = "") -> str:
    """Styled chip for showing a delta value."""
    if isinstance(value, (int, float)):
        direction = "up" if value > 0 else ("down" if value < 0 else "neutral")
        arrow = "↑" if value > 0 else ("↓" if value < 0 else "→")
        text = f"{arrow} {abs(value):.0f}"
    else:
        direction = "neutral"
        text = str(value)
    return f'<span class="spps-delta {direction}">{prefix}{text}</span>'
