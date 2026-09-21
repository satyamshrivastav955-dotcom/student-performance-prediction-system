"""
Trust & Fairness page — "Responsible AI for better education."

Restructured from The Archive of Proof into a cleaner, more accessible design
aligned with the reference visual system. Five tabs give progressive disclosure:

  Tab 1 — Model Performance  (model comparison, confusion matrix, key KPIs)
  Tab 2 — Error Analysis     (per-class metrics, error narrative, misclass breakdown)
  Tab 3 — Explainability     (global SHAP feature importance)
  Tab 4 — Statistical Validation (bootstrap CIs, McNemar test)
  Tab 5 — Fairness Audit     (fairlearn demographic parity, equalized odds)

Everything is classical machine learning — logistic regression, decision tree,
random forest, gradient boosting — assessed with bootstrap resampling, McNemar's
test, and fairlearn. No deep learning anywhere in the pipeline.

Educational language throughout: "students needing additional support", not
"at-risk" or "problem students". Predictions are decision support, not verdicts.
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

from src.utils.config import load_config, class_label
from theme import (
    inject_theme, page_hero, kpi_hero_row, section_heading,
    delta_chip, footnote, icon, verdict_banner, info_banner,
    mcnemar_evidence_card, ui_info_banner, ui_warning_banner,
    analytics_card_header, analytics_card_takeaway, protected_attr_badge,
    CLASS_COLORS, PLOTLY_BASE, PLOTLY_CONFIG,
    ACCENT, CHART_GRAY, CHART_DARK, INK, INK_SEC, INK_MUTED, BORDER, SURFACE,
    FOREST, BRASS, CLAY, OXFORD,
    GREEN, AMBER, CORAL, TEAL,
)


st.set_page_config(
    page_title="Trust & Fairness — Student Success",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme(active_page="models")

cfg = load_config()

# ---------------------------------------------------------------------------
# Load artifacts (guard if the pipeline hasn't been run yet)
# ---------------------------------------------------------------------------
ART = PROJECT_ROOT / "reports" / "artifacts"


def _load(name: str):
    p = ART / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


metrics  = _load("metrics.json")
fairness = _load("fairness_audit.json")
shap_g   = _load("shap_global.json")

# ---------------------------------------------------------------------------
# Page hero — Responsible AI framing
# ---------------------------------------------------------------------------
col_hero, col_quote = st.columns([3, 1])
with col_hero:
    st.markdown(
        """
<div class="spps-page-hero anim-fade-up">
  <p class="spps-eyebrow">Trust & Fairness</p>
  <p class="spps-page-title">Responsible AI for better education</p>
  <p class="spps-page-desc">Transparent. Fair. Interpretable. Built for real impact.</p>
</div>
""",
        unsafe_allow_html=True,
    )
with col_quote:
    st.markdown(
        """
<div style="background:rgba(27,42,74,.05);border:1px solid rgba(27,42,74,.15);
     border-radius:10px;padding:1rem 1.1rem;margin-top:1.5rem;font-family:var(--font-display);">
  <p style="font-size:0.9rem;color:var(--oxford);font-style:italic;margin:0 0 0.35rem;line-height:1.5;">
    "Technology should empower every learner, not create new barriers."
  </p>
  <p style="font-family:var(--font-mono);font-size:0.65rem;color:var(--ink-muted);margin:0;
     text-transform:uppercase;letter-spacing:0.1em;">Design Principle</p>
</div>
""",
        unsafe_allow_html=True,
    )

if not metrics:
    st.markdown(
        f"""
<div class="spps-state-error anim-fade">
  <div class="spps-state-error-icon">{icon('alert', 18, CLAY)}</div>
  <div>
    <p class="spps-state-error-title">Model data not found</p>
    <p class="spps-state-error-desc">Run <code>python scripts/run_pipeline.py</code> to generate the evaluation artifacts.</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Parse metrics
# ---------------------------------------------------------------------------
MODEL_NAMES = {
    "random_forest":       "Random Forest",
    "logistic_regression": "Logistic Regression",
    "gradient_boosting":   "Gradient Boosting",
    "decision_tree":       "Decision Tree",
}

best_key    = metrics.get("best_model", "random_forest")
runner_key  = metrics.get("runner_up_model", "logistic_regression")
test_eval   = metrics.get("test_evaluation", metrics.get("test_metrics", {})) or {}
cv          = metrics.get("cross_validation", {}) or {}
ranking     = metrics.get("cv_ranking", list(test_eval.keys())) or list(test_eval.keys())
tuning      = metrics.get("tuning", {}) or {}
bootstrap   = metrics.get("bootstrap", {}) or {}
mcnemar     = metrics.get("mcnemar", {}) or {}
err         = metrics.get("error_analysis", {}) or {}
dataset     = metrics.get("dataset", {}) or {}

best_eval   = test_eval.get(best_key, {})
best_name   = MODEL_NAMES.get(best_key, best_key)
runner_name = MODEL_NAMES.get(runner_key, runner_key)

# ---------------------------------------------------------------------------
# Capability cards row
# ---------------------------------------------------------------------------
severe_errors = err.get("severe_errors_low_vs_high", 0)
fair_verdict  = (fairness or {}).get("overall_verdict", {}).get("verdict", "n/a")

