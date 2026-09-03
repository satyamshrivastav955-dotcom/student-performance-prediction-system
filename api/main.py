"""
FastAPI service — the prediction API.

A lightweight REST endpoint that serves the exact same model the dashboard uses.
Both call ``src.models.predict.predict_one``, so predictions are guaranteed to
be identical (the test suite asserts this explicitly).

Endpoints:
    GET  /health   — is the service running and is the model loaded?
    POST /predict  — predict performance for one student
    GET  /docs     — auto-generated OpenAPI documentation
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    HealthResponse,
    PredictionResponse,
    ProbabilityDistribution,
    ShapFactor,
    StudentInput,
)
from src.models.predict import ModelNotTrainedError, load_model_bundle, model_is_available, predict_one
from src.utils.config import friendly, load_config

cfg = load_config()
api_cfg = cfg.get("api", {})

app = FastAPI(
    title=api_cfg.get("title", "Student Performance Prediction API"),
    version=api_cfg.get("version", "1.0.0"),
    description=(
        "Predict student performance (High / Medium / Low) from engagement metrics "
        "and demographic data. Built as part of the SkillOrbit ML Capstone."
    ),
)

# CORS — allow the dashboard and any other frontend to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=api_cfg.get("cors_origins", ["*"]),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """Check whether the service is running and the model is loaded."""
    model_loaded = model_is_available()
    model_name = None
    if model_loaded:
        try:
            bundle = load_model_bundle()
            model_name = bundle.get("model_name")
        except Exception:
            pass

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        model_name=model_name,
        version=api_cfg.get("version", "1.0.0"),
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(student: StudentInput):
    """Predict the performance band for a single student.

    Returns the predicted class (L/M/H), confidence, full probability
    distribution, and optionally the top SHAP factors driving the prediction.
    """
    try:
        student_dict = student.model_dump()
        result = predict_one(student_dict, cfg=cfg)
    except ModelNotTrainedError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    # Build probability distribution
    probs_raw = result.get("probabilities", {})
    probabilities = ProbabilityDistribution(
        L=probs_raw.get("L", 0.0),
        M=probs_raw.get("M", 0.0),
        H=probs_raw.get("H", 0.0),
    )

    # Optionally include SHAP factors
    top_factors = None
    if api_cfg.get("include_shap_in_response", True):
        try:
            from src.explainability.shap_utils import explain_student
            explanation = explain_student(student_dict, cfg=cfg)
            contributions = explanation.get("contributions", [])
            shap_top_n = api_cfg.get("shap_top_n", 5)
            top_factors = [
                ShapFactor(
                    feature=friendly(c.get("original_feature", c.get("feature", "")), cfg),
                    value=c.get("student_value", ""),
                    impact=round(float(c.get("shap_value", 0)), 4),
                    direction="helping" if c.get("shap_value", 0) > 0 else "hurting",
                )
                for c in contributions[:shap_top_n]
            ]
        except Exception:
            # SHAP is best-effort in the API — don't fail the prediction
            top_factors = None

    return PredictionResponse(
        predicted_class=result["predicted_class"],
        predicted_label=result["predicted_label"],
        confidence=result.get("confidence", 0.0),
        confidence_level=result.get("confidence_level", "unknown"),
        confidence_note=result.get("confidence_note"),
        probabilities=probabilities,
        model_name=result.get("model_name"),
        is_borderline=result.get("is_borderline"),
        top_factors=top_factors,
    )


# ---------------------------------------------------------------------------
# Startup event — warm-load the model
# ---------------------------------------------------------------------------
@app.on_event("startup")
def _warm_model():
    """Pre-load the model on startup so the first request isn't slow."""
    if model_is_available():
        try:
            load_model_bundle()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Run directly with: python api/main.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=api_cfg.get("host", "0.0.0.0"),
        port=api_cfg.get("port", 8000),
        reload=True,
    )
