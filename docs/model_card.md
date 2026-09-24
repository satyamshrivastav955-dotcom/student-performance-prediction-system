# Model Card: Student Performance Prediction System (SPPS)

## 1. Model Details

- **Model Name:** Random Forest Ensemble Classifier (`RandomForestClassifier`)
- **Model Version:** 1.0.0 (Production Release)
- **Model Architecture:** Bagged ensemble of decision trees with cost-complexity pruning and bootstrap aggregation
- **Developer:** Satyam Shrivastav (Computer Engineering, Capstone Project for SkillOrbit)
- **Serialization Format:** Python `joblib` bundle (`models/model.joblib`), encapsulating both the scikit-learn `ColumnTransformer` preprocessing pipeline and the fitted tree estimator.
- **License:** MIT License

---

## 2. Intended Use & Target Users

### Primary Intended Use
The system is designed strictly as a **decision-support early-warning tool** for educators, academic advisors, and institutional retention committees. Its primary purpose is to:
1. Identify students exhibiting behavioural telemetry patterns associated with academic underperformance (Low band) before summative examinations.
2. Provide transparent, game-theoretic explanations (TreeSHAP) illustrating which behavioral factors are driving the assessment.
3. Offer minimal viable counterfactual pathways (DiCE) to inform targeted pedagogical interventions.

### Target Users
- **Course Instructors & Lecturers:** To identify disengaged students early and tailor classroom participation initiatives.
- **Academic Counselors & Advisors:** To hold evidence-based guidance sessions with at-risk students.
- **Department Heads & Deans:** To evaluate class-level cohort dynamics and simulate policy changes (e.g., LMS resource enrichment).

### Out-of-Scope & Prohibited Applications
- **Automated Grading:** Never to be used to assign official grades or academic credentials.
- **Punitive Action or Disciplinary Tracking:** Never to be used to justify disciplinary sanctions or academic expulsion.
- **Admissions & High-Stakes Streaming:** Prohibited from screening incoming applicants or tracking students into restrictive educational tracks.
- **Autonomous Decision-Making:** Prohibited from executing interventions without human-in-the-loop educator review.

---

## 3. Training & Validation Data

- **Dataset:** xAPI-Edu-Data benchmark (Amrieh, Hamtini, & Aljarah, 2016).
- **Cohort Size:** $N = 478$ unique students (480 raw instances, 2 exact duplicates eliminated).
- **Data Splitting:** Stratified 80/20 train/test holdout split ($N_{\text{train}} = 382$, $N_{\text{test}} = 96$).
  - Training class distribution: Low = 100 (26.2%), Medium = 169 (44.2%), High = 113 (29.6%).
  - Test class distribution: Low = 25 (26.0%), Medium = 42 (43.8%), High = 29 (30.2%).
- **Feature Space (16 Predictors):**
  - **4 Continuous Telemetry Metrics:** `raisedhands`, `VisITedResources`, `AnnouncementsView`, `Discussion` (scaled via `StandardScaler`).
  - **9 Nominal Attributes:** `gender`, `NationalITy`, `PlaceofBirth`, `StageID`, `GradeID`, `SectionID`, `Topic`, `Semester`, `Relation` (encoded via `OneHotEncoder(handle_unknown='ignore')`).
  - **3 Binary Indicators:** `StudentAbsenceDays`, `ParentAnsweringSurvey`, `ParentschoolSatisfaction` (ordinally encoded 0/1).

---

## 4. Performance & Evaluation Summary

All evaluation metrics are computed on the untouched 20% holdout test partition ($N = 96$) and cross-validated across 5 stratified folds.

### Overall Benchmark Metrics
- **Holdout Accuracy:** **82.29%** (79 / 96 correctly classified)
- **Macro-Averaged F1-Score:** **82.82%** (0.8282)
- **Weighted F1-Score:** **82.21%** (0.8221)
- **Cohen's Kappa ($\kappa$):** **0.7285** (Substantial agreement beyond chance)
- **Severe Error Rate:** **0.0%** (0 / 96 severe misclassifications: no Actual High classified as Low; no Actual Low classified as High)
- **Bootstrap 95% Confidence Intervals (2,000 resamples):**
  - Accuracy 95% CI: `[0.7500, 0.8958]`
  - Macro-F1 95% CI: `[0.7521, 0.8984]`

