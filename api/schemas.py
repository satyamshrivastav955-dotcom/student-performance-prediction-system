"""
Pydantic schemas for the FastAPI service.

These models define the exact shape of every request and response. The
auto-generated OpenAPI docs at ``/docs`` are built from these, so getting
them right means the API is self-documenting.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class StudentInput(BaseModel):
    """The data needed to predict a single student's performance.

    Every field matches a column in the xAPI-Edu-Data dataset. Numeric fields
    are integers 0-100 representing engagement counts; categorical fields are
    strings matching the dataset's vocabulary.
    """

    raisedhands: int = Field(..., ge=0, le=100, description="Hands raised in class (0-100)")
    VisITedResources: int = Field(..., ge=0, le=100, description="Learning resources opened (0-100)")
    AnnouncementsView: int = Field(..., ge=0, le=100, description="Announcements read (0-100)")
    Discussion: int = Field(..., ge=0, le=100, description="Discussion posts (0-100)")
    gender: str = Field(..., description="Student gender (M/F)")
    NationalITy: str = Field(..., description="Student nationality")
    PlaceofBirth: str = Field(..., description="Place of birth")
    StageID: str = Field(..., description="School stage (e.g., MiddleSchool, lowerlevel)")
    GradeID: str = Field(..., description="Grade (e.g., G-04, G-08)")
    SectionID: str = Field(..., description="Class section (A, B, C)")
    Topic: str = Field(..., description="Subject (e.g., Math, Science, English)")
    Semester: str = Field(..., description="Semester (F = first, S = second)")
    Relation: str = Field(..., description="Responsible parent (Father/Mum)")
    ParentAnsweringSurvey: str = Field(..., description="Parent answered school survey (Yes/No)")
    ParentschoolSatisfaction: str = Field(..., description="Parent satisfaction with school (Good/Bad)")
    StudentAbsenceDays: str = Field(..., description="Absence level (Under-7 / Above-7)")

    model_config = {
        "json_schema_extra": {
            "examples": [
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
                    "StudentAbsenceDays": "Under-7",
                }
            ]
        }
    }


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class ProbabilityDistribution(BaseModel):
    """Probability for each performance band."""
    L: float = Field(..., description="Probability of Low performance")
    M: float = Field(..., description="Probability of Medium performance")
    H: float = Field(..., description="Probability of High performance")


class ShapFactor(BaseModel):
    """One SHAP contribution factor."""
    feature: str = Field(..., description="Feature name (human-readable)")
    value: Any = Field(..., description="Student's value for this feature")
    impact: float = Field(..., description="SHAP value (positive = helps, negative = hurts)")
    direction: str = Field(..., description="'helping' or 'hurting' the prediction")


class PredictionResponse(BaseModel):
    """Full prediction result for a single student."""
    predicted_class: str = Field(..., description="Predicted performance band (L/M/H)")
    predicted_label: str = Field(..., description="Human-readable label (Low/Medium/High)")
    confidence: float = Field(..., description="Model's confidence (0-1)")
    confidence_level: str = Field(..., description="Confidence band (high/moderate/low)")
    confidence_note: Optional[str] = Field(None, description="Plain-English confidence explanation")
    probabilities: ProbabilityDistribution = Field(..., description="Full probability distribution")
    model_name: Optional[str] = Field(None, description="Name of the model that made this prediction")
    is_borderline: Optional[bool] = Field(None, description="Whether this student is near a class boundary")
    top_factors: Optional[List[ShapFactor]] = Field(None, description="Top SHAP factors driving this prediction")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether the model is available")
    model_name: Optional[str] = Field(None, description="Name of the loaded model")
    version: str = Field(..., description="API version")
