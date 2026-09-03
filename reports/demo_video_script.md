# 90-Second Demo Video Script: Student Performance Prediction System

**Target Duration:** ~90 seconds (1 minute 30 seconds)  
**Presenter:** Satyam (Student / Developer)  
**Screen Setup:** Browser displaying Streamlit Dashboard (`localhost:8501`) and FastAPI Swagger UI (`localhost:8000/docs`).

---

### [0:00 - 0:15] Section 1: Problem Framing & Solution Overview
**Visual:** Webcam / Title slide, switching to the Streamlit Dashboard landing page.  
**Spoken Audio:**  
> "Hi everyone! In academic institutions, identifying students who need extra support often happens too late—after exams are graded.  
> Today, I'm presenting the **Student Performance Prediction System**, an end-to-end classical machine learning platform that doesn't just predict who is at risk, but explains *why*, and shows *exactly what actions* will help them succeed."

---

### [0:15 - 0:45] Section 2: EDA & What-If Live Simulation
**Visual:** Navigate to `1_Overview.py` briefly to show the attendance chart, then click into `3_What_If_Simulator.py`. Select Student #14 (originally predicted 'Low'). Move the `VisITedResources` slider from 15 to 65, and toggle `StudentAbsenceDays` to 'Under-7'. Show the live badge switch to 'Medium' / 'High'.  
**Spoken Audio:**  
> "Starting with our exploratory analysis: across 478 students, attendance and digital resource engagement are the strongest statistically proven drivers of performance ($p < 10^{-45}$).  
> Here in the What-If Simulator, we can see this in real time. For this student currently predicted 'Low', if we increase their learning resource visits and drop their absences below 7 days, the model dynamically updates their predicted band to 'Medium' with 81% confidence."

---

### [0:45 - 1:15] Section 3: Explainability, Counterfactuals & Cohort Simulation
**Visual:** Navigate to `2_Individual_Predictor.py`. Show the SHAP waterfall feature breakdown and the Counterfactual Recommendation card. Then jump to `4_Cohort_Simulator.py` and run a +15% participation intervention.  
**Spoken Audio:**  
> "What makes this system truly unique is its prescriptive power.  
> Using SHAP game-theoretic values, every single prediction is decomposed into exact feature contributions—so teachers know what's pulling a student down.  
> Even better, our counterfactual engine generates realistic paths: 'Raise hands from 10 to 45 and reduce absences to shift to High'.  
> And for administrators, our Monte Carlo cohort simulator models entire policy shifts—showing that a 15% class-wide participation boost lifts approximately 20 students out of the at-risk category."

---

### [1:15 - 1:30] Section 4: Architecture, API & Conclusion
**Visual:** Switch tab to FastAPI Swagger UI (`/docs`), execute `POST /predict`, and show the JSON response with confidence and SHAP values. Briefly flash the passing pytest terminal.  
**Spoken Audio:**  
> "Under the hood, we deliberately used tuned tree ensembles—our Random Forest achieved 82.3% accuracy and 0.828 macro-F1 with bootstrapped confidence intervals and fairness checks.  
> The system ships with both a Streamlit UI and a production FastAPI REST endpoint, covered by automated unit tests and CI.  
> Thank you!"

---

### Production Notes & Checklist:
- [x] Streamlit dashboard running locally on port 8501 (`streamlit run dashboard/app.py`).
- [x] FastAPI running on port 8000 (`uvicorn api.main:app --port 8000`).
- [x] Pre-select Student #14 or similar in the What-If simulator for smooth slider demonstration.
- [x] Keep screen recording at 1080p, 60fps with clear audio.
