"""
NEWS2 (National Early Warning Score 2) -- a REAL, published clinical scoring
system, not something we invented.

Source: Royal College of Physicians (UK), used across NHS England and
NHS Scotland to detect patient deterioration. Reference table reproduced
from multiple public clinical trial protocol documents and NHS clinical
guidance (see README for citation).

WHY THIS EXISTS (vs. our earlier custom rule-based formula):
NEWS2 does NOT try to diagnose a specific disease from vitals -- it
measures physiological deterioration in general, which is exactly why
it's valid across virtually any condition. This is the correct way to
build a "works for all diseases" vitals score: by deliberately NOT
tying it to any particular diagnosis, unlike a disease-prediction model.

This module is independent of the ML risk model (services/triage.py).
It can be used as:
  1. A clinically-grounded fallback when the ML model can't run
  2. A comparison/sanity-check against the ML model's output
  3. A standalone score, citable as a real clinical tool in interviews

NOT IMPLEMENTED: the "supplemental oxygen" +2 modifier and the SpO2
Scale 2 (for COPD/hypercapnic patients) variant, since our data model
doesn't currently capture oxygen therapy status or chronic respiratory
diagnosis. This is a known, documented simplification -- see README.
"""
from dataclasses import dataclass


@dataclass
class News2Result:
    total_score: int
    risk_level: str  # "LOW", "LOW-MEDIUM", "MEDIUM", "HIGH"
    triage_level: str  # mapped to our existing P1-P4 scale
    component_scores: dict  # per-parameter breakdown, for transparency
    red_flag: bool  # True if any single parameter scored 3 (NEWS2 "red score" rule)


def _score_respiration_rate(rate: int | None) -> int | None:
    if rate is None:
        return None
    if rate <= 8 or rate >= 25:
        return 3
    if 21 <= rate <= 24:
        return 2
    if 9 <= rate <= 11:
        return 1
    return 0  # 12-20


def _score_spo2(spo2: float | None) -> int | None:
    """Scale 1 only -- standard patients, not COPD/hypercapnic (see module docstring)."""
    if spo2 is None:
        return None
    if spo2 <= 91:
        return 3
    if 92 <= spo2 <= 93:
        return 2
    if 94 <= spo2 <= 95:
        return 1
    return 0  # >= 96


def _score_systolic_bp(sbp: int | None) -> int | None:
    if sbp is None:
        return None
    if sbp <= 90 or sbp >= 220:
        return 3
    if 91 <= sbp <= 100:
        return 2
    if 101 <= sbp <= 110:
        return 1
    return 0  # 111-219


def _score_pulse(pulse: int | None) -> int | None:
    if pulse is None:
        return None
    if pulse <= 40 or pulse >= 131:
        return 3
    if 111 <= pulse <= 130:
        return 2
    if 41 <= pulse <= 50 or 91 <= pulse <= 110:
        return 1
    return 0  # 51-90


def _score_temperature(temp: float | None) -> int | None:
    if temp is None:
        return None
    if temp <= 35.0:
        return 3
    if temp >= 39.1:
        return 2
    if 38.1 <= temp <= 39.0:
        return 1
    if 35.1 <= temp <= 36.0:
        return 1
    return 0  # 36.1-38.0


def _score_consciousness(is_alert: bool | None) -> int | None:
    """True = Alert (0). False = any of Confused/Voice/Pain/Unresponsive (3)."""
    if is_alert is None:
        return None
    return 0 if is_alert else 3


_RISK_TO_TRIAGE = {
    "LOW": "P4 - ROUTINE",
    "LOW-MEDIUM": "P3 - LESS URGENT",
    "MEDIUM": "P2 - URGENT",
    "HIGH": "P1 - IMMEDIATE",
}


def calculate_news2(
    respiration_rate: int | None = None,
    spo2: float | None = None,
    systolic_bp: int | None = None,
    pulse: int | None = None,
    temperature: float | None = None,
    is_alert: bool | None = None,
) -> News2Result:
    """
    Calculates a real NEWS2 score from available vitals. Any missing
    parameter is simply excluded from the total (scored as contributing 0
    and flagged as None in component_scores) rather than guessed --
    NEWS2 is meant to be calculated from whatever vitals were actually
    measured, not from invented defaults.
    """
    components = {
        "respiration_rate": _score_respiration_rate(respiration_rate),
        "spo2": _score_spo2(spo2),
        "systolic_bp": _score_systolic_bp(systolic_bp),
        "pulse": _score_pulse(pulse),
        "temperature": _score_temperature(temperature),
        "consciousness": _score_consciousness(is_alert),
    }

    scored_values = [v for v in components.values() if v is not None]
    total = sum(scored_values)
    red_flag = any(v == 3 for v in scored_values)

    # NEWS2 official risk thresholds (see module docstring for source)
    if red_flag and total < 5:
        risk_level = "LOW-MEDIUM"  # the "red score" rule overrides total <5
    elif total >= 7:
        risk_level = "HIGH"
    elif total >= 5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return News2Result(
        total_score=total,
        risk_level=risk_level,
        triage_level=_RISK_TO_TRIAGE[risk_level],
        component_scores=components,
        red_flag=red_flag,
    )
