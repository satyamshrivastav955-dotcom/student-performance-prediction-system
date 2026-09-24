"""
scripts/generate_diagrams.py
Generates publication-quality architectural and engineering diagrams for the
Student Performance Prediction System using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

OUT_DIR = Path("docs/diagrams")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Set common font and style
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'


def create_system_architecture():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title & Subtitle
    ax.text(8, 9.6, "Student Performance Prediction System — System Architecture", 
            ha='center', va='center', fontsize=18, fontweight='bold', color='#0F172A')
    ax.text(8, 9.2, "Production Machine Learning Architecture with Explainability, Fairness Auditing & Dual Serving", 
            ha='center', va='center', fontsize=11, color='#475569')

    # Helper for rounded boxes
    def draw_box(x, y, w, h, bg, border, title, desc, title_color='#0F172A', desc_color='#334155'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                      facecolor=bg, edgecolor=border, linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.35, title, ha='center', va='top', 
                fontsize=11, fontweight='bold', color=title_color, zorder=3)
        ax.text(x + w/2, y + (h - 0.4)/2, desc, ha='center', va='center', 
                fontsize=8.5, color=desc_color, multialignment='center', zorder=3)

    # Helper for arrows
    def draw_arrow(x1, y1, x2, y2, color='#64748B', style='->', lw=1.5, label=''):
        arrow = patches.FancyArrowPatch((x1, y1), (x2, y2),
                                        arrowstyle=style, color=color, linewidth=lw,
                                        mutation_scale=15, zorder=1)
        ax.add_patch(arrow)
        if label:
            ax.text((x1 + x2)/2, (y1 + y2)/2 + 0.15, label, ha='center', va='bottom',
                    fontsize=8, color='#64748B', fontweight='bold', zorder=4)

    # 1. DATA LAYER (Left column)
    draw_box(0.8, 6.0, 3.2, 2.2, '#EFF6FF', '#3B82F6', 
             "1. Data Ingestion & Cleaning",
             "• xAPI-Edu-Data (N=478)\n• 16 Academic & Socio-Behavioral\n• Zero-loss Schema Validation\n• Exact Duplicate Elimination\n• Median & Mode Imputation",
             title_color='#1D4ED8')

    draw_box(0.8, 3.0, 3.2, 2.2, '#EFF6FF', '#3B82F6',
             "2. Feature Pipeline",
             "• ColumnTransformer Pipeline\n• StandardScaler (Continuous)\n• OneHotEncoder (Categorical)\n• Ordinal Encoding (Binary)\n• Strict Train-Fold Isolation",
             title_color='#1D4ED8')

    draw_arrow(2.4, 6.0, 2.4, 5.2, '#3B82F6', '->', 2)

    # 2. MODEL ENGINE LAYER (Center column)
    draw_box(5.0, 4.5, 3.6, 3.7, '#ECFDF5', '#10B981',
             "3. Machine Learning Engine",
             "• Champion: Random Forest\n• 5-Fold Stratified Cross-Validation\n• Holdout Accuracy: 82.29%\n• Holdout Macro-F1: 82.82%\n• Cohen's Kappa: 0.7285\n• Severe Error Rate: 0.0% (0/96)\n• Artifact: model.joblib bundle",
             title_color='#047857')

    draw_arrow(4.0, 4.1, 5.0, 5.5, '#10B981', '->', 2, 'Features')

    # 3. INTELLIGENCE & GOVERNANCE LAYER (Right column)
    draw_box(9.6, 6.6, 5.6, 2.0, '#FAF5FF', '#8B5CF6',
             "4. Explainability & Recourse (XAI)",
             "• TreeSHAP: Exact additive feature attribution\n• Global weights: Absence (28.5%), Resources (20.2%)\n• DiCE Counterfactuals: Actionable minimal adjustments\n• Protected Demographics (Gender, Nationality) FROZEN",
             title_color='#6D28D9')

    draw_box(9.6, 4.0, 5.6, 2.0, '#FEF2F2', '#EF4444',
             "5. Fairness & Ethical Governance",
             "• Fairlearn Disparity Audits (EEOC 80% Rule)\n• Demographic Parity Ratio: 0.982 across Gender\n• Equalized Odds Gap: Within acceptable bounds\n• Non-causal Framing & Plain-English Interpretations",
             title_color='#B91C1C')

    draw_box(9.6, 1.4, 5.6, 2.0, '#FFFBEB', '#F59E0B',
             "6. Cohort Policy Simulation",
             "• 500-Run Monte Carlo Stochastic Engine\n• What-If Institutional Policy Scenario Modeling\n• Engagement +15% -> +7.7 pp High\n• Attendance Drive -> -8.2 pp Low Risk",
             title_color='#B45309')

    draw_arrow(8.6, 6.7, 9.6, 7.3, '#8B5CF6', '->', 2)
    draw_arrow(8.6, 5.7, 9.6, 5.0, '#EF4444', '->', 2)
    draw_arrow(8.6, 4.8, 9.6, 2.7, '#F59E0B', '->', 2)

    # 4. SERVING & PRESENTATION LAYER (Bottom Left & Center)
    draw_box(0.8, 0.6, 3.4, 1.8, '#F0FDF4', '#22C55E',
             "7. FastAPI REST Microservice",
             "• Endpoints: GET /health, POST /predict\n• Pydantic v2 Contract Validation\n• Sub-10ms CPU Inference Latency\n• Full Probability & SHAP Payloads",
             title_color='#15803D')

    draw_box(5.0, 0.6, 3.6, 1.8, '#F0F9FF', '#0284C7',
             "8. Streamlit Decision Hub",
             "• 7 Interactive Pages (Overview to Ethics)\n• Dynamic What-If Slider Engine\n• 100% Inference Parity with API\n• Accessible Academic UI Design System",
             title_color='#0369A1')

    draw_arrow(6.8, 4.5, 6.8, 2.4, '#0284C7', '<->', 2, 'Bundle')
    draw_arrow(5.0, 1.5, 4.2, 1.5, '#64748B', '<->', 1.5, 'Sync')
    draw_arrow(5.0, 4.7, 3.5, 2.4, '#15803D', '->', 1.5)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "system_architecture.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved docs/diagrams/system_architecture.png")


def create_ml_pipeline():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(8, 8.5, "Student Performance Prediction System — Machine Learning Pipeline", 
            ha='center', va='center', fontsize=18, fontweight='bold', color='#0F172A')
    ax.text(8, 8.1, "Rigorous, Leak-Free Preprocessing, 5-Fold Stratified Validation, and Model Arena Evaluation", 
            ha='center', va='center', fontsize=11, color='#475569')

    # Draw steps horizontally
    steps = [
        ("Step 1: Ingestion & Validation", 
         "• xAPI-Edu-Data (N=478)\n• 16 Features (4 num, 12 cat)\n• Duplicates Dropped (N=2)\n• Range Check: [0, 100]\n• Pydantic Schema Check", 
         '#EFF6FF', '#2563EB', '#1D4ED8'),
        ("Step 2: Train/Test Split", 
         "• 80/20 Stratified Split\n• Training: N=382\n• Holdout Test: N=96\n• Stratification by Class\n• Fixed Random Seed (42)", 
         '#F0FDF4', '#16A34A', '#15803D'),
        ("Step 3: ColumnTransformer", 
         "• Fit strictly on Train Folds\n• StandardScaler: 4 Continuous\n• OneHotEncoder: 8 Nominal\n• OrdinalEncoder: 4 Binary\n• Zero Data Leakage", 
         '#FAF5FF', '#9333EA', '#7E22CE'),
        ("Step 4: 5-Fold Model Arena", 
         "• Stratified 5-Fold CV\n• Random Forest: 82.29%\n• Logistic Reg: 73.96%\n• Gradient Boost: 70.83%\n• Decision Tree: 69.79%", 
         '#FFFBEB', '#D97706', '#B45309'),
        ("Step 5: Statistical Audit", 
         "• McNemar's Test: p=0.0143\n• Bootstrap 95% Macro-F1:\n  [0.7521, 0.8984]\n• Cohen's Kappa: 0.7285\n• 0 Severe Errors (0/96)", 
         '#ECFDF5', '#059669', '#047857'),
    ]

    for i, (title, content, bg, border, tcolor) in enumerate(steps):
        x = 0.5 + i * 3.1
        y = 3.6
        w = 2.7
        h = 3.8
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                      facecolor=bg, edgecolor=border, linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.4, title, ha='center', va='top', 
                fontsize=10, fontweight='bold', color=tcolor, zorder=3)
        ax.text(x + w/2, y + (h - 0.5)/2, content, ha='center', va='center', 
                fontsize=8.5, color='#334155', multialignment='center', zorder=3)

        if i < len(steps) - 1:
            arrow = patches.FancyArrowPatch((x + w + 0.05, y + h/2), (x + w + 0.35, y + h/2),
                                            arrowstyle='->', color='#64748B', linewidth=2,
                                            mutation_scale=15, zorder=1)
            ax.add_patch(arrow)

    # Bottom summary box for Champion Artifact
    rect_bottom = patches.FancyBboxPatch((1.5, 0.8), 13.0, 2.0, boxstyle="round,pad=0.15",
                                         facecolor='#F8FAFC', edgecolor='#0F172A', linewidth=1.5, zorder=2)
    ax.add_patch(rect_bottom)
    ax.text(8.0, 2.3, "Champion Model Serialization & Deployment Artifact (model.joblib)", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#0F172A', zorder=3)
    ax.text(8.0, 1.4, "Contains: Fitted ColumnTransformer + Tuned RandomForestClassifier + Class Mappings + Feature Metadata\nServes simultaneously: Streamlit Interactive UI (7 Pages) & FastAPI High-Performance Microservice (<10ms inference)",
            ha='center', va='center', fontsize=9.5, color='#334155', multialignment='center', zorder=3)

    arrow_down = patches.FancyArrowPatch((14.0, 3.6), (14.0, 2.8),
                                        arrowstyle='->', color='#0F172A', linewidth=2,
                                        mutation_scale=15, zorder=1)
    ax.add_patch(arrow_down)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "ml_pipeline.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved docs/diagrams/ml_pipeline.png")


def create_data_flow():
    fig, ax = plt.subplots(figsize=(15, 9), dpi=300)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(7.5, 8.5, "Student Performance Prediction System — End-to-End Data Flow", 
            ha='center', va='center', fontsize=18, fontweight='bold', color='#0F172A')
    ax.text(7.5, 8.1, "Tracing telemetry from raw input through inference, explainability, counterfactual recourse & presentation", 
            ha='center', va='center', fontsize=11, color='#475569')

    # Flow blocks
    blocks = [
        (0.6, 4.8, 3.0, 2.5, "1. User / Client Input", 
         "• Student Check-In Form\n• REST JSON Request (POST /predict)\n• 16 behavioral & academic features\n• Pydantic v2 Schema Validation", '#EFF6FF', '#3B82F6', '#1D4ED8'),
        (4.2, 4.8, 3.2, 2.5, "2. Preprocessing & Encode", 
         "• Type enforcement & imputation\n• Numeric standardization\n• One-Hot categorical expansion\n• Feature vector formulation (x)", '#FAF5FF', '#8B5CF6', '#6D28D9'),
        (8.0, 4.8, 3.2, 2.5, "3. RF Inference Engine", 
         "• Random Forest Classifier\n• Ensemble probability voting\n• Predicted Band: High / Med / Low\n• Confidence score calculation", '#ECFDF5', '#10B981', '#047857'),
        (11.8, 4.8, 2.8, 2.5, "4. Multi-Class Output", 
         "• Predicted Label\n• Probabilities: P(L), P(M), P(H)\n• Borderline Detection Flag\n• Severe Error Guardrail", '#FFFBEB', '#F59E0B', '#B45309'),
    ]

    for x, y, w, h, title, content, bg, border, tcol in blocks:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                      facecolor=bg, edgecolor=border, linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.35, title, ha='center', va='top', 
                fontsize=10.5, fontweight='bold', color=tcol, zorder=3)
        ax.text(x + w/2, y + (h - 0.4)/2, content, ha='center', va='center', 
                fontsize=8.5, color='#334155', multialignment='center', zorder=3)

    # Arrows between top blocks
    for i in range(len(blocks) - 1):
        x1 = blocks[i][0] + blocks[i][2]
        y1 = blocks[i][1] + blocks[i][3]/2
        x2 = blocks[i+1][0]
        y2 = blocks[i+1][1] + blocks[i+1][3]/2
        arrow = patches.FancyArrowPatch((x1 + 0.05, y1), (x2 - 0.05, y2),
                                        arrowstyle='->', color='#64748B', linewidth=2,
                                        mutation_scale=15, zorder=1)
        ax.add_patch(arrow)

    # Lower Intelligence Branches
    intel_blocks = [
        (4.2, 1.2, 4.5, 2.5, "5. XAI: TreeSHAP Attributions", 
         "• Exact Shapley local values (phi_i)\n• Decomposes prediction into pushing/pulling forces\n• Identifies primary academic deficits (e.g. Absences)\n• Contextualizes risk for educators", '#FEF2F2', '#EF4444', '#B91C1C'),
        (9.3, 1.2, 5.1, 2.5, "6. Recourse: DiCE Counterfactuals", 
         "• Generates minimal viable behavioral shift (delta_x)\n• Demographics (Gender, Nationality) STRICTLY FROZEN\n• Feasible, monotonic engagement increases\n• Prescriptive actions (e.g. Visits: 18 -> 65)", '#F0FDF4', '#22C55E', '#15803D')
    ]

    for x, y, w, h, title, content, bg, border, tcol in intel_blocks:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                      facecolor=bg, edgecolor=border, linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.35, title, ha='center', va='top', 
                fontsize=10.5, fontweight='bold', color=tcol, zorder=3)
        ax.text(x + w/2, y + (h - 0.4)/2, content, ha='center', va='center', 
                fontsize=8.5, color='#334155', multialignment='center', zorder=3)

    # Branching arrows
    arrow_shap = patches.FancyArrowPatch((9.6, 4.8), (6.5, 3.7),
                                         arrowstyle='->', color='#EF4444', linewidth=1.8,
                                         mutation_scale=15, zorder=1)
    ax.add_patch(arrow_shap)

    arrow_dice = patches.FancyArrowPatch((13.2, 4.8), (11.8, 3.7),
                                         arrowstyle='->', color='#22C55E', linewidth=1.8,
                                         mutation_scale=15, zorder=1)
    ax.add_patch(arrow_dice)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "data_flow.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved docs/diagrams/data_flow.png")


if __name__ == "__main__":
    create_system_architecture()
    create_ml_pipeline()
    create_data_flow()
