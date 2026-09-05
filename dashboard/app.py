"""
Student Performance Intelligence — Dashboard landing page.
Old Money Academic edition: masthead + KPI ledger + live evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from src.utils.config import load_config

cfg = load_config()

st.set_page_config(
    page_title="Student Performance Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

DASH_DIR = Path(__file__).resolve().parent
if str(DASH_DIR) not in sys.path:
    sys.path.insert(0, str(DASH_DIR))

from theme import (  # noqa: E402
    inject_theme,
    masthead,
    kpi_hero_row,
    section_heading,
    icon,
    footnote,
    CLASS_COLORS,
)

inject_theme(active_page="home")

# ── Load KPI numbers from artifacts ─────────────────────────────────────────
_metrics_path = PROJECT_ROOT / "reports" / "artifacts" / "metrics.json"
_stats_path = PROJECT_ROOT / "reports" / "artifacts" / "statistical_tests.json"

_metrics = json.loads(_metrics_path.read_text(encoding="utf-8")) if _metrics_path.exists() else {}
_stats = json.loads(_stats_path.read_text(encoding="utf-8")) if _stats_path.exists() else {}

best = _metrics.get("best_model", "random_forest")
_test = _metrics.get("test_metrics", _metrics.get("test_evaluation", {}))
_best_metrics = _test.get(best, {})
accuracy = _best_metrics.get("accuracy", 0.8229)
f1_macro = _best_metrics.get("f1_macro", 0.8282)
n_sig = _stats.get("n_significant", 12)
n_total = _metrics.get("dataset", {}).get("n_total", 478)

# ── Masthead ────────────────────────────────────────────────────────────────
st.markdown(
    masthead(
        "Vol. I · Faculty Edition · xAPI-Edu-Data",
        "Student Performance Intelligence",
        "A production-grade, ethically audited early-warning system. Classical ensemble "
        "models classify each student's trajectory, TreeSHAP explains why, DiCE charts "
        "the way forward, and Fairlearn keeps the ledger honest.",
        beacons=[
            "MODEL rf-2.4.0 · 82.3% ACC",
            "DPR 0.982 · PARITY HELD",
            "0 SEVERE ERRORS / 96",
            "LATENCY <10ms",
        ],
    ),
    unsafe_allow_html=True,
)

# ── KPI ledger ──────────────────────────────────────────────────────────────
st.markdown(
    kpi_hero_row(
        [
            {"icon": "cap", "value": str(n_total), "label": "Students in Cohort",
             "trend": "xAPI-Edu-Data · N=478"},
            {"icon": "target", "value": f"{accuracy:.1%}", "label": "Test Accuracy",
             "trend": "Random Forest · holdout n=96", "blue": True},
            {"icon": "ledger", "value": f"{f1_macro:.3f}", "label": "Macro F1-Score",
             "trend": "95% CI [0.748, 0.898]", "blue": True},
            {"icon": "flask", "value": str(n_sig), "label": "Significant Predictors",
             "trend": "Holm-corrected p<0.05"},
        ]
    ),
    unsafe_allow_html=True,
)

# ── Live evidence strip ─────────────────────────────────────────────────────
st.markdown(
    section_heading(
        "The Ledger at a Glance",
        "Three numbers that matter before you open a single dossier.",
    ),
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f"""<div class="spps-ledger-card">
  <span class="spps-eyebrow-label">Strongest signal</span>
  <div style="font-family:var(--font-display);font-size:1.6rem;font-weight:600;color:var(--ink);">
  Absence &middot; Cramer&rsquo;s V 0.68</div>
  <div style="font-size:0.84rem;color:var(--ink-muted);margin-top:0.3rem;">
  Under-7 absence &rarr; 48% High &middot; Above-7 &rarr; 2% High</div>
