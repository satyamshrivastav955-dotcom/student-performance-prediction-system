# Responsible AI & Ethical Use Guidelines

## 1. Executive Summary & Purpose

The **Student Performance Prediction System (SPPS)** is engineered exclusively as a **decision-support advisory tool** to empower educators, academic counselors, and pedagogical retention teams. It uses predictive analytics to flag students exhibiting behavioral disengagement patterns before final exams.

Machine learning models deployed in educational environments carry ethical risks of stigmatization, bias amplification, and false certainty. This document establishes institutional guidelines, scientific guardrails, and operational boundaries for responsible deployment.

---

## 2. Core Ethical Principles

### Principle 1: Human-in-the-Loop Decision Support
The system **must never make autonomous decisions** regarding student standing, academic evaluation, disciplinary measures, or course access. All predictions, risk classifications, and counterfactual pathways must be reviewed and interpreted by qualified educators who possess contextual understanding of individual student circumstances.

### Principle 2: Strict Demographic Invariance
In all counterfactual recourse models (DiCE), **demographic features (`gender`, `NationalITy`, `PlaceofBirth`) are strictly frozen**. The system mathematically never suggests changing personal identity or background to achieve a better academic outcome. Prescriptions focus solely on modifiable, actionable behaviors (e.g., attending class, engaging with digital resources, participating in discussions).

### Principle 3: Transparency & Right to Explanation
No student should be labeled by a black-box model without transparent explanations. When a student is identified as needing academic support, educators have access to exact **TreeSHAP attributions** and plain-English factor breakdowns illustrating which behaviors informed the prediction.

### Principle 4: Deficit-Free Framing
System recommendations must be communicated constructively. Low predicted performance must be framed as an **opportunity for targeted support**, never as an innate deficit, fatalistic outcome, or permanent label.

---

## 3. Scientific Distinctions & Guardrails

### 3.1 Association vs. Causality
- **Empirical Reality:** The model identifies statistical correlations between digital LMS telemetry and academic performance bands.
- **Scientific Guardrail:** A strong correlation (such as `StudentAbsenceDays` Cramér's $V = 0.6798$ or `VisITedResources` $\eta^2 = 0.4881$) does **not** constitute proof of direct causality. An increase in resource clicks will not magically cause higher grades unless accompanied by genuine comprehension and active learning.

### 3.2 Recommendations are Pedagogical Hypotheses, Not Guarantees
- Counterfactual outputs (e.g. *"Increasing resource visits from 20 to 65 shifts predicted band from Low to Medium"*) indicate model decision boundaries.
- They represent **evidence-based interventions to test**, not deterministic contractual promises of academic success.

### 3.3 Cohort Simulation as Scenario Exploration
- The 500-run Monte Carlo cohort simulation demonstrates aggregate trends under synthetic behavioral shifts.
- It is a **planning and sensitivity analysis tool for administrators**, not an empirical forecast of policy outcomes.

---

## 4. Algorithmic Fairness & Subgroup Representation

### 4.1 Verified Disparity Metrics
Audits conducted via Fairlearn demonstrate that the champion Random Forest model satisfies the regulatory **four-fifths rule**:
- **Demographic Parity Ratio across Gender (M vs F):** **0.982** ($\ge 0.80$, passing).
- **Equalized Odds Gap:** Maintained below 0.07 across False Positive and True Positive rates.

### 4.2 Subgroup Sample Size Caveats
- While large demographic cohorts (e.g., Kuwait, Jordan) are well-represented, certain nationalities have small sample sizes ($N < 20$, such as USA, Venezuela, Iran).
- Disparity metrics on small sub-cohorts carry wide statistical uncertainty. Administrators must exercise caution and avoid drawing sweeping conclusions about specific minority groups from this benchmark.

---

## 5. Prohibited Uses

The following uses are **strictly prohibited**:
1. **Automated Grading:** Assigning semester grades or calculating GPA using model predictions.
2. **Admissions Screening:** Rejecting or admitting applicants based on predictive profiles.
3. **Punitive Tracking / Streaming:** Restricting students from advanced coursework or locking them into remedial tracks.
4. **Secret Profiling:** Maintaining algorithmic risk flags without the student's or guardian's knowledge.
5. **Funding Allocation Penalties:** Decreasing departmental or teacher funding based on cohort performance predictions.

---

## 6. Institutional Deployment Checklist

Before activating the system in a live institutional environment:
- [x] Educator orientation on interpreting SHAP waterfall plots and confidence intervals.
- [x] Clear guidance that probabilities represent model uncertainty, not student intelligence.
- [x] Verification that all student data stored or transmitted complies with relevant privacy regulations (e.g. FERPA, GDPR).
- [x] Human review protocol established for any student predicted in the Low performance tier.
- [x] Periodic re-auditing of model fairness metrics upon ingestion of new semester cohorts.
