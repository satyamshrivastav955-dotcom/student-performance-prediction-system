# Student Performance Prediction System: Capstone Project Report
**Internship Organization:** SkillOrbit Machine Learning Capstone  
**Author:** Satyam (3rd Year, Computer Engineering)  
**Track:** Machine Learning & Classical Predictive Modeling (Type 3 / Exceptional Tier)  
**Submission Version:** 1.0.0  

---

## Executive Summary

This report documents the design, rigorous empirical evaluation, explainability architecture, and deployment of the **Student Performance Prediction System (SPPS)**. The primary objective is to accurately classify students into three academic performance tiers (**High**, **Medium**, **Low**) using student engagement and behavioural metrics, while providing transparent causal explanations (SHAP), actionable counterfactual paths (via algorithmic search), fairness audits, and policy-level cohort intervention simulations.

In strict compliance with the project guidelines prohibiting deep learning architectures or artificial complexity, this project demonstrates that **classical statistical machine learning**, coupled with rigorous hypothesis testing, disciplined cross-validation, and responsible AI practices, provides superior generalization, actionable interpretability, and robust performance on educational tabular datasets.

### Key Milestones & Quantitative Findings:
- **Cleaned Dataset:** 478 student records (exact duplicates removed, multi-stage schema validation, robust imputation).
- **Primary Driver of Performance:** Attendance (`StudentAbsenceDays`, Cramer's $V = 0.672$) and interactive platform engagement (`raisedhands`, $\eta^2 = 0.424$; `VisITedResources`, $\eta^2 = 0.402$).
- **Statistical Significance:** 12 factors confirmed statistically significant predictors under ANOVA and Chi-Square tests following **Holm-Bonferroni correction** ($\alpha = 0.05$).
- **Winning Model:** **Random Forest Classifier** achieving a test macro-F1 of **0.8282** (Accuracy: **82.29%**).
- **Statistical Justification:** 2,000-iteration empirical bootstrap establishes a 95% Confidence Interval for Macro-F1 of **[0.7478, 0.8978]**. McNemar's exact test ($p < 0.05$) formally validates the model's superiority over baseline classifiers.
- **Explainability & Recommendations:** Unified SHAP attributions at the individual student level map directly into actionable prescriptive feedback.
- **Responsible AI:** Demographic parity and equalized odds fairness audits across protected attributes (`gender`, `NationalITy`) reveal no systematic adverse impact according to the EEOC 80% rule of thumb.

---

## 1. Problem Definition & Objectives

Educational data mining seeks to identify students at risk of underperformance early enough to stage effective pedagogical interventions. Standard automated tools often suffer from two major flaws:
1. **Black-box opacity:** Providing a risk score without an understandable justification leaves educators unsure which factors to address.
2. **Generic advice:** Recommending blanket actions ("study more") rather than tailored, feasible changes grounded in the student's actual behavioral profile.

### Project Goals
1. **Accurate Classification:** Categorize students into **High (H)**, **Medium (M)**, and **Low (L)** performance bands.
2. **Statistical Rigor:** Prove which academic and socio-behavioral attributes correlate with success using formal inferential statistics.
3. **Actionable Explainability:** Deconstruct individual model decisions via SHAP game-theoretic attributions and compute minimal, realistic counterfactual scenarios.
4. **Policy-Level Simulation:** Model school-wide and classroom-wide interventions using Monte Carlo simulations to guide administrator policy decisions.
5. **Dual Deployment Surfaces:** Deliver an interactive Streamlit application and an enterprise-ready FastAPI REST service.

---

## 2. Dataset Selection & Preprocessing Pipeline

### 2.1 Dataset Choice: xAPI-Edu-Data
The system utilizes the **xAPI-Edu-Data** benchmark dataset (Amrieh, Hamtini, & Aljarah, 2016), reflecting learner interactions logged within an educational learning management system (LMS).
- **Target Variable:** `Class` with categories `L` (0-69), `M` (70-89), and `H` (90-100). The dataset naturally encodes the three-class objective specified in the SkillOrbit brief without artificial post-hoc discretization.
- **Features (16 Total):**
  - Continuous behavioral counters: `raisedhands`, `VisITedResources`, `AnnouncementsView`, `Discussion`.
  - Binary/categorical indicators: `StudentAbsenceDays` (Under-7, Above-7), `ParentAnsweringSurvey` (Yes/No), `ParentschoolSatisfaction` (Good/Bad), `Relation` (Father/Mum).
  - Demographic & academic context: `gender`, `NationalITy`, `PlaceofBirth`, `StageID`, `GradeID`, `SectionID`, `Topic`, `Semester`.

### 2.2 Preprocessing Architecture
To eliminate data leakage and ensure production consistency, preprocessing is split into two layers:
1. **Data Cleaning (`clean_dataframe`):**
   - Whitespace stripping and normalization of categorical strings.
   - Exact duplicate removal (2 duplicate rows dropped; final $N = 478$).
   - Missing value strategy: Median imputation for continuous variables, mode imputation for categorical attributes.
   - Numeric range validation: Bounded strictly between $[0, 100]$.
2. **Scikit-Learn Preprocessing Pipeline (`build_preprocessor`):**
   - Packaged inside a `ColumnTransformer` embedded directly within the serialized model artifact.
   - Continuous engagement features transformed via `StandardScaler`.
   - Nominal attributes encoded via `OneHotEncoder(handle_unknown='ignore')`.
   - Binary attributes mapped ordinally (`Under-7` $\to 0$, `Above-7` $\to 1$) to maintain interpretability in SHAP directional plots.

---

## 3. Exploratory Data Analysis & Statistical Testing

### 3.1 Class Balance
The cohort displays realistic classroom imbalance:
- **Medium (M):** 211 students (44.1%)
- **High (H):** 142 students (29.7%)
- **Low (L):** 125 students (26.2%)  
Because Low-performing students constitute only ~26% of the data, evaluation strictly prioritizes **Macro-F1** over raw accuracy to prevent majority-class bias.

### 3.2 Formal Hypothesis Testing
Rather than relying on informal visual heuristics, we conducted formal hypothesis tests for all 16 attributes against performance band `Class`. To mitigate family-wise error rate inflation across 13 distinct tests, p-values were adjusted using the **Holm-Bonferroni step-down method** ($\alpha = 0.05$).

| Feature | Statistical Test | Test Statistic | Raw $p$-value | Holm-Corrected $p$ | Effect Size Metric | Effect Size | Interpretation |
|---|---|---|---|---|---|---|---|
| **StudentAbsenceDays** | Chi-Square ($\chi^2$) | 215.71 | $1.43 \times 10^{-47}$ | $1.86 \times 10^{-46}$ | Cramer's $V$ | 0.672 | Enormous |
| **raisedhands** | One-Way ANOVA ($F$) | 174.50 | $1.52 \times 10^{-57}$ | $1.97 \times 10^{-56}$ | $\eta^2$ | 0.424 | Large |
| **VisITedResources** | One-Way ANOVA ($F$) | 159.20 | $1.72 \times 10^{-53}$ | $2.06 \times 10^{-52}$ | $\eta^2$ | 0.402 | Large |
| **AnnouncementsView** | One-Way ANOVA ($F$) | 94.63 | $1.52 \times 10^{-34}$ | $1.67 \times 10^{-33}$ | $\eta^2$ | 0.285 | Large |
| **ParentAnsweringSurvey** | Chi-Square ($\chi^2$) | 90.17 | $2.63 \times 10^{-20}$ | $2.63 \times 10^{-19}$ | Cramer's $V$ | 0.434 | Large |
| **ParentschoolSatisfaction** | Chi-Square ($\chi^2$) | 47.96 | $3.86 \times 10^{-11}$ | $3.47 \times 10^{-10}$ | Cramer's $V$ | 0.317 | Moderate |
| **Discussion** | One-Way ANOVA ($F$) | 37.49 | $1.65 \times 10^{-15}$ | $1.65 \times 10^{-14}$ | $\eta^2$ | 0.136 | Moderate |
| **Relation** | Chi-Square ($\chi^2$) | 42.14 | $7.08 \times 10^{-10}$ | $5.66 \times 10^{-9}$ | Cramer's $V$ | 0.297 | Moderate |
| **gender** | Chi-Square ($\chi^2$) | 19.34 | $6.30 \times 10^{-5}$ | $3.78 \times 10^{-4}$ | Cramer's $V$ | 0.201 | Small-Moderate |

*Assumption Auditing:* Levene’s test for equality of variance was performed for continuous metrics. Because variance equality did not strictly hold across all engagement counters, non-parametric **Kruskal-Wallis $H$** tests were conducted simultaneously; all continuous features remained significant ($p < 10^{-14}$), confirming robust distributional separation.

---

## 4. Model Training, Selection & Statistical Validation

### 4.1 Candidate Architectures & Rationale
Four classical learning algorithms representing distinct functional hypotheses were evaluated:
1. **Logistic Regression (Multinomial with L2 regularization):** Honest parametric baseline.
2. **Decision Tree (CART with cost-complexity pruning):** White-box rule model.
3. **Random Forest (Bagged tree ensemble):** Low-variance variance-reduction model.
4. **Gradient Boosting (HistGradientBoosting / XGBoost):** Sequential residual-minimizing ensemble.

*Architectural Choice:* Deep neural networks were explicitly avoided. With $N = 478$ instances, complex neural parameterizations overfit rapidly and lack the localized exact tree-path explainability required for ethical decision-support systems.

### 4.2 Cross-Validation & Test Performance
Models were tuned using `RandomizedSearchCV` (40 hyperparameter iterations over 5 stratified folds) to maximize **Macro-F1**. Held-out test metrics ($N_{test} = 96$, 20% stratified holdout) are summarized below:

| Model Architecture | 5-Fold CV Macro-F1 | Test Accuracy | Test Macro-F1 | Class 'L' F1 | Class 'M' F1 | Class 'H' F1 | Status |
|---|---|---|---|---|---|---|---|
| **Random Forest** | **0.7812** | **82.29%** | **0.8282** | **0.8679** | **0.7952** | **0.8214** | **Selected Winner** |
| Gradient Boosting | 0.7745 | 80.21% | 0.8038 | 0.8571 | 0.7711 | 0.7830 | Runner-up |
| Logistic Regression | 0.7510 | 76.04% | 0.7589 | 0.8333 | 0.7250 | 0.7184 | Baseline |
| Decision Tree | 0.7180 | 71.88% | 0.7140 | 0.8000 | 0.6905 | 0.6512 | Interpretable |

### 4.3 Statistical Significance: Bootstrapping & McNemar's Test
To ensure model selection was not an artifact of random test split sampling:
1. **Empirical Bootstrapping (2,000 Resamples):**
   - **Random Forest Macro-F1 95% CI:** `[0.7478, 0.8978]` (Point estimate: 0.8282)
   - **Gradient Boosting Macro-F1 95% CI:** `[0.7194, 0.8762]` (Point estimate: 0.8038)
2. **McNemar's Paired Test:** An exact binomial test was performed on discordant prediction pairs between Random Forest and the baseline models ($p < 0.05$), confirming that the ensemble’s superior error pattern is statistically non-random.

---

## 5. Explainability Architecture (SHAP)

### 5.1 Global Attributions
Using TreeSHAP, model attributions were calculated over the test set. Encoded one-hot categorical sub-features were re-aggregated to their parent semantic variables.
- **Top 1 Factor:** `StudentAbsenceDays` — mean absolute SHAP impact of $0.184$.
- **Top 2 Factor:** `VisITedResources` — mean absolute SHAP impact of $0.162$.
- **Top 3 Factor:** `raisedhands` — mean absolute SHAP impact of $0.151$.
- **Top 4 Factor:** `AnnouncementsView` — mean absolute SHAP impact of $0.098$.

### 5.2 Local Explanations
For every individual student query, the system decomposes predicted probabilities into additive feature attributions:
$$\text{Log-Odds}(y = C) = \phi_0 + \sum_{j=1}^M \phi_j$$
This guarantees that educators can see exactly which specific behavioral deficits pulled a student toward the 'Low' category.

---

## 6. Counterfactual Prescriptive Engine

Prediction alone is descriptive; intervention requires **prescription**.
The counterfactual engine determines the minimum perturbation $\delta$ in actionable feature space that alters the model's prediction from Low/Medium to High:
$$\min_{\mathbf{x}'} \text{dist}(\mathbf{x}, \mathbf{x}') \quad \text{s.t.} \quad f(\mathbf{x}') = \text{Target Class}$$

### Actionability Guardrails
1. **Protected Attributes Pinned:** Demographic traits (`gender`, `NationalITy`, `PlaceofBirth`) are strictly immutable.
2. **Monotonicity Enforcement:** Engagement recommendations must not suggest reducing effort.
3. **Plausibility Bounds:** Changes are bounded within observed 60% relative IQR shifts.

*Sample Real Output:*  
> *Student #34 (Actual: L, Predicted: L with 91% confidence):*  
> "If learning resource visits increase from 12 to 45 and class absences drop from Above-7 to Under-7, the predicted performance band improves to **Medium** (78% confidence)."

---

## 7. Responsible AI: Fairness Audit

Educational prediction algorithms risk reinforcing demographic disparities. Using the `fairlearn` toolkit, fairness audits were conducted across `gender` and `NationalITy`.

### Audit Metrics & Thresholds
The evaluation adopted the standard EEOC **four-fifths rule** (Demographic Parity Ratio $\ge 0.80$, Difference $\le 0.10$):

| Protected Attribute | Demographic Parity Ratio (H) | Demographic Parity Diff | Equalized Odds Gap | Verdict |
|---|---|---|---|---|
| **Gender** (M vs F) | **0.864** | **0.052** | **0.068** | **Passed** ($\ge 0.80$, no disparate impact) |
| **Nationality** (Major Groups) | **0.812** | **0.089** | **0.094** | **Passed** (No systemic violation) |

*Small-Group Caveat:* Nationalities with sample sizes $N < 20$ (e.g., USA, Iran, Venezuela in this dataset) were flagged as statistically unreliable for standalone disparity calculation, adhering to responsible reporting standards.

---

## 8. Policy-Level Cohort Simulator

To support academic deans and department heads, the system features a **Monte Carlo Cohort Simulator**. Rather than examining one student, it evaluates systemic policy shifts across all 478 students simultaneously:

| Policy Scenario | Simulated Class Shift | Mean Result (95% CI) | Administrative Interpretation |
|---|---|---|---|
| **Class Participation (+15%)** | $L \to M / H$ | Low: $-4.2\text{pp} \pm 0.8\text{pp}$ | Targeted active learning shifts ~20 borderline students out of risk. |
| **Attendance Drive (30% flip)** | $L \to M / H$ | Low: $-8.6\text{pp} \pm 1.1\text{pp}$ | Attendance initiatives provide the highest single ROI for student retention. |
| **Holistic Engagement (+15% all, 25% abs)** | $L \to M / H$ | Low: $-11.4\text{pp} \pm 1.4\text{pp}$ | High tier expands from 29.7% to 38.2% of the student body. |

---

## 9. System Deployment & Delivery

### 9.1 Streamlit Multi-Page Web Application
The user interface adheres to a clean, card-based design with an off-white background (`#FAFAFA`) and soft status badges:
- **Page 1: Overview:** Dynamic visualizations of dataset distributions, attendance cross-tabulations, and statistical effect rankings.
- **Page 2: Individual Predictor:** Real-time inference with probability distributions, SHAP waterfall cards, and prescriptive advice.
- **Page 3: What-If Simulator:** Interactive feature sliders enabling students to explore performance sensitivities live.
- **Page 4: Cohort Simulator:** Class-wide intervention modeling with Monte Carlo confidence intervals.

### 9.2 Production FastAPI REST Service
A lightweight, asynchronous REST microservice (`api/main.py`) exposes:
- `GET /health`: Service health and model status check.
- `POST /predict`: JSON payload validation via Pydantic with automated confidence intervals and top SHAP attributions.
- `GET /docs`: OpenAPI interactive specification.
- A ready-to-import Postman collection (`api/postman_collection.json`).

---

## 10. Automated Testing & Continuous Integration

The codebase contains an automated pytest test suite (`tests/`):
- `test_preprocess.py`: Verifies zero duplicates, missing value handling, clipping, and target encoding round-trips.
- `test_models.py`: Validates model serialization, output schema, and mathematical equivalence between dashboard and API inference paths.
- `test_api.py`: Tests REST endpoint responses, input boundary validation (HTTP 422), and health contracts.
- **CI Pipeline (`.github/workflows/ci.yml`):** Runs the pipeline and test suite on Python 3.11 with code coverage checks on every commit.

---

## 11. Conclusion

The Student Performance Prediction System achieves the requirements of the SkillOrbit ML Capstone project. By adhering strictly to classical machine learning and rigorous statistical principles, the project delivers:
1. **Predictive Accuracy:** 82.3% accuracy and 0.828 Macro-F1 via a tuned Random Forest pipeline.
2. **Empirical Transparency:** Full statistical significance verification (ANOVA, $\chi^2$, Holm correction, bootstrap CIs, McNemar's test).
3. **Actionable Utility:** Individual SHAP diagnostics paired with counterfactual recommendations and policy-level cohort simulations.
4. **Engineering Rigor:** Clean separation of concerns, complete test coverage, CI configuration, and multi-surface deployment.
