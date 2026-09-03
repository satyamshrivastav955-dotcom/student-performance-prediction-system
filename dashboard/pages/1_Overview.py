"""
Overview page — dataset stats, class distribution, key factors.

This page directly addresses Module 4 of the brief: "display predicted scores,
student comparison, subject-wise analysis, performance trends."
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
import plotly.express as px
import plotly.graph_objects as go

from src.data.preprocess import load_processed
from src.utils.config import load_config, class_label, friendly
from theme import (
    inject_theme, page_hero, hero_stat, stat_card,
    class_breakdown_bars, section_heading,
    ACCENT, CHART_GRAY, CHART_DARK, CLASS_COLORS, PLOTLY_BASE,
    INK, INK_SEC, INK_MUTED, BORDER, SURFACE,
)

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")
inject_theme()

cfg = load_config()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    return load_processed()

df = load_data()

# ---------------------------------------------------------------------------
# Page hero
# ---------------------------------------------------------------------------
st.markdown(page_hero(
    "Overview",
    "Dataset statistics and the key factors that predict student performance."
), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hero stat + supporting metrics
# ---------------------------------------------------------------------------
n_students = len(df)
n_features = (
    len(cfg["data"]["numeric_features"])
    + len(cfg["data"]["nominal_features"])
    + len(cfg["data"]["binary_features"])
)
majority_class = df["Class"].value_counts().idxmax()
majority_label = class_label(majority_class, cfg)

# Hero: total students as the headline editorial number
st.markdown(hero_stat(
    value=f"{n_students:,}",
    label="Students in dataset",
    note=(
        "xAPI-Edu-Data — real engagement data from a learning management system. "
        "Three performance bands: High, Medium, and Low."
    ),
), unsafe_allow_html=True)

# Supporting stats in a 3-column row
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(stat_card("Input features", str(n_features),
                           "Engagement counters + demographics", delay=1),
                unsafe_allow_html=True)
with c2:
    st.markdown(stat_card("Performance classes", "3",
                           "High · Medium · Low", delay=2),
                unsafe_allow_html=True)
with c3:
    st.markdown(stat_card("Majority class", majority_label,
                           "Largest group in the dataset", delay=3),
                unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# Class distribution
# ---------------------------------------------------------------------------
st.markdown(section_heading("Performance Distribution"), unsafe_allow_html=True)

class_counts_series = df["Class"].value_counts().reindex(["H", "M", "L"])
class_counts_dict   = class_counts_series.to_dict()

col_chart, col_stats = st.columns([3, 1])

with col_chart:
    # Accent for High, gray scale for M and L
    bar_colors = [CLASS_COLORS.get(c, CHART_GRAY) for c in ["H", "M", "L"]]
    fig = go.Figure(go.Bar(
        x=[class_label(c, cfg) for c in ["H", "M", "L"]],
        y=class_counts_series.values,
        marker_color=bar_colors,
        text=[str(v) for v in class_counts_series.values],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono, monospace", size=12, color=INK_SEC),
    ))
    fig.update_layout(
        **PLOTLY_BASE,
        showlegend=False,
        yaxis=dict(showgrid=True, gridcolor="#EBEBEA", gridwidth=1,
                   tickfont=dict(size=12), linecolor="rgba(0,0,0,0)"),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        '<p class="spps-chart-caption">The dataset has an uneven class distribution: '
        'Medium is the largest group, followed by High and Low. This is why we use '
        'stratified splitting and macro-F1 (which weights each class equally) rather '
        'than plain accuracy.</p>',
        unsafe_allow_html=True,
    )

with col_stats:
    st.markdown(
        '<p class="spps-stat-card-label" style="margin-top:0.25rem;">Class breakdown</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        class_breakdown_bars(class_counts_dict, n_students),
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Engagement metrics by performance band
# ---------------------------------------------------------------------------
st.markdown(section_heading("Engagement Metrics by Performance Band"), unsafe_allow_html=True)

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
    yaxis=dict(title="Average score", showgrid=True, gridcolor="#EBEBEA",
               tickfont=dict(size=12), linecolor="rgba(0,0,0,0)"),
)
st.plotly_chart(fig, use_container_width=True)
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
st.markdown(section_heading("Attendance and Parent Engagement"), unsafe_allow_html=True)

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
            family="Space Grotesk, sans-serif", size=13, color=INK_SEC
        )),
        xaxis=dict(title="Absence level", showgrid=False),
        yaxis=dict(title="% of students", showgrid=True, gridcolor="#EBEBEA"),
    )
    st.plotly_chart(fig, use_container_width=True)
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
            family="Space Grotesk, sans-serif", size=13, color=INK_SEC
        )),
        xaxis=dict(title="Parent answered survey", showgrid=False),
        yaxis=dict(title="% of students", showgrid=True, gridcolor="#EBEBEA"),
    )
    st.plotly_chart(fig, use_container_width=True)
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
st.markdown(section_heading("Performance by Subject"), unsafe_allow_html=True)

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
    xaxis=dict(title="% of students", showgrid=True, gridcolor="#EBEBEA"),
    yaxis=dict(showgrid=False, tickfont=dict(size=11)),
)
st.plotly_chart(fig, use_container_width=True)
st.markdown(
    '<p class="spps-chart-caption">Some subjects have a higher proportion of '
    'Low-performing students than others. This may reflect differences in the '
    'student populations taking each subject, not necessarily subject difficulty.</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Advanced: correlation heatmap
# ---------------------------------------------------------------------------
with st.expander("Advanced: Correlation Matrix"):
    numeric_df = df[numeric_features].copy()
    corr = numeric_df.corr()

    fig = px.imshow(
        corr,
        x=[friendly(f, cfg) for f in numeric_features],
        y=[friendly(f, cfg) for f in numeric_features],
        color_continuous_scale=[
            [0.0, "#3D3D3D"],
            [0.5, "#F7F7F5"],
            [1.0, ACCENT],
        ],
        zmin=-1, zmax=1,
        aspect="auto",
    )
    fig.update_layout(
        **PLOTLY_BASE,
        height=380,
        coloraxis_colorbar=dict(tickfont=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        '<p class="spps-chart-caption">Correlation between engagement features. '
        'Hands raised and resource visits are moderately correlated; '
        'discussion posts are more independent.</p>',
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Statistical test results (if available)
# ---------------------------------------------------------------------------
from src.utils.config import get_path, load_json  # noqa: E402

stats_path = get_path("stats_file", cfg)
if stats_path.exists():
    with st.expander("Statistical Test Results (ANOVA & Chi-Square)"):
        stats = load_json(stats_path)
        sig_factors = stats.get("significant_factors", [])

        if sig_factors:
            st.markdown(
                '<p style="font-size:0.875rem;color:var(--ink-sec);">'
                '<strong>Statistically significant predictors</strong> '
                '(after Holm-Bonferroni correction):</p>',
                unsafe_allow_html=True,
            )
            sig_df = pd.DataFrame(sig_factors)
            if "feature" in sig_df.columns:
                sig_df["Feature"] = sig_df["feature"].apply(
                    lambda f: friendly(f, cfg)
                )
                display_cols = ["Feature"]
                if "test" in sig_df.columns:
                    display_cols.append("test")
                if "p_value_corrected" in sig_df.columns:
                    sig_df["p-value (corrected)"] = sig_df[
                        "p_value_corrected"
                    ].apply(lambda p: f"{p:.2e}" if p < 0.001 else f"{p:.4f}")
                    display_cols.append("p-value (corrected)")
                if "effect_size" in sig_df.columns:
                    sig_df["Effect Size"] = sig_df["effect_size"].round(3)
                    display_cols.append("Effect Size")
                if "effect_label" in sig_df.columns:
                    display_cols.append("effect_label")
                st.dataframe(
                    sig_df[display_cols],
                    use_container_width=True,
                    hide_index=True,
                )
            st.markdown(
                '<p class="spps-chart-caption">These features have a statistically '
                'significant relationship with student performance after correcting '
                'for multiple testing. Effect size indicates how strong the '
                'relationship is (small / medium / large).</p>',
                unsafe_allow_html=True,
            )
        else:
            st.info(
                "No statistically significant factors found "
                "(this is unusual — check the analysis)."
            )

st.markdown(
    '<p style="font-size:0.8rem;color:var(--ink-muted);font-family:var(--font-mono);">'
    'Data source: xAPI-Edu-Data (Amrieh, Hamtini &amp; Aljarah, 2016)'
    '</p>',
    unsafe_allow_html=True,
)