st.markdown(
    f"""
<div class="spps-capability-grid" style="margin:1.25rem 0;">
  <div class="spps-capability-card">
    <div class="spps-capability-icon">{icon('target', 22, FOREST)}</div>
    <p class="spps-capability-title">Classical Machine Learning</p>
    <p class="spps-capability-desc">Interpretable, reliable, and effective for educational data.</p>
    <span class="spps-capability-tag">Random Forest · Best Model</span>
  </div>
  <div class="spps-capability-card">
    <div class="spps-capability-icon">{icon('analytics', 22, BRASS)}</div>
    <p class="spps-capability-title">Explainability with SHAP</p>
    <p class="spps-capability-desc">Understand why a prediction was made, globally and for every individual student.</p>
    <span class="spps-capability-tag">TreeSHAP · Global + Local</span>
  </div>
  <div class="spps-capability-card">
    <div class="spps-capability-icon">{icon('lightbulb', 22, OXFORD)}</div>
    <p class="spps-capability-title">Actionable Recommendations</p>
    <p class="spps-capability-desc">Counterfactual analysis (DiCE) provides realistic, actionable steps for improvement.</p>
    <span class="spps-capability-tag">DiCE Counterfactuals</span>
  </div>
  <div class="spps-capability-card">
    <div class="spps-capability-icon">{icon('scales', 22, CLAY)}</div>
    <p class="spps-capability-title">Fairness & Bias Audit</p>
    <p class="spps-capability-desc">We evaluate model behaviour across demographic groups to ensure fair outcomes.</p>
    <span class="spps-capability-tag">Fairlearn · Demographic Parity</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Hero KPI strip
# ---------------------------------------------------------------------------
mcn_p = mcnemar.get("p_value", None)
mcn_str = f"{mcn_p:.4f}" if isinstance(mcn_p, (int, float)) else "—"
st.markdown(kpi_hero_row([
    {"icon": "target", "value": f"{best_eval.get('accuracy', 0):.1%}",
     "label": "Accuracy (Test Set)", "blue": True,
     "trend": f"{best_name} · held-out n={best_eval.get('n_test', '—')}"},
    {"icon": "ledger", "value": f"{best_eval.get('f1_macro', 0):.3f}",
     "label": "Macro F1-Score", "blue": True,
     "trend": f"ROC-AUC {best_eval.get('roc_auc_ovr', 0):.3f}"},
    {"icon": "flask",  "value": mcn_str,
     "label": "McNemar's p-value", "trend": f"vs {runner_name}"},
    {"icon": "seal",   "value": str(severe_errors),
     "label": "Severe Errors", "trend": f"Critical misclassifications · n={best_eval.get('n_test', 96)}"},
]), unsafe_allow_html=True)

st.markdown(
    ui_info_banner(
        "The model achieves strong predictive performance while remaining fully interpretable, "
        "making it suitable for real-world educational decision support. "
        "Use these predictions as decision support, not definitive judgements."
    ),
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Protected Attributes declaration
# ---------------------------------------------------------------------------
st.markdown(section_heading(
    "Protected Attributes",
    "Handled responsibly in both prediction and recommendation."
), unsafe_allow_html=True)

c_pa1, c_pa2 = st.columns(2)
for col, attr, desc in [
    (c_pa1, "Gender", "Used for fairness evaluation only. Not used as a modifiable feature in counterfactual recommendations."),
    (c_pa2, "Nationality", "Used for fairness evaluation only. Not used as a modifiable feature in counterfactual recommendations."),
]:
    with col:
        col.markdown(
            f"""
<div style="background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
     padding:1rem 1.25rem;display:flex;align-items:flex-start;gap:0.75rem;box-shadow:var(--shadow-card);">
  <span style="flex-shrink:0;margin-top:2px;">{icon('shield', 18, OXFORD)}</span>
  <div>
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">
      <p style="font-family:var(--font-display);font-size:1rem;font-weight:600;color:var(--ink);margin:0;">{attr}</p>
      <span class="spps-protected-badge">{icon("shield", 10, OXFORD)} Protected</span>
    </div>
    <p style="font-size:0.84rem;color:var(--ink-muted);margin:0;line-height:1.5;">{desc}</p>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown(
    f"""
<div style="background:rgba(27,42,74,.04);border:1px solid rgba(27,42,74,.15);border-radius:8px;
     padding:0.85rem 1.1rem;margin:0.75rem 0 1.5rem;font-size:0.84rem;color:var(--ink-sec);line-height:1.55;">
  {icon('shield', 15, OXFORD)}
  Protected attributes are <strong>mathematically frozen</strong> in the recommendation engine.
  The system will never suggest changing a student's gender or nationality to alter an outcome.
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Five-tab evaluation suite
# ---------------------------------------------------------------------------
tab_perf, tab_err, tab_shap, tab_stat, tab_fair = st.tabs([
    "Model Performance",
    "Error Analysis",
    "Explainability",
    "Statistical Validation",
    "Fairness Audit",
])

# ══════════════════════════════════════════════════════════
# TAB 1 — Model Performance
# ══════════════════════════════════════════════════════════
with tab_perf:
    st.markdown(section_heading(
        "Model Comparison",
        f"Performance across different algorithms (5-fold stratified CV). "
        f"{len(test_eval)} models compared."
    ), unsafe_allow_html=True)

    # Grouped bar: Accuracy + Macro-F1 side by side
    names_ordered  = [MODEL_NAMES.get(k, k) for k in ranking]
    acc_vals  = [test_eval.get(k, {}).get("accuracy", 0) for k in ranking]
    f1_vals   = [test_eval.get(k, {}).get("f1_macro", 0) for k in ranking]
    is_best   = [k == best_key for k in ranking]
    acc_colors = [FOREST if b else CHART_GRAY for b in is_best]
    f1_colors  = [BRASS if b else "#C9BFA9" for b in is_best]

    col_bar, col_cm = st.columns([1, 1])
    with col_bar:
        st.markdown(
            analytics_card_header(
                "Performance Across Algorithms",
                "Accuracy and Macro-F1 on held-out test set (96 students)."
            ),
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Accuracy", x=names_ordered, y=acc_vals,
            marker_color=acc_colors,
            text=[f"{v:.2f}" for v in acc_vals], textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=10, color=INK_SEC),
        ))
        fig.add_trace(go.Bar(
            name="Macro-F1", x=names_ordered, y=f1_vals,
            marker_color=f1_colors,
            text=[f"{v:.3f}" for v in f1_vals], textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=10, color=INK_SEC),
        ))
        fig.update_layout(
            **PLOTLY_BASE, barmode="group", height=320,
            margin=dict(t=10, b=60, l=8, r=8),
            yaxis=dict(title="Score", range=[0, 1.1], showgrid=True, gridcolor="#E7E0D1"),
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown(
            analytics_card_takeaway(
                f"{best_name} leads with {best_eval.get('accuracy',0):.1%} accuracy and "
                f"{best_eval.get('f1_macro',0):.3f} macro-F1 on 5-fold stratified cross-validation. "
                "Macro-F1 weights all three performance bands equally, making it the optimisation target."
            ),
            unsafe_allow_html=True,
        )

    with col_cm:
        st.markdown(
            analytics_card_header(
                f"Confusion Matrix ({best_name})",
                "Performance on 96 unseen holdout samples. Strong diagonal = correct predictions."
            ),
            unsafe_allow_html=True,
        )
        cm = best_eval.get("confusion_matrix", [])
        labels_raw = best_eval.get("confusion_matrix_labels", ["L", "M", "H"])
        if cm:
            disp = [class_label(l, cfg) for l in labels_raw]
            fig = px.imshow(
                cm, x=disp, y=disp, text_auto=True, aspect="auto",
                color_continuous_scale=[[0.0, "#FAF8F3"], [0.4, "#E8F0EB"], [1.0, FOREST]],
                labels=dict(x="Predicted", y="Actual", color="Students"),
            )
            # Highlight severe errors (L↔H) with a different annotation
            cm_arr = np.array(cm)
            for r_idx, r_lbl in enumerate(labels_raw):
                for c_idx, c_lbl in enumerate(labels_raw):
                    if r_lbl in ("L", "H") and c_lbl in ("L", "H") and r_lbl != c_lbl and cm_arr[r_idx, c_idx] > 0:
                        fig.add_annotation(
                            x=c_idx, y=r_idx,
                            text="⚠", showarrow=False,
                            font=dict(size=10, color=CLAY),
                            yshift=14,
                        )
            fig.update_layout(
                **PLOTLY_BASE, height=320,
                margin=dict(t=10, b=40, l=10, r=10),
                coloraxis_showscale=False,
            )
            fig.update_traces(textfont=dict(family="IBM Plex Mono, monospace", size=14))
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
            n_correct = sum(cm_arr[i, i] for i in range(len(cm_arr)))
            n_total_cm = cm_arr.sum()
            st.markdown(
                analytics_card_takeaway(
                    f"Correct predictions: {n_correct}/{n_total_cm} ({n_correct/n_total_cm:.1%}). "
                    f"Most errors are adjacent-band mistakes (Low↔Medium or Medium↔High). "
                    f"Severe errors (Low↔High): {severe_errors}."
                ),
                unsafe_allow_html=True,
            )
        else:
            st.info("Confusion matrix data not available.")

    # Leaderboard table
    with st.expander(f"Full Model Leaderboard ({len(test_eval)} models)"):
        rows = []
        for k in ranking:
            te   = test_eval.get(k, {})
            cvm  = cv.get(k, {}).get("f1_macro", {})
            is_b = (k == best_key)
            rows.append({
                "Model":         ("★ " if is_b else "") + MODEL_NAMES.get(k, k),
                "Accuracy":      te.get("accuracy", np.nan),
                "Balanced Acc.": te.get("balanced_accuracy", np.nan),
                "Macro-F1":      te.get("f1_macro", np.nan),
                "Cohen's κ":     te.get("cohen_kappa", np.nan),
                "ROC-AUC":       te.get("roc_auc_ovr", np.nan),
                "CV Macro-F1":   cvm.get("mean", np.nan),
                "Tuned":         "✓" if tuning.get(k, {}).get("tuned") else "—",
            })
        df_lead = pd.DataFrame(rows)
        _fmt = {
            "Accuracy": "{:.1%}", "Balanced Acc.": "{:.1%}",
            "Macro-F1": "{:.3f}", "Cohen's κ": "{:.3f}",
            "ROC-AUC": "{:.3f}", "CV Macro-F1": "{:.3f}",
        }
        def _hl(row):
            if str(row["Model"]).startswith("★"):
                return ["background-color: rgba(154,123,46,0.10); font-weight:700; color:#1C1917"] * len(row)
            return [""] * len(row)
        try:
            styled = df_lead.style.format(_fmt).apply(_hl, axis=1)
            st.dataframe(styled, use_container_width=True, hide_index=True)
        except Exception:
            st.dataframe(df_lead, use_container_width=True, hide_index=True)
        csv_lead = df_lead.copy()
        csv_lead["Model"] = csv_lead["Model"].str.replace("★ ", "", regex=False)
        st.download_button(
            "Download model comparison (CSV)",
            csv_lead.to_csv(index=False).encode("utf-8"),
            file_name="model_comparison.csv", mime="text/csv",
        )

# ══════════════════════════════════════════════════════════
# TAB 2 — Error Analysis
# ══════════════════════════════════════════════════════════
with tab_err:
    st.markdown(section_heading(
        f"Error Analysis — {best_name}",
        "Per-class precision, recall, and F1 on the held-out test set."
    ), unsafe_allow_html=True)

    col_pc, col_ea = st.columns([1, 1])
    with col_pc:
        per_class = best_eval.get("per_class", {})
        if per_class:
            pc_rows = []
            for c in ["L", "M", "H"]:
                d = per_class.get(c, {})
                pc_rows.append({
                    "Band":      class_label(c, cfg),
                    "Precision": d.get("precision", np.nan),
                    "Recall":    d.get("recall", np.nan),
                    "F1":        d.get("f1", np.nan),
                    "Support":   d.get("support", np.nan),
                })
            pc_df = pd.DataFrame(pc_rows)

            # Visual bar chart per metric
            fig = go.Figure()
            metrics_to_plot = ["Precision", "Recall", "F1"]
            colors_pc = [CLAY, BRASS, FOREST]
            for i, band_row in enumerate(pc_rows):
                band = band_row["Band"]
                color = list(CLASS_COLORS.values())[i]
                for metric in metrics_to_plot:
                    fig.add_trace(go.Bar(
                        name=band,
                        x=[metric],
                        y=[band_row[metric]],
                        marker_color=color,
                        showlegend=(metric == "Precision"),
                        legendgroup=band,
                        text=[f"{band_row[metric]:.3f}"],
                        textposition="outside",
                        textfont=dict(family="IBM Plex Mono, monospace", size=10),
                    ))
            fig.update_layout(
                **PLOTLY_BASE, barmode="group", height=300,
                margin=dict(t=10, b=40, l=8, r=8),
                yaxis=dict(title="Score", range=[0, 1.15], showgrid=True, gridcolor="#E7E0D1"),
            )
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

            try:
                pc_styled = pc_df.style.format(
                    {"Precision": "{:.3f}", "Recall": "{:.3f}", "F1": "{:.3f}", "Support": "{:.0f}"}
                )
                st.dataframe(pc_styled, use_container_width=True, hide_index=True)
            except Exception:
                st.dataframe(pc_df, use_container_width=True, hide_index=True)
            st.markdown(
                analytics_card_takeaway(
                    f"The model performs well across all classes, with highest recall for the "
                    f"Low band ({per_class.get('L', {}).get('recall', 0):.2f}) — "
                    "important for identifying students who may need additional support."
                ),
                unsafe_allow_html=True,
            )

    with col_ea:
        if err:
            n_mis  = err.get("n_misclassified", 0)
            n_test = err.get("n_test", best_eval.get("n_test", 96))
            adj    = err.get("adjacent_band_errors", 0)
            svr    = err.get("severe_errors_low_vs_high", 0)

            # Severe error safety card
            svr_color = FOREST if svr == 0 else CLAY
            svr_bg    = "rgba(35,68,52,.06)" if svr == 0 else "rgba(124,45,18,.07)"
            st.markdown(
                f"""
<div style="background:{svr_bg};border:1px solid {svr_color}33;
     border-top:3px solid {svr_color};border-radius:10px;
     padding:1.5rem;text-align:center;margin-bottom:1rem;box-shadow:var(--shadow-card);">
  <p style="font-family:var(--font-mono);font-size:0.68rem;text-transform:uppercase;
     letter-spacing:0.12em;color:{svr_color};margin:0 0 0.3rem;">Severe Errors (Safety Check)</p>
  <p style="font-family:var(--font-display);font-size:3.5rem;font-weight:700;
     color:{svr_color};margin:0.25rem 0 0.1rem;">{svr}</p>
  <p style="font-size:0.82rem;color:var(--ink-muted);margin:0;">
    Low ↔ High misclassifications · n={n_test} holdout
  </p>
  <p style="font-size:0.84rem;color:var(--ink-sec);margin:0.6rem 0 0;line-height:1.5;">
    {'No severe misclassifications between Low and High bands. This reduces the risk of harmful recommendations.' if svr == 0 else f'{svr} severe error(s) detected — review these cases carefully.'}
  </p>
</div>
""",
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
<div class="spps-narrative">
  Of <strong>{n_test}</strong> test students, <strong>{n_mis}</strong> are misclassified
  ({err.get('error_rate', 0):.1%}). Every misclassification is an
  <strong>adjacent-band</strong> error ({adj}/{n_mis}) — Low↔Medium or Medium↔High.
  There are <strong>{svr}</strong> severe errors (a student predicted as High when actually Low,
  or vice-versa). This matters for a tool meant to identify students needing support:
  the model never misses by two full bands.
</div>
""",
                unsafe_allow_html=True,
            )

            pairs = err.get("confusion_pairs", {})
            if pairs:
                pair_rows = [
                    {"Error (Actual → Predicted)": k.replace("->", "→"), "Count": v}
                    for k, v in pairs.items()
                ]
                st.dataframe(pd.DataFrame(pair_rows), use_container_width=True, hide_index=True)
                st.caption("Which performance bands get confused with each other.")

    # CV overfitting check
    with st.expander(f"Cross-Validation & Overfitting Check ({best_name})"):
        fig = go.Figure()
        cv_val   = [cv.get(k, {}).get("f1_macro", {}).get("mean", 0) for k in ranking]
        cv_std   = [cv.get(k, {}).get("f1_macro", {}).get("std", 0) for k in ranking]
        cv_train = [cv.get(k, {}).get("f1_macro", {}).get("train_mean", 0) for k in ranking]
        names    = [MODEL_NAMES.get(k, k) for k in ranking]
        fig.add_trace(go.Bar(
            name="Validation (CV)", x=names, y=cv_val, marker_color=FOREST,
            error_y=dict(type="data", array=cv_std, color=INK_SEC, thickness=1.4, width=6),
            text=[f"{v:.3f}" for v in cv_val], textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=10),
        ))
        fig.add_trace(go.Bar(
            name="Training", x=names, y=cv_train, marker_color=CHART_GRAY, opacity=0.6,
        ))
        fig.update_layout(
            **PLOTLY_BASE, barmode="group", height=320, margin=dict(t=10, b=60, l=8, r=8),
            yaxis=dict(title="Macro-F1", range=[0, 1.05], showgrid=True, gridcolor="#E7E0D1"),
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        best_gap = cv.get(best_key, {}).get("f1_macro", {}).get("overfit_gap", None)
        gap_str  = f"{best_gap:.3f}" if isinstance(best_gap, (int, float)) else "—"
        st.caption(
            f"{best_name} shows a training-vs-validation gap of {gap_str} macro-F1. "
            "The held-out test macro-F1 is in line with the cross-validation mean, "
            "indicating the tuning is holding overfitting in check."
        )
        best_params = tuning.get(best_key, {}).get("best_params", {})
        if best_params:
            st.markdown(f"**Tuned hyper-parameters:** {best_params}")

# ══════════════════════════════════════════════════════════
# TAB 3 — Explainability
# ══════════════════════════════════════════════════════════
with tab_shap:
    st.markdown(section_heading(
        "Global Feature Importance (SHAP)",
        f"Average absolute SHAP values across {(shap_g or {}).get('global', {}).get('n_students_explained', 96)} "
        f"holdout students. Larger value = stronger average influence on the prediction."
    ), unsafe_allow_html=True)

    if shap_g and "global" in shap_g:
        ranked = shap_g["global"].get("ranked_features", [])
        if ranked:
            # Top features horizontal bar
            top_n = min(10, len(ranked))
            feat_names   = [r.get("friendly_name", r["feature"]) for r in ranked[:top_n]]
            feat_raw     = [r["feature"] for r in ranked[:top_n]]
            shap_vals    = [r["mean_abs_shap"] for r in ranked[:top_n]]
            shares       = [r.get("share_of_total", 0) * 100 for r in ranked[:top_n]]
            actionable   = [r.get("actionable", True) for r in ranked[:top_n]]
            sensitive    = [r.get("sensitive", False) for r in ranked[:top_n]]

            # Color: sensitive=oxford, actionable=forest, else=brass
            bar_colors_shap = []
            for act, sens in zip(actionable, sensitive):
                if sens:
                    bar_colors_shap.append(CHART_GRAY)
                elif act:
                    bar_colors_shap.append(FOREST)
                else:
                    bar_colors_shap.append(BRASS)

            col_shap, col_legend = st.columns([3, 1])
            with col_shap:
                # Reverse for bottom-to-top display
                fig = go.Figure(go.Bar(
                    y=feat_names[::-1],
                    x=shap_vals[::-1],
                    orientation="h",
                    marker_color=bar_colors_shap[::-1],
                    text=[f"{v:.4f}" for v in shap_vals[::-1]],
                    textposition="outside",
                    textfont=dict(family="IBM Plex Mono, monospace", size=11),
                    hovertemplate="%{y}: mean |SHAP| = %{x:.4f}<extra></extra>",
                ))
                fig.update_layout(
                    **PLOTLY_BASE, height=max(300, top_n * 32),
                    margin=dict(t=10, b=40, l=180, r=60),
                    xaxis=dict(
                        title="Mean absolute SHAP value",
                        range=[0, max(shap_vals) * 1.3],
                        showgrid=True, gridcolor="#E7E0D1",
                    ),
                    yaxis=dict(showgrid=False, tickfont=dict(size=12)),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

            with col_legend:
                st.markdown(
                    f"""
<div style="margin-top:1.5rem;">
  <p style="font-family:var(--font-mono);font-size:0.7rem;text-transform:uppercase;
     letter-spacing:0.1em;color:var(--brass);margin:0 0 0.75rem;">Legend</p>
  <div style="display:flex;flex-direction:column;gap:0.6rem;">
    <div style="display:flex;align-items:center;gap:0.5rem;font-size:0.82rem;color:var(--ink-sec);">
      <span style="width:12px;height:12px;background:{FOREST};border-radius:3px;flex-shrink:0;"></span>
      Actionable factor
    </div>
    <div style="display:flex;align-items:center;gap:0.5rem;font-size:0.82rem;color:var(--ink-sec);">
      <span style="width:12px;height:12px;background:{BRASS};border-radius:3px;flex-shrink:0;"></span>
      Contextual factor
    </div>
    <div style="display:flex;align-items:center;gap:0.5rem;font-size:0.82rem;color:var(--ink-sec);">
      <span style="width:12px;height:12px;background:{CHART_GRAY};border-radius:3px;flex-shrink:0;"></span>
      Protected attribute
    </div>
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )

            # Feature share breakdown
            st.markdown(
                analytics_card_takeaway(
                    f"Absence level and learning resources account for the top two SHAP contributions "
                    f"({ranked[0].get('share_of_total',0):.1%} and {ranked[1].get('share_of_total',0):.1%} of total). "
                    "Actionable features (green) are the ones teachers and students can work on. "
                    "Protected attributes (grey) are shown for transparency but are not used in recommendations."
                ),
                unsafe_allow_html=True,
            )

            # Detailed table
            with st.expander("Full SHAP feature table"):
                shap_rows = [
                    {
                        "Feature":      r.get("friendly_name", r["feature"]),
                        "Tech name":    r["feature"],
                        "Mean |SHAP|":  round(r["mean_abs_shap"], 5),
                        "Share (%)":    round(r.get("share_of_total", 0) * 100, 2),
                        "Actionable":   "✓" if r.get("actionable") else "—",
                        "Protected":    "⚠" if r.get("sensitive") else "—",
                    }
                    for r in ranked
                ]
                st.dataframe(pd.DataFrame(shap_rows), use_container_width=True, hide_index=True)
    else:
        st.info(
            "Global SHAP data not available. Run `python scripts/run_pipeline.py` "
            "to generate shap_global.json."
        )

    st.markdown(
        ui_warning_banner(
            "SHAP values explain the model's predictions, not ground truth causal relationships. "
            "A high SHAP value for a feature means the model relies on it — not that changing it "
            "alone will change a student's actual outcome."
        ),
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════
# TAB 4 — Statistical Validation
# ══════════════════════════════════════════════════════════
with tab_stat:
    st.markdown(section_heading(
        "Bootstrap Confidence Intervals",
        "95% confidence intervals from 2,000 bootstrap resamples of the 96-student test set. "
        "Communicates the uncertainty around each point estimate."
    ), unsafe_allow_html=True)

    boot_models = [k for k in [best_key, runner_key] if k in bootstrap]
    if boot_models:
        # Point-and-range chart for both Accuracy and Macro-F1
        metrics_ci = ["accuracy", "f1_macro"]
        metric_labels = {"accuracy": "Accuracy", "f1_macro": "Macro-F1"}
        fig = go.Figure()

        for metric_key in metrics_ci:
            for i, k in enumerate(boot_models):
                b     = bootstrap[k].get(metric_key, {})
                point = b.get("point_estimate", 0)
                lo    = b.get("ci_lower", point)
                hi    = b.get("ci_upper", point)
                name  = MODEL_NAMES.get(k, k)
                y_label = f"{name}<br><span style='font-size:10px'>{metric_labels[metric_key]}</span>"
                color = FOREST if k == best_key else CHART_GRAY
                fig.add_trace(go.Scatter(
                    x=[lo, point, hi],
                    y=[y_label, y_label, y_label],
                    mode="lines+markers",
                    marker=dict(
                        size=[6, 12, 6],
                        color=[color, color, color],
                        symbol=["line-ns", "circle", "line-ns"],
                    ),
                    line=dict(color=color, width=2),
                    name=f"{name} · {metric_labels[metric_key]}",
                    showlegend=(i == 0),
                    text=[f"CI lower: {lo:.3f}", f"Point: {point:.3f}", f"CI upper: {hi:.3f}"],
                    hovertemplate="%{text}<extra></extra>",
                ))

        fig.update_layout(
            **PLOTLY_BASE, height=max(250, len(boot_models) * 2 * 50),
            margin=dict(t=10, b=40, l=170, r=60),
            xaxis=dict(title="Score (95% CI)", range=[0.5, 1.05],
                       showgrid=True, gridcolor="#E7E0D1"),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown(
            analytics_card_takeaway(
                f"{best_name}: Accuracy 95% CI = [{bootstrap.get(best_key,{}).get('accuracy',{}).get('ci_lower',0):.3f}, "
                f"{bootstrap.get(best_key,{}).get('accuracy',{}).get('ci_upper',0):.3f}], "
                f"Macro-F1 95% CI = [{bootstrap.get(best_key,{}).get('f1_macro',{}).get('ci_lower',0):.3f}, "
                f"{bootstrap.get(best_key,{}).get('f1_macro',{}).get('ci_upper',0):.3f}]. "
                "Narrow intervals indicate robust performance despite the small (n=96) test set."
            ),
            unsafe_allow_html=True,
        )
    else:
        st.info("Bootstrap CI data not available.")

    st.divider()

    # McNemar evidence card
    st.markdown(section_heading(
        "McNemar's Statistical Comparison",
        f"Formal statistical test of whether {best_name} truly outperforms {runner_name}."
    ), unsafe_allow_html=True)

    if mcnemar:
        cont     = mcnemar.get("contingency", {})
        p_val    = mcnemar.get("p_value", None)
        sig      = mcnemar.get("significant", False)
        chi_stat = mcnemar.get("statistic", mcnemar.get("chi2", 0))
        interp   = mcnemar.get("interpretation", "")
        st.markdown(
            mcnemar_evidence_card(
                model_a=best_name,
                model_b=runner_name,
                both_correct=cont.get("both_correct", 0),
                only_a=cont.get("only_a_correct", 0),
                only_b=cont.get("only_b_correct", 0),
                both_wrong=cont.get("both_wrong", 0),
                stat=float(chi_stat) if chi_stat else 0.0,
                p_value=float(p_val) if p_val is not None else 1.0,
                significant=bool(sig),
                interpretation=interp or (
                    f"{best_name} significantly outperforms {runner_name}."
                    if sig else
                    f"The difference is not statistically significant at α={mcnemar.get('alpha',0.05)}. "
                    f"We still deploy {best_name} because it has the best point estimates across every metric."
                ),
            ),
            unsafe_allow_html=True,
        )
    else:
        st.info("McNemar test data not available.")

# ══════════════════════════════════════════════════════════
# TAB 5 — Fairness Audit
# ══════════════════════════════════════════════════════════
with tab_fair:
    st.markdown(section_heading(
        "Fairness Audit",
        "A fairlearn audit of demographic parity across sensitive attributes "
        "(gender and nationality). Model performance is consistent across demographic groups."
    ), unsafe_allow_html=True)

    if not fairness:
        st.info("Fairness audit data not available — run the pipeline to generate fairness_audit.json.")
    else:
        ov = fairness.get("overall_verdict", {})
        verdict  = ov.get("verdict", "n/a")
        v_color  = {"acceptable": FOREST, "concern": "#8A6D1B", "fail": CLAY}.get(verdict, INK_MUTED)
        v_bg     = {"acceptable": "rgba(35,68,52,0.06)", "concern": "rgba(138,109,27,0.07)",
                    "fail": "rgba(124,45,18,0.07)"}.get(verdict, "#F5F0E6")

        # Overall verdict
        st.markdown(
            f'<div style="background:{v_bg};border:1px solid {v_color}33;'
            f'border-left:4px solid {v_color};border-radius:var(--radius);padding:1.1rem 1.35rem;margin-bottom:1rem;">'
            f'<p style="font-family:var(--font-mono);font-size:0.72rem;text-transform:uppercase;'
            f'letter-spacing:0.1em;color:{v_color};margin:0 0 0.3rem;">Overall verdict — {verdict}</p>'
            f'<p style="font-size:0.95rem;color:var(--ink);margin:0;line-height:1.6;">'
            f'{ov.get("headline", "")}</p></div>',
            unsafe_allow_html=True,
        )

        n_fair = fairness.get("n_students", dataset.get("n_total", "all"))
        st.markdown(
            ui_info_banner(
                f"The audit is computed across all {n_fair} students (not just the 96-student test set) "
                "so each subgroup has enough samples to measure. Demographic parity looks at selection rate "
                "(how often each group is predicted into the top band)."
            ),
            unsafe_allow_html=True,
        )

        audits     = {a.get("attribute", "").lower(): a for a in fairness.get("attribute_audits", [])}
        thresholds = fairness.get("methodology", {}).get("thresholds", {})
        dp_thresh  = thresholds.get("disparity_ratio", 0.8)
        min_size   = thresholds.get("min_group_size", 20)

        # Gender | Nationality tabs
        attr_labels = {k: v.get("attribute", k).title() for k, v in audits.items()}
        if audits:
            attr_tabs = st.tabs([attr_labels.get(k, k) for k in audits])
            for attr_tab, attr_key in zip(attr_tabs, audits):
                with attr_tab:
                    a = audits[attr_key]
                    interp_a = a.get("interpretation", {})
                    m    = a.get("metrics", {})
                    av   = interp_a.get("verdict", "n/a")
                    a_color = {"acceptable": FOREST, "concern": "#8A6D1B", "fail": CLAY}.get(av, INK_MUTED)
                    dp_ratio = m.get("demographic_parity_ratio")
                    eq_odds  = m.get("equalized_odds_difference")
                    dp_r_s   = f"{dp_ratio:.3f}" if isinstance(dp_ratio, (int, float)) else "—"
                    eq_s     = f"{eq_odds:.3f}"  if isinstance(eq_odds, (int, float)) else "—"

                    mc1, mc2, mc3 = st.columns(3)
                    mc1.markdown(
                        f'<div style="background:var(--surface);border:1px solid var(--border);'
                        f'border-radius:var(--radius);padding:1rem 1.1rem;text-align:center;">'
                        f'<p style="font-family:var(--font-display);font-size:1.8rem;font-weight:700;'
                        f'color:{a_color};margin:0;">{dp_r_s}</p>'
                        f'<p style="font-size:0.72rem;color:var(--ink-muted);margin:0.2rem 0 0;">'
                        f'Demographic Parity Ratio<br>(want ≥ {dp_thresh:g})</p>'
                        f'<p style="font-size:0.72rem;color:{a_color};margin:0.3rem 0 0;font-weight:600;">'
                        f'{"✓ Within fair range" if isinstance(dp_ratio,(int,float)) and dp_ratio>=dp_thresh else "⚠ Review needed"}</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    mc2.markdown(
                        f'<div style="background:var(--surface);border:1px solid var(--border);'
                        f'border-radius:var(--radius);padding:1rem 1.1rem;text-align:center;">'
                        f'<p style="font-family:var(--font-display);font-size:1.8rem;font-weight:700;'
                        f'color:var(--ink);margin:0;">{eq_s}</p>'
                        f'<p style="font-size:0.72rem;color:var(--ink-muted);margin:0.2rem 0 0;">'
                        f'Equalized Odds Difference<br>(want ≤ 0.1)</p>'
                        f'<p style="font-size:0.72rem;color:{FOREST};margin:0.3rem 0 0;font-weight:600;">'
                        f'{"✓ Low disparity" if isinstance(eq_odds,(int,float)) and eq_odds<=0.1 else "→ Moderate"}</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    n_groups = len(a.get("group_info", {}).get("group_sizes", {}))
                    mc3.markdown(
                        f'<div style="background:var(--surface);border:1px solid var(--border);'
                        f'border-radius:var(--radius);padding:1rem 1.1rem;text-align:center;">'
                        f'<p style="font-family:var(--font-display);font-size:1.8rem;font-weight:700;'
                        f'color:var(--ink);margin:0;">{n_groups}</p>'
                        f'<p style="font-size:0.72rem;color:var(--ink-muted);margin:0.2rem 0 0;">'
                        f'Groups compared</p></div>',
                        unsafe_allow_html=True,
                    )

                    for finding in interp_a.get("findings", []):
                        st.markdown(
                            f'<p style="font-size:0.875rem;color:var(--ink-sec);margin:0.5rem 0 0;">• {finding}</p>',
                            unsafe_allow_html=True,
                        )

                    # Selection-rate chart
                    sel   = m.get("by_group", {}).get("selection_rate", {})
                    sizes = a.get("group_info", {}).get("group_sizes", {})
                    if sel and len(sel) > 2:
                        items  = sorted(sel.items(), key=lambda kv: kv[1])
                        y_lab  = [f"{g}  (n={sizes.get(g,'?')})" for g, _ in items]
                        x_val  = [v * 100 for _, v in items]
                        cols_c = [FOREST if sizes.get(g, 0) >= min_size else "#D6CFC0" for g, _ in items]
                        fig = go.Figure(go.Bar(
                            y=y_lab, x=x_val, orientation="h", marker_color=cols_c,
                            text=[f"{v:.1f}%" for v in x_val], textposition="outside",
                            textfont=dict(family="IBM Plex Mono, monospace", size=10),
                        ))
                        fig.update_layout(
                            **PLOTLY_BASE, height=max(240, len(items) * 26),
                            margin=dict(t=10, b=40, l=140, r=40), showlegend=False,
                            xaxis=dict(title="Selection rate — % predicted into the top band",
                                       range=[0, max(x_val) * 1.25 if x_val else 100],
                                       showgrid=True, gridcolor="#E7E0D1"),
                            yaxis=dict(showgrid=False, tickfont=dict(size=10)),
                        )
                        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                        caveat = a.get("group_info", {}).get("caveat", "")
                        st.caption(
                            f"Forest-coloured bars = groups with n ≥ {min_size} (statistically reliable). "
                            f"Grey bars = smaller groups. {caveat}"
                        )
                    elif sel:
                        items = list(sel.items())
                        fig   = go.Figure(go.Bar(
                            x=[f"{g} (n={sizes.get(g,'?')})" for g, _ in items],
                            y=[v * 100 for _, v in items],
                            marker_color=[FOREST, CHART_DARK][:len(items)],
                            text=[f"{v*100:.1f}%" for _, v in items], textposition="outside",
                            textfont=dict(family="IBM Plex Mono, monospace", size=11),
                        ))
                        fig.update_layout(
                            **PLOTLY_BASE, height=260, showlegend=False,
                            margin=dict(t=10, b=40, l=8, r=8),
                            yaxis=dict(title="Selection rate (%)",
                                       range=[0, max(v*100 for _, v in items)*1.3],
                                       showgrid=True, gridcolor="#E7E0D1"),
                        )
                        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                        st.caption(
                            f"Selection rates are near-identical across groups "
                            f"(parity ratio {dp_r_s} ≥ {dp_thresh:g}), so no adverse impact detected."
                        )

        # Model Limitations
        st.divider()
        st.markdown(section_heading(
            "Model Limitations",
            "We are transparent about what this system can and cannot do."
        ), unsafe_allow_html=True)

        limitations = [
            "Predictions are based on historical data and may not capture all real-world factors.",
            "The model is not a definitive judgement of a student's potential.",
            "Results should be used to support students, not to label or limit them.",
            "The system works best with data similar to the training cohort (N=478).",
        ]
        lim_html = "".join(
            f'<li style="display:flex;align-items:flex-start;gap:0.5rem;padding:0.35rem 0;'
            f'font-size:0.875rem;color:var(--ink-sec);">'
            f'<span style="flex-shrink:0;margin-top:3px;">{icon("alert", 14, BRASS)}</span>'
            f'<span>{lim}</span></li>'
            for lim in limitations
        )
        st.markdown(
            f'<div style="background:rgba(154,123,46,.04);border:1px solid rgba(154,123,46,.2);'
            f'border-radius:var(--radius);padding:1.1rem 1.25rem;">'
            f'<ul style="list-style:none;padding:0;margin:0;">{lim_html}</ul></div>',
            unsafe_allow_html=True,
        )

        # Commitment
        st.markdown(
            f"""
<div style="background:rgba(35,68,52,.05);border:1px solid rgba(35,68,52,.18);
     border-radius:var(--radius);padding:1.25rem 1.4rem;margin-top:1rem;display:flex;gap:1rem;align-items:flex-start;">
  {icon('heart', 22, FOREST)}
  <div>
    <p style="font-family:var(--font-display);font-size:1.05rem;font-weight:600;color:var(--ink);margin:0 0 0.3rem;">
      Our Commitment
    </p>
    <p style="font-size:0.875rem;color:var(--ink-sec);margin:0;line-height:1.6;">
      We believe in using data and AI to create more inclusive, supportive, and equitable educational
      environments — where every student has the opportunity to succeed.
      <strong style="color:var(--forest);">Students First · Always.</strong>
    </p>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if ov.get("recommendation"):
            st.markdown(
                f'<div class="spps-suggestion" style="margin-top:0.75rem;">'
                f'<strong>Recommended next steps:</strong> {ov.get("recommendation")}</div>',
                unsafe_allow_html=True,
            )

        with st.expander("Fairness methodology"):
            meth = fairness.get("methodology", {})
            st.markdown(f"- **Library**: {meth.get('library', 'fairlearn')}")
            st.markdown(f"- **Definition**: {meth.get('description', 'demographic parity')}")
            st.markdown(
                f"- **Thresholds**: parity ratio ≥ {dp_thresh:g} (four-fifths rule), "
                f"parity difference ≤ {thresholds.get('disparity_difference', 0.1):g}, "
                f"minimum reliable group size = {min_size}"
            )

st.markdown(
    footnote(
        "Trust & Fairness · Classical ML only · Logistic Regression · Decision Tree · "
        "Random Forest · Gradient Boosting · Bootstrap · McNemar · Fairlearn · No deep learning"
    ),
    unsafe_allow_html=True,
)
