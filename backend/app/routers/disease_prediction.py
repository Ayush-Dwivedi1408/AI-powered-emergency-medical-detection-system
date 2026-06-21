"""
Disease prediction endpoints.

Deliberately separate from /visits/ and /patients/ -- this feature does
NOT write to the database, does NOT affect triage priority, and is not
tied to any patient record. It's a standalone "symptom checker" demo,
kept architecturally isolated from the actual triage system so there's
no risk of it silently influencing real triage decisions.
"""
from fastapi import APIRouter
from app.schemas import schemas
from app.services import disease_prediction

router = APIRouter(prefix="/symptoms", tags=["disease-prediction"])


@router.get("/available")
def list_available_symptoms():
    """Returns the 132 symptom names the model understands, for the
    frontend to render as a checklist."""
    return {"symptoms": disease_prediction.get_available_symptoms()}


@router.get("/model-info")
def model_info():
    """Transparency endpoint -- model status, dataset provenance, and
    honesty context. Same pattern as /visits/model-info."""
    return disease_prediction.get_model_status()


@router.post("/predict", response_model=schemas.DiseasePredictionResponse)
def predict_disease(request: schemas.DiseasePredictionRequest):
    result = disease_prediction.predict_disease(request.symptoms)
    return schemas.DiseasePredictionResponse(
        available=result.available,
        symptoms_provided=result.symptoms_provided,
        top_predictions=[
            schemas.DiseasePredictionItem(
                disease=p.disease,
                probability=p.probability,
                first_aid_tier=p.first_aid_tier,
                first_aid_advice=p.first_aid_advice,
            )
            for p in result.top_predictions
        ],
        disclaimer=result.disclaimer,
        error=result.error,
    )
