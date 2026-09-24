# System Architecture & Technical Specifications

## 1. System Overview & Engineering Philosophy

The **Student Performance Prediction System (SPPS)** is engineered as a decoupled, multi-tier intelligence platform designed for institutional decision support. It bridges educational telemetry logging with classical ensemble machine learning, game-theoretic explainability, algorithmic recourse, and policy-level simulation.

In strict compliance with academic standards rejecting opaque black-box neural networks for tabular student data, the architecture relies exclusively on **classical, sample-efficient tree ensembles** ($N = 478$), guaranteed leak-free feature pipelines, and transparent mathematical auditing.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            DATA & PREPROCESSING                              │
│   Raw xAPI-Edu-Data ───► Data Cleaning ───► ColumnTransformer Pipeline      │
│   (478 Students)          (Deduplicate,       (StandardScaler, One-Hot,      │
│                            Impute, Clip)       Ordinal Binary)               │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           CORE ML INFERENCE ENGINE                           │
│                     Champion Model: Tuned Random Forest                      │
│            Accuracy: 82.29% | Macro-F1: 82.82% | Severe Errors: 0/96         │
│                 Encapsulated in 'models/model.joblib'                        │
└───────────────────────┬───────────────────────────────┬──────────────────────┘
                        │                               │
                        ▼                               ▼
┌────────────────────────────────────────┐ ┌───────────────────────────────────┐
│     EXPLAINABILITY & RECOURSE (XAI)    │ │   GOVERNANCE & SIMULATION         │
│ • TreeSHAP (Exact Shapley Attributions)│ │ • Fairlearn Disparity Auditing    │
│ • DiCE Counterfactual Engine           │ │ • 500-Run Monte Carlo Policy Sim  │
│   (Protected Demographics FROZEN)      │ │ • Statistical Significance Engine │
└───────────────────────┬────────────────┘ └──────────────┬────────────────────┘
                        │                                 │
                        ▼                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           DUAL SERVING INFRASTRUCTURE                        │
│   ┌────────────────────────────────────┐ ┌─────────────────────────────────┐ │
│   │     FastAPI REST Microservice      │ │   Streamlit Multi-Page Portal   │ │
│   │     • GET /health, POST /predict   │ │   • 7 Interactive Views         │ │
│   │     • Sub-10ms Inference Latency   │ │   • What-If Live Sliders        │ │
│   │     • Pydantic v2 Schema Contracts │ │   • Institutional Theme System  │ │
│   └────────────────────────────────────┘ └─────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Decoupled Pipeline Layers

### 2.1 Layer 1: Data Ingestion & Transformation
- **Ingestion (`src/data/make_dataset.py`):** Loads raw records from `data/raw/xAPI-Edu-Data.csv`. Removes duplicate rows, validates schema adherence, and checks numeric boundaries ($[0, 100]$).
- **Leak-Free Transformation (`src/features/build_features.py`):** Encapsulated inside scikit-learn's `ColumnTransformer`. Transformers are fitted strictly inside training folds during 5-fold cross-validation.
  - **Numeric Branch:** `StandardScaler()` applied to 4 continuous engagement features (`raisedhands`, `VisITedResources`, `AnnouncementsView`, `Discussion`).
  - **Nominal Branch:** `OneHotEncoder(handle_unknown='ignore')` applied to 9 categorical features.
  - **Binary Branch:** Ordinal mapping for `StudentAbsenceDays` (0 = Under-7, 1 = Above-7), `ParentAnsweringSurvey` (0 = No, 1 = Yes), and `ParentschoolSatisfaction` (0 = Bad, 1 = Good).

### 2.2 Layer 2: Machine Learning Inference Engine
- **Champion Architecture:** Tuned `RandomForestClassifier` with balanced sub-sampling and 200 estimators.
- **Model Bundle (`models/model.joblib`):** Contains the fitted preprocessor pipeline, trained classifier, target class mappings (`L`, `M`, `H`), feature column metadata, and training configuration.
- **Zero Training-Serving Skew:** Both the web dashboard and REST API import the identical inference entrypoint: `src.models.predict.predict_one()`.

### 2.3 Layer 3: Explainable AI & Recourse Architecture
- **TreeSHAP Attributions (`src/explainability/shap_utils.py`):** Computes exact, efficient local Shapley attributions:
  $$\text{Log-Odds}(y = C) = \phi_0 + \sum_{j=1}^{M} \phi_j$$
  One-hot encoded categories are automatically aggregated back to their semantic parent variable for human interpretability.
- **DiCE Counterfactuals (`src/explainability/counterfactuals.py`):** Solves constrained optimization for actionable behavioral shifts:
  $$\min_{\mathbf{x}'} \text{dist}(\mathbf{x}, \mathbf{x}') \quad \text{s.t.} \quad f(\mathbf{x}') = \text{Target Class}$$
  **Protected demographic traits (`gender`, `NationalITy`, `PlaceofBirth`) are strictly frozen.** The engine guarantees that interventions only suggest actionable behavioral modifications.

### 2.4 Layer 4: Governance, Auditing & Simulation
- **Fairlearn Disparity Auditor (`src/evaluation/fairness.py`):** Evaluates Demographic Parity Difference, Demographic Parity Ratio, and Equalized Odds across sensitive groups.
- **Monte Carlo Simulator (`src/simulation/cohort_sim.py`):** Runs 500 stochastic simulation iterations over the entire student cohort to estimate the impact of institutional policy scenarios with empirical 95% confidence intervals.

---

## 3. Dual-Channel Serving Architecture

### 3.1 FastAPI High-Performance Microservice (`api/main.py`)
- Built on Starlette and Uvicorn.
- Request/Response validation powered by **Pydantic v2** (`api/schemas.py`).
- Pre-warms model bundle on startup via `@app.on_event("startup")` for zero-cold-start sub-10ms response times.
- Exposes CORS middleware allowing browser clients and dashboard integration.

### 3.2 Streamlit Decision Hub (`dashboard/app.py`)
- Employs Streamlit Navigation API across 7 focused operational pages:
  1. `1_Overview.py`: Cohort EDA and statistical effect rankings.
  2. `2_Individual_Predictor.py`: Student check-in, probability gauge, SHAP waterfall, and prescription card.
  3. `3_What_If_Simulator.py`: Real-time behavioral slider exploration.
  4. `4_Cohort_Simulator.py`: Class-wide policy intervention modeling.
  5. `5_Model_and_Fairness.py`: Model arena comparison, confusion matrix, and Fairlearn demographic audit.
  6. `6_Analytics.py`: Deep-dive subject and topic correlation matrices.
  7. `7_About.py`: Academic documentation, data dictionary, and methodology.
- Standardized UI component system (`dashboard/theme.py`) providing cards, badges, and responsive CSS.

---

## 4. Architectural Verification & Testing

The system architecture is covered by automated unit and integration tests (`tests/`):
- `tests/test_preprocess.py`: Verifies zero duplicates, missing value imputation, and pipeline transformations.
- `tests/test_models.py`: Asserts model persistence, probability normalization ($\sum P = 1.0$), and **100% inference equivalence between API and UI**.
- `tests/test_api.py`: Validates REST endpoints, schema validation (HTTP 422), and health contracts.
- **Result:** **43 / 43 tests passing** with continuous integration configured via GitHub Actions (`.github/workflows/ci.yml`).