### Model Arena Comparison (Holdout Test)
| Model Architecture | Test Accuracy | Test Macro-F1 | Cohen's Kappa | Severe Errors |
|:---|:---:|:---:|:---:|:---:|
| **Random Forest (Champion)** | **82.29%** | **0.8282** | **0.7285** | **0 / 96** |
| Logistic Regression | 73.96% | 0.7477 | 0.6027 | 0 / 96 |
| Gradient Boosting | 70.83% | 0.7093 | 0.5511 | 0 / 96 |
| Pruned Decision Tree | 69.79% | 0.6974 | 0.5367 | 0 / 96 |

- **McNemar's Significance Test:** Random Forest vs. Pruned Decision Tree yields discordant pairs $b = 13, c = 1$, $\chi^2 = 8.64, p = 0.0143$, confirming statistically significant superiority ($p < 0.05$).

### Holdout Confusion Matrix
```
                Predicted
              Low  Medium  High
Actual Low     23     2      0
Actual Med      5    33      4
Actual High     0     6     23
```

### Class-Wise Diagnostic Performance
- **Low (At-Risk Tier, $N=25$):** Precision: 82.1%, **Recall: 92.0%**, F1-Score: 86.8%
- **Medium (Core Tier, $N=42$):** Precision: 80.5%, Recall: 78.6%, F1-Score: 79.5%
- **High (Honors Tier, $N=29$):** Precision: 85.2%, Recall: 79.3%, F1-Score: 82.1%

---

## 5. Explainability & Counterfactual Recourse

### Global Attributions (TreeSHAP)
- Feature attributions calculated over the test set indicate that behavioral effort and attendance dominate model decisions:
  1. `StudentAbsenceDays`: 28.5% of total predictive attribution
  2. `VisITedResources`: 20.2%
  3. `raisedhands`: 11.9%
  4. `Relation`: 8.5%
  5. `AnnouncementsView`: 7.9%

### Individual Prescriptions (DiCE Counterfactuals)
- **Demographic Invariance Guarantee:** Demographic attributes (`gender`, `NationalITy`, `PlaceofBirth`) are strictly frozen during optimization. The system mathematically never suggests changing a demographic trait to improve academic outcome.
- **Empirical Feasibility:** In audit evaluations across 5 representative at-risk students, all 5/5 students achieved feasible 1–2 feature recourse paths into Medium/High performance (predominantly through attendance normalization and increased LMS resource usage).

---

## 6. Algorithmic Fairness & Ethical Audit (Fairlearn)

Fairness evaluations were conducted on holdout and cohort splits using the Fairlearn library across protected demographic groups (`gender`, `NationalITy`).
- **Demographic Parity Ratio across Gender (M vs F):** **0.982** (Substantially exceeds the EEOC 80% / 0.80 four-fifths threshold).
- **Equalized Odds Gap across Gender:** Under 0.07 across true positive and false positive rates.
- **Subgroup Caveat:** Certain national cohorts have small sample counts in the benchmark ($N < 20$, e.g., USA, Venezuela, Iran). Disparity estimates on these small sub-cohorts carry wide estimation uncertainty and must not be interpreted as definitive institutional trends.

---

## 7. Limitations & Scientific Guardrails

1. **Association vs. Causality:** The underlying dataset is cross-sectional. The model establishes statistical associations between digital telemetry and performance bands; it does not measure or prove causal pedagogical mechanisms.
2. **Behavioral Proxies:** Portal resource clicks and hand raises are behavioral proxies for engagement, not direct measurements of cognitive understanding or mastery.
3. **Institutional Specificity:** The system was developed on Kalboard 360 LMS data from a specific educational context; out-of-distribution performance on different student populations must be evaluated prior to broader deployment.
4. **Scenario Simulation Scope:** Monte Carlo cohort simulations represent synthetic model-based sensitivity analyses, not guaranteed policy outcomes.
