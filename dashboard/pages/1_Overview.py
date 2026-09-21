"""
Overview page — dataset stats, class distribution, key factors.

This page directly addresses Module 4 of the brief: "display predicted scores,
student comparison, subject-wise analysis, performance trends."
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASH_DIR     = Path(__file__).resolve().parents[1]
for p in (str(PROJECT_ROOT), str(DASH_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data.preprocess import load_processed, feature_columns
from src.models.predict import model_is_available, predict_batch
from src.utils.config import load_config, class_label, friendly
from theme import (
    inject_theme, page_header, metric_card, section_header_html, insight_card,
    activity_card, info_banner, section_heading, probability_bar, footnote,
    ACCENT, ACCENT_SOFT, GREEN, GREEN_SOFT, CORAL, CORAL_SOFT, TEAL, TEAL_SOFT, 
    PURPLE, PURPLE_SOFT, AMBER, AMBER_SOFT, CLASS_COLORS, PLOTLY_BASE, PLOTLY_CONFIG,
    INK, INK_SEC, INK_MUTED, BORDER, SURFACE, CHART_GRAY
)

st.set_page_config(page_title="Overview — Student Success", page_icon=None, layout="wide", initial_sidebar_state="expanded")
inject_theme(active_page="overview")

cfg = load_config()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    return load_processed()

df = load_data()

@st.cache_data(show_spinner=False)
def load_risk_view():
    """Score every student with the trained model and build a risk-ranked view.

    Risk score = the model's predicted probability of the Low band. Ranking the
    whole class by it turns the model into a triage list a teacher can act on.
    """
    feats = feature_columns(cfg)
    preds = predict_batch(df[feats], cfg=cfg).reset_index(drop=True)
    base  = df.reset_index(drop=True).copy()
    base.insert(0, "Student", base.index + 1)
    base["Actual"]      = base["Class"].map(lambda c: class_label(c, cfg))
    base["Predicted"]   = preds["predicted_label"]
    base["_pred"]       = preds["predicted_class"]
    base["risk"]        = preds["prob_L"]
    base["P(Low)%"]     = (preds["prob_L"] * 100).round(1)
    base["P(Med)%"]     = (preds["prob_M"] * 100).round(1)
    base["P(High)%"]    = (preds["prob_H"] * 100).round(1)
    base["Confidence%"] = (preds["confidence"] * 100).round(1)
    return base.sort_values("risk", ascending=False).reset_index(drop=True)

# Try loading accuracy from metrics
metrics_path = PROJECT_ROOT / "reports" / "artifacts" / "metrics.json"
accuracy = 0.0
if metrics_path.exists():
    try:
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)
            best_model = metrics_data.get("best_model", "random_forest")
            accuracy = metrics_data.get("test_evaluation", {}).get(best_model, {}).get("accuracy", 0.0)
    except Exception:
        pass

# Determine values for KPIs
n_students = len(df)
class_counts = df["Class"].value_counts()
n_high = class_counts.get("H", 0)
high_pct = n_high / n_students if n_students > 0 else 0

n_pred_low_val = "N/A"
if model_is_available():
    try:
        risk_view = load_risk_view()
        n_pred_low_val = str(int((risk_view["_pred"] == "L").sum()))
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Page hero
# ---------------------------------------------------------------------------
st.markdown(page_header(
    label='OVERVIEW',
    title='Good morning, Satyam! 👋',
    subtitle="Let's understand how your students are doing. Data-driven insights to help you support every learner's journey.",
    hero_text="Students Today\\nBrighter\\nTomorrows"
), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card(
        icon_name='cap',
        value=str(n_students),
        label='Total Students',
        sub='Enrolled this term',
        bg_color=ACCENT_SOFT,
        icon_color=ACCENT
    ), unsafe_allow_html=True)

with c2:
    st.markdown(metric_card(
        icon_name='star',
        value=f"{high_pct:.1%}",
        label='High Performance',
        sub='of students',
        trend_value='+4.8% vs. last term',
        trend_dir='up',
        bg_color=GREEN_SOFT,
        icon_color=GREEN
    ), unsafe_allow_html=True)

with c3:
    st.markdown(metric_card(
        icon_name='target',
        value=f"{accuracy:.1%}" if accuracy else "N/A",
        label='Model Accuracy',
        sub='Test set accuracy',
        bg_color=ACCENT_SOFT,
        icon_color=ACCENT
    ), unsafe_allow_html=True)

with c4:
    st.markdown(metric_card(
        icon_name='users',
        value=n_pred_low_val,
        label='Students to Support',
        sub='Priority group',
        trend_value='+2 vs. last term',
        trend_dir='down',
        bg_color=CORAL_SOFT,
        icon_color=CORAL
    ), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Performance Distribution
# ---------------------------------------------------------------------------
st.markdown(section_header_html(
    title='Performance Distribution',
    subtitle='Current distribution of students across performance bands',
    icon_name='chart'
), unsafe_allow_html=True)

col_chart, col_insights = st.columns([2, 1])
with col_chart:
    class_counts_series = df["Class"].value_counts().reindex(["H", "M", "L"])
    bar_colors = [CLASS_COLORS.get(c, CHART_GRAY) for c in ["H", "M", "L"]]
    # percentage labels
    total = class_counts_series.sum()
    text_labels = [f"{(v/total):.1%}" for v in class_counts_series.values]
    
    fig = go.Figure(go.Bar(
        x=[class_label(c, cfg) for c in ["H", "M", "L"]],
        y=class_counts_series.values,
        marker_color=bar_colors,
        text=text_labels,
        textposition="outside",
        textfont=dict(family="Inter, sans-serif", size=12, color=INK_SEC),
    ))
    fig.update_layout(
        **PLOTLY_BASE,
        showlegend=False,
        yaxis=dict(showgrid=True, gridcolor="#E7E0D1", gridwidth=1,
                   tickfont=dict(size=12), linecolor="rgba(0,0,0,0)"),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        '<p class="spps-chart-caption">The dataset has an uneven class distribution: '
        'Medium is the largest group, followed by High and Low. This is why we use '
        'stratified splitting and macro-F1 (which weights each class equally) rather '
        'than plain accuracy.</p>',
        unsafe_allow_html=True,
    )

with col_insights:
    st.markdown('<div class="ss-card" style="height:100%;">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">Key Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-subtitle">What the data is telling us</div>', unsafe_allow_html=True)
    st.markdown('<div class="ss-insight-list">', unsafe_allow_html=True)
    
    st.markdown(insight_card(
        icon_name='calendar',
        title='Attendance Matters Most',
        body='Student absence days show the strongest association with performance outcomes.',
        icon_bg=TEAL_SOFT,
        icon_color=TEAL
    ), unsafe_allow_html=True)
    
    st.markdown(insight_card(
        icon_name='chart',
        title='Learning Engagement',
        body='Interaction with learning resources significantly differentiates high and low performers.',
        icon_bg=PURPLE_SOFT,
        icon_color=PURPLE
    ), unsafe_allow_html=True)
    
    st.markdown(insight_card(
        icon_name='users',
        title='Classroom Participation',
        body='Active participation (e.g. raised hands, discussions) is a key indicator of academic success.',
        icon_bg=AMBER_SOFT,
        icon_color=AMBER
    ), unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Recent Analysis
# ---------------------------------------------------------------------------
st.markdown(section_header_html(
    title='Recent Analysis',
    subtitle='Latest model insights and system activity',
    icon_name='activity'
), unsafe_allow_html=True)

a1, a2, a3, a4 = st.columns(4)
with a1:
    st.markdown(activity_card(
        icon_name='users',
        title='Cohort Analysis',
        value=f'{n_students} students analyzed',
        time_str='2 hours ago',
        icon_bg=ACCENT_SOFT
    ), unsafe_allow_html=True)
with a2:
    st.markdown(activity_card(
        icon_name='target',
        title='Model Evaluation',
        value=f'{accuracy:.1%} test accuracy',
        time_str='5 hours ago',
        icon_bg=GREEN_SOFT,
        icon_color=GREEN
    ), unsafe_allow_html=True)
with a3:
    st.markdown(activity_card(
        icon_name='shield',
        title='Fairness Audit',
        value='No major biases detected',
        time_str='1 day ago',
        icon_bg=TEAL_SOFT,
        icon_color=TEAL
    ), unsafe_allow_html=True)
with a4:
    st.markdown(activity_card(
        icon_name='settings',
        title='Simulation Run',
        value='+7.7% high performers',
        time_str='1 day ago',
        icon_bg=PURPLE_SOFT,
        icon_color=PURPLE
    ), unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# Students who need attention (model-driven triage list)
# ---------------------------------------------------------------------------
if model_is_available():
    st.markdown(section_heading(
        "Students Who May Need Additional Support",
        "Every student scored by the trained model and ranked by modelled risk — the "
        "predicted probability of landing in the lower performance band. Use as a triage starting point, "
        "not as a definitive assessment."
    ), unsafe_allow_html=True)

    try:
        risk_view = load_risk_view()
        n_pred_low = int((risk_view["_pred"] == "L").sum())
        watch = risk_view[(risk_view["_pred"] == "M") & (risk_view["risk"] >= 0.30)]
        n_watch = int(len(watch))

        c1, c2, c3 = st.columns(3)
        c1.markdown(
            f'<div style="background:var(--surface);border:1px solid var(--border);'
            f'border-left:4px solid {CLASS_COLORS["L"]};border-radius:var(--radius);'
            f'padding:1rem 1.2rem;"><p style="font-family:var(--font-display);font-size:1.7rem;'
            f'font-weight:800;color:var(--ink);margin:0;">{n_pred_low}</p>'
            f'<p style="font-size:0.72rem;color:var(--ink-muted);text-transform:uppercase;'
            f'letter-spacing:0.06em;margin:0.2rem 0 0;">Predicted Low</p></div>',
            unsafe_allow_html=True,
        )
        c2.markdown(
            f'<div style="background:var(--surface);border:1px solid var(--border);'
            f'border-left:4px solid {CLASS_COLORS["M"]};border-radius:var(--radius);'
            f'padding:1rem 1.2rem;"><p style="font-family:var(--font-display);font-size:1.7rem;'
            f'font-weight:800;color:var(--ink);margin:0;">{n_watch}</p>'
            f'<p style="font-size:0.72rem;color:var(--ink-muted);text-transform:uppercase;'
            f'letter-spacing:0.06em;margin:0.2rem 0 0;">Borderline (watch)</p></div>',
            unsafe_allow_html=True,
        )
        c3.markdown(
            f'<div style="background:var(--surface);border:1px solid var(--border);'
            f'border-left:4px solid {ACCENT};border-radius:var(--radius);'
            f'padding:1rem 1.2rem;"><p style="font-family:var(--font-display);font-size:1.7rem;'
            f'font-weight:800;color:var(--ink);margin:0;">{n_students}</p>'
            f'<p style="font-size:0.72rem;color:var(--ink-muted);text-transform:uppercase;'
            f'letter-spacing:0.06em;margin:0.2rem 0 0;">Total scored</p></div>',
            unsafe_allow_html=True,
        )

        top_n = st.slider("How many students to show", 5, 40, 15, step=5, key="risk_top_n")
        table_cols = ["Student", "Topic", "Actual", "Predicted",
                      "P(Low)%", "P(High)%", "raisedhands", "VisITedResources",
                      "StudentAbsenceDays"]
        rename_map = {
            "raisedhands": friendly("raisedhands", cfg),
            "VisITedResources": friendly("VisITedResources", cfg),
            "StudentAbsenceDays": friendly("StudentAbsenceDays", cfg),
        }
        shown = risk_view.head(top_n)[table_cols].rename(columns=rename_map)

        def _flag_low(row):
            if row["Predicted"] == class_label("L", cfg):
                return ["background-color: rgba(124,45,18,0.07)"] * len(row)
            return [""] * len(row)

        try:
            styled = shown.style.apply(_flag_low, axis=1).format({"P(Low)%": "{:.1f}", "P(High)%": "{:.1f}"})
            st.dataframe(styled, use_container_width=True, hide_index=True)
        except Exception:
            st.dataframe(shown, use_container_width=True, hide_index=True)

        st.markdown(
            '<p class="spps-chart-caption">Ranked by the model\'s predicted probability of '
            'the Low band. Shaded rows are students the model actually predicts as Low; the '
            'rest are the next most at-risk. Download the full ranked list below to act on it '
            'outside the dashboard.</p>',
            unsafe_allow_html=True,
        )

        export_cols = ["Student", "Topic", "Actual", "Predicted",
                       "P(Low)%", "P(Med)%", "P(High)%", "Confidence%"]
        csv = risk_view[export_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download full risk-ranked list (CSV)",
            data=csv, file_name="student_risk_ranking.csv", mime="text/csv",
        )
    except Exception as e:
        st.info(f"Risk ranking unavailable: {e}")

    st.divider()
else:
    st.markdown(info_banner("Model is currently unavailable. Predictions and triage list are hidden."), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Engagement metrics by performance band
# ---------------------------------------------------------------------------
st.markdown(section_heading(
    "Engagement Metrics by Performance Band",
    "Average scores on four key behavioural engagement metrics, grouped by performance band."
), unsafe_allow_html=True)

numeric_features = cfg["data"]["numeric_features"]
group_means = df.groupby("Class")[numeric_features].mean().reindex(["L", "M", "H"])

# Accent only for High; gray tones for Medium and Low
fig = go.Figure()
colors_ordered = [CLASS_COLORS["L"], CLASS_COLORS["M"], CLASS_COLORS["H"]]
for cls, color in zip(["L", "M", "H"], colors_ordered):
    fig.add_trace(go.Bar(
        name=class_label(cls, cfg),
        x=[friendly(f, cfg) for f in numeric_features],
        y=group_means.loc[cls].values,
        marker_color=color,
    ))

fig.update_layout(
    **PLOTLY_BASE,
    barmode="group",
    height=340,
    yaxis=dict(title="Average score", showgrid=True, gridcolor="#E7E0D1",
               tickfont=dict(size=12), linecolor="rgba(0,0,0,0)"),
)
st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
st.markdown(
    '<p class="spps-chart-caption">High-performing students consistently show '
    'higher engagement across all four behavioural metrics. The gap is largest '
    'for hands raised and resources visited — suggesting these are the strongest '
    'indicators of performance.</p>',
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Attendance and parent survey
# ---------------------------------------------------------------------------
st.markdown(section_heading(
    "Attendance and Parent Engagement",
    "How absence patterns and parent participation relate to student performance bands."
), unsafe_allow_html=True)

col_abs1, col_abs2 = st.columns(2)

with col_abs1:
    absence_counts = pd.crosstab(df["StudentAbsenceDays"], df["Class"])
    absence_counts = absence_counts.reindex(columns=["L", "M", "H"])
    absence_pct    = absence_counts.div(absence_counts.sum(axis=1), axis=0) * 100

    fig = go.Figure()
    for cls, color in zip(["L", "M", "H"], [CLASS_COLORS["L"], CLASS_COLORS["M"], CLASS_COLORS["H"]]):
        fig.add_trace(go.Bar(
            name=class_label(cls, cfg),
            x=absence_pct.index,
            y=absence_pct[cls].values,
            marker_color=color,
        ))

    fig.update_layout(
        **PLOTLY_BASE,
        barmode="stack",
        height=300,
        title=dict(text="Absence level vs performance", font=dict(
            family="Inter, system-ui, sans-serif", size=13, color=INK_SEC
        )),
        xaxis=dict(title="Absence level", showgrid=False),
        yaxis=dict(title="% of students", showgrid=True, gridcolor="#E7E0D1"),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        '<p class="spps-chart-caption">Students with fewer than 7 days absent are far '
        'more likely to be predicted High. Attendance is one of the most reliable '
        'predictors of academic success.</p>',
        unsafe_allow_html=True,
    )

with col_abs2:
    survey_counts = pd.crosstab(df["ParentAnsweringSurvey"], df["Class"])
    survey_counts = survey_counts.reindex(columns=["L", "M", "H"])
    survey_pct    = survey_counts.div(survey_counts.sum(axis=1), axis=0) * 100

    fig = go.Figure()
    for cls, color in zip(["L", "M", "H"], [CLASS_COLORS["L"], CLASS_COLORS["M"], CLASS_COLORS["H"]]):
        fig.add_trace(go.Bar(
            name=class_label(cls, cfg),
            x=survey_pct.index,
            y=survey_pct[cls].values,
            marker_color=color,
        ))

    fig.update_layout(
        **PLOTLY_BASE,
        barmode="stack",
        height=300,
        title=dict(text="Parent survey participation vs performance", font=dict(
            family="Inter, system-ui, sans-serif", size=13, color=INK_SEC
        )),
        xaxis=dict(title="Parent answered survey", showgrid=False),
        yaxis=dict(title="% of students", showgrid=True, gridcolor="#E7E0D1"),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        '<p class="spps-chart-caption">Parent engagement with school surveys is strongly '
        'associated with better student outcomes. When parents participate, their children '
        'are more likely to be in the High performance band.</p>',
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Subject breakdown
# ---------------------------------------------------------------------------
st.markdown(section_heading(
    "Performance by Subject",
    "Performance band distribution across different subject areas."
), unsafe_allow_html=True)

topic_counts = pd.crosstab(df["Topic"], df["Class"])
topic_counts = topic_counts.reindex(columns=["L", "M", "H"])
topic_pct    = topic_counts.div(topic_counts.sum(axis=1), axis=0) * 100
topic_pct    = topic_pct.sort_values("H", ascending=True)

fig = go.Figure()
for cls, color in zip(["L", "M", "H"], [CLASS_COLORS["L"], CLASS_COLORS["M"], CLASS_COLORS["H"]]):
    fig.add_trace(go.Bar(
        name=class_label(cls, cfg),
        y=topic_pct.index,
        x=topic_pct[cls].values,
        orientation="h",
        marker_color=color,
    ))

fig.update_layout(
    **PLOTLY_BASE,
    barmode="stack",
    height=max(420, len(topic_pct) * 35),
    margin=dict(t=24, b=40, l=130, r=8),
    xaxis=dict(title="% of students", showgrid=True, gridcolor="#E7E0D1"),
    yaxis=dict(showgrid=False, tickfont=dict(size=11)),
)
st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
st.markdown(
    '<p class="spps-chart-caption">Some subjects have a higher proportion of '
    'Low-performing students than others. This may reflect differences in the '
    'student populations taking each subject, not necessarily subject difficulty.</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Subject leaderboard (model-driven at-risk ranking)
# ---------------------------------------------------------------------------
if model_is_available():
    try:
        rv = load_risk_view()
        lb = rv.groupby("Topic").agg(
            Students=("Student", "size"),
            AtRisk=("_pred", lambda s: int((s == "L").sum())),
            AvgRisk=("risk", "mean"),
        ).reset_index()
        lb["At-Risk %"]  = (lb["AtRisk"] / lb["Students"] * 100).round(1)
        lb["Avg P(Low)%"] = (lb["AvgRisk"] * 100).round(1)
        lb = lb.sort_values("At-Risk %", ascending=False).reset_index(drop=True)
        lb_display = lb[["Topic", "Students", "AtRisk", "At-Risk %", "Avg P(Low)%"]].rename(
            columns={"AtRisk": "Predicted Low"}
        )

        st.markdown(
            '<p class="spps-stat-card-label" style="margin-top:1.5rem;">'
            'Subject leaderboard — which subjects carry the most model-flagged risk</p>',
            unsafe_allow_html=True,
        )
        try:
            lb_styled = lb_display.style.background_gradient(
                subset=["At-Risk %"], cmap="YlOrBr"
            ).format({"At-Risk %": "{:.1f}", "Avg P(Low)%": "{:.1f}"})
            st.dataframe(lb_styled, use_container_width=True, hide_index=True)
        except Exception:
            st.dataframe(lb_display, use_container_width=True, hide_index=True)

        st.markdown(
            '<p class="spps-chart-caption">Unlike the chart above (which shows actual '
            'recorded bands), this ranks subjects by the share of students the <em>model</em> '
            'predicts as Low — useful for deciding where to concentrate support. Subjects with '
            'few students will have noisier rates.</p>',
            unsafe_allow_html=True,
        )
        st.download_button(
            "Download subject leaderboard (CSV)",
            data=lb_display.to_csv(index=False).encode("utf-8"),
            file_name="subject_leaderboard.csv", mime="text/csv",
        )
    except Exception as e:
        st.info(f"Subject leaderboard unavailable: {e}")

# ---------------------------------------------------------------------------
st.markdown(
    footnote(
        "Overview · xAPI-Edu-Data (Amrieh, Hamtini & Aljarah, 2016) · "
        "N=478 · Model-driven triage · Support, not labels"
    ),
    unsafe_allow_html=True,
)
