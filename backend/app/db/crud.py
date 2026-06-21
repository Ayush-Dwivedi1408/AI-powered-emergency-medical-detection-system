"""
CRUD layer: all direct DB queries live here, not in the route handlers.

Why this separation matters (and didn't exist in the C++ version): routers
should only handle HTTP concerns (status codes, request/response shaping).
Keeping queries here means the same logic is reusable -- e.g. the future
ML pipeline can import these functions directly without going through HTTP.
"""
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas


# ---------- Patient ----------

def create_patient(db: Session, patient: schemas.PatientCreate) -> models.Patient:
    db_patient = models.Patient(name=patient.name, age=patient.age)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def get_patient(db: Session, patient_id: int) -> models.Patient | None:
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()


def get_patients(db: Session, skip: int = 0, limit: int = 100) -> list[models.Patient]:
    return db.query(models.Patient).offset(skip).limit(limit).all()


# Triage levels ranked by urgency, used to sort the dashboard list so
# P1 always appears above P4 regardless of insertion order or alphabetical
# sort (which would put "P1" before "P2" coincidentally, but is fragile --
# this makes the ordering explicit and correct on purpose).
_TRIAGE_RANK = {
    "P1 - IMMEDIATE": 0,
    "P2 - URGENT": 1,
    "P3 - LESS URGENT": 2,
    "P4 - ROUTINE": 3,
}


def get_patients_with_latest_visit(db: Session) -> list[dict]:
    """
    Returns each patient along with a summary of their most recent visit,
    sorted by triage urgency (P1 first) and then by most recent visit.
    Patients with no visits yet are sorted last.
    """
    patients = db.query(models.Patient).all()
    results = []
    for p in patients:
        latest = (
            db.query(models.Visit)
            .filter(models.Visit.patient_id == p.id)
            .order_by(models.Visit.created_at.desc())
            .first()
        )
        visit_count = (
            db.query(models.Visit).filter(models.Visit.patient_id == p.id).count()
        )
        results.append({
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "created_at": p.created_at,
            "latest_risk_score": latest.risk_score if latest else None,
            "latest_triage_level": latest.triage_level if latest else None,
            "latest_visit_at": latest.created_at if latest else None,
            "visit_count": visit_count,
        })

    results.sort(
        key=lambda r: (
            _TRIAGE_RANK.get(r["latest_triage_level"], 99),
            -(r["latest_visit_at"].timestamp() if r["latest_visit_at"] else 0),
        )
    )
    return results


def delete_patient(db: Session, patient_id: int) -> bool:
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return False
    db.delete(db_patient)
    db.commit()
    return True


# ---------- Condition ----------

def get_conditions(db: Session) -> list[models.Condition]:
    return db.query(models.Condition).all()


def get_condition(db: Session, condition_id: int) -> models.Condition | None:
    return db.query(models.Condition).filter(models.Condition.id == condition_id).first()


# ---------- Visit ----------

def create_visit(
    db: Session,
    visit: schemas.VisitCreate,
    risk_score: int,
    triage_level: str,
    risk_engine: str,
    news2_score: int | None = None,
    news2_risk_level: str | None = None,
) -> models.Visit:
    db_visit = models.Visit(
        patient_id=visit.patient_id,
        condition_id=visit.condition_id,
        pulse=visit.pulse,
        spo2=visit.spo2,
        temperature=visit.temperature,
        respiration_rate=visit.respiration_rate,
        systolic_bp=visit.systolic_bp,
        is_alert=visit.is_alert,
        notes=visit.notes,
        risk_score=risk_score,
        triage_level=triage_level,
        risk_engine=risk_engine,
        news2_score=news2_score,
        news2_risk_level=news2_risk_level,
    )
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    return db_visit


def get_visits_for_patient(db: Session, patient_id: int) -> list[models.Visit]:
    return (
        db.query(models.Visit)
        .filter(models.Visit.patient_id == patient_id)
        .order_by(models.Visit.created_at.asc())
        .all()
    )


def get_all_visits(db: Session, skip: int = 0, limit: int = 200) -> list[models.Visit]:
    return (
        db.query(models.Visit)
        .order_by(models.Visit.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
