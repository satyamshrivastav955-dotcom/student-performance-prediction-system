# Data Dictionary: Student Performance Prediction System

## 1. Overview & Dataset Provenance

- **Dataset Identifier:** `xAPI-Edu-Data` (Open-access educational dataset)
- **Primary Citation:** Amrieh, E. A., Hamtini, T., & Aljarah, I. (2016). *Mining Educational Data to Predict Student's academic Performance using Ensemble Methods*. International Journal of Database Theory and Application, 9(8), 119-136.
- **Total Records:** 478 student records (after deduplication of 2 exact identical duplicate rows from 480 raw records)
- **Total Features:** 16 predictive attributes (4 continuous behavioral telemetry counters, 9 multi-class nominal categories, 3 binary indicators)
- **Target Variable:** `Class` (Three-tier academic achievement band: Low, Medium, High)
- **Data Collection Modality:** Telemetry logging from Kalboard 360 Learning Management System (LMS) using the xAPI (Experience API) standard.

---

## 2. Feature Specification Table

| Feature Name | Friendly Display Name | Data Type | Measurement Scale | Role | Value Range / Allowed Categories | Actionability & Constraints | Pedagogical Description |
|:---|:---|:---|:---|:---|:---|:---|:---|
| `raisedhands` | Hands raised in class | Integer | Ratio ($[0, 100]$) | Predictor | $0 \le x \le 100$ | **Actionable** (Monotonically non-decreasing) | Number of times the student actively raised their hand or volunteered during classroom lectures. |
| `VisITedResources` | Learning resources opened | Integer | Ratio ($[0, 100]$) | Predictor | $0 \le x \le 100$ | **Actionable** (Monotonically non-decreasing) | Number of course modules, lecture slides, digital lab notes, or reading packages opened on the LMS. |
| `AnnouncementsView` | Announcements read | Integer | Ratio ($[0, 100]$) | Predictor | $0 \le x \le 100$ | **Actionable** (Monotonically non-decreasing) | Frequency of reading teacher notices, test updates, homework reminders, and class alerts on the portal. |
| `Discussion` | Discussion posts | Integer | Ratio ($[0, 100]$) | Predictor | $0 \le x \le 100$ | **Actionable** (Monotonically non-decreasing) | Number of contributions made to peer discussion forums, Q&A boards, and group study comment threads. |
| `StudentAbsenceDays` | School absence level | String / Ordinal | Binary Nominal | Predictor | `Under-7`, `Above-7` | **Actionable** (`Above-7` $\to$ `Under-7`) | Categorical absence indicator during the semester. `Above-7` indicates severe truancy/chronic absenteeism (> 7 missed days). |
| `ParentAnsweringSurvey` | Parent answered survey | String / Ordinal | Binary Nominal | Predictor | `Yes`, `No` | **Actionable** (`No` $\to$ `Yes`) | Indicates whether the student's legal parent or guardian completed institutional feedback surveys. |
| `ParentschoolSatisfaction` | Parent school satisfaction | String / Ordinal | Binary Nominal | Predictor | `Good`, `Bad` | Contextual Observation | Guardian's perceived rating and overall satisfaction level regarding school administration and pedagogy. |
| `Relation` | Responsible parent/guardian | String | Nominal (2 categories) | Predictor | `Father`, `Mum` | Contextual Observation | The designated primary contact parent handling school liaison and academic progress tracking. |
| `gender` | Gender | String | Nominal (2 categories) | Predictor / Sensitive | `M`, `F` | **Frozen / Immutable** (Demographic protected attribute) | Biological sex / gender of the student. Strictly prohibited from counterfactual modification. |
| `NationalITy` | Nationality | String | Nominal (14 categories) | Predictor / Sensitive | `KW` (Kuwait), `Jordan`, `Palestine`, `Iraq`, `Lebanon`, `Tunis`, `SaudiArabia`, `Egypt`, `Syria`, `USA`, `Iran`, `Lybia`, `Morocco`, `venzuela` | **Frozen / Immutable** (Demographic protected attribute) | Citizenship / nationality of the student. Audited for demographic parity and equalized odds. |
| `PlaceofBirth` | Place of birth | String | Nominal (14 categories) | Predictor | Same 14 geographical country labels as nationality | **Frozen / Immutable** | City/nation where the student was born. |
| `StageID` | School stage | String | Nominal (3 categories) | Predictor | `lowerlevel` (Elementary), `MiddleSchool`, `HighSchool` | Contextual Structural | Broad tier of schooling in the K-12 academic trajectory. |
| `GradeID` | Grade level | String | Nominal (10 categories) | Predictor | `G-02`, `G-04`, `G-05`, `G-06`, `G-07`, `G-08`, `G-09`, `G-10`, `G-11`, `G-12` | Contextual Structural | Specific class grade level from grade 2 through grade 12. |
| `SectionID` | Class section | String | Nominal (3 categories) | Predictor | `A`, `B`, `C` | Contextual Structural | Physical classroom room/cohort assignment within the grade level. |
| `Topic` | Course subject | String | Nominal (12 categories) | Predictor | `IT`, `French`, `Arabic`, `Science`, `English`, `Biology`, `Spanish`, `Chemistry`, `Geology`, `Quran`, `Math`, `History` | Contextual Structural | Academic discipline / course curriculum subject being evaluated. |
| `Semester` | Academic term | String | Nominal (2 categories) | Predictor | `F` (First semester / Fall), `S` (Second semester / Spring) | Contextual Temporal | Current academic reporting period within the school calendar year. |
| **`Class`** | **Performance tier** | **String** | **Ordinal / Multi-class** | **Target** | **`L` (Low: 0–69%)**, **`M` (Medium: 70–89%)**, **`H` (High: 90–100%)** | **System Prediction Target** | **Final consolidated performance category assigned at conclusion of academic evaluation.** |

---

## 3. Data Cleaning, Imputation & Validation Rules

1. **Exact Duplicate Elimination:**  
   Raw files with duplicate student records across all 16 features are identified and dropped. Exactly 2 duplicates were detected in initial ingestion, reducing sample from $N=480$ to $N=478$.
2. **Whitespace Normalization:**  
   All string entries undergo `.strip()` to prevent whitespace-induced cardinality inflation (e.g., `"Jordan "` vs `"Jordan"`).
3. **Continuous Bound Verification:**  
   All 4 continuous variables (`raisedhands`, `VisITedResources`, `AnnouncementsView`, `Discussion`) are bounded within $[0, 100]$. Runtime checks enforce that any input $x < 0$ or $x > 100$ throws a validation error.
4. **Missing Value Strategy:**  
   - Continuous attributes: Imputed with median of the training split.
   - Categorical attributes: Imputed with mode of the training split.
5. **Categorical Encoding Strategy:**  
   - 9 nominal features are encoded via `OneHotEncoder(handle_unknown='ignore')`.
   - 3 binary indicators are encoded ordinally:
     - `StudentAbsenceDays`: `Under-7` $\to 0$, `Above-7` $\to 1$ (higher represents truancy risk).
     - `ParentAnsweringSurvey`: `No` $\to 0$, `Yes` $\to 1$ (higher represents parental engagement).
     - `ParentschoolSatisfaction`: `Bad` $\to 0$, `Good` $\to 1$ (higher represents parental satisfaction).