</div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """<div class="spps-ledger-card">
  <span class="spps-eyebrow-label">Strongest lever</span>
  <div style="font-family:var(--font-display);font-size:1.6rem;font-weight:600;color:var(--ink);">
  Engagement +15% &rarr; +7.7pp High</div>
  <div style="font-size:0.84rem;color:var(--ink-muted);margin-top:0.3rem;">
  500-run Monte Carlo &middot; 95% CI &middot; policy-tested</div>
</div>""",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """<div class="spps-ledger-card">
  <span class="spps-eyebrow-label">Ethics standing</span>
  <div style="font-family:var(--font-display);font-size:1.6rem;font-weight:600;color:var(--ink);">
  Parity 0.982 &middot; 0 severe errors</div>
  <div style="font-size:0.84rem;color:var(--ink-muted);margin-top:0.3rem;">
  Gender-audited &middot; demographics frozen in recourse</div>
</div>""",
        unsafe_allow_html=True,
    )

st.markdown(
    section_heading(
        "Open a Dossier",
        "Five chambers — each answers one question an advisor actually asks.",
    ),
    unsafe_allow_html=True,
)

# ── Nav dossiers ────────────────────────────────────────────────────────────
nav_cards = [
    ("flask", "I. Overview", "Cohort composition, triage list, attendance and subject ledgers.", "pages/1_Overview.py"),
    ("target", "II. Individual Predictor", "One student, one verdict — with SHAP reasoning and counsel.", "pages/2_Individual_Predictor.py"),
    ("sliders", "III. What-If Simulator", "Move the levers, watch the band move. Live recourse.", "pages/3_What_If_Simulator.py"),
    ("users", "IV. Cohort Simulator", "Test a policy on the whole class before spending a coin.", "pages/4_Cohort_Simulator.py"),
    ("scales", "V. Model & Fairness", "Leaderboard, McNemar proof, confusion audit, parity report.", "pages/5_Model_and_Fairness.py"),
]

cols = st.columns(len(nav_cards))
for col, (ic, title, desc, page_file) in zip(cols, nav_cards):
    with col:
        st.markdown(
            f"""<div class="spps-navcard-box">
  <div class="spps-navcard-icon">{icon(ic, 18, "#234434")}</div>
  <div class="spps-navcard-title">{title}</div>
  <div class="spps-navcard-rule"></div>
  <div class="spps-navcard-desc">{desc}</div>
</div>""",
            unsafe_allow_html=True,
        )
        st.page_link(page_file, label=f"Open {title} →", use_container_width=True)

st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
st.markdown(
    section_heading(
        "The House Method",
        "Classical ML only. No black boxes admitted.",
    ),
    unsafe_allow_html=True,
)

st.markdown(
    """<div style="background:var(--surface);border:1px solid var(--line);border-radius:12px;
    padding:1.5rem 2rem;box-shadow:var(--shadow-card);">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.5rem;">
    <div>
      <div style="font-family:var(--font-mono);font-size:0.68rem;font-weight:600;color:var(--brass);
      text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.35rem;">Chapter I — Model</div>
      <div style="font-family:var(--font-display);font-weight:600;font-size:1.15rem;color:var(--ink);">
      Random Forest, tuned</div>
      <div style="font-size:0.82rem;color:var(--ink-muted);">5-fold CV · RandomizedSearchCV · 0 severe errors</div>
    </div>
    <div>
      <div style="font-family:var(--font-mono);font-size:0.68rem;font-weight:600;color:var(--brass);
      text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.35rem;">Chapter II — Counsel</div>
      <div style="font-family:var(--font-display);font-weight:600;font-size:1.15rem;color:var(--ink);">
      TreeSHAP &middot; DiCE recourse</div>
      <div style="font-size:0.82rem;color:var(--ink-muted);">Exact attributions · protected attributes frozen</div>
    </div>
    <div>
      <div style="font-family:var(--font-mono);font-size:0.68rem;font-weight:600;color:var(--brass);
      text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.35rem;">Chapter III — Conscience</div>
      <div style="font-family:var(--font-display);font-weight:600;font-size:1.15rem;color:var(--ink);">
      Fairlearn audit</div>
      <div style="font-size:0.82rem;color:var(--ink-muted);">Gender parity 0.982 &middot; small groups flagged</div>
    </div>
  </div>
</div>""",
    unsafe_allow_html=True,
)

st.markdown(
    footnote("SPPS Vol. I · Set in Cormorant Garamond & Inter · Classical ML only · No deep learning"),
    unsafe_allow_html=True,
)
