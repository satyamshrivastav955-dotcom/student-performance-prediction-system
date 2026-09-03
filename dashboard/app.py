"""
Student Performance Insights — Streamlit dashboard entry point.

This is the file you run with ``streamlit run dashboard/app.py``. It sets up
the page config, sidebar navigation, and shared state. The actual page content
lives in ``dashboard/pages/``.

The dashboard is designed for students and teachers, not ML engineers. Every
design decision prioritises clarity over information density.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on sys.path so ``from src.…`` imports work
# regardless of where Streamlit was launched from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.utils.config import load_config

# ---------------------------------------------------------------------------
# Page configuration — must be the first Streamlit call
# ---------------------------------------------------------------------------
cfg = load_config()
dash = cfg.get("dashboard", {})

st.set_page_config(
    page_title=dash.get("title", "Student Performance Insights"),
    page_icon=dash.get("page_icon", "📘"),
    layout=dash.get("layout", "wide"),
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Inject shared design system
# ---------------------------------------------------------------------------
# Add dashboard dir to path so 'from theme import …' works from pages too
DASH_DIR = Path(__file__).resolve().parent
if str(DASH_DIR) not in sys.path:
    sys.path.insert(0, str(DASH_DIR))

from theme import (  # noqa: E402
    inject_theme, page_hero, hero_stat, stat_card,
    result_panel, CLASS_COLORS, CLASS_LABELS,
    ACCENT, BG, INK, INK_SEC, INK_MUTED, BORDER, PLOTLY_BASE,
)

inject_theme()


# ---------------------------------------------------------------------------
# Helper functions shared across pages (stored in session state for pages)
# ---------------------------------------------------------------------------

def class_badge(cls: str, label: str | None = None) -> str:
    """Return a minimal HTML class label (no bright badge background)."""
    label = label or CLASS_LABELS.get(cls, cls)
    color = CLASS_COLORS.get(cls, "#525252")
    return (
        f'<span style="font-family:var(--font-display);font-weight:600;'
        f'color:{color};font-size:0.9rem;">{label}</span>'
    )


def confidence_text(confidence: float) -> str:
    """Return styled confidence text using accent color."""
    return (
        f'<span class="spps-conf-badge">{confidence:.0%}</span>'
    )


def chart_caption(text: str) -> None:
    """Display a plain-English caption below a chart."""
    st.markdown(
        f'<p class="spps-chart-caption">{text}</p>',
        unsafe_allow_html=True,
    )


def metric_card(title: str, value: str, subtitle: str = "") -> None:
    """Display a styled metric card using the new design system."""
    st.markdown(stat_card(title, value, subtitle), unsafe_allow_html=True)


# Store helpers in session state for pages to access
st.session_state["class_badge"]     = class_badge
st.session_state["confidence_text"] = confidence_text
st.session_state["chart_caption"]   = chart_caption
st.session_state["metric_card"]     = metric_card

# ---------------------------------------------------------------------------
# Landing page content
# ---------------------------------------------------------------------------

st.markdown(page_hero(
    "Student Performance Insights",
    "An analytics tool for students and teachers — understand what shapes "
    "academic outcomes, identify who might need support, and explore the "
    "impact of classroom interventions."
), unsafe_allow_html=True)

# Check if model is trained
from src.models.predict import model_is_available  # noqa: E402

if not model_is_available():
    st.error(
        "⚠️ **No trained model found.** Please run the training pipeline first:\n\n"
        "```\npython scripts/run_pipeline.py\n```\n\n"
        "The dashboard needs a trained model to make predictions."
    )
    st.stop()

# Navigation grid
st.markdown("""
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:0.75rem;margin:1.5rem 0 2rem 0;">

  <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
              padding:1.25rem 1.5rem;" class="anim-fade-up anim-fade-up-1">
    <p style="font-family:var(--font-display);font-size:0.95rem;font-weight:600;
              color:var(--ink);margin:0 0 0.25rem 0;">Overview</p>
    <p style="font-size:0.85rem;color:var(--ink-sec);margin:0;">
      Dataset statistics, class distribution, key engagement factors.
    </p>
  </div>

  <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
              padding:1.25rem 1.5rem;" class="anim-fade-up anim-fade-up-2">
    <p style="font-family:var(--font-display);font-size:0.95rem;font-weight:600;
              color:var(--ink);margin:0 0 0.25rem 0;">Predict for a Student</p>
    <p style="font-size:0.85rem;color:var(--ink-sec);margin:0;">
      Predict performance, explain the reasoning, and get personalised advice.
    </p>
  </div>

  <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
              padding:1.25rem 1.5rem;" class="anim-fade-up anim-fade-up-3">
    <p style="font-family:var(--font-display);font-size:0.95rem;font-weight:600;
              color:var(--ink);margin:0 0 0.25rem 0;">Try What-If Scenarios</p>
    <p style="font-size:0.85rem;color:var(--ink-sec);margin:0;">
      Adjust a student's data and watch the prediction update in real time.
    </p>
  </div>

  <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
              padding:1.25rem 1.5rem;" class="anim-fade-up anim-fade-up-4">
    <p style="font-family:var(--font-display);font-size:0.95rem;font-weight:600;
              color:var(--ink);margin:0 0 0.25rem 0;">Simulate the Whole Class</p>
    <p style="font-size:0.85rem;color:var(--ink-sec);margin:0;">
      Model the class-wide impact of an intervention using Monte Carlo simulation.
    </p>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown(
    f'<p style="font-size:0.8rem;color:var(--ink-muted);font-family:var(--font-mono);">'
    f'Model: {cfg["project"]["name"]} v{cfg["project"]["version"]} &nbsp;·&nbsp; '
    f'Built by {cfg["project"]["author"]} &nbsp;·&nbsp; '
    f'Classical ML — no deep learning'
    f'</p>',
    unsafe_allow_html=True,
)
