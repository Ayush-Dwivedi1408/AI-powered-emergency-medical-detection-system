"""
ORM models.

Patient   -> replaces the old Patient[10] fixed array. One row per patient,
             persists across restarts (unlike the C++ version).
Visit     -> replaces RecordSystem's records[100] string array. One row per
             emergency event/visit, with real vitals + risk + triage stored
             as actual columns instead of a formatted string blob.
Condition -> replaces the hardcoded HeartAttack/Stroke/... subclasses.
             Same data, but as rows so it can be queried, extended, or
             edited without touching code.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.session import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    visits = relationship(
        "Visit", back_populates="patient", cascade="all, delete-orphan"
    )


class Condition(Base):
    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)       # e.g. "Heart Attack"
    base_severity = Column(String, nullable=False)           # LOW/MODERATE/HIGH/CRITICAL
    base_risk_score = Column(Integer, nullable=False)        # 0-10, same scale as old code
    first_aid = Column(String, nullable=False)
    medicine = Column(String, nullable=False)

    visits = relationship("Visit", back_populates="condition")


class Visit(Base):
    """
    One row per emergency event for a patient. This is the "vitals snapshot"
    that later feeds the ML risk engine in Phase 2 -- pulse/spo2/temperature
    are stored per-visit (not just on the patient) because vitals change
    every visit, which is the whole point of tracking trends.
    """
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    condition_id = Column(Integer, ForeignKey("conditions.id"), nullable=True)

    pulse = Column(Integer, nullable=True)
    spo2 = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    respiration_rate = Column(Integer, nullable=True)   # NEWS2 parameter
    systolic_bp = Column(Integer, nullable=True)        # NEWS2 parameter
    is_alert = Column(Boolean, nullable=True)            # NEWS2 consciousness parameter (True=Alert)

    risk_score = Column(Integer, nullable=False, default=0)   # 0-100 (ML model or rule-based fallback)
    triage_level = Column(String, nullable=True)              # P1/P2/P3/P4
    risk_engine = Column(String, nullable=True, default="rule_based")  # "ml_model" or "rule_based"
    news2_score = Column(Integer, nullable=True)               # real NEWS2 total (0-?), independent of ML model
    news2_risk_level = Column(String, nullable=True)            # LOW/LOW-MEDIUM/MEDIUM/HIGH, per NEWS2 spec
    notes = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="visits")
    condition = relationship("Condition", back_populates="visits")
