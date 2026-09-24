"""
scripts/generate_pptx.py
Builds the complete 20-slide academic/portfolio presentation deck
'Student_Performance_Prediction_System_Final.pptx' with professional styling,
metrics cards, architecture diagrams, screenshots, and complete speaker notes.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pathlib import Path

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette Definitions
C_NAVY = RGBColor(15, 23, 42)       # #0F172A
C_SLATE = RGBColor(71, 85, 105)     # #475569
C_DARK = RGBColor(30, 41, 59)       # #1E293B
C_LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
C_WHITE = RGBColor(255, 255, 255)
C_BLUE = RGBColor(37, 99, 235)      # #2563EB
C_EMERALD = RGBColor(5, 150, 105)   # #059669
C_PURPLE = RGBColor(124, 58, 237)   # #7C3AED
C_AMBER = RGBColor(217, 119, 6)     # #D97706
C_CARD_BG = RGBColor(241, 245, 249) # #F1F5F9
C_BORDER = RGBColor(203, 213, 225)  # #CBD5E1

blank_layout = prs.slide_layouts[6]


def add_header(slide, title_text, category="STUDENT PERFORMANCE PREDICTION SYSTEM"):
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = category.upper()
    p_c.font.size = Pt(9.5)
    p_c.font.bold = True
    p_c.font.color.rgb = C_BLUE

    # Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
    tf = t_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = C_NAVY


def add_card(slide, left, top, width, height, bg_color=C_WHITE, border_color=C_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.2)
    return shape


# ---------------------------------------------------------------------------
# SLIDE 1: Title
# ---------------------------------------------------------------------------
s1 = prs.slides.add_slide(blank_layout)
# Background rect
bg1 = add_card(s1, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), C_LIGHT_BG, C_BLUE)

tb1 = s1.shapes.add_textbox(Inches(1.4), Inches(1.5), Inches(10.5), Inches(2.2))
tf1 = tb1.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "Student Performance Prediction System"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = C_NAVY

p2 = tf1.add_paragraph()
p2.text = "An End-to-End Decision-Support Platform with Classical Ensemble ML, Game-Theoretic Explainability (TreeSHAP), Algorithmic Recourse (DiCE), and Fairness Auditing"
p2.font.size = Pt(14)
p2.font.color.rgb = C_SLATE
p2.space_before = Pt(12)

# Details card
dt_box = s1.shapes.add_textbox(Inches(1.4), Inches(4.2), Inches(10.5), Inches(1.8))
tf_dt = dt_box.text_frame
tf_dt.word_wrap = True

p3 = tf_dt.paragraphs[0]
p3.text = "Candidate: Satyam Shrivastav  |  Track: Machine Learning Capstone  |  SkillOrbit Academic Evaluation"
p3.font.size = Pt(12)
p3.font.bold = True
p3.font.color.rgb = C_DARK

p4 = tf_dt.add_paragraph()
p4.text = "Evaluated Champion: Tuned Random Forest (82.29% Accuracy, 82.82% Macro-F1, 0 Severe Errors)\nDual Deployed: Streamlit Decision Hub (7 Pages) & High-Performance FastAPI REST Microservice"
p4.font.size = Pt(11)
p4.font.color.rgb = C_SLATE
p4.space_before = Pt(6)

s1.notes_slide.notes_text_frame.text = (
    "Good morning, evaluators and faculty. Today I am presenting the completed and deployed Student Performance "
    "Prediction System for my SkillOrbit Machine Learning Capstone. In educational institutions, early warning systems "
    "are crucial for student success, but traditional tools often fail because they are either opaque black boxes or "
    "provide vague advice. In this project, we built an end-to-end platform that not only predicts academic bands with 82.3% accuracy, "
    "but explains why using SHAP, provides actionable counterfactual guidance with frozen demographics, audits fairness with Fairlearn, "
    "and serves both an interactive 7-page dashboard and a sub-10ms FastAPI endpoint. Let us begin with the problem statement."
)


# ---------------------------------------------------------------------------
# SLIDE 2: Problem Statement & Pedagogical Motivation
# ---------------------------------------------------------------------------
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "Problem Statement & Educational Context", "EDUCATIONAL DATA MINING")

# Left Column: The Challenge
add_card(s2, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), C_WHITE, C_BORDER)
tb_p1 = s2.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_p1 = tb_p1.text_frame
tf_p1.word_wrap = True

p = tf_p1.paragraphs[0]
p.text = "The Pedagogical Challenge"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = C_NAVY

points_left = [
    "Summative assessments identify learning deficits too late for proactive intervention.",
    "Traditional early-warning indicators provide arbitrary risk scores without diagnostic context.",
    "Generic guidance ('study more') fails to provide students with achievable, concrete targets.",
    "Opaque black-box models risk codifying demographic bias without oversight.",
    "Educators need evidence-based decision support, not uninterpretable machine decisions."
]
for pt in points_left:
    p = tf_p1.add_paragraph()
    p.text = "• " + pt
    p.font.size = Pt(11.5)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(8)

# Right Column: The Solution
add_card(s2, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), C_CARD_BG, C_BLUE)
tb_p2 = s2.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.6))
tf_p2 = tb_p2.text_frame
tf_p2.word_wrap = True

p = tf_p2.paragraphs[0]
p.text = "The Engineering Response"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = C_BLUE

points_right = [
    "Predictive Multi-Class Modeling: Classifies students into Low, Medium, and High performance tiers.",
    "Game-Theoretic Attribution (TreeSHAP): Isolate exact push/pull forces for every individual student.",
    "Actionable Recourse (DiCE): Compute minimal behavioral shifts while strictly freezing demographics.",
    "Algorithmic Fairness Audit: Rigorous demographic parity evaluation across gender and nationality.",
    "Dual-Channel Production: Accessible Streamlit portal + sub-10ms FastAPI REST microservice."
]
for pt in points_right:
    p = tf_p2.add_paragraph()
    p.text = "✔ " + pt
    p.font.size = Pt(11.5)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(8)

s2.notes_slide.notes_text_frame.text = (
    "In educational institutions, identifying students at risk of failing typically happens after midterm or final exams—"
    "when it is already too late for proactive intervention. Many automated tools output a simple failure percentage, but "
    "cannot explain why the student is at risk or what specific behavioral adjustments would change that outcome. "
    "Furthermore, using complex neural networks on small student datasets risks severe overfitting and hidden bias. "
    "Our system addresses this by engineering a transparent, sample-efficient classical machine learning pipeline that pairs "
    "accurate classification with individual explanation and actionable recourse."
)


# ---------------------------------------------------------------------------
# SLIDE 3: Project Objectives & Completed Scope
# ---------------------------------------------------------------------------
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Project Objectives & Completed Scope", "CAPSTONE REQUIREMENTS")

obj_cards = [
    ("1. Rigorous Data Pipeline", "Clean, deduplicate, and validate multi-modal telemetry; zero data leakage via scikit-learn ColumnTransformer fitted inside cross-validation folds.", C_BLUE),
    ("2. Classical ML Benchmark", "Evaluate Logistic Regression, Decision Trees, Random Forest, and Gradient Boosting under 5-fold CV to select the optimal sample-efficient model.", C_EMERALD),
    ("3. Actionable Explainability", "Deconstruct individual predictions with TreeSHAP and calculate minimal realistic recourse paths with DiCE while freezing protected traits.", C_PURPLE),
    ("4. Ethical Governance", "Conduct algorithmic fairness audits using Fairlearn for demographic parity and equalized odds across gender and nationality cohorts.", C_AMBER),
    ("5. Cohort Policy Simulation", "Run 500-iteration Monte Carlo stochastic simulations to test institutional intervention policies before implementation.", C_BLUE),
    ("6. Production Deployment", "Deliver dual serving surfaces: an interactive 7-page Streamlit portal and a sub-10ms FastAPI microservice, backed by 43 automated tests.", C_EMERALD),
]

for i, (title, desc, accent) in enumerate(obj_cards):
    col = i % 3
    row = i // 3
    x = Inches(0.8 + col * 4.0)
    y = Inches(1.5 + row * 2.7)
    add_card(s3, x, y, Inches(3.7), Inches(2.4), C_WHITE, accent)
    tb = s3.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), Inches(3.3), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = accent
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = C_DARK
    p2.space_before = Pt(6)

s3.notes_slide.notes_text_frame.text = (
    "Here we see the six primary objectives defined by the SkillOrbit capstone brief, all of which have been fully completed. "
    "First, building a leak-free data pipeline with multi-stage schema validation. Second, benchmarking classical models without "
    "unnecessary deep learning complexity. Third, delivering exact game-theoretic explanations and counterfactual recourse. "
    "Fourth, auditing algorithmic fairness under established regulatory guidelines. Fifth, providing policy-level cohort simulation. "
    "And sixth, deploying the entire system across both an interactive user dashboard and an enterprise REST API."
)


# ---------------------------------------------------------------------------
# SLIDE 4: Solution Architecture & Engineering Workflow
# ---------------------------------------------------------------------------
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "End-to-End System Architecture", "SYSTEM ARCHITECTURE")

# Embed diagram
diag_path = Path("docs/diagrams/system_architecture.png")
if diag_path.exists():
    s4.shapes.add_picture(str(diag_path), Inches(0.8), Inches(1.4), Inches(11.733), Inches(5.5))

s4.notes_slide.notes_text_frame.text = (
    "This high-level architecture diagram illustrates the five decoupled layers of the completed system. "
    "On the left, raw LMS telemetry flows through our data validation and leak-free preprocessing pipeline. "
    "In the center, our champion Random Forest model evaluates multi-class performance bands. "
    "On the right, predictions feed directly into our TreeSHAP explainability engine, DiCE counterfactual recourse generator, "
    "Fairlearn disparity auditor, and Monte Carlo cohort simulator. "
    "At the bottom, both our 7-page Streamlit portal and FastAPI REST service consume the identical serialized model bundle, "
    "guaranteeing zero training-serving skew and sub-10ms response times."
)


# ---------------------------------------------------------------------------
# SLIDE 5: The xAPI-Edu-Data Benchmark & Data Quality
# ---------------------------------------------------------------------------
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Dataset Provenance & Quality Engineering", "DATASET SPECIFICATIONS")

# Left Column: Data Details
add_card(s5, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), C_WHITE, C_BORDER)
tb_d1 = s5.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_d1 = tb_d1.text_frame
tf_d1.word_wrap = True

p = tf_d1.paragraphs[0]
p.text = "Benchmark Characteristics (xAPI-Edu-Data)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

specs = [
    ("Source Benchmark", "xAPI-Edu-Data (Amrieh et al., 2016)"),
    ("Target Variable", "Class (Low: 0-69, Medium: 70-89, High: 90-100)"),
    ("Cohort Size", "N = 478 unique records (2 exact duplicates purged)"),
    ("Class Balance", "Medium: 211 (44.1%), High: 142 (29.7%), Low: 125 (26.2%)"),
    ("Behavioral Features", "raisedhands, VisITedResources, AnnouncementsView, Discussion"),
    ("Contextual Indicators", "AbsenceDays, SurveyResponse, SchoolSatisfaction, Relation"),
    ("Demographics", "gender, NationalITy, PlaceofBirth, Stage, Grade, Topic, Semester")
]
for k, v in specs:
    p = tf_d1.add_paragraph()
    p.text = f"• {k}: {v}"
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(5)

# Right Column: Distribution Image
img_dist = Path("reports/figures/01_class_distribution.png")
if img_dist.exists():
    s5.shapes.add_picture(str(img_dist), Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))

s5.notes_slide.notes_text_frame.text = (
    "Turning to our dataset: we utilized the benchmark xAPI-Edu-Data dataset, capturing real student telemetry from the "
    "Kalboard 360 LMS. A key advantage of this dataset is that the target variable ships natively as three performance tiers: "
    "Low, Medium, and High—eliminating any need for arbitrary post-hoc thresholding. "
    "Notice the class distribution: Medium constitutes 44.1%, High 29.7%, and Low 26.2%. "
    "Because the at-risk Low cohort represents only a quarter of the students, evaluating models strictly on overall accuracy "
    "would be misleading. Therefore, we designated Macro-F1 as our primary optimization metric to ensure equal weighting across classes."
)


# ---------------------------------------------------------------------------
# SLIDE 6: Leak-Free Preprocessing Pipeline
# ---------------------------------------------------------------------------
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "Leak-Free Preprocessing Pipeline", "FEATURE ENGINEERING")

diag_pipe = Path("docs/diagrams/ml_pipeline.png")
if diag_pipe.exists():
    s6.shapes.add_picture(str(diag_pipe), Inches(0.8), Inches(1.4), Inches(11.733), Inches(5.5))

s6.notes_slide.notes_text_frame.text = (
    "Data leakage is a frequent flaw in academic machine learning projects. Here we detail our leak-free engineering pipeline. "
    "First, we split the 478 students into an 80% training set (382 students) and an untouched 20% holdout test set (96 students), "
    "stratifying across the target classes. "
    "Second, our scikit-learn ColumnTransformer is fitted strictly inside the training folds. "
    "Continuous engagement counters are normalized using StandardScaler, nominal categories are one-hot encoded, and binary features "
    "are mapped ordinally to maintain SHAP directional readability. "
    "The entire transformation pipeline is serialized directly inside model.joblib, ensuring that test and inference data "
    "never leak statistical properties into model parameters."
)


# ---------------------------------------------------------------------------
# SLIDE 7: Exploratory Data Analysis & Student Distributions
# ---------------------------------------------------------------------------
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Exploratory Telemetry Distributions", "EXPLORATORY DATA ANALYSIS")

img_box = Path("reports/figures/03_boxplots_by_class.png")
if img_box.exists():
    s7.shapes.add_picture(str(img_box), Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2))

# Right card: Key EDA insights
add_card(s7, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.2), C_WHITE, C_BORDER)
tb_eda = s7.shapes.add_textbox(Inches(7.4), Inches(1.8), Inches(4.8), Inches(4.6))
tf_eda = tb_eda.text_frame
tf_eda.word_wrap = True

p = tf_eda.paragraphs[0]
p.text = "Key Behavioral Observations"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = C_NAVY

eda_pts = [
    ("Platform Resource Access", "High-performing students average 78.8 LMS resource visits vs. just 18.4 for Low-performing students—a nearly 4x gap."),
    ("Classroom Participation", "Hands raised in class shows sharp tier separation (Means: Low=16.8, Med=48.9, High=70.3)."),
    ("Absence Threshold", "Over 70% of Low-performing students have >7 absences, establishing truancy as the primary risk factor."),
    ("Discussion Forum Variance", "While positive, discussion posts exhibit wider variance, indicating self-directed participation varies across topics.")
]
for title, desc in eda_pts:
    p = tf_eda.add_paragraph()
    p.text = f"• {title}: {desc}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(8)

s7.notes_slide.notes_text_frame.text = (
    "Looking at the exploratory distributions on this slide, we observe striking behavioral divergence across performance bands. "
    "In the boxplots on the left, high-achieving students open nearly four times as many digital learning resources as struggling peers "
    "(an average of 78.8 visits compared to 18.4). "
    "A similar separation is visible in classroom hand-raising, where low-performing students average under 17 interactions. "
    "Chronic absenteeism is heavily concentrated in the low band. "
    "These visual patterns strongly suggest that digital telemetry carries rich signal, but we must verify this statistically."
)


# ---------------------------------------------------------------------------
# SLIDE 8: Inferential Statistics & Effect Size Rankings
# ---------------------------------------------------------------------------
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Formal Hypothesis Testing & Effect Sizes", "STATISTICAL ANALYSIS")

img_rank = Path("reports/figures/07_effect_size_ranking.png")
if img_rank.exists():
    s8.shapes.add_picture(str(img_rank), Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2))

# Right: Statistical Table Card
add_card(s8, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.2), C_WHITE, C_BORDER)
tb_st = s8.shapes.add_textbox(Inches(7.4), Inches(1.7), Inches(4.8), Inches(4.7))
tf_st = tb_st.text_frame
tf_st.word_wrap = True

p = tf_st.paragraphs[0]
p.text = "Verified Statistical Effect Sizes"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

p2 = tf_st.add_paragraph()
p2.text = "All tests corrected via Holm-Bonferroni (FWER α = 0.05)"
p2.font.size = Pt(10)
p2.font.color.rgb = C_SLATE
p2.space_before = Pt(2)

stat_rows = [
    ("StudentAbsenceDays", "Chi-Square", "Cramer's V = 0.6798", "Enormous"),
    ("VisITedResources", "One-Way ANOVA", "eta^2 = 0.4881", "Large"),
    ("raisedhands", "One-Way ANOVA", "eta^2 = 0.4235", "Large"),
    ("ParentAnsweringSurvey", "Chi-Square", "Cramer's V = 0.4494", "Large"),
    ("Relation (Parent)", "Chi-Square", "Cramer's V = 0.3230", "Moderate"),
    ("ParentSatisfaction", "Chi-Square", "Cramer's V = 0.3155", "Moderate"),
    ("AnnouncementsView", "One-Way ANOVA", "eta^2 = 0.3106", "Large"),
    ("Discussion", "One-Way ANOVA", "eta^2 = 0.1478", "Moderate"),
]
for feat, test, eff, lbl in stat_rows:
    p = tf_st.add_paragraph()
    p.text = f"• {feat}: {eff} ({lbl})"
    p.font.size = Pt(10)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(4)

s8.notes_slide.notes_text_frame.text = (
    "Rather than relying on informal heuristics, we conducted formal hypothesis tests for every single feature against student performance. "
    "To guard against false positives across 13 distinct tests, all p-values were adjusted using the Holm-Bonferroni step-down correction at alpha 0.05. "
    "As shown in the table and chart, 12 features were confirmed statistically significant. "
    "School absences exhibited an enormous association with a Cramer's V of 0.6798. "
    "Learning resources and hand-raising yielded massive ANOVA eta-squared effect sizes of 0.4881 and 0.4235. "
    "Non-parametric Kruskal-Wallis tests simultaneously confirmed these separations without relying on normality assumptions."
)


# ---------------------------------------------------------------------------
# SLIDE 9: Machine Learning Model Arena & Selection
# ---------------------------------------------------------------------------
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "Classical Model Arena & Selection Rationale", "MODEL BENCHMARKING")

# Left Column: Arena Table
add_card(s9, Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2), C_WHITE, C_BORDER)
tb_ar = s9.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.4), Inches(4.6))
tf_ar = tb_ar.text_frame
tf_ar.word_wrap = True

p = tf_ar.paragraphs[0]
p.text = "Holdout Benchmark Performance (N = 96)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

arena_data = [
    ("Random Forest (Champion)", "82.29%", "0.8282", "0.7285", "0 / 96", C_EMERALD),
    ("Logistic Regression", "73.96%", "0.7477", "0.6027", "0 / 96", C_NAVY),
    ("Gradient Boosting", "70.83%", "0.7093", "0.5511", "0 / 96", C_NAVY),
    ("Pruned Decision Tree", "69.79%", "0.6974", "0.5367", "0 / 96", C_NAVY),
]
for name, acc, f1, kappa, sev, col in arena_data:
    p = tf_ar.add_paragraph()
    p.text = f"{name}\nAccuracy: {acc}  |  Macro-F1: {f1}  |  Kappa: {kappa}  |  Severe: {sev}"
    p.font.size = Pt(10.5)
    p.font.bold = (col == C_EMERALD)
    p.font.color.rgb = col
    p.space_before = Pt(8)

# Right Column: Why Classical Over Deep Learning
add_card(s9, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.2), C_CARD_BG, C_BLUE)
tb_dl = s9.shapes.add_textbox(Inches(7.4), Inches(1.8), Inches(4.8), Inches(4.6))
tf_dl = tb_dl.text_frame
tf_dl.word_wrap = True

p = tf_dl.paragraphs[0]
p.text = "Why Classical ML over Deep Learning?"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_BLUE

dl_reasons = [
    ("Sample Efficiency", "On tabular cohorts with N = 478, deep neural nets overfit severely and memorize noise."),
    ("Exact TreeSHAP", "Tree ensembles provide mathematically exact, additive Shapley values, unlike gradient approximations."),
    ("Constrained Recourse", "Tree decision paths allow deterministic counterfactual optimization with frozen protected demographics."),
    ("Ultra-Low Latency", "CPU execution delivers sub-10ms response times without GPU dependencies."),
    ("Statistical Justification", "McNemar's test (p = 0.0143) validates Random Forest superiority over decision tree baselines.")
]
for title, desc in dl_reasons:
    p = tf_dl.add_paragraph()
    p.text = f"✔ {title}: {desc}"
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(6)

s9.notes_slide.notes_text_frame.text = (
    "Slide 9 displays our model benchmarking results across four classical architectures. "
    "Random Forest emerged as the clear champion, achieving 82.29% holdout accuracy, 82.82% Macro-F1, and a Cohen's Kappa of 0.7285. "
    "Notice how it outperforms multinomial logistic regression by over 8 percentage points, and gradient boosting by over 11 points. "
    "Evaluators often ask: why not use deep learning? On tabular cohorts with 478 students, deep neural networks overfit rapidly. "
    "More importantly, an unexplained prediction is legally and pedagogically unusable in education. "
    "Random Forest gives us optimal sample efficiency, exact TreeSHAP attribution, and sub-10ms CPU inference."
)


# ---------------------------------------------------------------------------
# SLIDE 10: Final Model Evaluation & Benchmark Results
# ---------------------------------------------------------------------------
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "Champion Random Forest Holdout Evaluation", "FINAL EVALUATION")

# 4 Metric Cards across the top
top_metrics = [
    ("Holdout Accuracy", "82.29%", "79 / 96 Students Correct", C_BLUE),
    ("Macro-F1 Score", "82.82%", "Balanced across L / M / H", C_EMERALD),
    ("Cohen's Kappa (κ)", "0.7285", "Substantial Agreement", C_PURPLE),
    ("Severe Error Rate", "0.0%", "0 / 96 Critical Errors", C_EMERALD),
]
for i, (m_title, m_val, m_sub, m_col) in enumerate(top_metrics):
    x = Inches(0.8 + i * 3.0)
    add_card(s10, x, Inches(1.5), Inches(2.7), Inches(1.8), C_WHITE, m_col)
    tb = s10.shapes.add_textbox(x + Inches(0.15), Inches(1.65), Inches(2.4), Inches(1.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = m_title.upper()
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = C_SLATE
    p2 = tf.add_paragraph()
    p2.text = m_val
    p2.font.size = Pt(24)
    p2.font.bold = True
    p2.font.color.rgb = m_col
    p3 = tf.add_paragraph()
    p3.text = m_sub
    p3.font.size = Pt(9)
    p3.font.color.rgb = C_DARK

# Bottom Card: Confidence Intervals & Statistical Rigor
add_card(s10, Inches(0.8), Inches(3.6), Inches(11.733), Inches(3.1), C_CARD_BG, C_BORDER)
tb_bt = s10.shapes.add_textbox(Inches(1.2), Inches(3.8), Inches(11.0), Inches(2.6))
tf_bt = tb_bt.text_frame
tf_bt.word_wrap = True

p = tf_bt.paragraphs[0]
p.text = "Empirical Bootstrap & Hypothesis Validation"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = C_NAVY

b_pts = [
    "Empirical 2,000-Iteration Bootstrap: Accuracy 95% CI is [0.7500, 0.8958]; Macro-F1 95% CI is [0.7521, 0.8984].",
    "McNemar's Paired Test vs. Decision Tree: Discordant pairs b = 13, c = 1, chi-square = 8.64, p = 0.0143 (statistically significant at α = 0.05).",
    "Balanced Class-Wise Performance: F1-Scores are 86.8% for Low tier, 79.5% for Medium tier, and 82.1% for High tier.",
    "Conservative Boundary Calibration: The model favors adjacent tier errors (Low <-> Med or Med <-> High) rather than severe misclassifications."
]
for pt in b_pts:
    p = tf_bt.add_paragraph()
    p.text = "• " + pt
    p.font.size = Pt(11.5)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(6)

s10.notes_slide.notes_text_frame.text = (
    "Slide 10 details the final holdout performance of our champion Random Forest model. "
    "It attained an accuracy of 82.29%, a macro-F1 of 82.82%, and a Cohen's kappa of 0.7285, indicating substantial inter-rater reliability. "
    "Crucially, to verify that this was not an artifact of a lucky test split, we ran a 2,000-iteration empirical bootstrap, "
    "establishing that the true population Macro-F1 lies between 75.2% and 89.8% with 95% confidence. "
    "Furthermore, McNemar's exact test yields p = 0.0143, confirming that the improvement over baseline trees is statistically significant."
)


# ---------------------------------------------------------------------------
# SLIDE 11: Confusion Matrix & Error Analysis
# ---------------------------------------------------------------------------
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "Confusion Matrix & Severe Error Audit", "ERROR AUDITING")

# Left Column: Matrix Graphic / Table
add_card(s11, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), C_WHITE, C_BORDER)
tb_cm = s11.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_cm = tb_cm.text_frame
tf_cm.word_wrap = True

p = tf_cm.paragraphs[0]
p.text = "Holdout Confusion Matrix (N = 96)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

p2 = tf_cm.add_paragraph()
p2.text = (
    "                Predicted\n"
    "              Low   Medium   High\n"
    "Actual Low     23      2       0\n"
    "Actual Med      5     33       4\n"
    "Actual High     0      6      23\n"
)
p2.font.size = Pt(12)
p2.font.bold = True
p2.font.color.rgb = C_DARK
p2.space_before = Pt(12)

p3 = tf_cm.add_paragraph()
p3.text = "Diagonal elements represent correct predictions (79 / 96).\nNotice that the top-right and bottom-left corners are ZERO."
p3.font.size = Pt(10.5)
p3.font.color.rgb = C_SLATE
p3.space_before = Pt(8)

# Right Column: Error Interpretation
add_card(s11, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), C_CARD_BG, C_EMERALD)
tb_er = s11.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.6))
tf_er = tb_er.text_frame
tf_er.word_wrap = True

p = tf_er.paragraphs[0]
p.text = "Diagnostic Error Analysis"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_EMERALD

diag_pts = [
    ("Zero Severe Errors", "0 / 96 severe misclassifications. No Actual High student was predicted as Low, and no Actual Low student was predicted as High."),
    ("Class 'Low' Sensitivity", "Recall for Low-performing students is 92.0% (23 / 25 flagged), ensuring 9 out of 10 at-risk students are caught early."),
    ("Adjacent Class Errors Only", "All 17 misclassifications occurred exclusively between adjacent categories (Low <-> Med or Med <-> High)."),
    ("Borderline Sensitivity", "Misclassified instances had an average winning margin under 12%, representing genuinely borderline student engagement profiles.")
]
for title, desc in diag_pts:
    p = tf_er.add_paragraph()
    p.text = f"✔ {title}: {desc}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(6)

s11.notes_slide.notes_text_frame.text = (
    "Slide 11 breaks down our confusion matrix and severe error audit. "
    "In educational settings, not all errors are created equal. Predicting a high-achieving student as failing, or vice versa, "
    "is a severe error that destroys institutional trust. "
    "As you can see, our severe error rate is exactly 0.0%—zero out of 96 students. "
    "All 17 errors occurred between adjacent boundaries, such as a borderline Medium student scoring high enough to touch the Low threshold. "
    "Most importantly for an early warning system, our sensitivity for the Low class is 92.0%, ensuring nearly all at-risk students receive support."
)


# ---------------------------------------------------------------------------
# SLIDE 12: Game-Theoretic Explainability (TreeSHAP)
# ---------------------------------------------------------------------------
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "Game-Theoretic Explainability (TreeSHAP)", "EXPLAINABLE AI")

img_shap = Path("reports/figures/12_shap_global_importance.png")
if img_shap.exists():
    s12.shapes.add_picture(str(img_shap), Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2))

# Right Column: SHAP Principles
add_card(s12, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.2), C_WHITE, C_BORDER)
tb_sh = s12.shapes.add_textbox(Inches(7.4), Inches(1.8), Inches(4.8), Inches(4.6))
tf_sh = tb_sh.text_frame
tf_sh.word_wrap = True

p = tf_sh.paragraphs[0]
p.text = "TreeSHAP Attribution Weights"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

shap_weights = [
    ("School Absences (StudentAbsenceDays)", "28.5%", "Single largest factor determining risk"),
    ("Digital Resources (VisITedResources)", "20.2%", "Primary positive driver of high performance"),
    ("Classroom Hand Raising (raisedhands)", "11.9%", "Direct marker of lecture engagement"),
    ("Responsible Guardian (Relation)", "8.5%", "Parental involvement impact"),
    ("Announcements Read (AnnouncementsView)", "7.9%", "Adherence to course schedule"),
]
for feat, pct, note in shap_weights:
    p = tf_sh.add_paragraph()
    p.text = f"• {feat} — {pct}\n  ({note})"
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(6)

p_last = tf_sh.add_paragraph()
p_last.text = "Guaranteed Efficiency: Additive local Shapley values sum exactly to the difference between model output and expected baseline."
p_last.font.size = Pt(9.5)
p_last.font.color.rgb = C_SLATE
p_last.space_before = Pt(8)

s12.notes_slide.notes_text_frame.text = (
    "Moving to explainability on Slide 12: we integrated TreeSHAP to compute exact Shapley feature attributions. "
    "Unlike heuristic feature importance metrics, SHAP values are rooted in cooperative game theory and satisfy the axioms of efficiency, "
    "symmetry, and additivity. "
    "Globally, attendance accounts for 28.5% of total predictive weight, followed by digital learning resources at 20.2% and hand-raising at 11.9%. "
    "At the individual student level, TreeSHAP decomposes predictions into an additive waterfall, showing educators exactly which behavioral "
    "deficits dragged a student into the at-risk category."
)


# ---------------------------------------------------------------------------
# SLIDE 13: Algorithmic Recourse & Counterfactual Paths (DiCE)
# ---------------------------------------------------------------------------
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "Actionable Counterfactual Recourse (DiCE)", "ALGORITHMIC RECOURSE")

# Left Column: Principles Card
add_card(s13, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), C_WHITE, C_BORDER)
tb_cf = s13.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_cf = tb_cf.text_frame
tf_cf.word_wrap = True

p = tf_cf.paragraphs[0]
p.text = "Ethical Recourse Formulation"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

cf_rules = [
    ("Mathematical Objective", "Find minimal behavioral perturbation delta_x such that predicted class improves to Medium/High."),
    ("Strict Demographic Invariance", "Gender, Nationality, and Place of Birth are MATHEMATICALLY FROZEN. The system never suggests changing demographics."),
    ("Monotonic Actionability", "Engagement features are only permitted to increase (e.g. raise more hands, open more resources)."),
    ("Realistic Perturbation Bounds", "Feature shifts are bounded within observed student interquartile ranges (IQR).")
]
for title, desc in cf_rules:
    p = tf_cf.add_paragraph()
    p.text = f"✔ {title}: {desc}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(8)

# Right Column: Empirical Example Card
add_card(s13, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), C_CARD_BG, C_PURPLE)
tb_ex = s13.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.6))
tf_ex = tb_ex.text_frame
tf_ex.word_wrap = True

p = tf_ex.paragraphs[0]
p.text = "Verified Recourse Case Study"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_PURPLE

p2 = tf_ex.add_paragraph()
p2.text = "Student Profile (Evaluated At-Risk Instance):"
p2.font.size = Pt(12)
p2.font.bold = True
p2.font.color.rgb = C_NAVY
p2.space_before = Pt(6)

p3 = tf_ex.add_paragraph()
p3.text = "• Baseline: Visits = 15, Raised Hands = 10, Absences = Above-7\n• Predicted Band: Low (88% Confidence)"
p3.font.size = Pt(11)
p3.font.color.rgb = C_DARK
p3.space_before = Pt(4)

p4 = tf_ex.add_paragraph()
p4.text = "Minimal Actionable Pathway Generated by DiCE:"
p4.font.size = Pt(12)
p4.font.bold = True
p4.font.color.rgb = C_PURPLE
p4.space_before = Pt(10)

p5 = tf_ex.add_paragraph()
p5.text = (
    "1. Increase resource visits from 15 to 65 (+50 visits)\n"
    "2. Reduce semester absences from Above-7 to Under-7\n\n"
    "Result: Predicted band shifts to Medium (81% confidence).\n"
    "Audit Finding: 5 / 5 evaluated at-risk students found feasible 1–2 feature recourse paths."
)
p5.font.size = Pt(11)
p5.font.color.rgb = C_DARK
p5.space_before = Pt(4)

s13.notes_slide.notes_text_frame.text = (
    "Slide 13 presents our counterfactual recourse engine using DiCE. "
    "A prediction only tells an educator where a student is; counterfactuals show how to change that outcome. "
    "We formulate this as a constrained optimization problem seeking the minimal behavioral shift necessary to reach a higher academic band. "
    "Most importantly, protected demographic attributes—such as gender, nationality, and place of birth—are mathematically frozen. "
    "As shown in the verified case study, for a student predicted Low, increasing resource visits and reducing absences shifts their prediction to Medium with 81% confidence. "
    "In our audit, 100% of tested at-risk students had realistic, feasible 1-to-2 feature recourse pathways."
)


# ---------------------------------------------------------------------------
# SLIDE 14: Prescriptive Recommendation Engine
# ---------------------------------------------------------------------------
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "Prescriptive Recommendation Engine", "DECISION SUPPORT")

rec_cards = [
    ("Attendance Intervention", "Flagged when absences exceed 7 days. Action: Deploy mentor check-in within 48 hours; investigate transportation or personal barriers.", C_AMBER),
    ("LMS Learning Resources", "Flagged when resource visits fall below cohort median (<45). Action: Provide structured reading modules and guided lab exercises.", C_BLUE),
    ("Active Hand-Raising", "Flagged when lecture participation is below 20. Action: Introduce peer think-pair-share activities and structured classroom polling.", C_EMERALD),
    ("Discussion Board Engagement", "Flagged when discussion forum posts <15. Action: Assign low-stakes collaborative discussion prompts and peer Q&A credits.", C_PURPLE),
]

for i, (title, desc, acc) in enumerate(rec_cards):
    col = i % 2
    row = i // 2
    x = Inches(0.8 + col * 5.9)
    y = Inches(1.5 + row * 2.7)
    add_card(s14, x, y, Inches(5.6), Inches(2.4), C_WHITE, acc)
    tb = s14.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2), Inches(5.0), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = acc
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_DARK
    p2.space_before = Pt(8)

s14.notes_slide.notes_text_frame.text = (
    "Slide 14 outlines our prescriptive recommendation engine. "
    "We translate counterfactual mathematical outputs into concrete, plain-English pedagogical guidance. "
    "For instance, when attendance is flagged, the system does not simply print 'attend class'; it advises scheduling a 48-hour mentor check-in "
    "to identify root causes. "
    "When resource interaction is low, it suggests assigning structured reading packages. "
    "We emphasize throughout that these recommendations are evidence-based hypotheses for educators to test, not contractual guarantees."
)


# ---------------------------------------------------------------------------
# SLIDE 15: Cohort-Level Analytics & Topic Breakdown
# ---------------------------------------------------------------------------
s15 = prs.slides.add_slide(blank_layout)
add_header(s15, "Cohort Performance Patterns & Subject Analysis", "COHORT ANALYTICS")

img_topic = Path("reports/figures/10_topic_breakdown.png")
if img_topic.exists():
    s15.shapes.add_picture(str(img_topic), Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2))

# Right Column: Analytical Insights
add_card(s15, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.2), C_WHITE, C_BORDER)
tb_an = s15.shapes.add_textbox(Inches(7.4), Inches(1.8), Inches(4.8), Inches(4.6))
tf_an = tb_an.text_frame
tf_an.word_wrap = True

p = tf_an.paragraphs[0]
p.text = "Subject Performance Patterns"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

topic_insights = [
    ("Subject Differences", "Analysis across 12 subjects reveals varying performance distributions (Cramer's V = 0.2269, p = 0.0034)."),
    ("High-Engagement Subjects", "Courses such as Biology and Geology exhibit higher proportions of High-performing students."),
    ("Struggling Subjects", "IT and History show higher concentrations of Low-tier students, correlating with lower portal resource visits."),
    ("Non-Longitudinal Integrity", "We strictly classify these as cross-sectional 'Performance Patterns' rather than longitudinal trends, upholding scientific rigor.")
]
for title, desc in topic_insights:
    p = tf_an.add_paragraph()
    p.text = f"• {title}: {desc}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(8)

s15.notes_slide.notes_text_frame.text = (
    "On Slide 15, we zoom out from individual students to cohort-level analytics across 12 academic subjects. "
    "The data reveals significant subject-level variation, with Cramér's V = 0.2269. "
    "Subjects like Biology and Geology show elevated proportions of High performers, whereas IT and History have higher Low-tier concentration, "
    "correlating with lower portal interaction. "
    "In keeping with academic rigor, we deliberately label these 'Performance Patterns' rather than claiming longitudinal trends, "
    "accurately reflecting the cross-sectional nature of the dataset."
)


# ---------------------------------------------------------------------------
# SLIDE 16: Algorithmic Fairness Audit (Fairlearn)
# ---------------------------------------------------------------------------
s16 = prs.slides.add_slide(blank_layout)
add_header(s16, "Algorithmic Fairness & Demographic Audit", "RESPONSIBLE AI")

# Left: Audit Metric Cards
add_card(s16, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), C_WHITE, C_BORDER)
tb_fn = s16.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_fn = tb_fn.text_frame
tf_fn.word_wrap = True

p = tf_fn.paragraphs[0]
p.text = "Fairlearn Demographic Audit Results"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

fn_metrics = [
    ("Demographic Parity Ratio (Gender)", "0.982", "Passed (EEOC 80% Rule requires >= 0.80)"),
    ("Demographic Parity Difference", "0.052", "Minimal difference between Male and Female"),
    ("Equalized Odds Gap", "< 0.070", "True positive & false positive balance"),
    ("Four-Fifths Rule Status", "COMPLIANT", "No systematic disparate impact detected across gender")
]
for name, val, desc in fn_metrics:
    p = tf_fn.add_paragraph()
    p.text = f"• {name}: {val}\n  Status: {desc}"
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(6)

# Right: Limitations & Nuance
add_card(s16, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), C_CARD_BG, C_AMBER)
tb_fn2 = s16.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.6))
tf_fn2 = tb_fn2.text_frame
tf_fn2.word_wrap = True

p = tf_fn2.paragraphs[0]
p.text = "Responsible AI Disclaimers & Subgroup Limits"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_AMBER

disclaimers = [
    ("No Absolute Bias Claims", "We do NOT claim the model is 'unbiased'; rather, we present verified empirical audit metrics."),
    ("Subgroup Sample Size", "Nationalities with small samples (N < 20, e.g. USA, Venezuela, Iran) have wide estimation bounds."),
    ("Protected Attributes", "Gender and Nationality are NEVER used as basis for adverse action or counterfactual recommendations."),
    ("Continuous Monitoring", "Fairness metrics must be re-audited whenever new semester cohorts are ingested.")
]
for title, desc in disclaimers:
    p = tf_fn2.add_paragraph()
    p.text = f"⚠ {title}: {desc}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(8)

s16.notes_slide.notes_text_frame.text = (
    "Slide 16 details our algorithmic fairness audit conducted using the Fairlearn library. "
    "Educational machine learning requires strict governance. We evaluated Demographic Parity and Equalized Odds across protected attributes. "
    "Across gender, our Demographic Parity Ratio is 0.982, comfortably surpassing the EEOC four-fifths standard of 0.80. "
    "In keeping with academic honesty, we do not make sweeping claims that the model is 'completely unbiased'. "
    "We document that smaller nationality subgroups with sample sizes under 20 carry wider statistical uncertainty and require ongoing audit."
)


# ---------------------------------------------------------------------------
# SLIDE 17: Monte Carlo Cohort Policy Simulation
# ---------------------------------------------------------------------------
s17 = prs.slides.add_slide(blank_layout)
add_header(s17, "Monte Carlo Cohort Policy Simulation", "POLICY SIMULATION")

# Left Column: Simulator Method
add_card(s17, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), C_WHITE, C_BORDER)
tb_sim = s17.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_sim = tb_sim.text_frame
tf_sim.word_wrap = True

p = tf_sim.paragraphs[0]
p.text = "Stochastic Simulation Engine (500 Runs)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

sim_desc = [
    "Simulates institutional policy interventions across all 478 students simultaneously.",
    "Applies stochastic Gaussian perturbation to behavioral parameters with clipping to [0, 100].",
    "Generates empirical 95% confidence intervals across 500 independent Monte Carlo draws.",
    "Framed strictly as model-based scenario exploration, NOT guaranteed causal intervention."
]
for pt in sim_desc:
    p = tf_sim.add_paragraph()
    p.text = "• " + pt
    p.font.size = Pt(11.5)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(8)

# Right Column: Policy Scenario Table
add_card(s17, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), C_CARD_BG, C_BLUE)
tb_scen = s17.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.6))
tf_scen = tb_scen.text_frame
tf_scen.word_wrap = True

p = tf_scen.paragraphs[0]
p.text = "Tested Institutional Policy Scenarios"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_BLUE

scenarios = [
    ("Classroom Engagement (+15%)", "+7.7 pp High tier", "Active learning initiative lifts borderline students"),
    ("Attendance Drive (Truancy Cut)", "-8.2 pp Low tier", "Reduces at-risk student body significantly"),
    ("Digital Resources (+25%)", "+4.4 pp High tier", "Expanding LMS module accessibility"),
    ("Full Support Package", "+16.7 pp High tier", "Combined attendance + LMS + participation")
]
for name, shift, note in scenarios:
    p = tf_scen.add_paragraph()
    p.text = f"✔ {name}:\n  Impact: {shift} ({note})"
    p.font.size = Pt(11)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(6)

s17.notes_slide.notes_text_frame.text = (
    "Slide 17 covers our Monte Carlo cohort policy simulator. "
    "Administrators need to know how school-wide initiatives might impact overall grade distributions. "
    "We model this through 500 stochastic simulation iterations over the entire student body. "
    "For example, a 15% increase in classroom engagement yields a simulated +7.7 percentage-point expansion in high-performing students. "
    "An attendance drive cutting chronic truancy reduces the low-performing cohort by 8.2 percentage points. "
    "We clearly communicate to stakeholders that these represent model-based scenario explorations to guide policy planning, not guaranteed causal outcomes."
)


# ---------------------------------------------------------------------------
# SLIDE 18: Streamlit Decision Hub (7 Interactive Views)
# ---------------------------------------------------------------------------
s18 = prs.slides.add_slide(blank_layout)
add_header(s18, "Streamlit Decision Hub: 7 Operational Views", "USER INTERFACE")

img_dash = Path("docs/screenshots/01_overview.png")
if img_dash.exists():
    s18.shapes.add_picture(str(img_dash), Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2))

# Right Column: View Directory
add_card(s18, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.2), C_WHITE, C_BORDER)
tb_ui = s18.shapes.add_textbox(Inches(7.4), Inches(1.7), Inches(4.8), Inches(4.7))
tf_ui = tb_ui.text_frame
tf_ui.word_wrap = True

p = tf_ui.paragraphs[0]
p.text = "Operational View Directory"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

views = [
    ("1. Overview", "Telemetry distributions, attendance cross-tabs, effect rankings"),
    ("2. Student Check-In", "Real-time inference, probability distribution, SHAP waterfall"),
    ("3. Explore Improvements", "Live What-If behavioral sliders with instant recalculation"),
    ("4. Class Insights", "500-run Monte Carlo policy simulation visualizer"),
    ("5. Trust & Fairness", "Model comparison arena & Fairlearn demographic audit"),
    ("6. Cohort Analytics", "Topic-wise performance patterns & correlation matrices"),
    ("7. About Project", "Data dictionary, academic citations, model card documentation")
]
for v_name, v_desc in views:
    p = tf_ui.add_paragraph()
    p.text = f"• {v_name}: {v_desc}"
    p.font.size = Pt(10)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(4)

s18.notes_slide.notes_text_frame.text = (
    "Slide 18 showcases our deployed Streamlit Decision Hub. "
    "Structured into seven purpose-built operational views, it serves both classroom teachers and institutional administrators. "
    "Features include student check-in with SHAP waterfalls, real-time What-If sliders, class-wide intervention simulation, "
    "and a dedicated Trust & Fairness governance panel. "
    "The interface follows a clean, accessible design system with responsive layouts and full mobile support."
)


# ---------------------------------------------------------------------------
# SLIDE 19: FastAPI Microservice, Testing (43/43 Passed) & CI
# ---------------------------------------------------------------------------
s19 = prs.slides.add_slide(blank_layout)
add_header(s19, "FastAPI Microservice & Automated Testing", "DEPLOYMENT & CI")

# Left: API Details
add_card(s19, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), C_WHITE, C_BORDER)
tb_api = s19.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_api = tb_api.text_frame
tf_api.word_wrap = True

p = tf_api.paragraphs[0]
p.text = "FastAPI Production Microservice"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

api_bullets = [
    ("Endpoints", "GET /health, POST /predict, POST /explain, GET /docs"),
    ("Pydantic v2 Contracts", "Strict input boundary validation with 422 error handlers"),
    ("Sub-10ms Latency", "Model pre-warmed at startup for zero-cold-start inference"),
    ("100% Serving Parity", "Shares exact model.joblib artifact with Streamlit UI"),
    ("Self-Documenting", "Interactive OpenAPI Swagger UI at /docs and ReDoc")
]
for title, desc in api_bullets:
    p = tf_api.add_paragraph()
    p.text = f"✔ {title}: {desc}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(6)

# Right: Test Suite Details
add_card(s19, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), C_CARD_BG, C_EMERALD)
tb_tst = s19.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.6))
tf_tst = tb_tst.text_frame
tf_tst.word_wrap = True

p = tf_tst.paragraphs[0]
p.text = "Automated Test Suite & CI (43 / 43 Passed)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_EMERALD

test_bullets = [
    ("test_preprocess.py (13 tests)", "Verifies zero duplicates, missing value imputation, boundary clipping, and encoding round-trips."),
    ("test_models.py (16 tests)", "Asserts model serialization, probability sum = 1.0, and 100% mathematical inference parity between API and UI."),
    ("test_api.py (14 tests)", "Validates HTTP status codes, schema bounds, and health endpoint contracts."),
    ("Continuous Integration", "GitHub Actions workflow runs pipeline, test suite, and linting on every commit.")
]
for title, desc in test_bullets:
    p = tf_tst.add_paragraph()
    p.text = f"✔ {title}: {desc}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(6)

s19.notes_slide.notes_text_frame.text = (
    "On Slide 19, we highlight our production engineering rigor. "
    "In addition to the web UI, we deployed a high-performance FastAPI REST microservice capable of sub-10 millisecond inference per student. "
    "Crucially, our automated test suite contains 43 unit and integration tests covering preprocessing, model persistence, and REST endpoints. "
    "The test suite explicitly asserts 100% mathematical parity between API and dashboard outputs, eliminating training-serving skew. "
    "All 43 tests pass under automated continuous integration via GitHub Actions."
)


# ---------------------------------------------------------------------------
# SLIDE 20: Conclusion & Academic Impact
# ---------------------------------------------------------------------------
s20 = prs.slides.add_slide(blank_layout)
add_header(s20, "Academic Conclusion & Capstone Summary", "PROJECT COMPLETION")

# Left Column: Summary Card
add_card(s20, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), C_WHITE, C_BORDER)
tb_cn = s20.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_cn = tb_cn.text_frame
tf_cn.word_wrap = True

p = tf_cn.paragraphs[0]
p.text = "Capstone Key Accomplishments"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_NAVY

achievements = [
    "Predictive Accuracy: Champion Random Forest achieves 82.29% accuracy, 82.82% Macro-F1, and zero severe errors.",
    "Statistical Discipline: 12 features confirmed statistically significant under Holm-Bonferroni corrected ANOVA and Chi-Square tests.",
    "Actionable Transparency: Unified TreeSHAP attributions and DiCE counterfactuals with strictly frozen protected attributes.",
    "Responsible AI: Demographic Parity Ratio of 0.982 across gender, complying with EEOC regulatory standards.",
    "Production Ready: Multi-surface deployment with Streamlit Decision Hub, sub-10ms FastAPI service, and 43 passing tests."
]
for pt in achievements:
    p = tf_cn.add_paragraph()
    p.text = "✔ " + pt
    p.font.size = Pt(11)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(6)

# Right Column: Future Work Card
add_card(s20, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), C_CARD_BG, C_PURPLE)
tb_fw = s20.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.6))
tf_fw = tb_fw.text_frame
tf_fw.word_wrap = True

p = tf_fw.paragraphs[0]
p.text = "Responsible Future Directions"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_PURPLE

fw_pts = [
    ("Multi-Institutional Cohorts", "Validating the model against external LMS environments across diverse higher-education campuses."),
    ("Longitudinal Tracking", "Collecting multi-semester temporal telemetry to model retention trajectories over multiple years."),
    ("Educator In-the-Loop Feedback", "Capturing qualitative feedback from academic advisors to refine recommendation phrasing."),
    ("Intervention Efficacy Studies", "Conducting prospective A/B studies to measure actual graduation and grade improvements following algorithmic early-warning alerts.")
]
for title, desc in fw_pts:
    p = tf_fw.add_paragraph()
    p.text = f"• {title}: {desc}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_DARK
    p.space_before = Pt(8)

s20.notes_slide.notes_text_frame.text = (
    "To conclude on Slide 20: the Student Performance Prediction System successfully fulfills every objective of the SkillOrbit capstone project. "
    "We have demonstrated that classical ensemble machine learning, when combined with statistical rigor and responsible AI practices, "
    "delivers superior accuracy, complete transparency, and actionable utility on educational data without unnecessary complexity. "
    "The system is fully tested, evaluated, and deployed, providing an end-to-end framework for data analysis, performance prediction, "
    "explanation, recommendation, what-if exploration, cohort simulation, and ethical decision support. "
    "Thank you very much for your time, and I am now pleased to take your questions."
)

prs.save("Student_Performance_Prediction_System_Final.pptx")
print("Saved Student_Performance_Prediction_System_Final.pptx (20 slides with complete speaker notes)")
