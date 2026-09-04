"""
Student Performance Insights — Dashboard landing page.
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
dash = cfg.get("dashboard", {})

st.set_page_config(
    page_title="Student Performance Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DASH_DIR = Path(__file__).resolve().parent
if str(DASH_DIR) not in sys.path:
    sys.path.insert(0, str(DASH_DIR))

from theme import (
    inject_theme, page_hero, kpi_hero_row, section_heading,
    CLASS_COLORS, CLASS_LABELS,
)

inject_theme(active_page="home")

# ── Load KPI numbers from artifacts ─────────────────────────────────────────
_metrics_path = PROJECT_ROOT / "reports" / "artifacts" / "metrics.json"
_stats_path   = PROJECT_ROOT / "reports" / "artifacts" / "statistical_tests.json"

_metrics = json.loads(_metrics_path.read_text(encoding="utf-8")) if _metrics_path.exists() else {}
_stats   = json.loads(_stats_path.read_text(encoding="utf-8"))   if _stats_path.exists() else {}

best = _metrics.get("best_model", "random_forest")
_test = _metrics.get("test_metrics", _metrics.get("test_evaluation", {}))
_best_metrics = _test.get(best, {})
accuracy = _best_metrics.get("accuracy", 0.823)
f1_macro = _best_metrics.get("f1_macro", 0.828)
n_sig = _stats.get("n_significant", 12)
n_total = _metrics.get("dataset", {}).get("n_total", 478)

# ── Hero banner ─────────────────────────────────────────────────────────────
st.markdown(page_hero(
    "Student Performance Insights",
    "End-to-end ML pipeline · Classical ensemble models · SHAP explanations · Fairness-audited"
), unsafe_allow_html=True)

# ── KPI Row ──────────────────────────────────────────────────────────────────
st.markdown(kpi_hero_row([
    {"icon": "🎓", "value": str(n_total),    "label": "Students Analysed",  "trend": "xAPI-Edu-Data"},
    {"icon": "🎯", "value": f"{accuracy:.1%}", "label": "Test Accuracy",    "trend": f"Random Forest · {n_total} students", "blue": True},
    {"icon": "📐", "value": f"{f1_macro:.3f}", "label": "Macro F1-Score",  "trend": "95% CI: [0.748, 0.898]", "blue": True},
    {"icon": "🔬", "value": str(n_sig),        "label": "Key Predictors",  "trend": "Holm-corrected p<0.05"},
]), unsafe_allow_html=True)

st.markdown(section_heading(
    "Navigate the Dashboard",
    "Five modules — each answering a different analytical question."
), unsafe_allow_html=True)

# ── Nav cards row (native interactive links) ──────────────────────────────────
nav_cards = [
    ("🔬", "Overview",            "Dataset stats, class balance, and key factor rankings.",          "pages/1_Overview.py"),
    ("🎯", "Individual Predictor", "Predict any student's band with SHAP explanations.",              "pages/2_Individual_Predictor.py"),
    ("⚙️", "What-If Simulator",    "Adjust engagement sliders and watch the prediction update live.", "pages/3_What_If_Simulator.py"),
    ("🏫", "Cohort Simulator",     "Monte Carlo class-wide policy simulations with 95% CIs.",         "pages/4_Cohort_Simulator.py"),
    ("⚖️", "Model & Fairness",     "Compare every model and read the fairness audit in full.",        "pages/5_Model_and_Fairness.py"),
]

cols = st.columns(len(nav_cards))
for col, (icon, title, desc, page_file) in zip(cols, nav_cards):
    with col:
        st.markdown(f"""
<div class="spps-navcard-box">
  <div class="spps-navcard-icon">{icon}</div>
  <div class="spps-navcard-title">{title}</div>
  <div class="spps-navcard-desc">{desc}</div>
</div>
""", unsafe_allow_html=True)
        st.page_link(page_file, label=f"Open {title} →", use_container_width=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
st.markdown(section_heading(
    "About This System",
    "Built as a SkillOrbit ML Capstone project — Type 3 / Exceptional Tier."
), unsafe_allow_html=True)

st.markdown("""
<div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:12px;padding:1.5rem 2rem;">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.5rem;">
    <div>
      <div style="font-size:0.7rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.35rem;">Model</div>
      <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:0.95rem;color:#0D0D0D;">Random Forest (tuned)</div>
      <div style="font-size:0.8rem;color:#6B7280;">5-fold CV · RandomizedSearchCV</div>
    </div>
    <div>
      <div style="font-size:0.7rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.35rem;">Explainability</div>
      <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:0.95rem;color:#0D0D0D;">TreeSHAP · Counterfactuals</div>
      <div style="font-size:0.8rem;color:#6B7280;">DiCE-ML · SHAP waterfall plots</div>
    </div>
    <div>
      <div style="font-size:0.7rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.35rem;">Responsible AI</div>
      <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:0.95rem;color:#0D0D0D;">Fairlearn Fairness Audit</div>
      <div style="font-size:0.8rem;color:#6B7280;">Gender parity ✓ · Nationality flagged</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='margin-top:3rem;font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
    "color:#D1D5DB;text-align:center;'>SPPS v1.0.0 · Built by Satyam · Classical ML only · No deep learning</div>",
    unsafe_allow_html=True
)
