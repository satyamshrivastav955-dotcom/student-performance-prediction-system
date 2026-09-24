# Methodology: Student Performance Prediction System

## 1. Pedagogical Problem Framing & Research Questions

Traditional educational early-warning systems often fail in practice because they:
1. Provide uninterpretable "black-box" risk scores that instructors cannot translate into targeted pedagogical support.
2. Recommend generic advice ("study harder") rather than granular, achievable behavioral modifications.
3. Risk propagating demographic disparities when models inadvertently leverage sensitive attributes.

### Research Questions
- **RQ1:** Can classical machine learning models accurately predict multi-class student performance bands (`Low`, `Medium`, `High`) using digital LMS behavioral telemetry and socio-demographic indicators without resorting to deep neural networks?
- **RQ2:** Which behavioral and academic features exhibit statistically significant associations with student performance after controlling for family-wise error rates?
- **RQ3:** How can game-theoretic explainability (SHAP) and counterfactual optimization (DiCE) be coupled to deliver actionable, pedagogically realistic recourse while strictly freezing protected demographic characteristics?
- **RQ4:** Does the model satisfy established fairness criteria (Demographic Parity and Equalized Odds) across gender and nationality cohorts?
- **RQ5:** Can stochastic Monte Carlo simulations reliably model the aggregate impact of institutional policy interventions on student cohort performance distributions?

---

## 2. Data Engineering & Preprocessing Pipeline

### 2.1 Dataset Ingestion & Validation
The dataset consists of $N = 480$ records logged by the Kalboard 360 LMS.
1. **Deduplication:** 2 exact duplicate rows across all 16 features were identified and purged, leaving $N = 478$ unique instances.
2. **Schema & Boundary Enforcement:** Telemetry counters (`raisedhands`, `VisITedResources`, `AnnouncementsView`, `Discussion`) were validated to lie strictly within $[0, 100]$.
3. **Imputation:** Median imputation was defined for continuous variables; mode imputation for categorical attributes (no missing values were observed in the final cleaned set).

### 2.2 Stratified Splitting & Leak-Free Transformation
To ensure robust evaluation:
- The cleaned dataset was partitioned into an **80% training set ($N_{\text{train}} = 382$)** and a **20% holdout test set ($N_{\text{test}} = 96$)**, stratified by the target variable `Class`.
- A scikit-learn `ColumnTransformer` was fitted strictly on training folds:
  - Continuous variables: Normalized via `StandardScaler()`.
  - Nominal variables (9 features): One-hot encoded via `OneHotEncoder(handle_unknown='ignore')`.
  - Binary variables (3 features): Encoded ordinally ($0/1$) to ensure straightforward directional interpretability.

---

## 3. Inferential Statistical Analysis

To avoid relying on informal visual heuristics, formal hypothesis testing was conducted across all 16 attributes against `Class`.

### 3.1 Continuous Features: ANOVA & Kruskal-Wallis
For continuous features across the three performance tiers:
- **One-Way ANOVA:** Computes between-group variance relative to within-group variance:
  $$F = \frac{\text{MS}_{\text{between}}}{\text{MS}_{\text{within}}}$$
- **Effect Size ($\eta^2$ - Eta Squared):**
  $$\eta^2 = \frac{\text{SS}_{\text{between}}}{\text{SS}_{\text{total}}}$$
- **Assumption Auditing:** Levene's test for equality of variance was conducted. Because variance homoscedasticity did not strictly hold for all counters, non-parametric **Kruskal-Wallis $H$ tests** were performed simultaneously. All features maintained statistical significance ($p < 10^{-14}$), confirming robust distributional separation.

### 3.2 Categorical Features: Chi-Square ($\chi^2$) & Cramér's $V$
For categorical features:
- **Pearson's Chi-Square Test of Independence:**
  $$\chi^2 = \sum \frac{(O - E)^2}{E}$$
