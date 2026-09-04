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
    CLASS_COLORS, PLOTLY_BASE, PLOTLY_CONFIG,
    ACCENT, CHART_GRAY, CHART_DARK, INK, INK_SEC, INK_MUTED, BORDER, SURFACE,
)

st.set_page_config(
    page_title="Predict for a Student", page_icon="🎯", layout="wide",
    initial_sidebar_state="collapsed",
)
inject_theme(active_page="predictor")

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
            # Narrative lead-in from the pre-split toward/against lists
            toward  = [c["friendly_name"] for c in explanation.get("pushing_toward", [])][:2]
            against = [c["friendly_name"] for c in explanation.get("pushing_against", [])][:2]
            if toward:
                st.markdown(shap_narrative(toward, direction="toward"), unsafe_allow_html=True)
            elif against:
                st.markdown(shap_narrative(against, direction="against"), unsafe_allow_html=True)

            base_val = explanation.get("base_value")
            allc     = explanation.get("all_contributions") or contributions

            # ── Primary view: SHAP waterfall (base rate → factors → final) ──
            waterfall_ok = False
            if base_val is not None:
                try:
                    K = 7
                    head      = allc[:K]
                    other_sum = float(sum(c["shap"] for c in allc[K:]))
                    total     = float(base_val) + float(sum(c["shap"] for c in allc))

                    labels = ["Base rate"] + [c["friendly_name"] for c in head]
                    meas   = ["absolute"]  + ["relative"] * len(head)
                    xvals  = [float(base_val)] + [float(c["shap"]) for c in head]
                    if abs(other_sum) > 1e-9:
                        labels.append("Other features"); meas.append("relative"); xvals.append(other_sum)
                    labels.append(f"P({predicted_label})"); meas.append("total"); xvals.append(total)

                    # Reverse so the base rate sits at the top of the horizontal chart
                    labels, meas, xvals = labels[::-1], meas[::-1], xvals[::-1]
                    txt = [f"{xv:.3f}" if mv in ("absolute", "total") else f"{xv:+.3f}"
                           for mv, xv in zip(meas, xvals)]

                    figw = go.Figure(go.Waterfall(
                        orientation="h", measure=meas, y=labels, x=xvals,
                        text=txt, textposition="outside",
                        connector={"line": {"color": BORDER, "width": 1}},
                        increasing={"marker": {"color": ACCENT}},
                        decreasing={"marker": {"color": CHART_DARK}},
                        totals={"marker": {"color": INK}},
                    ))
                    figw.update_layout(
                        **PLOTLY_BASE, showlegend=False,
                        height=max(300, len(labels) * 42),
                        margin=dict(t=20, b=40, l=170, r=80),
                        xaxis=dict(title=f"Contribution to P({predicted_label})",
                                   showgrid=True, gridcolor="#EBEBEA",
                                   zeroline=True, zerolinecolor="#C8C8C6", zerolinewidth=1.5),
                        yaxis=dict(showgrid=False, tickfont=dict(size=12)),
                    )
                    st.plotly_chart(figw, use_container_width=True, config=PLOTLY_CONFIG)
                    st.markdown(
                        '<p class="spps-chart-caption">A SHAP waterfall: starting from the average '
                        'prediction (base rate), each factor pushes the probability of the '
                        f'<strong>{predicted_label}</strong> band up (blue) or down (dark) until it '
                        'reaches this student\'s final score.</p>',
                        unsafe_allow_html=True,
                    )
                    waterfall_ok = True
                except Exception:
                    waterfall_ok = False

            # ── Fallback: horizontal impact bar (also the correct 'shap' key) ──
            if not waterfall_ok:
                top      = contributions[:8]
                features = [c["friendly_name"] for c in reversed(top)]
                values   = [float(c["shap"]) for c in reversed(top)]
                colors   = [ACCENT if v > 0 else CHART_DARK for v in values]
                figb = go.Figure(go.Bar(
                    y=features, x=values, orientation="h", marker_color=colors,
                    text=[f"{v:+.3f}" for v in values], textposition="outside",
                    textfont=dict(family="IBM Plex Mono, monospace", size=11),
                ))
                figb.update_layout(
                    **PLOTLY_BASE, margin=dict(t=20, b=40, l=160, r=60),
                    xaxis=dict(title="Impact on prediction", showgrid=True, gridcolor="#EBEBEA",
                               zeroline=True, zerolinecolor="#C8C8C6", zerolinewidth=1.5),
                    yaxis=dict(showgrid=False, tickfont=dict(size=12)),
                    height=max(260, len(top) * 42),
                )
                st.plotly_chart(figb, use_container_width=True, config=PLOTLY_CONFIG)
                st.markdown(
                    '<p class="spps-chart-caption">Blue pushes the prediction toward a higher '
                    'band; dark bars pull it lower. The longer the bar, the stronger that '
                    'factor\'s influence.</p>',
                    unsafe_allow_html=True,
                )

            # Plain-terms narrative (correct key is 'summary')
            if explanation.get("summary"):
                st.markdown(
                    f'<p style="font-size:0.9rem;color:var(--ink-sec);">'
                    f'<strong>In plain terms:</strong> {explanation["summary"]}'
                    f'</p>',
                    unsafe_allow_html=True,
                )

            # ── Student-vs-class radar ──
            numf = cfg["data"]["numeric_features"]
            try:
                stu_vals = [float(student_data.get(f, 0)) for f in numf]
                hi_avg = df[df["Class"] == "H"][numf].mean().reindex(numf).tolist()
                lo_avg = df[df["Class"] == "L"][numf].mean().reindex(numf).tolist()
                cats   = [friendly(f, cfg) for f in numf]

                def _loop(seq):
                    seq = list(seq)
                    return seq + [seq[0]]

                st.markdown(
                    '<p class="spps-stat-card-label" style="margin-top:1.5rem;">'
                    'This student vs class averages</p>',
                    unsafe_allow_html=True,
                )
                figr = go.Figure()
                figr.add_trace(go.Scatterpolar(
                    r=_loop(lo_avg), theta=_loop(cats), name="Low-band avg",
                    line_color=CHART_DARK, fill="toself", opacity=0.25))
                figr.add_trace(go.Scatterpolar(
                    r=_loop(hi_avg), theta=_loop(cats), name="High-band avg",
                    line_color=CHART_GRAY, fill="toself", opacity=0.25))
                figr.add_trace(go.Scatterpolar(
                    r=_loop(stu_vals), theta=_loop(cats), name="This student",
                    line_color=ACCENT, fill="toself", opacity=0.5))
                figr.update_layout(
                    **PLOTLY_BASE, height=400, margin=dict(t=30, b=40, l=40, r=40),
                    polar=dict(
                        radialaxis=dict(range=[0, 100], showline=False,
                                        gridcolor="#EBEBEA", tickfont=dict(size=10)),
                        angularaxis=dict(tickfont=dict(size=11)),
                        bgcolor="rgba(0,0,0,0)",
                    ),
                )
                st.plotly_chart(figr, use_container_width=True, config=PLOTLY_CONFIG)
                st.markdown(
                    '<p class="spps-chart-caption">Where this student\'s engagement sits relative '
                    'to the typical High-band and Low-band student. The closer the blue shape hugs '
                    'the High outline, the stronger the engagement profile.</p>',
                    unsafe_allow_html=True,
                )
            except Exception:
                pass

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


