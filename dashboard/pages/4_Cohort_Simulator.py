"""
Cohort Simulator page — Monte Carlo simulation of class-wide interventions.

This reframes the tool from per-student to policy-level decision support:
"If the whole class improved participation by 15%, how many would move
from Low to Medium?"
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

from src.models.predict import model_is_available
from src.utils.config import load_config, class_label, friendly
from theme import (
    inject_theme, page_hero, stat_card, section_heading, delta_chip,
    CLASS_COLORS, PLOTLY_BASE, PLOTLY_CONFIG,
    ACCENT, CHART_GRAY, CHART_DARK, INK, INK_SEC, INK_MUTED, BORDER, SURFACE,
)

st.set_page_config(
    page_title="Simulate the Whole Class", page_icon="🏫", layout="wide",
    initial_sidebar_state="collapsed",
)
inject_theme(active_page="cohort")

cfg = load_config()

if not model_is_available():
    st.error("⚠️ No trained model found. Run `python scripts/run_pipeline.py` first.")
    st.stop()

# ---------------------------------------------------------------------------
# Page hero
# ---------------------------------------------------------------------------
st.markdown(page_hero(
    "Simulate the Whole Class",
    "Model what happens to the entire class if you implement an intervention. "
    "Monte Carlo simulation runs hundreds of trials with realistic variation "
    "to give you confidence intervals, not just single numbers."
), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Intervention controls
# ---------------------------------------------------------------------------
st.markdown(section_heading("Design Your Intervention"), unsafe_allow_html=True)

col_sliders, col_info = st.columns([2, 1])

with col_sliders:
    st.markdown(
        '<p style="font-family:var(--font-display);font-size:0.875rem;'
        'font-weight:600;color:var(--ink);margin:0 0 0.75rem 0;">'
        'Engagement changes (% increase from each student\'s current level)</p>',
        unsafe_allow_html=True,
    )

    rh_pct   = st.slider(f"{friendly('raisedhands', cfg)}",       -30, 50, 0, step=5, key="sim_rh",   help="% increase in hand-raising")
    vr_pct   = st.slider(f"{friendly('VisITedResources', cfg)}",  -30, 50, 0, step=5, key="sim_vr",   help="% increase in resource visits")
    av_pct   = st.slider(f"{friendly('AnnouncementsView', cfg)}", -30, 50, 0, step=5, key="sim_av",   help="% increase in announcement reading")
    disc_pct = st.slider(f"{friendly('Discussion', cfg)}",        -30, 50, 0, step=5, key="sim_disc", help="% increase in discussion participation")

    st.markdown(
        '<hr style="border:none;border-top:1px solid var(--border);margin:1rem 0;">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-family:var(--font-display);font-size:0.875rem;'
        'font-weight:600;color:var(--ink);margin:0 0 0.5rem 0;">'
        'Attendance improvement</p>',
        unsafe_allow_html=True,
    )
    abs_pct = st.slider(
        "% of high-absence students switching to low absence",
        0, 100, 0, step=5,
        key="sim_abs",
        help="Fraction of 'Above-7' students who would reduce absences to 'Under-7'",
    )

with col_info:
    st.markdown(
        '<p class="spps-stat-card-label">Intervention summary</p>',
        unsafe_allow_html=True,
    )
    changes = []
    if rh_pct   != 0: changes.append((friendly("raisedhands", cfg),       rh_pct))
    if vr_pct   != 0: changes.append((friendly("VisITedResources", cfg),  vr_pct))
    if av_pct   != 0: changes.append((friendly("AnnouncementsView", cfg), av_pct))
    if disc_pct != 0: changes.append((friendly("Discussion", cfg),        disc_pct))
    if abs_pct  != 0: changes.append(("Attendance improvement",            abs_pct))

    if changes:
        for name, val in changes:
            chip = delta_chip(val, suffix="%")
            st.markdown(
                f'<p style="font-size:0.875rem;margin:0.3rem 0;color:var(--ink-sec);">'
                f'<strong style="color:var(--ink);">{name}</strong>: {chip}</p>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<p style="font-size:0.8125rem;color:var(--ink-muted);">'
            'No changes selected — adjust the sliders to define an intervention.</p>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<hr style="border:none;border-top:1px solid var(--border);margin:1rem 0;">',
        unsafe_allow_html=True,
    )
    n_runs = st.number_input(
        "Simulation runs",
        min_value=50, max_value=1000, value=200, step=50,
        help="More runs = more precise results, but slower",
    )

st.divider()

# ---------------------------------------------------------------------------
# Run simulation
# ---------------------------------------------------------------------------
if st.button("Run Simulation", type="primary", use_container_width=True):
    intervention: dict = {}
    if rh_pct   != 0: intervention["raisedhands"]       = rh_pct
    if vr_pct   != 0: intervention["VisITedResources"]  = vr_pct
    if av_pct   != 0: intervention["AnnouncementsView"] = av_pct
    if disc_pct != 0: intervention["Discussion"]        = disc_pct
    if abs_pct  != 0: intervention["StudentAbsenceDays"]= abs_pct

    if not intervention:
        st.warning("Please adjust at least one slider to define an intervention.")
        st.stop()

    with st.spinner(f"Running {n_runs} simulations…"):
        from src.simulation.cohort_simulator import simulate_custom
        result = simulate_custom(intervention, cfg=cfg, n_runs=n_runs)

    # ── Results ──────────────────────────────────────────────────────────────
    st.markdown(section_heading("Simulation Results"), unsafe_allow_html=True)

    baseline  = result["baseline"]
    simulated = result["simulated"]
    shift     = result["shift"]
    n_students = result["n_students"]

    # Headline metric cards
    c1, c2, c3 = st.columns(3)
    label_map = {"L": "Low", "M": "Medium", "H": "High"}
    for col, cls in zip([c1, c2, c3], ["L", "M", "H"]):
        with col:
            b_pct  = baseline["distribution"][cls] * 100
            s_pct  = simulated["distribution_mean"][cls] * 100
            d_pct  = shift[cls] * 100
            b_cnt  = baseline["counts"][cls]
            s_cnt  = simulated["mean_counts"][cls]
            direction = "↑" if d_pct > 0 else ("↓" if d_pct < 0 else "→")
            color_map_cls = {"H": ACCENT, "M": "#8C8C8C", "L": CHART_DARK}
            dot_color = color_map_cls[cls]

            # Positive for H means good, positive for L means bad
            if (cls == "H" and d_pct > 0) or (cls == "L" and d_pct < 0):
                delta_style = f"color:{ACCENT};"
            elif (cls == "H" and d_pct < 0) or (cls == "L" and d_pct > 0):
                delta_style = "color:#3D3D3D;"
            else:
                delta_style = "color:var(--ink-muted);"

            st.markdown(
                f"""
