"""
Risk + triage engine: Phase 2.

Loads the trained model (logistic regression or XGBoost, whichever won
during training -- see ml/train.py) and uses it to predict a risk band
from patient vitals + symptoms. Falls back to the Phase 1 rule-based
logic if the model file is missing or fails to load, so the API never
hard-crashes because of a missing artifact.

The function's core inputs are unchanged from Phase 1 (vitals + condition)
with new optional symptom flags added -- callers (routers/visits.py) don't
need to know which engine produced the result. The engine name is returned
separately so the API can stay transparent about it.
"""
import os
import joblib
import pandas as pd
from app.models import models

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_models", "risk_model.pkl")

_artifact = None
_load_error = None

try:
    _artifact = joblib.load(_MODEL_PATH)
except Exception as e:  # missing file, version mismatch, corrupt pickle, etc.
    _load_error = str(e)


# Risk band -> representative numeric score (midpoint of each band's range)
# used so the API can still return a single 0-100 risk_score alongside
# the predicted band, consistent with the Phase 1 schema.
_BAND_TO_SCORE_MIDPOINT = {0: 12, 1: 37, 2: 62, 3: 87}

_BAND_TO_TRIAGE = {
    0: "P4 - ROUTINE",
    1: "P3 - LESS URGENT",
    2: "P2 - URGENT",
    3: "P1 - IMMEDIATE",
}

# Severity string -> integer encoding, matching ml/generate_dataset.py
_SEVERITY_TO_INT = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "CRITICAL": 3}


def _rule_based_fallback(
    age: int,
    pulse: int | None,
    spo2: float | None,
    temperature: float | None,
    condition: models.Condition | None,
) -> tuple[int, str]:
    """Phase 1 logic, kept as a safety net if the ML model can't be loaded."""
    score = 0
    if condition is not None:
        score += condition.base_risk_score * 5
    if pulse is not None and (pulse > 100 or pulse < 50):
        score += 15
    if spo2 is not None and spo2 < 92:
        score += 20
    if temperature is not None and temperature >= 38.5:
        score += 10
    if age >= 60:
        score += 10
    score = min(score, 100)

    if score >= 70:
        triage = "P1 - IMMEDIATE"
    elif score >= 45:
        triage = "P2 - URGENT"
    elif score >= 20:
        triage = "P3 - LESS URGENT"
    else:
        triage = "P4 - ROUTINE"
    return score, triage


def calculate_risk_and_triage(
    age: int,
    pulse: int | None,
    spo2: float | None,
    temperature: float | None,
    condition: models.Condition | None,
    has_chest_pain: bool = False,
    has_breathing_diff: bool = False,
    has_bleeding: bool = False,
) -> tuple[int, str, str]:
    """
    Returns (risk_score 0-100, triage_level, engine_used).
    engine_used is "ml_model" or "rule_based" (fallback).
    """
    if _artifact is None:
        score, triage = _rule_based_fallback(age, pulse, spo2, temperature, condition)
        return score, triage, "rule_based"

    # Vitals are required by the model; if any are missing, we can't run
    # it meaningfully, so fall back rather than guessing default values
    # that could silently produce a misleading prediction.
    if pulse is None or spo2 is None or temperature is None:
        score, triage = _rule_based_fallback(age, pulse, spo2, temperature, condition)
        return score, triage, "rule_based"

    condition_severity = _SEVERITY_TO_INT.get(
        condition.base_severity if condition else "LOW", 0
    )

    row = pd.DataFrame([{
        "age": age,
        "pulse": pulse,
        "spo2": spo2,
        "temperature": temperature,
        "condition_severity": condition_severity,
        "has_chest_pain": int(has_chest_pain),
        "has_breathing_diff": int(has_breathing_diff),
        "has_bleeding": int(has_bleeding),
    }])[_artifact["features"]]  # enforce correct column order

    X = _artifact["scaler"].transform(row) if _artifact["needs_scaling"] else row

    band = int(_artifact["model"].predict(X)[0])
    score = _BAND_TO_SCORE_MIDPOINT[band]
    triage = _BAND_TO_TRIAGE[band]

    return score, triage, "ml_model"


def get_engine_status() -> dict:
    """For a /health or /model-info endpoint -- transparency about what's loaded."""
    if _artifact is None:
        return {"engine": "rule_based_fallback", "reason": _load_error}
    return {
        "engine": "ml_model",
        "model_name": _artifact["model_name"],
        "features": _artifact["features"],
    }
