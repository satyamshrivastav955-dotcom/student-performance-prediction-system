"""
What-If Simulator page — Explore Improvements.

Adjust key factors and see how different choices could impact performance.
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
    inject_theme, page_header, section_header_html, info_banner, 
    prediction_card_html, insight_card, next_steps_html, icon,
    ui_error_state, footnote,
    CLASS_COLORS, PLOTLY_BASE, PLOTLY_CONFIG,
    ACCENT, CHART_GRAY, CHART_DARK, INK, INK_SEC, INK_MUTED, BORDER,
)

st.set_page_config(
    page_title="Explore Improvements — Student Success", 
    page_icon=None, 
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme(active_page="whatif")

cfg = load_config()

if not model_is_available():
    st.markdown(
        ui_error_state(
            "Model not found",
            "No trained model was detected. Run the analysis pipeline first: python scripts/run_pipeline.py",
        ),
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(page_header(
    label='EXPLORE IMPROVEMENTS',
    title='What can change the outcome?',
    subtitle='Adjust key factors and see how different choices could impact performance.',
    hero_text='Better Choices\nBrighter Futures\n"Explore. Experiment. Empower."'
), unsafe_allow_html=True)

@st.cache_data
def load_data():
    return load_processed()

df = load_data()

# ---------------------------------------------------------------------------
# State Management
# ---------------------------------------------------------------------------
if "scenario_run" not in st.session_state:
    st.session_state.scenario_run = False
if "scenario_results" not in st.session_state:
    st.session_state.scenario_results = None

def reset_scenario():
    st.session_state.scenario_run = False

# ---------------------------------------------------------------------------
# Main Layout
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([1.1, 1], gap="large")

with col_left:
    st.markdown('<div class="ss-slider-section">', unsafe_allow_html=True)
    
    # Title & Reset
    header_col, reset_col = st.columns([3, 1])
    with header_col:
        st.markdown(section_header_html('Adjust Student Factors', subtitle='Move the sliders to create a new scenario', icon_name='sliders'), unsafe_allow_html=True)
    with reset_col:
        st.write("") # spacer
        if st.button("Reset to current", type="secondary", use_container_width=True):
            reset_scenario()
            st.rerun()
            
    baseline_idx = st.selectbox(
        "Base student",
        range(len(df)),
        format_func=lambda i: f"Student {i+1} (actual: {df.iloc[i]['Class']})",
        key="whatif_student",
        on_change=reset_scenario
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
            
    with st.expander("Fixed Characteristics (Not Adjustable)"):
        display_fixed = {friendly(k, cfg): v for k, v in fixed_features.items()}
        f_cols = st.columns(3)
        for i, (name, val) in enumerate(display_fixed.items()):
            f_cols[i % 3].markdown(
                f'<p style="font-size:0.8125rem;margin:0.15rem 0;">'
                f'<span style="color:var(--ink-muted);">{name}</span><br>'
                f'<strong style="color:var(--ink);">{val}</strong></p>',
                unsafe_allow_html=True,
            )
            
    st.divider()
    
    def render_slider_header(label, sublabel, icon_name, color_var):
        st.markdown(f'''
        <div class="ss-slider-row" style="margin-bottom:4px; margin-top: 16px;">
          <div class="ss-slider-icon-wrap" style="background:var(--{color_var}-soft);">
            {icon(icon_name, 18, f"var(--{color_var})")}
          </div>
          <div>
            <div class="ss-slider-label" style="min-width:auto;">{label}</div>
            <div class="ss-slider-sublabel">{sublabel}</div>
          </div>
        </div>
        ''', unsafe_allow_html=True)
        
    slider_values = {}
    
    # 1. Attendance (%) — icon calendar, TEAL color
    original_absence = str(baseline_row["StudentAbsenceDays"])
    render_slider_header('Attendance (%)', 'StudentAbsenceDays (Under-7 = 100, Above-7 = 40 proxy)', 'calendar', 'teal')
    slider_values["StudentAbsenceDays"] = st.selectbox(
        "Attendance", ["Under-7", "Above-7"],
        index=0 if original_absence == "Under-7" else 1,
        key="whatif_absence", label_visibility="collapsed", on_change=reset_scenario
    )
    
    # 2. Participation (%) — icon users, AMBER
    render_slider_header('Participation (%)', 'raisedhands', 'users', 'amber')
    slider_values["raisedhands"] = st.slider(
        "Participation", 0, 100, int(baseline_row["raisedhands"]),
        key="whatif_raisedhands", label_visibility="collapsed", on_change=reset_scenario
    )
    
    # 3. Learning Resources — icon book, PURPLE
    render_slider_header('Learning Resources', 'VisITedResources', 'book', 'purple')
    slider_values["VisITedResources"] = st.slider(
        "Learning Resources", 0, 100, int(baseline_row["VisITedResources"]),
        key="whatif_visited", label_visibility="collapsed", on_change=reset_scenario
    )
    
    # 4. Discussion Activity — icon users, CORAL
    render_slider_header('Discussion Activity', 'Discussion', 'users', 'coral')
    slider_values["Discussion"] = st.slider(
        "Discussion Activity", 0, 100, int(baseline_row["Discussion"]),
        key="whatif_discussion", label_visibility="collapsed", on_change=reset_scenario
    )
    
    # 5. Previous Performance (%) — icon chart, GREEN
    render_slider_header('Previous Performance (%)', 'AnnouncementsView', 'chart', 'green')
    slider_values["AnnouncementsView"] = st.slider(
        "Previous Performance", 0, 100, int(baseline_row["AnnouncementsView"]),
        key="whatif_announcements", label_visibility="collapsed", on_change=reset_scenario
    )
    
    with st.expander("Advanced Options"):
        original_survey = str(baseline_row["ParentAnsweringSurvey"])
        st.markdown('<p style="font-size:0.875rem;font-weight:600;margin-bottom:8px;">Parent Answering Survey</p>', unsafe_allow_html=True)
        slider_values["ParentAnsweringSurvey"] = st.selectbox(
            "Parent Answering Survey", ["Yes", "No"],
            index=0 if original_survey == "Yes" else 1,
            key="whatif_survey", label_visibility="collapsed", on_change=reset_scenario
        )
        
    st.write("")
    if st.button("▶ Run Scenario Analysis", type="primary", use_container_width=True):
        st.session_state.scenario_run = True
        student_data = {**fixed_features, **slider_values}
        st.session_state.pred_scenario = predict_one(student_data, cfg=cfg)
        
        # Calculate baseline
        st.session_state.pred_baseline = predict_one(
            {c: (int(baseline_row[c]) if c in cfg["data"]["numeric_features"] else str(baseline_row[c])) for c in feature_columns(cfg)},
            cfg=cfg
        )
        
        # Track changes
        changes = []
        for feat in ["raisedhands", "VisITedResources", "Discussion", "AnnouncementsView"]:
            old = int(baseline_row[feat])
            new = slider_values[feat]
            if old != new:
                changes.append((friendly(feat, cfg), old, new, new - old))
        if str(baseline_row["StudentAbsenceDays"]) != slider_values["StudentAbsenceDays"]:
            changes.append((friendly("StudentAbsenceDays", cfg), baseline_row["StudentAbsenceDays"], slider_values["StudentAbsenceDays"], None))
        if str(baseline_row["ParentAnsweringSurvey"]) != slider_values["ParentAnsweringSurvey"]:
            changes.append((friendly("ParentAnsweringSurvey", cfg), baseline_row["ParentAnsweringSurvey"], slider_values["ParentAnsweringSurvey"], None))
        st.session_state.changes_made = changes

    st.markdown(info_banner("This uses the trained model to predict how your changes may affect the outcome."), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown(section_header_html('Prediction Result', subtitle='See how your changes affect the predicted performance', icon_name='target'), unsafe_allow_html=True)
    
    baseline_pred = predict_one(
        {c: (int(baseline_row[c]) if c in cfg["data"]["numeric_features"] else str(baseline_row[c])) for c in feature_columns(cfg)},
        cfg=cfg
    )
    
    if not st.session_state.scenario_run:
        # Show baseline only
        st.markdown(prediction_card_html(
            baseline_pred["predicted_class"],
            baseline_pred["predicted_label"],
            baseline_pred.get("confidence", 0),
            baseline_pred.get("probabilities", {})
        ), unsafe_allow_html=True)
        
    else:
        # Show compare card
        prediction = st.session_state.pred_scenario
        baseline_pred = st.session_state.pred_baseline
        changes_made = st.session_state.changes_made
        
        def generate_prob_grid(probs, predicted_class):
            return f"""
            <div class="ss-prob-grid" style="margin-top:12px;">
              <div class="ss-prob-cell {'ss-prob-cell-low' if predicted_class=='L' else ''}" style="{'' if predicted_class=='L' else 'border-color:var(--line);background:var(--surface);'}">
                <div class="ss-prob-cell-val" style="{'' if predicted_class=='L' else 'color:var(--ink-sec);'}">{probs.get('L',0):.0%}</div>
                <div class="ss-prob-cell-label">Low</div>
              </div>
              <div class="ss-prob-cell {'ss-prob-cell-med' if predicted_class=='M' else ''}" style="{'' if predicted_class=='M' else 'border-color:var(--line);background:var(--surface);'}">
                <div class="ss-prob-cell-val" style="{'' if predicted_class=='M' else 'color:var(--ink-sec);'}">{probs.get('M',0):.0%}</div>
                <div class="ss-prob-cell-label">Medium</div>
              </div>
              <div class="ss-prob-cell {'ss-prob-cell-high' if predicted_class=='H' else ''}" style="{'' if predicted_class=='H' else 'border-color:var(--line);background:var(--surface);'}">
                <div class="ss-prob-cell-val" style="{'' if predicted_class=='H' else 'color:var(--ink-sec);'}">{probs.get('H',0):.0%}</div>
                <div class="ss-prob-cell-label">High</div>
              </div>
            </div>
            """
            
        bc = baseline_pred["predicted_class"]
        bl = baseline_pred["predicted_label"]
        b_conf = baseline_pred.get("confidence", 0)
        b_probs = baseline_pred.get("probabilities", {})
        
        pc = prediction["predicted_class"]
        pl = prediction["predicted_label"]
        p_conf = prediction.get("confidence", 0)
        p_probs = prediction.get("probabilities", {})
        
        c_map = {"H": "green", "M": "amber", "L": "coral"}
        bc_color = c_map.get(bc, "accent")
        pc_color = c_map.get(pc, "accent")
        
        compare_html = f"""
        <div class="ss-compare-grid">
          <div class="ss-compare-card">
            <div class="ss-compare-label">Current Profile</div>
            <div class="ss-compare-sublabel">Baseline</div>
            <div class="ss-pred-class-{bc_color.lower()}" style="font-size:2rem;">{bl}</div>
            <div class="ss-pred-conf">{b_conf:.0%} confidence</div>
            {generate_prob_grid(b_probs, bc)}
          </div>
          <div class="ss-compare-arrow">→</div>
          <div class="ss-compare-card" style="border-color:var(--accent-bdr); box-shadow:var(--shadow-md);">
            <div class="ss-compare-label">Your Scenario</div>
            <div class="ss-compare-sublabel">Predicted</div>
            <div class="ss-pred-class-{pc_color.lower()}" style="font-size:2rem;">{pl}</div>
            <div class="ss-pred-conf">{p_conf:.0%} confidence</div>
            {generate_prob_grid(p_probs, pc)}
          </div>
        </div>
        """
        st.markdown(compare_html, unsafe_allow_html=True)
        
        rank = ["L", "M", "H"]
        if rank.index(pc) > rank.index(bc):
            st.markdown(f"""
            <div class="ss-positive-change">
              <div style="color:var(--green);margin-top:2px;">{icon('check-circle', 18)}</div>
              <div class="ss-positive-change-text">
                <strong>Outcome Improved!</strong> The predicted performance jumped to {pl}.
              </div>
            </div>
            """, unsafe_allow_html=True)
        elif rank.index(pc) < rank.index(bc):
            st.markdown(f"""
            <div class="ss-warning-banner">
              <div style="color:var(--amber);margin-top:2px;">{icon('info', 18)}</div>
              <div class="ss-warning-banner-text">
                <strong>Outcome Declined.</strong> The predicted performance dropped to {pl}.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ss-info-banner">
              <div style="color:var(--accent);margin-top:2px;">{icon('info', 18)}</div>
              <div class="ss-info-banner-text">
                The performance band remained <strong>{pl}</strong>, though underlying probabilities may have shifted.
              </div>
            </div>
            """, unsafe_allow_html=True)

if st.session_state.scenario_run:
    st.markdown('<div style="margin-top:32px;"></div>', unsafe_allow_html=True)
    
    st.markdown(section_header_html("Performance Probability Comparison", icon_name="chart"), unsafe_allow_html=True)
    
    probs = st.session_state.pred_scenario.get("probabilities", {})
    baseline_probs = st.session_state.pred_baseline.get("probabilities", {})
    
    fig = go.Figure()
    for cls in ["L", "M", "H"]:
        fig.add_trace(go.Bar(
            x=[class_label(cls, cfg)],
            y=[baseline_probs.get(cls, 0) * 100],
            name="Current Profile",
            marker_color=CHART_GRAY,
            opacity=0.6,
            showlegend=(cls == "L"),
            legendgroup="original",
        ))

    for cls in ["L", "M", "H"]:
        color = ACCENT if cls == st.session_state.pred_scenario["predicted_class"] else CHART_DARK
        fig.add_trace(go.Bar(
            x=[class_label(cls, cfg)],
            y=[probs.get(cls, 0) * 100],
            name="Your Scenario",
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
        height=320,
        yaxis=dict(title="Probability (%)", range=[0, 110], showgrid=True, gridcolor="#E7E0D1"),
        margin=dict(t=30, b=40, l=40, r=20),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    
    st.write("")
    
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(section_header_html("Key Insights from This Scenario", icon_name="bulb"), unsafe_allow_html=True)
        if not st.session_state.changes_made:
            st.markdown(insight_card("info", "No Changes Made", "You ran the scenario without altering any parameters. Try adjusting the sliders above.", icon_bg="var(--surface-alt)", icon_color="var(--ink-muted)"), unsafe_allow_html=True)
        else:
            for name, old, new, diff in st.session_state.changes_made[:3]:
                if diff is not None:
                    dir_word = "Increased" if diff > 0 else "Decreased"
                    st.markdown(insight_card("activity", f"{dir_word} {name}", f"Changing {name} by {abs(diff)} points influenced the model's confidence in the outcome.", icon_bg="var(--accent-soft)", icon_color="var(--accent)"), unsafe_allow_html=True)
                else:
                    st.markdown(insight_card("activity", f"Changed {name}", f"Updated {name} from {old} to {new}, shifting the baseline characteristics.", icon_bg="var(--accent-soft)", icon_color="var(--accent)"), unsafe_allow_html=True)
                    
    with c2:
        st.markdown(section_header_html("Next Steps", icon_name="check-circle"), unsafe_allow_html=True)
        st.markdown(next_steps_html([
            "Set realistic improvement goals.",
            "Focus on the top 2-3 impact areas.",
            "Keep tracking progress over time.",
            "Use the Class Insights page to see broader impact."
        ]), unsafe_allow_html=True)

st.markdown(
    footnote(
        "Explore Improvements · What-If Simulation · Model-based Sensitivity · Demographic attributes frozen"
    ),
    unsafe_allow_html=True,
)