<div style="background:var(--surface);border:1px solid var(--border);
            border-left:4px solid {dot_color};border-radius:var(--radius);
            padding:1.25rem 1.35rem;margin-bottom:0.75rem;">
  <p style="font-family:var(--font-body);font-size:0.75rem;font-weight:500;
             color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.07em;
             margin:0 0 0.4rem 0;">{label_map[cls]}</p>
  <p style="font-family:var(--font-display);font-size:1.6rem;font-weight:700;
             color:var(--ink);letter-spacing:-0.02em;margin:0 0 0.2rem 0;">
    {b_pct:.1f}% → {s_pct:.1f}%
  </p>
  <p style="font-family:var(--font-mono);font-size:0.875rem;
             margin:0 0 0.25rem 0;{delta_style}">
    {direction} {abs(d_pct):.1f} pp
  </p>
  <p style="font-size:0.8rem;color:var(--ink-muted);margin:0;
             font-family:var(--font-mono);">
    {b_cnt} → ~{s_cnt:.0f} students
  </p>
</div>""",
                unsafe_allow_html=True,
            )

    # Before / After bar chart — generous whitespace, accent for "After"
    st.markdown(
        '<p class="spps-stat-card-label" style="margin-top:2rem;">Before vs After Intervention</p>',
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    for cls in ["L", "M", "H"]:
        label = class_label(cls, cfg)
        # Before — light gray
        fig.add_trace(go.Bar(
            x=[label],
            y=[baseline["distribution"][cls] * 100],
            name="Before",
            marker_color=CHART_GRAY,
            opacity=0.55,
            showlegend=(cls == "L"),
            legendgroup="before",
        ))
        # After — accent for H, dark gray for M/L, with CI error bars
        ci_lo = simulated["distribution_ci_lower"][cls] * 100
        ci_hi = simulated["distribution_ci_upper"][cls] * 100
        mean  = simulated["distribution_mean"][cls] * 100
        after_color = CLASS_COLORS[cls]
        fig.add_trace(go.Bar(
            x=[label],
            y=[mean],
            name="After (simulated)",
            marker_color=after_color,
            showlegend=(cls == "L"),
            legendgroup="after",
            error_y=dict(
                type="data",
                symmetric=False,
                array=[ci_hi - mean],
                arrayminus=[mean - ci_lo],
                color=INK_SEC,
                thickness=1.5,
                width=6,
            ),
            text=[f"{mean:.1f}%"],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=11),
        ))

    max_val = max(baseline["distribution"].values()) * 100
    fig.update_layout(
        **PLOTLY_BASE,
        barmode="group",
        height=400,
        margin=dict(t=24, b=60, l=8, r=8),
        yaxis=dict(
            title="% of students",
            range=[0, min(100, max_val * 1.35)],
            showgrid=True, gridcolor="#EBEBEA",
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown(
        '<p class="spps-chart-caption">Gray bars = current class distribution. '
        'Colored bars = simulated distribution after the intervention. '
        'Error bars show the 95% confidence interval from the Monte Carlo '
        'simulation — wider bars mean more uncertainty about the exact outcome.</p>',
        unsafe_allow_html=True,
    )

    # Summary text — give it generous whitespace as the visual focus
    st.markdown(
        '<div style="margin:2.5rem 0 2rem 0;padding:1.5rem 2rem;'
        'background:var(--surface);border:1px solid var(--border);'
        'border-radius:var(--radius);">'
        f'<p class="spps-stat-card-label">Summary</p>'
        f'<p style="font-size:1rem;color:var(--ink);line-height:1.65;margin:0;">'
        f'{result.get("summary", "")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Advanced: Simulation Details"):
        st.markdown(f"- **Simulation runs**: {n_runs}")
        st.markdown(f"- **Students in cohort**: {n_students}")
        st.markdown(f"- **Intervention**: {result.get('intervention_description', '')}")
        st.markdown("- **Method**: Monte Carlo with per-student Gaussian noise (10% std dev)")

        st.markdown("**95% Confidence Intervals:**")
        for cls in ["L", "M", "H"]:
            lbl   = class_label(cls, cfg)
            ci_lo = simulated["distribution_ci_lower"][cls] * 100
            ci_hi = simulated["distribution_ci_upper"][cls] * 100
            st.markdown(f"  - {lbl}: [{ci_lo:.1f}%, {ci_hi:.1f}%]")

st.divider()

# ---------------------------------------------------------------------------
# Pre-defined scenarios
# ---------------------------------------------------------------------------
st.markdown(section_heading("Pre-defined Scenarios"), unsafe_allow_html=True)
st.caption("Quick-access scenarios for common policy questions.")

from src.simulation.cohort_simulator import default_scenarios  # noqa: E402

scenarios = default_scenarios(cfg)
for scenario in scenarios:
    with st.expander(f"{scenario['name']} — {scenario['description']}"):
        intervention_text = ", ".join(
            f"{friendly(k, cfg)}: {'+' if v > 0 else ''}{v}%"
            for k, v in scenario["intervention"].items()
        )
        st.markdown(
            f'<p style="font-size:0.875rem;color:var(--ink-sec);">'
            f'<strong>Intervention:</strong> {intervention_text}</p>',
            unsafe_allow_html=True,
        )

        if st.button(f"Run: {scenario['name']}", key=f"run_{scenario['name']}"):
            with st.spinner("Running simulation…"):
                from src.simulation.cohort_simulator import simulate_custom
                res = simulate_custom(scenario["intervention"], cfg=cfg, n_runs=200)
            st.markdown(
                f'<div style="background:var(--surface);border:1px solid var(--border);'
                f'border-radius:var(--radius);padding:1rem 1.25rem;margin-top:0.75rem;">'
                f'<p style="font-size:0.9rem;color:var(--ink);margin:0;">'
                f'{res.get("summary", "")}</p></div>',
                unsafe_allow_html=True,
            )
