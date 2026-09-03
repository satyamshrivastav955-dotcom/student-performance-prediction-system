"""
Individual Predictor page — predict, explain, and advise for one student.

This is the centrepiece of the dashboard: select a student (or enter data
manually), see their predicted performance band, understand *why* via SHAP,
and get personalised recommendations including counterfactual suggestions.
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
    inject_theme, page_hero, stat_card, result_panel,
    shap_narrative, cf_card, suggestion_card, probability_bar,
    CLASS_COLORS, PLOTLY_BASE,
    ACCENT, CHART_GRAY, CHART_DARK, INK, INK_SEC, INK_MUTED, BORDER, SURFACE,
)

st.set_page_config(
    page_title="Predict for a Student", page_icon="🎯", layout="wide"
)
inject_theme()

cfg = load_config()

# ---------------------------------------------------------------------------
# Check model
# ---------------------------------------------------------------------------
if not model_is_available():
    st.error("⚠️ No trained model found. Run `python scripts/run_pipeline.py` first.")
    st.stop()

# ---------------------------------------------------------------------------
# Page hero
# ---------------------------------------------------------------------------
st.markdown(page_hero(
    "Predict for a Student",
    "Enter a student's data or pick an existing student to see their predicted "
    "performance band, understand the reasoning behind it, and get personalised advice."
), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    return load_processed()

df = load_data()

# ---------------------------------------------------------------------------
# Input mode selection
# ---------------------------------------------------------------------------
input_mode = st.radio(
    "How would you like to input student data?",
    ["Select from dataset", "Enter manually"],
    horizontal=True,
)

student_data: dict = {}

if input_mode == "Select from dataset":
    col_select, col_info = st.columns([1, 2])
    with col_select:
        student_idx = st.selectbox(
            "Choose a student",
            range(len(df)),
            format_func=lambda i: f"Student {i+1} (actual: {df.iloc[i]['Class']})",
        )

    row = df.iloc[student_idx]
    student_data = {
        c: (int(row[c]) if c in cfg["data"]["numeric_features"] else str(row[c]))
        for c in feature_columns(cfg)
    }

    with col_info:
        st.markdown(
            '<p class="spps-stat-card-label">Selected student\'s data</p>',
            unsafe_allow_html=True,
        )
        display_data = {friendly(k, cfg): v for k, v in student_data.items()}
        st.json(display_data)

else:
    st.markdown(
        '<p class="spps-stat-card-label" style="margin-top:1rem;">Student Details</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<p style="font-family:var(--font-display);font-size:0.9rem;'
            'font-weight:600;color:var(--ink);margin:0 0 0.5rem 0;">'
            'Engagement Metrics (0–100)</p>',
            unsafe_allow_html=True,
        )
        student_data["raisedhands"]       = st.slider(friendly("raisedhands", cfg),       0, 100, 50, key="input_rh")
        student_data["VisITedResources"]  = st.slider(friendly("VisITedResources", cfg),  0, 100, 50, key="input_vr")
        student_data["AnnouncementsView"] = st.slider(friendly("AnnouncementsView", cfg), 0, 100, 50, key="input_av")
        student_data["Discussion"]        = st.slider(friendly("Discussion", cfg),        0, 100, 50, key="input_disc")

    with col2:
        st.markdown(
            '<p style="font-family:var(--font-display);font-size:0.9rem;'
            'font-weight:600;color:var(--ink);margin:0 0 0.5rem 0;">'
            'Background Information</p>',
            unsafe_allow_html=True,
        )
        student_data["gender"]                   = st.selectbox(friendly("gender", cfg),                   sorted(df["gender"].unique()),           key="input_gender")
        student_data["NationalITy"]              = st.selectbox(friendly("NationalITy", cfg),              sorted(df["NationalITy"].unique()),       key="input_nat")
        student_data["PlaceofBirth"]             = st.selectbox(friendly("PlaceofBirth", cfg),             sorted(df["PlaceofBirth"].unique()),      key="input_pob")
        student_data["StageID"]                  = st.selectbox(friendly("StageID", cfg),                  sorted(df["StageID"].unique()),           key="input_stage")
        student_data["GradeID"]                  = st.selectbox(friendly("GradeID", cfg),                  sorted(df["GradeID"].unique()),           key="input_grade")
        student_data["SectionID"]                = st.selectbox(friendly("SectionID", cfg),                sorted(df["SectionID"].unique()),         key="input_section")
        student_data["Topic"]                    = st.selectbox(friendly("Topic", cfg),                    sorted(df["Topic"].unique()),             key="input_topic")
        student_data["Semester"]                 = st.selectbox(friendly("Semester", cfg),                 sorted(df["Semester"].unique()),          key="input_semester")
        student_data["Relation"]                 = st.selectbox(friendly("Relation", cfg),                 sorted(df["Relation"].unique()),          key="input_relation")
        student_data["ParentAnsweringSurvey"]    = st.selectbox(friendly("ParentAnsweringSurvey", cfg),    ["Yes", "No"],                            key="input_pas")
        student_data["ParentschoolSatisfaction"] = st.selectbox(friendly("ParentschoolSatisfaction", cfg), ["Good", "Bad"],                          key="input_pss")
        student_data["StudentAbsenceDays"]       = st.selectbox(friendly("StudentAbsenceDays", cfg),       ["Under-7", "Above-7"],                   key="input_abs")

st.divider()

# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------
if st.button("Run Prediction", type="primary", use_container_width=True):
    if not student_data:
        st.warning("Please enter or select student data first.")
        st.stop()

    with st.spinner("Generating prediction and explanation…"):
        prediction = predict_one(student_data, cfg=cfg)

    predicted_class = prediction["predicted_class"]
    predicted_label = prediction["predicted_label"]
    confidence      = prediction.get("confidence", 0)
    runner_up       = prediction.get("runner_up_class", "—")
    runner_prob     = prediction.get("runner_up_probability", 0)
    is_borderline   = prediction.get("is_borderline", False)

    # --- Result panel ---
    st.markdown(
        '<p class="spps-section-label" style="margin-top:0.5rem;">Prediction Result</p>',
        unsafe_allow_html=True,
    )

    col_res, col_probs = st.columns([1, 1])

    with col_res:
        st.markdown(
            result_panel(
                predicted_class, predicted_label, confidence,
                runner_up, runner_prob, is_borderline
            ),
            unsafe_allow_html=True,
        )
        if prediction.get("confidence_note"):
            st.caption(prediction["confidence_note"])

    with col_probs:
        probs = prediction.get("probabilities", {})
        if probs:
            st.markdown(
                '<p class="spps-stat-card-label">Probability distribution</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                probability_bar(probs, predicted_class),
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p class="spps-chart-caption">How the model distributes its '
                'confidence across the three performance bands. A dominant bar '
                'means high certainty; similar-height bars mean the student '
                'sits near a boundary.</p>',
                unsafe_allow_html=True,
            )

    st.divider()

    # --- SHAP Explanation ---
    st.markdown(
        '<p class="spps-section-label">Why This Prediction</p>',
        unsafe_allow_html=True,
    )
    st.caption(
        "SHAP (SHapley Additive exPlanations) — breaks down the model's "
        "reasoning into individual factors."
    )

    try:
        with st.spinner("Computing explanation…"):
            from src.explainability.shap_utils import explain_student
            explanation = explain_student(student_data, cfg=cfg)

        contributions = explanation.get("contributions", [])
        if contributions:
            top_n = min(8, len(contributions))
            top   = contributions[:top_n]

            features = [
                friendly(c.get("original_feature", c.get("feature", "")), cfg)
                for c in reversed(top)
            ]
            values = [c.get("shap_value", 0) for c in reversed(top)]

            # Color: accent for top positive, dark for top negative, gray for rest
            max_pos = max((v for v in values if v > 0), default=0)
            min_neg = min((v for v in values if v < 0), default=0)
            colors  = []
            for v in values:
                if v > 0 and abs(v - max_pos) < 1e-9:
                    colors.append(ACCENT)       # top positive → accent
                elif v < 0 and abs(v - min_neg) < 1e-9:
                    colors.append(CHART_DARK)   # top negative → dark
                elif v > 0:
                    colors.append("#8CAAD4")    # smaller positive → lighter accent
                else:
                    colors.append("#9C9C9A")    # smaller negative → mid gray

            # Narrative sentence (above chart)
            top_feats_positive = [
                friendly(c.get("original_feature", c.get("feature", "")), cfg)
                for c in top[:3] if c.get("shap_value", 0) > 0
            ]
            top_feats_negative = [
                friendly(c.get("original_feature", c.get("feature", "")), cfg)
                for c in top[:3] if c.get("shap_value", 0) < 0
            ]

            if top_feats_positive:
                st.markdown(
                    shap_narrative(top_feats_positive[:2], direction="toward"),
                    unsafe_allow_html=True,
                )
            elif top_feats_negative:
                st.markdown(
                    shap_narrative(top_feats_negative[:2], direction="against"),
                    unsafe_allow_html=True,
                )

            fig = go.Figure(go.Bar(
                y=features,
                x=values,
                orientation="h",
                marker_color=colors,
                text=[f"{v:+.3f}" for v in values],
                textposition="outside",
                textfont=dict(family="IBM Plex Mono, monospace", size=11),
            ))
            fig.update_layout(
                **PLOTLY_BASE,
                margin=dict(t=20, b=40, l=160, r=60),
                xaxis=dict(
                    title="Impact on prediction",
                    showgrid=True, gridcolor="#EBEBEA",
                    zeroline=True, zerolinecolor="#C8C8C6", zerolinewidth=1.5,
                ),
                yaxis=dict(showgrid=False, tickfont=dict(size=12)),
                height=max(260, top_n * 42),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                '<p class="spps-chart-caption">Blue pushes the prediction '
                'toward a higher band; dark bars pull it lower. The longer '
                'the bar, the stronger that factor\'s influence.</p>',
                unsafe_allow_html=True,
            )

            if explanation.get("narrative"):
                st.markdown(
                    f'<p style="font-size:0.9rem;color:var(--ink-sec);">'
                    f'<strong>In plain terms:</strong> {explanation["narrative"]}'
                    f'</p>',
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.warning(f"Could not generate SHAP explanation: {e}")

    st.divider()

    # --- Personalised Recommendations ---
    st.markdown(
        '<p class="spps-section-label">Personalised Recommendations</p>',
        unsafe_allow_html=True,
    )

    try:
        with st.spinner("Generating recommendations…"):
            from src.recommendations.engine import generate_recommendations
            rec = generate_recommendations(
                student_data, cfg=cfg, include_counterfactual=True
            )

        suggestions = rec.get("improvement_suggestions", [])
        if suggestions:
            for suggestion in suggestions:
                st.markdown(suggestion_card(suggestion), unsafe_allow_html=True)
        elif predicted_class == "H":
            st.markdown(
                suggestion_card(
                    "🌟 This student is predicted as High-performing. Keep up the current approach!"
                ),
                unsafe_allow_html=True,
            )
        else:
            st.info("No specific improvement suggestions generated for this student profile.")

        # Counterfactual suggestion
        cf = rec.get("counterfactual")
        if cf and cf.get("counterfactuals"):
            st.markdown(
                '<p class="spps-section-label" style="margin-top:1.5rem;">'
                'What Would Need to Change?</p>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Counterfactual explanation — the smallest realistic changes "
                "that would move the prediction to High."
            )

            for cf_item in cf["counterfactuals"][:2]:
                summary = cf_item.get("plain_summary", "")
                if summary:
                    # Extract a bold action line from the summary
                    action = summary.split(".")[0] if "." in summary else summary
                    detail = ". ".join(summary.split(".")[1:]).strip() if "." in summary else ""
                    st.markdown(
                        cf_card("→", action, detail),
                        unsafe_allow_html=True,
                    )

                changes = cf_item.get("changes", [])
                if changes:
                    with st.expander("See detailed changes"):
                        for change in changes:
                            feat = change.get("feature", "")
                            old  = change.get("original", "")
                            new  = change.get("counterfactual", "")
                            st.markdown(
                                f'<span style="font-size:0.875rem;">'
                                f'<strong>{friendly(feat, cfg)}</strong>: '
                                f'{old} → {new}</span>',
                                unsafe_allow_html=True,
                            )

    except Exception as e:
        st.warning(f"Could not generate recommendations: {e}")

    # Advanced details
    with st.expander("Advanced: Raw prediction data"):
        st.json(prediction)
