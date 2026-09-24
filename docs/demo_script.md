# Live Demonstration Script: Student Performance Prediction System

**Format:** 5–7 Minute Interactive Academic & Industry Presentation  
**Target Audience:** Capstone Evaluators, Academic Faculty, Technical Reviewers  
**Presenter:** Satyam Shrivastav (Project Lead / Engineer)  
**Primary Surfaces:** Streamlit Decision Hub (`localhost:8501`) & FastAPI OpenAPI Portal (`localhost:8000/docs`)

---

## Pre-Demo Technical Checklist

- [x] Model bundle verified at `models/model.joblib`.
- [x] Streamlit running locally on `http://localhost:8501` (`streamlit run dashboard/app.py`).
- [x] FastAPI running on `http://localhost:8000` (`python -m uvicorn api.main:app --port 8000`).
- [x] Terminal ready with `pytest` execution trace (43 / 43 passed).
- [x] Pre-selected demo student in check-in interface (e.g. Student #14 or custom at-risk profile).

---

## Presentation Walkthrough (Minute-by-Minute)

### Part 1: Problem Context & Architectural Vision (0:00 – 0:45)
**Screen:** Streamlit Dashboard landing page (`1_Overview.py`), showing key metrics cards and attendance distribution.  
**Spoken Narrative:**  
> "Good morning, evaluators. In educational institutions, identifying students who are falling behind typically happens summative-style—at midterm or final exam time, when it is already too late to stage an intervention.  
> Today, I am presenting the **Student Performance Prediction System**, a completed and deployed classical machine learning platform that addresses this challenge.  
> Unlike traditional black-box models that merely issue opaque risk scores, our system delivers transparent explainability, actionable counterfactual recourse, ethical fairness auditing, and institutional policy simulations.  
> Across 478 students in our benchmark dataset, we see that attendance and learning resource engagement are the strongest statistically verified drivers of academic achievement."

---

### Part 2: Individual Student Prediction (0:45 – 1:30)
**Screen:** Navigate to `Student Check-In` (`2_Individual_Predictor.py`). Load a representative student profile with high absences (`Above-7`) and low resource visits ($18$). Click **Analyze Performance Trajectory**.  
**Spoken Narrative:**  
> "Let's examine how an educator interacts with the system. We input a student's behavioral telemetry—in this case, an individual with low resource engagement and high truancy.  
> In under 10 milliseconds, our tuned Random Forest classifier evaluates the student. Here, the system predicts the student is in the **Low performance band** with 88% confidence.  
> Notice that we display the full probability distribution—88% Low, 10% Medium, and 2% High—ensuring teachers understand the model's certainty rather than just seeing a binary label."

---

### Part 3: Game-Theoretic Explainability (TreeSHAP) (1:30 – 2:15)
**Screen:** Scroll down to the **SHAP Waterfall Attribution Card** on the same page.  
**Spoken Narrative:**  
> "Crucially, the system doesn't stop at prediction. Underneath, our TreeSHAP engine computes the exact game-theoretic attributions for this student.  
> As we can see on this waterfall plot, high school absences (`Above-7`) pushed the log-odds down by 0.28, followed by opening only 18 learning resources, which added another -0.18 penalty.  
> The teacher immediately knows *why* this student was flagged: not because of their background or demographic identity, but because of specific, observable disengagement."

---

### Part 4: Prescriptive Recommendations & Counterfactuals (2:15 – 3:00)
**Screen:** Point to the **Prescriptive Guidance & Action Card**.  
**Spoken Narrative:**  
> "Now, how does the instructor help? Traditional advice is vague: 'work harder.'  
> Our DiCE algorithmic recourse engine calculates the minimal viable behavioral perturbation to alter the prediction.  
> Notice our ethical guardrails: **all demographic attributes like gender and nationality are strictly frozen**.  
> The system recommends: 'Increase LMS resource visits from 18 to 65 and reduce absences below 7 days.' If achieved, the model's predicted trajectory shifts from Low to Medium with 78% confidence. This gives educators a concrete, measurable roadmap for intervention."

---

### Part 5: Interactive What-If Exploration (3:00 – 3:45)
**Screen:** Navigate to `Explore Improvements` (`3_What_If_Simulator.py`). Adjust the `VisITedResources` slider dynamically from 18 to 70, and toggle `StudentAbsenceDays` from Above-7 to Under-7.  
**Spoken Narrative:**  
> "In guidance counseling, advisors can use our interactive **What-If Simulator** alongside the student.  
> As I adjust the resource slider live, watch the probability gauge dynamically update in real time.  
> When absences are reduced and resource interactions reach the 70th percentile, the badge shifts from red Low to green High. This empowers students by visually demonstrating how tangible behavioral changes affect their trajectory."

---

### Part 6: Cohort Analytics & Curricular Insights (3:45 – 4:30)
**Screen:** Navigate to `Cohort Analytics` (`6_Analytics.py`). Point to the subject-wise breakdown and correlation heatmap.  
**Spoken Narrative:**  
> "At the department level, administrators need macro-level intelligence. In our Cohort Analytics page, we examine performance patterns across 12 subjects.  
> We observe that courses with heavy hands-on platform requirements, like IT and Science, exhibit strong resource-engagement correlations, whereas subjects like History rely more heavily on classroom discussion.  
> Every effect size shown here is supported by formal hypothesis testing—including ANOVA $\eta^2$ values up to 0.488 and Chi-Square Cramér's $V$ values up to 0.679, all adjusted using the Holm-Bonferroni method."

---

### Part 7: Model Evaluation & Champion Selection (4:30 – 5:15)
**Screen:** Navigate to `Trust & Fairness` (`5_Model_and_Fairness.py`), tab **Model Evaluation**. Show the Model Arena comparison and Confusion Matrix.  
**Spoken Narrative:**  
> "Let's review our machine learning benchmark. We evaluated four classical architectures through 5-fold stratified cross-validation.  
> Our champion **Random Forest** achieved **82.29% holdout accuracy**, a **Macro-F1 of 82.82%**, and a **Cohen's Kappa of 0.7285**.  
> In our holdout confusion matrix of 96 students, we recorded **zero severe errors**—meaning not a single high-performing student was predicted as low, and no low-performing student was predicted as high.  
> Furthermore, McNemar's test yielded a chi-square of 8.64 ($p = 0.0143$), confirming that Random Forest's superior error profile over pruned decision trees is statistically significant."

---

### Part 8: Algorithmic Fairness & Ethical Audit (5:15 – 5:45)
**Screen:** Switch to the **Fairness Audit** tab on the same page.  
**Spoken Narrative:**  
> "Ethical AI is a core requirement of this project. Using the Fairlearn library, we audited demographic parity and equalized odds.  
> Across gender, our Demographic Parity Ratio is **0.982**, substantially exceeding the regulatory 80% four-fifths standard.  
> We also document subgroup limitations: smaller nationality groups with $N < 20$ carry wider confidence bounds, reinforcing that this system serves as decision-support, not automated judgment."

---

### Part 9: Dual Serving Architecture & API (5:45 – 6:15)
**Screen:** Switch browser tab to `http://localhost:8000/docs` (FastAPI Swagger UI). Click `POST /predict`, click **Try it out**, click **Execute**, and view the JSON response.  
**Spoken Narrative:**  
> "Finally, the system is fully deployed. In addition to this Streamlit interface, we built a production-grade **FastAPI REST microservice** serving the identical model artifact.  
> With Pydantic v2 validation, it provides sub-10ms response times, returning class predictions, full probabilities, and top SHAP factors directly for LMS integration.  
> The entire codebase is backed by 43 automated unit and integration tests running under continuous integration."

---

### Part 10: Conclusion & Transition to Q&A (6:15 – 6:45)
**Screen:** Return to the title slide or dashboard homepage.  
**Spoken Narrative:**  
> "In summary, the Student Performance Prediction System provides a complete, rigorously evaluated, and ethically audited decision-support platform for modern educational institutions.  
> It proves that classical machine learning, when combined with statistical discipline and modern explainability, delivers exceptional academic utility.  
> Thank you, and I look forward to your questions."