st.divider()

# ---------------------------------------------------------------------------
# Compare two students side by side
# ---------------------------------------------------------------------------
st.markdown(
    '<p class="spps-section-label">Compare Two Students</p>',
    unsafe_allow_html=True,
)
st.caption(
    "Pick any two students to see their predictions next to each other — useful "
    "for understanding why two similar-looking students land in different bands."
)


def _record(i: int) -> dict:
    r = df.iloc[i]
    return {
        c: (int(r[c]) if c in cfg["data"]["numeric_features"] else str(r[c]))
        for c in feature_columns(cfg)
    }


cmp_a, cmp_b = st.columns(2)
with cmp_a:
    idx_a = st.selectbox(
        "Student A", range(len(df)),
        format_func=lambda i: f"Student {i+1} (actual: {df.iloc[i]['Class']})",
        key="cmp_a",
    )
with cmp_b:
    idx_b = st.selectbox(
        "Student B", range(len(df)),
        index=min(1, len(df) - 1),
        format_func=lambda i: f"Student {i+1} (actual: {df.iloc[i]['Class']})",
        key="cmp_b",
    )

if st.button("Compare", key="cmp_btn", use_container_width=True):
    try:
        pa = predict_one(_record(idx_a), cfg=cfg)
        pb = predict_one(_record(idx_b), cfg=cfg)
    except Exception as e:
        st.error(f"Comparison failed: {e}")
    else:
        numf = cfg["data"]["numeric_features"]
        ca, cb = st.columns(2)
        for col, idx, pred in [(ca, idx_a, pa), (cb, idx_b, pb)]:
            with col:
                st.markdown(
                    result_panel(pred["predicted_class"], pred["predicted_label"],
                                 pred.get("confidence", 0)),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<p class="spps-stat-card-label" style="margin-top:0.75rem;">'
                    f'Student {idx+1} · actual {df.iloc[idx]["Class"]}</p>',
                    unsafe_allow_html=True,
                )
                probs = pred.get("probabilities", {})
                if probs:
                    st.markdown(probability_bar(probs, pred["predicted_class"]),
                                unsafe_allow_html=True)

        # Engagement comparison
        cats = [friendly(f, cfg) for f in numf]
        va = [int(df.iloc[idx_a][f]) for f in numf]
        vb = [int(df.iloc[idx_b][f]) for f in numf]
        figc = go.Figure()
        figc.add_trace(go.Bar(name=f"Student {idx_a+1}", x=cats, y=va, marker_color=ACCENT))
        figc.add_trace(go.Bar(name=f"Student {idx_b+1}", x=cats, y=vb,
                              marker_color=CHART_DARK, opacity=0.7))
        figc.update_layout(
            **PLOTLY_BASE, barmode="group", height=320, margin=dict(t=20, b=40, l=8, r=8),
            yaxis=dict(title="Engagement score", range=[0, 100],
                       showgrid=True, gridcolor="#EBEBEA"),
        )
        st.plotly_chart(figc, use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown(
            '<p class="spps-chart-caption">Side-by-side engagement metrics for the two '
            'selected students — the visual root of any difference in their predicted bands.</p>',
            unsafe_allow_html=True,
        )
