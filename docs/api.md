# FastAPI REST Microservice Documentation

## 1. Overview & Service Architecture

The **Student Performance Prediction System API** is a high-performance, asynchronous REST microservice implemented with **FastAPI** and **Pydantic v2**. It serves the exact same serialized model bundle (`models/model.joblib`) consumed by the Streamlit decision dashboard, ensuring 100% mathematical inference parity.

- **Base URL:** `http://localhost:8000`
- **Interactive OpenAPI Specification (Swagger UI):** `http://localhost:8000/docs`
- **ReDoc Alternative Documentation:** `http://localhost:8000/redoc`
- **OpenAPI Schema (JSON):** `http://localhost:8000/openapi.json`
- **Typical CPU Inference Latency:** `< 10ms` per student record

---

## 2. API Endpoints Summary

| Method | Endpoint | Description | Request Body | Response Model |
|:---|:---|:---|:---|:---|
| `GET` | `/health` | Service liveness, readiness, and model status check | None | `HealthResponse` |
| `POST` | `/predict` | Predict academic performance tier, confidence & probabilities | `StudentInput` | `PredictionResponse` |
| `POST` | `/explain` | Predict and calculate top SHAP game-theoretic factors | `StudentInput` | `PredictionResponse` (with `top_factors`) |
| `GET` | `/docs` | Interactive Swagger UI documentation browser | None | HTML |

---

## 3. Detailed Endpoint Specifications

### 3.1 Health Check: `GET /health`

Verifies that the FastAPI process is active and that the machine learning pipeline bundle is loaded into memory and ready for inference.

#### Request Example
```bash
curl -X GET "http://localhost:8000/health" -H "accept: application/json"
```

#### Response Model (`HealthResponse`)
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "random_forest",
  "version": "1.0.0"
}
```

- **Status Codes:**
  - `200 OK`: Service is healthy and model is loaded.
  - `503 Service Unavailable`: Service is running but model bundle failed to load or is missing.

---

### 3.2 Individual Prediction: `POST /predict`

Accepts a single student's 16 behavioral and demographic attributes, validates the payload against Pydantic schema boundaries, transforms features via the pipeline, and returns the predicted class, confidence, and full probability distribution.

#### Request Schema (`StudentInput`)
| Field | Type | Bounds / Values | Description |
|:---|:---|:---|:---|
| `raisedhands` | Integer | $0 \le x \le 100$ | Number of times student raised hand |
| `VisITedResources` | Integer | $0 \le x \le 100$ | Number of digital learning resources opened |
| `AnnouncementsView` | Integer | $0 \le x \le 100$ | Number of school/course announcements read |
| `Discussion` | Integer | $0 \le x \le 100$ | Frequency of discussion forum posts |
| `gender` | String | `"M"`, `"F"` | Student gender |
| `NationalITy` | String | Valid nationality string (e.g. `"KW"`, `"Jordan"`) | Student citizenship |
| `PlaceofBirth` | String | Valid place string (e.g. `"Kuwait"`, `"Jordan"`) | Place of birth |
| `StageID` | String | `"lowerlevel"`, `"MiddleSchool"`, `"HighSchool"` | School stage |
| `GradeID` | String | `"G-02"` through `"G-12"` | Grade level |
| `SectionID` | String | `"A"`, `"B"`, `"C"` | Classroom section |
| `Topic` | String | `"Math"`, `"Science"`, `"IT"`, `"English"`, etc. | Subject course |
| `Semester` | String | `"F"` (First), `"S"` (Second) | Academic semester |
| `Relation` | String | `"Father"`, `"Mum"` | Primary liaison parent |
| `ParentAnsweringSurvey` | String | `"Yes"`, `"No"` | Parent completed school survey |
| `ParentschoolSatisfaction`| String | `"Good"`, `"Bad"` | Parent school satisfaction |
| `StudentAbsenceDays` | String | `"Under-7"`, `"Above-7"` | Absence days during term |

#### Sample Request Payload
```json
{
  "raisedhands": 50,
  "VisITedResources": 60,
  "AnnouncementsView": 40,
  "Discussion": 30,
  "gender": "M",
  "NationalITy": "KW",
  "PlaceofBirth": "Kuwait",
  "StageID": "MiddleSchool",
  "GradeID": "G-08",
  "SectionID": "A",
  "Topic": "Math",
  "Semester": "F",
  "Relation": "Father",
  "ParentAnsweringSurvey": "Yes",
  "ParentschoolSatisfaction": "Good",
  "StudentAbsenceDays": "Under-7"
}
```

#### Sample Response (`PredictionResponse`)
```json
{
  "predicted_class": "M",
  "predicted_label": "Medium",
  "confidence": 0.74,
  "confidence_level": "moderate",
  "confidence_note": "The model predicts Medium with 74% confidence.",
  "probabilities": {
    "L": 0.08,
    "M": 0.74,
    "H": 0.18
  },
  "model_name": "random_forest",
  "is_borderline": false,
  "top_factors": null
}
```

---

### 3.3 Explainable Prediction: `POST /explain`

Executes prediction along with an on-demand TreeSHAP attribution pass to isolate the top factors pushing or pulling the student's probability towards their predicted tier.

#### Sample Response with SHAP Payloads
```json
{
  "predicted_class": "L",
  "predicted_label": "Low",
  "confidence": 0.88,
  "confidence_level": "high",
  "confidence_note": "High confidence assessment; multiple disengagement indicators present.",
  "probabilities": {
    "L": 0.88,
    "M": 0.10,
    "H": 0.02
  },
  "model_name": "random_forest",
  "is_borderline": false,
  "top_factors": [
    {
      "feature": "School absence level",
      "value": "Above-7",
      "impact": 0.2854,
      "direction": "helping"
    },
    {
      "feature": "Learning resources opened",
      "value": 12,
      "impact": 0.1842,
      "direction": "helping"
    },
    {
      "feature": "Hands raised in class",
      "value": 8,
      "impact": 0.1195,
      "direction": "helping"
    },
    {
      "feature": "Parent answered survey",
      "value": "No",
      "impact": 0.0841,
      "direction": "helping"
    },
    {
      "feature": "Announcements read",
      "value": 5,
      "impact": 0.0763,
      "direction": "helping"
    }
  ]
}
```

---

## 4. Client Integration Examples

### Python Integration (`requests`)
```python
import requests

