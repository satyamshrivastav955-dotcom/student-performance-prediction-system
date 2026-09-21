"""
Cohort Analytics page — polished analytical presentation of the historical cohort.

Six evidence-based charts drawn from real data:
  1. Performance Distribution
  2. Student Absence vs Performance
  3. Engagement vs Participation (scatter)
  4. Effect Size of Continuous Factors (ANOVA eta-squared)
  5. Categorical Factor Association (Cramér's V)
  6. Correlation Heatmap (behavioural variables)

Educational language throughout — no causality claimed, no stigmatising labels.
Data source: xAPI-Edu-Data (Amrieh, Hamtini & Aljarah, 2016), N=478.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASH_DIR     = Path(__file__).resolve().parents[1]
for p in (str(PROJECT_ROOT), str(DASH_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data.preprocess import load_processed, feature_columns
from src.utils.config import load_config, class_label, friendly
from theme import (
    inject_theme, page_hero, kpi_hero_row, section_heading,
    analytics_card_header, analytics_card_takeaway, takeaway_box,
    ui_error_state, ui_info_banner,
    CLASS_COLORS, PLOTLY_BASE, PLOTLY_CONFIG,
    ACCENT, CHART_GRAY, CHART_DARK, INK, INK_SEC, INK_MUTED, BORDER, SURFACE,
    FOREST, BRASS, CLAY, footnote,
)

st.set_page_config(
    page_title="Analytics — Cohort Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme(active_page="analytics")

cfg = load_config()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    return load_processed()

@st.cache_data
def load_stats():
    p = PROJECT_ROOT / "reports" / "artifacts" / "statistical_tests.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}

df   = load_data()
stats = load_stats()

# ---------------------------------------------------------------------------
# Page hero
# ---------------------------------------------------------------------------
st.markdown(page_hero(
    "Cohort Analytics",
    "Understand the patterns behind student performance. "
    "Every chart connects to real data from the 478-student historical cohort."
), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
n_total  = len(df)
cc       = df["Class"].value_counts()
n_high   = int(cc.get("H", 0))
n_med    = int(cc.get("M", 0))
n_low    = int(cc.get("L", 0))

st.markdown(kpi_hero_row([
    {"icon": "users", "value": str(n_total),  "label": "Total Students", "trend": "xAPI-Edu-Data · historical cohort"},
    {"icon": "seal",  "value": f"{n_high/n_total:.1%}", "label": "High Performers",   "blue": True, "trend": f"{n_high} students"},
    {"icon": "ledger","value": f"{n_med/n_total:.1%}",  "label": "Medium Performers", "trend": f"{n_med} students"},
    {"icon": "book",  "value": f"{n_low/n_total:.1%}",  "label": "Need Extra Support","trend": f"{n_low} students"},
]), unsafe_allow_html=True)

st.markdown(
    ui_info_banner(
        "These charts describe associations in historical data from 478 students. "
        "Association does not imply causation. Use these insights to support students, not to label them."
    ),
    unsafe_allow_html=True,
)

st.divider()

# ============================================================
# Row 1: Performance Distribution | Absence vs Performance
# ============================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        analytics_card_header(
            "Performance Distribution",
            "Distribution of students across predicted performance bands."
        ),
        unsafe_allow_html=True,
    )
    class_counts = df["Class"].value_counts().reindex(["H", "M", "L"])
    bar_colors   = [CLASS_COLORS.get(c, CHART_GRAY) for c in ["H", "M", "L"]]
    labels_disp  = [class_label(c, cfg) for c in ["H", "M", "L"]]
    pcts         = [class_counts[c] / n_total * 100 for c in ["H", "M", "L"]]
    fig = go.Figure(go.Bar(
        x=labels_disp,
        y=[class_counts[c] for c in ["H", "M", "L"]],
        marker_color=bar_colors,
        text=[f"{p:.1f}%" for p in pcts],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono, monospace", size=12, color=INK_SEC),
        hovertemplate="%{x}: %{y} students<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_BASE, showlegend=False, height=300,
        margin=dict(t=10, b=40, l=8, r=8),
        yaxis=dict(title="Number of students", showgrid=True, gridcolor="#E7E0D1"),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        analytics_card_takeaway(
            f"Medium is the largest group ({n_med/n_total:.1%}), followed by High ({n_high/n_total:.1%}) "
            f"and students needing extra support ({n_low/n_total:.1%}). "
            "This uneven distribution is why we optimise for macro-F1 rather than plain accuracy."
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        analytics_card_header(
            "Student Absence vs Performance",
            "Proportion of students with ≤7 and >7 absence days across performance bands."
        ),
        unsafe_allow_html=True,
    )
    abs_ct  = pd.crosstab(df["StudentAbsenceDays"], df["Class"]).reindex(columns=["L", "M", "H"])
    abs_pct = abs_ct.div(abs_ct.sum(axis=1), axis=0) * 100

    fig = go.Figure()
    for cls in ["L", "M", "H"]:
        fig.add_trace(go.Bar(
            name=class_label(cls, cfg),
            x=abs_pct.index,
            y=abs_pct[cls].values,
            marker_color=CLASS_COLORS[cls],
            text=[f"{v:.0f}%" for v in abs_pct[cls].values],
            textposition="inside",
            textfont=dict(family="IBM Plex Mono, monospace", size=11, color="#FFFFFF"),
            hovertemplate=f"{class_label(cls, cfg)}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        **PLOTLY_BASE, barmode="stack", height=300,
        margin=dict(t=10, b=40, l=8, r=8),
        xaxis=dict(title="Absence days", showgrid=False),
        yaxis=dict(title="% of students", showgrid=True, gridcolor="#E7E0D1"),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    # Get chi-square Cramér's V for absence from stats
    abs_v = None
    if stats and "chi_square" in stats:
        abs_v = stats["chi_square"].get("StudentAbsenceDays", {}).get("cramer_v")
    cv_str = f" (Cramér's V = {abs_v:.3f})" if abs_v else ""
    st.markdown(
        analytics_card_takeaway(
            f"Higher absence is strongly associated with lower performance{cv_str}. "
            "Students in the low-absence category show a markedly different performance pattern."
        ),
        unsafe_allow_html=True,
    )

st.divider()

# ============================================================
# Row 2: Engagement Scatter | Effect Size
# ============================================================
col3, col4 = st.columns(2)

with col3:
    st.markdown(
        analytics_card_header(
            "Engagement vs Participation",
            "Relationship between learning resource usage and class participation, coloured by performance band."
        ),
        unsafe_allow_html=True,
    )
    scatter_df = df[["VisITedResources", "raisedhands", "Class"]].copy()
    scatter_df["Band"] = scatter_df["Class"].map({"H": "High", "M": "Medium", "L": "Needs Support"})
    color_map = {"High": FOREST, "Medium": BRASS, "Needs Support": CLAY}
    fig = px.scatter(
        scatter_df,
        x="VisITedResources",
        y="raisedhands",
        color="Band",
        color_discrete_map=color_map,
        labels={
            "VisITedResources": "Learning Resources Opened",
            "raisedhands": "Hands Raised in Class",
        },
        opacity=0.65,
        height=300,
    )
    fig.update_traces(marker=dict(size=6))
    fig.update_layout(
        **PLOTLY_BASE,
        margin=dict(t=10, b=40, l=8, r=8),
        legend=dict(orientation="h", y=-0.28, font=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    # Get ANOVA eta-squared for both features
    rh_eta  = stats.get("anova", {}).get("raisedhands", {}).get("eta_squared", None) if stats else None
    vr_eta  = stats.get("anova", {}).get("VisITedResources", {}).get("eta_squared", None) if stats else None
    eta_str = ""
    if rh_eta and vr_eta:
        eta_str = f" (η² = {vr_eta:.3f} and {rh_eta:.3f} respectively)"
    st.markdown(
        analytics_card_takeaway(
            f"Students who visit more resources and participate more in class tend to perform in higher bands{eta_str}. "
            "Each point represents one student. The clustering by colour suggests these two behaviours are informative predictors."
        ),
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        analytics_card_header(
            "Effect Size of Continuous Factors",
            "ANOVA effect size (η²) for each continuous behavioural variable. Larger = stronger association with performance."
        ),
        unsafe_allow_html=True,
    )
    anova_data = stats.get("anova", {}) if stats else {}
    effect_rows = []
    for feat, val in anova_data.items():
        eta = val.get("eta_squared")
        lbl = val.get("effect_size_label", "")
        fname = val.get("friendly_name", friendly(feat, cfg))
        if eta is not None:
            effect_rows.append({"Feature": fname, "η²": eta, "Effect": lbl, "_raw": feat})

    if effect_rows:
        eff_df = pd.DataFrame(effect_rows).sort_values("η²", ascending=True)
        # Color by effect size label
        color_map_eff = {"large": FOREST, "medium": BRASS, "small": CHART_GRAY}
        bar_colors_eff = [color_map_eff.get(r, CHART_GRAY) for r in eff_df["Effect"]]
        fig = go.Figure(go.Bar(
            y=eff_df["Feature"],
            x=eff_df["η²"],
            orientation="h",
            marker_color=bar_colors_eff,
            text=[f"{v:.3f}" for v in eff_df["η²"]],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=11),
            hovertemplate="%{y}: η² = %{x:.3f}<extra></extra>",
        ))
        fig.update_layout(
            **PLOTLY_BASE, height=300,
            margin=dict(t=10, b=40, l=150, r=50),
            xaxis=dict(title="η² (ANOVA effect size)", range=[0, max(eff_df["η²"]) * 1.25],
                       showgrid=True, gridcolor="#E7E0D1"),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        top_feat = eff_df.iloc[-1]["Feature"] if not eff_df.empty else "Learning resources"
        top_eta  = eff_df.iloc[-1]["η²"] if not eff_df.empty else 0
        st.markdown(
            analytics_card_takeaway(
                f"{top_feat} shows the largest effect size (η² = {top_eta:.3f}), meaning it explains the most variance "
                "in performance bands among continuous factors. Large effect = strong statistical association."
            ),
            unsafe_allow_html=True,
        )
    else:
        st.info("Effect size data not available. Run the analysis pipeline to generate statistical_tests.json.")

st.divider()

# ============================================================
# Row 3: Categorical Association | Correlation Heatmap
# ============================================================
col5, col6 = st.columns(2)

with col5:
    st.markdown(
        analytics_card_header(
            "Categorical Factor Association",
            "Cramér's V for categorical variables vs performance band. Ranges 0 (no association) to 1 (perfect)."
        ),
        unsafe_allow_html=True,
    )
    chi_data = stats.get("chi_square", {}) if stats else {}
    cat_rows = []
    for feat, val in chi_data.items():
        cv   = val.get("cramer_v")
        lbl  = val.get("effect_size_label", "")
        fname = val.get("friendly_name", friendly(feat, cfg))
        if cv is not None:
            cat_rows.append({"Feature": fname, "Cramér's V": cv, "Effect": lbl, "_raw": feat})

    if cat_rows:
        cat_df = pd.DataFrame(cat_rows).sort_values("Cramér's V", ascending=True)
        color_map_cat = {"large": FOREST, "medium": BRASS, "small": CHART_GRAY}
        bar_colors_cat = [color_map_cat.get(r, CHART_GRAY) for r in cat_df["Effect"]]
        fig = go.Figure(go.Bar(
            y=cat_df["Feature"],
            x=cat_df["Cramér's V"],
            orientation="h",
            marker_color=bar_colors_cat,
            text=[f"{v:.3f}" for v in cat_df["Cramér's V"]],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=11),
            hovertemplate="%{y}: V = %{x:.3f}<extra></extra>",
        ))
        fig.update_layout(
            **PLOTLY_BASE, height=300,
            margin=dict(t=10, b=40, l=155, r=50),
            xaxis=dict(title="Cramér's V", range=[0, min(1.0, max(cat_df["Cramér's V"]) * 1.3)],
                       showgrid=True, gridcolor="#E7E0D1"),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        top_cat  = cat_df.iloc[-1]["Feature"] if not cat_df.empty else "Absence"
        top_cv   = cat_df.iloc[-1]["Cramér's V"] if not cat_df.empty else 0
        top_eff  = cat_df.iloc[-1]["Effect"] if not cat_df.empty else ""
        st.markdown(
            analytics_card_takeaway(
                f"{top_cat} shows the strongest categorical association with performance "
                f"(Cramér's V = {top_cv:.3f}, {top_eff} effect). "
                "These associations are statistically significant after Holm–Bonferroni correction."
            ),
            unsafe_allow_html=True,
        )
    else:
        st.info("Chi-square data not available. Run the analysis pipeline.")

with col6:
    st.markdown(
        analytics_card_header(
            "Correlation Heatmap (Behavioural Variables)",
            "Pearson correlation between key continuous features. Values near ±1 indicate strong linear association."
        ),
        unsafe_allow_html=True,
    )
    numeric_features = cfg["data"]["numeric_features"]
    numeric_df  = df[numeric_features].copy()
    corr        = numeric_df.corr()
    friendly_labels = [friendly(f, cfg) for f in numeric_features]
    fig = px.imshow(
        corr,
        x=friendly_labels,
        y=friendly_labels,
        color_continuous_scale=[
            [0.0, "#7C2D12"],
            [0.5, "#FAF8F3"],
            [1.0, FOREST],
        ],
        zmin=-1, zmax=1,
        aspect="auto",
        text_auto=".2f",
    )
    fig.update_traces(textfont=dict(family="IBM Plex Mono, monospace", size=11))
    fig.update_layout(
        **PLOTLY_BASE, height=300,
        margin=dict(t=10, b=60, l=10, r=10),
        coloraxis_colorbar=dict(tickfont=dict(size=10), len=0.8),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        analytics_card_takeaway(
            "Resource usage, participation, and announcement views are moderately positively correlated, "
            "suggesting complementary learning behaviours. Discussion posts are more independent. "
            "High correlations between features can affect model interpretation."
        ),
        unsafe_allow_html=True,
    )

st.divider()

# ============================================================
# Key Takeaways section
# ============================================================
st.markdown(section_heading(
    "Key Takeaways",
    f"Patterns observed across {n_total} students in the historical cohort."
), unsafe_allow_html=True)

takeaways = [
    ("Attendance and engagement are strong indicators",
     "Absence days and learning resource usage show the strongest statistical associations with "
     "performance band, both in ANOVA effect sizes and Cramér's V."),
    ("Multiple factors contribute to outcomes",
     "No single factor tells the whole story. The model combines behavioural, attendance, and "
     "family-engagement signals to form its predictions."),
    ("These are associations, not causes",
     "These patterns are drawn from historical data, not a controlled study. They suggest where to "
     "focus support, not that a single action will definitively change an outcome."),
    ("Use to support, not to label",
     "These insights are designed to help educators identify where additional support may be most "
     "beneficial — not to categorise or stigmatise students."),
]

t_cols = st.columns(2)
for i, (title, body) in enumerate(takeaways):
    col = t_cols[i % 2]
    with col:
        col.markdown(
            f'<div class="spps-ledger-card" style="margin-bottom:0.75rem;">'
            f'<p style="font-family:var(--font-display);font-size:1rem;font-weight:600;'
            f'color:var(--ink);margin:0 0 0.3rem;">{title}</p>'
            f'<p style="font-size:0.84rem;color:var(--ink-sec);margin:0;line-height:1.6;">{body}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.divider()

# ============================================================
# Engagement by Band — detailed breakdown
# ============================================================
with st.expander("Detailed: Engagement Metrics by Performance Band"):
    group_means = df.groupby("Class")[numeric_features].mean().reindex(["L", "M", "H"])
    fig = go.Figure()
    for cls, color in zip(["L", "M", "H"], [CLASS_COLORS["L"], CLASS_COLORS["M"], CLASS_COLORS["H"]]):
        fig.add_trace(go.Bar(
            name=class_label(cls, cfg),
            x=[friendly(f, cfg) for f in numeric_features],
            y=group_means.loc[cls].values,
            marker_color=color,
            text=[f"{v:.1f}" for v in group_means.loc[cls].values],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=10),
        ))
    fig.update_layout(
        **PLOTLY_BASE, barmode="group", height=340,
        yaxis=dict(title="Mean score", showgrid=True, gridcolor="#E7E0D1"),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.caption(
        "Mean behavioural engagement scores across the three performance bands. "
        "All four metrics show a clear gradient from lower to higher performing bands."
    )

with st.expander("Detailed: Statistical Test Summary"):
    if stats:
        anova_rows = []
        for feat, val in stats.get("anova", {}).items():
            anova_rows.append({
                "Feature":    val.get("friendly_name", friendly(feat, cfg)),
                "Test":       "ANOVA / Kruskal-Wallis",
                "F-statistic": round(val.get("f_statistic", 0), 2),
                "η² (effect)": round(val.get("eta_squared", 0), 4),
                "Effect size": val.get("effect_size_label", ""),
                "Significant": "✓" if val.get("significant") else "—",
            })
        chi_rows = []
        for feat, val in stats.get("chi_square", {}).items():
            chi_rows.append({
                "Feature":    val.get("friendly_name", friendly(feat, cfg)),
                "Test":       "Chi-square",
                "Cramér's V": round(val.get("cramer_v", 0), 4),
                "Effect size": val.get("effect_size_label", ""),
                "Significant": "✓" if val.get("significant") else "—",
            })
        if anova_rows:
            st.markdown("**Continuous features (ANOVA)**")
            st.dataframe(pd.DataFrame(anova_rows), use_container_width=True, hide_index=True)
        if chi_rows:
            st.markdown("**Categorical features (Chi-square)**")
            st.dataframe(pd.DataFrame(chi_rows), use_container_width=True, hide_index=True)
        st.caption(f"Correction: {stats.get('correction','Holm')} · α = {stats.get('alpha', 0.05)}")
    else:
        st.info("Statistical tests data not available.")

st.markdown(
    footnote(
        "Cohort Analytics · xAPI-Edu-Data (Amrieh, Hamtini & Aljarah, 2016) · "
        "N=478 · Classical ML only · Associations, not causations"
    ),
    unsafe_allow_html=True,
)
