from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import crud
from app.schemas import schemas
from app.services import triage
from app.services import news2

router = APIRouter(prefix="/visits", tags=["visits"])


@router.get("/model-info")
def model_info():
    """Transparency endpoint: shows whether the ML model or rule-based
    fallback is currently active, and which features the model expects."""
    return triage.get_engine_status()


@router.post("/", response_model=schemas.VisitOut, status_code=201)
def create_visit(visit: schemas.VisitCreate, db: Session = Depends(get_db)):
    patient = crud.get_patient(db, visit.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    condition = None
    if visit.condition_id is not None:
        condition = crud.get_condition(db, visit.condition_id)
        if not condition:
            raise HTTPException(status_code=404, detail="Condition not found")

    risk_score, triage_level, risk_engine = triage.calculate_risk_and_triage(
        age=patient.age,
        pulse=visit.pulse,
        spo2=visit.spo2,
        temperature=visit.temperature,
        condition=condition,
        has_chest_pain=visit.has_chest_pain,
        has_breathing_diff=visit.has_breathing_diff,
        has_bleeding=visit.has_bleeding,
    )

    # NEWS2 is calculated independently of the ML engine -- it's a real,
    # published clinical score (not our model), so it's stored alongside
    # the ML risk score rather than replacing it. Useful both as a
    # clinically-grounded sanity check on the ML model, and as a fallback
    # value that's never "made up."
    news2_result = news2.calculate_news2(
        respiration_rate=visit.respiration_rate,
        spo2=visit.spo2,
        systolic_bp=visit.systolic_bp,
        pulse=visit.pulse,
        temperature=visit.temperature,
        is_alert=visit.is_alert,
    )

    return crud.create_visit(
        db, visit, risk_score, triage_level, risk_engine,
        news2_score=news2_result.total_score,
        news2_risk_level=news2_result.risk_level,
    )


@router.get("/", response_model=list[schemas.VisitOut])
def list_all_visits(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    return crud.get_all_visits(db, skip, limit)


@router.get("/patient/{patient_id}", response_model=list[schemas.VisitOut])
def get_patient_visits(patient_id: int, db: Session = Depends(get_db)):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.get_visits_for_patient(db, patient_id)
