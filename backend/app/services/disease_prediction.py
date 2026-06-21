"""
Disease prediction service.

IMPORTANT, READ FIRST: this is a SEPARATE, INDEPENDENT feature from the
vitals-based risk engine (services/triage.py) and the NEWS2 score
(services/news2.py). It does not feed into triage priority or replace
either of those. It exists to answer a different question -- "which
diseases statistically match this symptom checklist, in a non-clinical
demo dataset" -- and should never be treated as a diagnosis.

DATA SOURCE: trained on Training.csv/Testing.csv (see
ml/disease_prediction/README.md for full provenance + honesty notes).
That dataset is highly synthetic and near-deterministic -- 94% of
training rows are exact duplicates of ~304 unique symptom patterns
across 41 diseases. The model's high accuracy reflects that
determinism, not genuine diagnostic skill. EVERY caller of this
service (API responses, frontend display) must surface this context;
it should never be hidden behind a bare percentage.
"""
import os
import joblib
import pandas as pd
from dataclasses import dataclass, field
from app.services.first_aid_data import get_first_aid

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_models", "disease_model.pkl")

_artifact = None
_load_error = None

try:
    _artifact = joblib.load(_MODEL_PATH)
except Exception as e:
    _load_error = str(e)


@dataclass
class DiseasePrediction:
    disease: str
    probability: float
    first_aid_tier: str = "unknown"   # "common" or "serious"
    first_aid_advice: str = ""


@dataclass
class DiseasePredictionResult:
    available: bool
    top_predictions: list[DiseasePrediction] = field(default_factory=list)
    symptoms_provided: int = 0
    disclaimer: str = (
        "This is a non-clinical demo prediction based on a synthetic/"
        "templated public dataset, not real patient records. It is NOT "
        "a medical diagnosis. The first-aid guidance shown is general "
        "supportive-care information only -- it contains no specific "
        "medicine names or dosages, and is not a substitute for "
        "professional medical treatment. Consult a qualified healthcare "
        "professional for any real health concern."
    )
    error: str | None = None


def get_available_symptoms() -> list[str]:
    """Returns the full list of 132 symptom names the model understands,
    for the frontend to render as a checklist."""
    if _artifact is None:
        return []
    return _artifact["symptom_columns"]


def predict_disease(symptoms: list[str], top_n: int = 5) -> DiseasePredictionResult:
    """
    Takes a list of symptom names (must match get_available_symptoms()
    exactly) and returns the top_n most likely diseases with probabilities.

    Deliberately returns multiple ranked candidates, not a single bare
    answer -- a list of "statistically closest matches" is a more honest
    framing than "the AI says you have X", and is harder to mistake for
    a confident diagnosis.
    """
    if _artifact is None:
        return DiseasePredictionResult(
            available=False,
            error=f"Disease prediction model not loaded: {_load_error}",
        )

    known_symptoms = set(_artifact["symptom_columns"])
    valid_symptoms = [s for s in symptoms if s in known_symptoms]

    if not valid_symptoms:
        return DiseasePredictionResult(
            available=True,
            symptoms_provided=0,
            top_predictions=[],
        )

    row = pd.DataFrame(
        [[1 if col in valid_symptoms else 0 for col in _artifact["symptom_columns"]]],
        columns=_artifact["symptom_columns"],
    )

    proba = _artifact["model"].predict_proba(row)[0]
    classes = _artifact["label_encoder"].classes_

    top_indices = proba.argsort()[-top_n:][::-1]
    predictions = []
    for i in top_indices:
        if proba[i] <= 0:
            continue
        disease_name = classes[i]
        first_aid = get_first_aid(disease_name)
        predictions.append(DiseasePrediction(
            disease=disease_name,
            probability=round(float(proba[i]), 4),
            first_aid_tier=first_aid["tier"],
            first_aid_advice=first_aid["advice"],
        ))

    return DiseasePredictionResult(
        available=True,
        symptoms_provided=len(valid_symptoms),
        top_predictions=predictions,
    )


def get_model_status() -> dict:
    if _artifact is None:
        return {"available": False, "reason": _load_error}
    return {
        "available": True,
        "model_name": _artifact["model_name"],
        "num_symptoms": len(_artifact["symptom_columns"]),
        "num_diseases": len(_artifact["disease_classes"]),
        "data_source": (
            "Kaggle 'Disease Prediction Using Machine Learning' dataset, "
            "traceable to a Columbia University DBMI knowledge base project. "
            "Synthetic/templated, not real patient records."
        ),
    }