- **Effect Size (Cramér's $V$):**
  $$V = \sqrt{\frac{\chi^2}{N \min(r-1, c-1)}}$$

### 3.3 Multiple Testing Correction: Holm-Bonferroni
To control the Family-Wise Error Rate (FWER) across 13 distinct hypothesis tests, raw $p$-values were adjusted using the **Holm-Bonferroni step-down method** at significance level $\alpha = 0.05$:
$$p_{(i)} \le \frac{\alpha}{m - i + 1}$$

#### Summary of Confirmed Statistical Effect Sizes
| Feature | Test Type | Test Statistic | Raw $p$-value | Holm Adjusted $p$ | Effect Size Metric | Value | Effect Label |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **`StudentAbsenceDays`** | Chi-Square | $\chi^2 = 215.71$ | $1.43 \times 10^{-47}$ | $1.86 \times 10^{-46}$ | Cramér's $V$ | **0.6798** | Enormous |
| **`VisITedResources`** | One-Way ANOVA | $F = 226.44$ | $8.64 \times 10^{-70}$ | $1.12 \times 10^{-68}$ | $\eta^2$ | **0.4881** | Large |
| **`raisedhands`** | One-Way ANOVA | $F = 174.50$ | $1.52 \times 10^{-57}$ | $1.97 \times 10^{-56}$ | $\eta^2$ | **0.4235** | Large |
| **`ParentAnsweringSurvey`** | Chi-Square | $\chi^2 = 90.17$ | $2.63 \times 10^{-20}$ | $2.63 \times 10^{-19}$ | Cramér's $V$ | **0.4494** | Large |
| **`Relation`** | Chi-Square | $\chi^2 = 42.14$ | $7.08 \times 10^{-10}$ | $5.66 \times 10^{-9}$ | Cramér's $V$ | **0.3230** | Moderate |
| **`ParentschoolSatisfaction`** | Chi-Square | $\chi^2 = 47.96$ | $3.86 \times 10^{-11}$ | $3.47 \times 10^{-10}$ | Cramér's $V$ | **0.3155** | Moderate |
| **`AnnouncementsView`** | One-Way ANOVA | $F = 94.63$ | $1.52 \times 10^{-34}$ | $1.67 \times 10^{-33}$ | $\eta^2$ | **0.3106** | Large |
| **`Discussion`** | One-Way ANOVA | $F = 37.49$ | $1.65 \times 10^{-15}$ | $1.65 \times 10^{-14}$ | $\eta^2$ | **0.1478** | Moderate |
| **`Topic`** | Chi-Square | $\chi^2 = 49.12$ | $0.0006$ | $0.0034$ | Cramér's $V$ | **0.2269** | Moderate |
| **`NationalITy`** | Chi-Square | $\chi^2 = 55.18$ | $0.0008$ | $0.0041$ | Cramér's $V$ | **0.2401** | Moderate |

---

## 4. Machine Learning Model Development & Validation

### 4.1 Candidate Architectures
Four classical algorithms were benchmarked:
1. **Multinomial Logistic Regression:** Linear baseline with L2 regularization.
2. **Decision Tree Classifier:** Single CART tree with cost-complexity pruning.
3. **Random Forest Classifier:** Bagged tree ensemble with bootstrap aggregation.
4. **Gradient Boosting Classifier:** Sequential residual-minimizing ensemble.

### 4.2 Cross-Validation Strategy
- **5-Fold Stratified Cross-Validation:** Hyperparameter tuning was conducted using `RandomizedSearchCV` over 40 parameter iterations per candidate.
- **Primary Optimization Metric:** **Macro-F1** score was chosen as the optimization objective to prevent bias toward the majority Medium class (44.1%) at the expense of the at-risk Low class (26.2%).

---

## 5. Model Evaluation & Statistical Significance

### 5.1 Holdout Performance
On the 96-student stratified test holdout:
- **Random Forest:** Accuracy: **82.29%**, Macro-F1: **82.82%**, Cohen's Kappa: **0.7285**, Severe Errors: **0 / 96**.
- **Logistic Regression:** Accuracy: 73.96%, Macro-F1: 74.77%, Cohen's Kappa: 0.6027.
- **Gradient Boosting:** Accuracy: 70.83%, Macro-F1: 70.93%, Cohen's Kappa: 0.5511.
- **Pruned Decision Tree:** Accuracy: 69.79%, Macro-F1: 69.74%, Cohen's Kappa: 0.5367.

### 5.2 McNemar's Paired Significance Test
To verify whether Random Forest significantly outperformed the interpretable baseline (Decision Tree):
- Contigency table of discordant pairs: $b = 13$ (RF correct, DT incorrect), $c = 1$ (DT correct, RF incorrect).
- McNemar's test statistic:
  $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c} = \frac{(|13 - 1| - 1)^2}{14} = \frac{121}{14} = 8.64$$
  $$p = 0.0143 \quad (p < 0.05)$$
  The superiority of Random Forest is statistically significant.

### 5.3 Empirical Bootstrapping (2,000 Iterations)
Empirical 95% confidence intervals were generated by sampling with replacement:
- **Accuracy 95% CI:** `[0.7500, 0.8958]`
- **Macro-F1 95% CI:** `[0.7521, 0.8984]`

---

## 6. Explainable AI & Recourse Formulation

### 6.1 TreeSHAP Attributions
Shapley values satisfy efficiency, symmetry, and additivity:
$$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} [f(S \cup \{i\}) - f(S)]$$
TreeSHAP decomposes the multi-class prediction into directional forces. Features are presented with plain-English names (e.g. `StudentAbsenceDays` $\to$ "School absence level").

### 6.2 DiCE Counterfactual Generation
The counterfactual engine solves:
$$\mathbf{x}^* = \arg\min_{\mathbf{x}'} \text{dist}(\mathbf{x}, \mathbf{x}') + \lambda (f(\mathbf{x}') - y^*)^2$$
Subject to:
1. **Demographic Invariance:** $\mathbf{x}'_{\text{demographic}} = \mathbf{x}_{\text{demographic}}$ strictly for `gender`, `NationalITy`, and `PlaceofBirth`.
2. **Actionability & Monotonicity:** Engagement features (`raisedhands`, `VisITedResources`, etc.) are only permitted to increase or remain constant.

---

## 7. Responsible AI: Fairness Audit (Fairlearn)

Using the `fairlearn` audit suite:
- **Demographic Parity Ratio:**
  $$\text{DPR} = \frac{\min_{g} P(\hat{Y} = H \mid G = g)}{\max_{g} P(\hat{Y} = H \mid G = g)}$$
  Across gender, the ratio was evaluated at **0.982**, substantially exceeding the 0.80 four-fifths regulatory threshold.
- **Equalized Odds Difference:** Assesses balance in True Positive Rates and False Positive Rates across demographic groups.

---

## 8. Stochastic Monte Carlo Cohort Simulation

To simulate institutional policy interventions across the cohort:
1. Baseline behavioral parameters are adjusted according to a proposed policy scenario (e.g. $+15\%$ classroom engagement, attendance drive).
2. For each student, perturbed features are sampled from a stochastic normal distribution truncated to $[0, 100]$.
3. Across **500 Monte Carlo simulation runs**, the model generates synthetic class distributions.
4. The mean shift and empirical 95% confidence interval are reported to institutional decision-makers.
