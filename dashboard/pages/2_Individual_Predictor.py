"""
Individual Predictor page — predict, explain, and advise for one student.
"""
from __future__ import annotations
import sys
from pathlib import Path
import html

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
    inject_theme, page_header, prediction_card_html, profile_bar, 
    recommendation_card_html, scenario_card_html, section_header_html,
    ui_error_state, CLASS_COLORS, PLOTLY_BASE, PLOTLY_CONFIG,
    ACCENT, CHART_GRAY, CHART_DARK, INK, INK_SEC, INK_MUTED, BORDER, SURFACE, GREEN, CORAL, AMBER,
    TEAL, PURPLE, footnote,
)

st.set_page_config(
    page_title="Student Check-In — Student Success", layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme(active_page="predictor")

cfg = load_config()

if not model_is_available():
    st.markdown(
        ui_error_state(
            "Model not found",
            "No trained model was detected. Run the analysis pipeline first: "
            "python scripts/run_pipeline.py",
        ),
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(page_header(
    label="STUDENT CHECK-IN",
    title="Understand an individual student's performance",
    subtitle="View predictions, explanations, and personalized recommendations.",
    hero_text='Every Student\nHas Potential\n"Data-driven insights for personalized growth."'
), unsafe_allow_html=True)

@st.cache_data
def load_data():
    return load_processed()

df = load_data()

col1, col2, col3 = st.columns([1.2, 1.3, 1.2])

student_data: dict = {}
manual_mode = False

with col1:
    st.markdown('<p class="spps-section-label">Select a Student</p>', unsafe_allow_html=True)
    
    input_mode = st.radio(
        "Input Mode",
        ["Select from dataset", "Enter manually"],
        horizontal=True,
        label_visibility="collapsed"
    )
    manual_mode = (input_mode == "Enter manually")
    
    if not manual_mode:
        student_idx = st.selectbox(
            "Choose a student",
            range(len(df)),
            format_func=lambda i: f"A{i+1:04d} — Student {i+1}",
            label_visibility="collapsed"
        )
        row = df.iloc[student_idx]
        student_data = {
            c: (int(row[c]) if c in cfg["data"]["numeric_features"] else str(row[c]))
            for c in feature_columns(cfg)
        }
        
        initials = f"S{str(student_idx+1)[-1]}"
        student_id = f"A{student_idx+1:04d}"
        
        st.markdown(f"""
        <div class="ss-card">
          <div style="display:flex; align-items:center; gap:16px; margin-bottom:16px;">
            <div class="ss-avatar" style="width:48px; height:48px; font-size:1.2rem;">{initials}</div>
            <div>
              <div style="font-size:1.1rem; font-weight:700; color:var(--ink);">Student {student_idx+1}</div>
              <div style="font-size:0.8rem; color:var(--ink-muted);">ID: {student_id}</div>
            </div>
          </div>
          <div style="font-size:0.875rem; color:var(--ink-sec); line-height:1.6;">
            <strong>Subject:</strong> {row['Topic']}<br>
            <strong>Stage:</strong> {row['StageID']}<br>
            <strong>Nationality:</strong> {row['NationalITy']}<br>
            <strong>Actual band:</strong> {row['Class']}
          </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown('<div class="ss-card" style="padding:16px;">', unsafe_allow_html=True)
        st.markdown('<p style="font-weight:600; font-size:0.9rem; margin-bottom:8px;">Engagement Metrics</p>', unsafe_allow_html=True)
        student_data["raisedhands"]       = st.slider(friendly("raisedhands", cfg),       0, 100, 50, key="input_rh")
        student_data["VisITedResources"]  = st.slider(friendly("VisITedResources", cfg),  0, 100, 50, key="input_vr")
        student_data["AnnouncementsView"] = st.slider(friendly("AnnouncementsView", cfg), 0, 100, 50, key="input_av")
        student_data["Discussion"]        = st.slider(friendly("Discussion", cfg),        0, 100, 50, key="input_disc")
        
        st.markdown('<p style="font-weight:600; font-size:0.9rem; margin:16px 0 8px;">Background</p>', unsafe_allow_html=True)
        student_data["gender"]                   = st.selectbox(friendly("gender", cfg), sorted(df["gender"].unique()))
        student_data["NationalITy"]              = st.selectbox(friendly("NationalITy", cfg), sorted(df["NationalITy"].unique()))
        student_data["PlaceofBirth"]             = st.selectbox(friendly("PlaceofBirth", cfg), sorted(df["PlaceofBirth"].unique()))
        student_data["StageID"]                  = st.selectbox(friendly("StageID", cfg), sorted(df["StageID"].unique()))
        student_data["GradeID"]                  = st.selectbox(friendly("GradeID", cfg), sorted(df["GradeID"].unique()))
        student_data["SectionID"]                = st.selectbox(friendly("SectionID", cfg), sorted(df["SectionID"].unique()))
        student_data["Topic"]                    = st.selectbox(friendly("Topic", cfg), sorted(df["Topic"].unique()))
        student_data["Semester"]                 = st.selectbox(friendly("Semester", cfg), sorted(df["Semester"].unique()))
        student_data["Relation"]                 = st.selectbox(friendly("Relation", cfg), sorted(df["Relation"].unique()))
        student_data["ParentAnsweringSurvey"]    = st.selectbox(friendly("ParentAnsweringSurvey", cfg), ["Yes", "No"])
        student_data["ParentschoolSatisfaction"] = st.selectbox(friendly("ParentschoolSatisfaction", cfg), ["Good", "Bad"])
        student_data["StudentAbsenceDays"]       = st.selectbox(friendly("StudentAbsenceDays", cfg), ["Under-7", "Above-7"])
        st.markdown('</div>', unsafe_allow_html=True)

run_pred = True
if manual_mode:
    run_pred = st.button("Run Prediction", type="primary", use_container_width=True)

predicted_class = "M"
predicted_label = "Medium"
confidence = 0.0
probs = {}
explanation = {}
contributions = []
prediction = {}

if run_pred and student_data:
    with st.spinner("Generating prediction..."):
        prediction = predict_one(student_data, cfg=cfg)
        predicted_class = prediction["predicted_class"]
        predicted_label = prediction["predicted_label"]
        confidence = prediction.get("confidence", 0)
        probs = prediction.get("probabilities", {})
        
        from src.explainability.shap_utils import explain_student
        explanation = explain_student(student_data, cfg=cfg)
        contributions = explanation.get("contributions", [])

with col2:
    st.markdown('<p class="spps-section-label">Predicted Performance</p>', unsafe_allow_html=True)
    if run_pred and student_data:
        st.markdown(
            prediction_card_html(predicted_class, predicted_label, confidence, probs),
            unsafe_allow_html=True
        )
        
        st.markdown('<div style="margin-top:24px;">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-size:1.1rem; font-weight:700; margin:0 0 4px;">Why this prediction?</h3>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.875rem; color:var(--ink-muted); margin:0 0 16px;">Key factors influencing this student\'s predicted performance.</p>', unsafe_allow_html=True)
        
        if contributions:
            toward = explanation.get("pushing_toward", [])
            against = explanation.get("pushing_against", [])
            
            t1, t2 = st.columns(2)
            with t1:
                st.markdown('<div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--green); margin-bottom:8px;">Top Positive Factors</div>', unsafe_allow_html=True)
                for c in toward[:3]:
                    val = float(c["shap"])
                    pct = min(100, (val / 0.5) * 100) # scale approx
                    st.markdown(f"""
                    <div class="ss-shap-row">
                      <div class="ss-shap-label" style="min-width:100px; font-size:0.75rem;">{c['friendly_name']}</div>
                      <div class="ss-shap-track"><div class="ss-shap-fill-pos" style="width:{pct}%;"></div></div>
                      <div class="ss-shap-val" style="color:var(--green);">+{val:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            with t2:
                st.markdown('<div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--coral); margin-bottom:8px;">Factors Pulling Down</div>', unsafe_allow_html=True)
                for c in against[:3]:
                    val = abs(float(c["shap"]))
                    pct = min(100, (val / 0.5) * 100) # scale approx
                    st.markdown(f"""
                    <div class="ss-shap-row">
                      <div class="ss-shap-label" style="min-width:100px; font-size:0.75rem;">{c['friendly_name']}</div>
                      <div class="ss-shap-track"><div class="ss-shap-fill-neg" style="width:{pct}%;"></div></div>
                      <div class="ss-shap-val" style="color:var(--coral);">-{val:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if explanation.get("summary"):
                st.markdown(f"""
                <div class="ss-means-card" style="margin-top:16px;">
                  <div class="ss-means-title">What this means</div>
                  <div class="ss-means-text">{explanation['summary']}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<p class="spps-section-label">Academic Profile</p>', unsafe_allow_html=True)
    if student_data:
        st.markdown('<div class="ss-card">', unsafe_allow_html=True)
        st.markdown(profile_bar("Raised Hands", float(student_data.get("raisedhands", 0))), unsafe_allow_html=True)
        st.markdown(profile_bar("Visited Resources", float(student_data.get("VisITedResources", 0))), unsafe_allow_html=True)
        st.markdown(profile_bar("Announcements", float(student_data.get("AnnouncementsView", 0))), unsafe_allow_html=True)
        st.markdown(profile_bar("Discussion", float(student_data.get("Discussion", 0))), unsafe_allow_html=True)
        
        abs_days = student_data.get("StudentAbsenceDays", "")
        bg_col = "var(--green-soft)" if abs_days == "Under-7" else "var(--coral-soft)"
        txt_col = "var(--green)" if abs_days == "Under-7" else "var(--coral)"
        st.markdown(f"""
        <div style="margin-top:12px; font-size:0.8125rem;">
          <span style="color:var(--ink-sec); margin-right:8px;">Absence Days:</span>
          <span style="background:{bg_col}; color:{txt_col}; padding:3px 8px; border-radius:12px; font-weight:600;">{abs_days}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<p class="spps-section-label" style="margin-top:24px;">Personalized Recommendations</p>', unsafe_allow_html=True)
        
        if run_pred:
            from src.recommendations.engine import generate_recommendations
            rec = generate_recommendations(student_data, cfg=cfg, include_counterfactual=True)
            suggestions = rec.get("improvement_suggestions", [])
            
            if not suggestions and predicted_class == "H":
                suggestions = ["This student is predicted as High-performing. Hold the course — consistency is the counsel."]
            
            icons = ["check-circle", "users", "book", "activity"]
            colors = [GREEN, TEAL, PURPLE, AMBER]
            
            st.markdown('<div class="ss-rec-list">', unsafe_allow_html=True)
            for i, suggestion in enumerate(suggestions[:4]):
                ic = icons[i % len(icons)]
                co = colors[i % len(colors)]
                st.markdown(recommendation_card_html("Action Step", suggestion, icon_name=ic, icon_color=co), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

st.divider()

st.markdown(section_header_html(
    title="What could change this outcome?",
    subtitle="Explore how small changes in key factors could improve the predicted performance."
), unsafe_allow_html=True)

if run_pred and student_data:
    cf = rec.get("counterfactual")
    if cf and cf.get("counterfactuals"):
        st.markdown('<div class="ss-cf-grid">', unsafe_allow_html=True)
        for i, cf_item in enumerate(cf["counterfactuals"][:3]):
            summary = cf_item.get("plain_summary", "")
            action = summary.split(".")[0] if "." in summary else summary
            detail = ". ".join(summary.split(".")[1:]).strip() if "." in summary else ""
            
            changes = cf_item.get("changes", [])
            from_val = "..."
            to_val = "..."
            if changes:
                from_val = f"{changes[0].get('original', '')}"
                to_val = f"{changes[0].get('counterfactual', '')}"
                
            st.markdown(scenario_card_html(
                path_num=i+1,
                type_label="Improvement Path",
                title=action,
                desc=detail,
                from_val=from_val,
                to_val=to_val
            ), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_btn = st.columns([4, 1])
        with col_btn[1]:
            st.button("Generate More Options", use_container_width=True)

with st.expander("Compare Two Students"):
    st.caption("Pick any two students to see their predictions next to each other.")
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
            
            ca, cb = st.columns(2)
            for col, idx, pred in [(ca, idx_a, pa), (cb, idx_b, pb)]:
                with col:
                    st.markdown(f"**Student {idx+1}** · Actual: {df.iloc[idx]['Class']}")
                    st.markdown(prediction_card_html(pred["predicted_class"], pred["predicted_label"], pred.get("confidence", 0), pred.get("probabilities", {})), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Comparison failed: {e}")

with st.expander("Advanced: Raw prediction data"):
    if run_pred:
        st.json(prediction)

st.markdown(
    footnote(
        "Student Check-In · Decision Support Platform · Ethical ML · Predictions are advisory, not definitive"
    ),
    unsafe_allow_html=True,
)

