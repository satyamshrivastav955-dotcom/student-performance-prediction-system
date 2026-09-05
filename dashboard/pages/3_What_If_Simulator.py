"""
What-If Simulator page — sliders for attendance/participation/etc.,
live-updating predicted class + confidence.

This lets a student or teacher ask: "What would happen if I changed
this one thing?" and see the answer instantly.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASH_DIR     = Path(__file__).resolve().parents[1]
for p in (str(PROJECT_ROOT), str(DASH_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.data.preprocess import feature_columns, load_processed
from src.models.predict import model_is_available, predict_one
from src.utils.config import load_config, class_label, friendly
from theme import (
    inject_theme, page_hero, result_panel, probability_bar, delta_chip,
    CLASS_COLORS, PLOTLY_BASE, PLOTLY_CONFIG,
    ACCENT, CHART_GRAY, CHART_DARK, INK, INK_SEC, INK_MUTED, BORDER,
)

st.set_page_config(
    page_title="What-If Simulator — Counsel Room", page_icon=None, layout="wide",
    initial_sidebar_state="collapsed",
)
inject_theme(active_page="whatif")

cfg = load_config()

if not model_is_available():
    st.error("No trained model found. Run `python scripts/run_pipeline.py` first.")
    st.stop()

# ---------------------------------------------------------------------------
# Page hero
# ---------------------------------------------------------------------------
st.markdown(page_hero(
    "The Counsel Room",
    "Move the levers of habit and watch the verdict move. Every change is live, "
    "every counsel is actionable — demographics never move."
), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load baseline student
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    return load_processed()

df = load_data()

st.markdown(
    '<p class="spps-stat-card-label">1. Choose a starting point</p>',
    unsafe_allow_html=True,
)
col_base, col_info = st.columns([1, 2])

with col_base:
    baseline_idx = st.selectbox(
        "Base student",
        range(len(df)),
        format_func=lambda i: f"Student {i+1} (actual: {df.iloc[i]['Class']})",
        key="whatif_student",
    )

baseline_row = df.iloc[baseline_idx]

# Non-actionable features stay fixed
fixed_features: dict = {}
for col in feature_columns(cfg):
    if col not in cfg["data"]["actionable_features"]:
        fixed_features[col] = (
            int(baseline_row[col]) if col in cfg["data"]["numeric_features"]
            else str(baseline_row[col])
        )

with col_info:
    st.markdown(
        '<p class="spps-stat-card-label">Fixed characteristics (not adjustable)</p>',
        unsafe_allow_html=True,
    )
    display_fixed = {friendly(k, cfg): v for k, v in fixed_features.items()}
    cols = st.columns(3)
    for i, (name, val) in enumerate(display_fixed.items()):
        cols[i % 3].markdown(
            f'<p style="font-size:0.8125rem;margin:0.15rem 0;">'
            f'<span style="color:var(--ink-muted);">{name}</span><br>'
            f'<strong style="color:var(--ink);">{val}</strong></p>',
            unsafe_allow_html=True,
        )

st.divider()

# ---------------------------------------------------------------------------
# Adjustable sliders
# ---------------------------------------------------------------------------
st.markdown(
    '<p class="spps-stat-card-label">2. Adjust engagement metrics</p>',
    unsafe_allow_html=True,
)
st.caption("Move the sliders to see how the prediction changes.")

col_sliders, col_result = st.columns([1, 1])

with col_sliders:
    numeric_features = cfg["data"]["numeric_features"]
    slider_values: dict = {}

    for feat in numeric_features:
        original = int(baseline_row[feat])
        slider_values[feat] = st.slider(
            f"{friendly(feat, cfg)} (was: {original})",
            min_value=0,
            max_value=100,
            value=original,
            key=f"whatif_{feat}",
        )

    st.markdown(
        '<hr style="border:none;border-top:1px solid var(--border);margin:1rem 0;">',
        unsafe_allow_html=True,
    )

    original_absence = str(baseline_row["StudentAbsenceDays"])
    slider_values["StudentAbsenceDays"] = st.selectbox(
        f"{friendly('StudentAbsenceDays', cfg)} (was: {original_absence})",
        ["Under-7", "Above-7"],
        index=0 if original_absence == "Under-7" else 1,
        key="whatif_absence",
    )

    original_survey = str(baseline_row["ParentAnsweringSurvey"])
    slider_values["ParentAnsweringSurvey"] = st.selectbox(
        f"{friendly('ParentAnsweringSurvey', cfg)} (was: {original_survey})",
        ["Yes", "No"],
        index=0 if original_survey == "Yes" else 1,
        key="whatif_survey",
    )

# Build full student record
student_data = {**fixed_features, **slider_values}

with col_result:
    # --- Prediction ---
    try:
        prediction = predict_one(student_data, cfg=cfg)
        baseline_pred = predict_one(
            {c: (int(baseline_row[c]) if c in cfg["data"]["numeric_features"]
                 else str(baseline_row[c]))
             for c in feature_columns(cfg)},
            cfg=cfg,
        )
    except Exception as e:
        st.error(f"Prediction failed: {e}")
        st.stop()

    predicted_class = prediction["predicted_class"]
    predicted_label = prediction["predicted_label"]
    confidence      = prediction.get("confidence", 0)
    baseline_class  = baseline_pred["predicted_class"]
    baseline_label  = baseline_pred["predicted_label"]
    class_changed   = predicted_class != baseline_class

    # Calm result panel
    st.markdown(
        '<p class="spps-stat-card-label">Live Prediction</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        result_panel(predicted_class, predicted_label, confidence),
        unsafe_allow_html=True,
    )

    # Class change note
    if class_changed:
        rank = ["L", "M", "H"]
        improved = rank.index(predicted_class) > rank.index(baseline_class)
        arrow = "↑" if improved else "↓"
        direction_word = "improved" if improved else "declined"
        st.markdown(
            f'<p style="font-size:0.875rem;color:var(--ink-sec);margin-top:0.5rem;">'
            f'<span style="font-family:var(--font-mono);color:var(--accent);">{arrow}</span> '
            f'Class {direction_word} from <strong>{baseline_label}</strong> '
            f'to <strong>{predicted_label}</strong>.</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<p style="font-size:0.8125rem;color:var(--ink-muted);margin-top:0.5rem;">'
            f'→ Class unchanged from <strong>{baseline_label}</strong>.</p>',
            unsafe_allow_html=True,
        )

    # Live CSS probability bars (animate on slider change via CSS transition)
    probs          = prediction.get("probabilities", {})
    baseline_probs = baseline_pred.get("probabilities", {})

    if probs:
        st.markdown(
            '<p class="spps-stat-card-label" style="margin-top:1.25rem;">Current probabilities</p>',
            unsafe_allow_html=True,
        )
        st.markdown(probability_bar(probs, predicted_class), unsafe_allow_html=True)

        # Compact before/after comparison chart
        st.markdown(
            '<p class="spps-stat-card-label" style="margin-top:1.25rem;">Before vs After</p>',
            unsafe_allow_html=True,
        )
        fig = go.Figure()

        # Baseline (faded gray)
        for cls in ["L", "M", "H"]:
            fig.add_trace(go.Bar(
                x=[class_label(cls, cfg)],
                y=[baseline_probs.get(cls, 0) * 100],
                name="Original",
                marker_color=CHART_GRAY,
                opacity=0.6,
                showlegend=(cls == "L"),
                legendgroup="original",
            ))

        # Current (accent for predicted class, dark gray for others)
        for cls in ["L", "M", "H"]:
            color = ACCENT if cls == predicted_class else CHART_DARK
            fig.add_trace(go.Bar(
                x=[class_label(cls, cfg)],
                y=[probs.get(cls, 0) * 100],
                name="What-If",
                marker_color=color,
                showlegend=(cls == "L"),
                legendgroup="whatif",
                text=[f"{probs.get(cls, 0):.0%}"],
                textposition="outside",
                textfont=dict(family="IBM Plex Mono, monospace", size=11),
            ))

        fig.update_layout(
            **PLOTLY_BASE,
            barmode="group",
            height=260,
            yaxis=dict(title="Probability (%)", range=[0, 110],
                       showgrid=True, gridcolor="#E7E0D1"),
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown(
            '<p class="spps-chart-caption">Stone bars = original verdict. '
            'Forest and brass bars = counsel-room scenario.</p>',
            unsafe_allow_html=True,
        )

    # Changes made
    changes_made = []
    for feat in numeric_features:
        original = int(baseline_row[feat])
        current  = slider_values[feat]
        if original != current:
            diff = current - original
            changes_made.append((friendly(feat, cfg), original, current, diff))

    if str(baseline_row["StudentAbsenceDays"]) != slider_values["StudentAbsenceDays"]:
        changes_made.append((
            friendly("StudentAbsenceDays", cfg),
            baseline_row["StudentAbsenceDays"],
            slider_values["StudentAbsenceDays"],
            None,
        ))
    if str(baseline_row["ParentAnsweringSurvey"]) != slider_values["ParentAnsweringSurvey"]:
        changes_made.append((
            friendly("ParentAnsweringSurvey", cfg),
            baseline_row["ParentAnsweringSurvey"],
            slider_values["ParentAnsweringSurvey"],
            None,
        ))

    if changes_made:
        st.markdown(
            '<p class="spps-stat-card-label" style="margin-top:1.25rem;">Changes made</p>',
            unsafe_allow_html=True,
        )
        for name, old, new, diff in changes_made:
            chip_html = delta_chip(diff) if isinstance(diff, (int, float)) else ""
            st.markdown(
                f'<p style="font-size:0.875rem;margin:0.25rem 0;color:var(--ink-sec);">'
                f'<strong style="color:var(--ink);">{name}</strong>: '
                f'{old} → {new} {chip_html}</p>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<p style="font-size:0.8125rem;color:var(--ink-muted);margin-top:1rem;">'
            'No changes from the baseline — adjust the sliders above.</p>',
            unsafe_allow_html=True,
        )
