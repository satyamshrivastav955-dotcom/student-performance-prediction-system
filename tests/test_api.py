"""
Tests for the FastAPI service.

Uses FastAPI's TestClient (which runs in-process, no HTTP server needed) to
verify that the API endpoints work correctly and return the expected schemas.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.predict import model_is_available

# Skip all tests if model not trained
pytestmark = pytest.mark.skipif(
    not model_is_available(),
    reason="No trained model found — run 'python scripts/run_pipeline.py --only train' first"
)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from api.main import app
    return TestClient(app)


@pytest.fixture
def sample_student():
    """A valid student payload for testing."""
    return {
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
        "StudentAbsenceDays": "Under-7",
    }


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_status(self, client):
        data = client.get("/health").json()
        assert "status" in data
        assert data["status"] in ("healthy", "degraded")

    def test_health_model_loaded(self, client):
        data = client.get("/health").json()
        assert data["model_loaded"] is True


class TestPredictEndpoint:
    def test_predict_returns_200(self, client, sample_student):
        response = client.post("/predict", json=sample_student)
        assert response.status_code == 200

    def test_predict_has_required_fields(self, client, sample_student):
        data = client.post("/predict", json=sample_student).json()
        assert "predicted_class" in data
        assert "predicted_label" in data
        assert "confidence" in data
        assert "probabilities" in data

    def test_predicted_class_is_valid(self, client, sample_student):
        data = client.post("/predict", json=sample_student).json()
        assert data["predicted_class"] in ("L", "M", "H")

    def test_confidence_in_range(self, client, sample_student):
        data = client.post("/predict", json=sample_student).json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_probabilities_sum_to_one(self, client, sample_student):
        data = client.post("/predict", json=sample_student).json()
        probs = data["probabilities"]
        total = probs["L"] + probs["M"] + probs["H"]
        assert abs(total - 1.0) < 0.01

    def test_invalid_input_returns_422(self, client):
        """Missing required fields should return a validation error."""
        response = client.post("/predict", json={"raisedhands": 50})
        assert response.status_code == 422

    def test_out_of_range_numeric(self, client, sample_student):
        """Numeric values outside 0-100 should be rejected."""
        bad = dict(sample_student)
        bad["raisedhands"] = 150
        response = client.post("/predict", json=bad)
        assert response.status_code == 422

    def test_prediction_deterministic(self, client, sample_student):
        """Same input should always produce the same output."""
        r1 = client.post("/predict", json=sample_student).json()
        r2 = client.post("/predict", json=sample_student).json()
        assert r1["predicted_class"] == r2["predicted_class"]
        assert r1["confidence"] == r2["confidence"]

    def test_api_dashboard_agreement(self, client, sample_student):
        """The API prediction should match what predict_one returns directly."""
        from src.models.predict import predict_one

        api_result = client.post("/predict", json=sample_student).json()
        direct_result = predict_one(sample_student)

        assert api_result["predicted_class"] == direct_result["predicted_class"]
        assert abs(api_result["confidence"] - direct_result["confidence"]) < 0.001


class TestOpenAPIDocs:
    def test_docs_available(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "/predict" in schema["paths"]
        assert "/health" in schema["paths"]