payload = {
    "raisedhands": 75,
    "VisITedResources": 85,
    "AnnouncementsView": 60,
    "Discussion": 45,
    "gender": "F",
    "NationalITy": "Jordan",
    "PlaceofBirth": "Jordan",
    "StageID": "MiddleSchool",
    "GradeID": "G-08",
    "SectionID": "A",
    "Topic": "English",
    "Semester": "S",
    "Relation": "Mum",
    "ParentAnsweringSurvey": "Yes",
    "ParentschoolSatisfaction": "Good",
    "StudentAbsenceDays": "Under-7"
}

response = requests.post("http://localhost:8000/predict", json=payload)
data = response.json()
print(f"Predicted Tier: {data['predicted_label']} (Confidence: {data['confidence'] * 100:.1f}%)")
print(f"Probabilities: {data['probabilities']}")
```

### cURL CLI Integration
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "raisedhands": 20,
    "VisITedResources": 15,
    "AnnouncementsView": 10,
    "Discussion": 12,
    "gender": "M",
    "NationalITy": "KW",
    "PlaceofBirth": "Kuwait",
    "StageID": "HighSchool",
    "GradeID": "G-10",
    "SectionID": "B",
    "Topic": "IT",
    "Semester": "F",
    "Relation": "Father",
    "ParentAnsweringSurvey": "No",
    "ParentschoolSatisfaction": "Bad",
    "StudentAbsenceDays": "Above-7"
  }'
```

---

## 5. Error Handling & Status Codes

- **`200 OK`**: Successful prediction or health status response.
- **`422 Unprocessable Entity`**: Request payload failed Pydantic schema validation (e.g. numeric engagement counter out of bounds $[0, 100]$, missing required attribute, or invalid type).
- **`503 Service Unavailable`**: Machine learning model file is unavailable or failed to initialize into runtime memory.
- **`500 Internal Server Error`**: Unexpected pipeline runtime error during inference execution.
