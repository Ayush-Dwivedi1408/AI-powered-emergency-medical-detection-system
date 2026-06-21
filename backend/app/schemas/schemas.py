"""
Pydantic schemas: validation + the shape of data going in/out of the API.

This is what was completely missing from the C++ version -- there, typing a
letter for "age" was undefined behavior. Here, FastAPI rejects it
automatically with a clear 422 error before our code ever runs, because
every field below has an enforced type and constraint.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


# ---------- Patient ----------

class PatientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., gt=0, le=130)  # gt=0 fixes the old "age <= 0 throws" rule, but cleanly


class PatientCreate(PatientBase):
    pass


class PatientOut(PatientBase):
    model_config = ConfigDict(from_attributes=True)  # allows reading from ORM objects directly

    id: int
    created_at: datetime


# ---------- Condition ----------

class ConditionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    base_severity: str
    base_risk_score: int
    first_aid: str
    medicine: str


# ---------- Visit ----------

class VisitCreate(BaseModel):
    patient_id: int
    condition_id: Optional[int] = None

    pulse: Optional[int] = Field(None, ge=20, le=250)
    spo2: Optional[float] = Field(None, ge=0, le=100)
    temperature: Optional[float] = Field(None, ge=30, le=45)  # Celsius
    notes: Optional[str] = Field(None, max_length=500)

    # NEWS2 parameters (Royal College of Physicians scoring system).
    # All optional -- NEWS2 is calculated from whatever vitals are
    # actually available, same principle as the ML model's vitals.
    respiration_rate: Optional[int] = Field(None, ge=4, le=60, description="breaths per minute")
    systolic_bp: Optional[int] = Field(None, ge=40, le=300, description="mmHg")
    is_alert: Optional[bool] = Field(None, description="True=Alert, False=Confused/Voice/Pain/Unresponsive")

    # Symptom flags consumed by the ML risk model (Phase 2). Optional with
    # safe defaults so existing Phase 1 clients/tests don't break.
    has_chest_pain: bool = False
    has_breathing_diff: bool = False
    has_bleeding: bool = False


class VisitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    condition_id: Optional[int]
    pulse: Optional[int]
    spo2: Optional[float]
    temperature: Optional[float]
    respiration_rate: Optional[int] = None
    systolic_bp: Optional[int] = None
    is_alert: Optional[bool] = None
    risk_score: int
    triage_level: Optional[str]
    risk_engine: Optional[str] = None
    news2_score: Optional[int] = None
    news2_risk_level: Optional[str] = None
    notes: Optional[str]
    created_at: datetime


class PatientDetailOut(PatientOut):
    """Patient + their visit history, for the dashboard's patient-detail view."""
    visits: list[VisitOut] = []


class PatientWithLatestVisit(PatientOut):
    """Patient + summary of their most recent visit, for the dashboard's
    priority-sorted list view. Avoids shipping full visit history when
    the list only needs to know "how urgent is this patient right now"."""
    latest_risk_score: Optional[int] = None
    latest_triage_level: Optional[str] = None
    latest_visit_at: Optional[datetime] = None
    visit_count: int = 0


# ---------- Analytics ----------

class TriageDistribution(BaseModel):
    triage_level: str
    count: int


class ConditionFrequency(BaseModel):
    condition_name: str
    count: int


class AnalyticsSummary(BaseModel):
    total_patients: int
    total_visits: int
    average_risk_score: float
    triage_distribution: list[TriageDistribution]
    condition_frequency: list[ConditionFrequency]
    risk_score_histogram: list[int]  # 10 buckets of width 10, i.e. 0-9, 10-19, ... 90-100


# ---------- Disease Prediction (separate feature, NOT tied to visits/triage) ----------

class DiseasePredictionRequest(BaseModel):
    symptoms: list[str] = Field(..., min_length=1, max_length=132)


class DiseasePredictionItem(BaseModel):
    disease: str
    probability: float
    first_aid_tier: str
    first_aid_advice: str


class DiseasePredictionResponse(BaseModel):
    available: bool
    symptoms_provided: int
    top_predictions: list[DiseasePredictionItem]
    disclaimer: str
    error: Optional[str] = None
