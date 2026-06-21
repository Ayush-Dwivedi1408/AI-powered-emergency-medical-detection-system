"""
Unit tests on app.services.triage directly -- no HTTP, no DB. These test
the risk engine in isolation, which is useful for fast iteration when
retraining the model (see ml/README.md) and for verifying the fallback
logic without needing a running API.
"""
from app.services import triage
from app.models import models


def _condition(severity="LOW", base_score=2):
    return models.Condition(
        name="Test Condition",
        base_severity=severity,
        base_risk_score=base_score,
        first_aid="n/a",
        medicine="n/a",
    )


def test_full_vitals_uses_ml_engine():
    score, level, engine = triage.calculate_risk_and_triage(
        age=70, pulse=140, spo2=85.0, temperature=39.0,
        condition=_condition("CRITICAL", 10),
        has_chest_pain=True, has_breathing_diff=True, has_bleeding=False,
    )
    assert engine == "ml_model"
    assert 0 <= score <= 100
    assert level in ("P1 - IMMEDIATE", "P2 - URGENT", "P3 - LESS URGENT", "P4 - ROUTINE")


def test_missing_pulse_falls_back():
    score, level, engine = triage.calculate_risk_and_triage(
        age=30, pulse=None, spo2=97.0, temperature=37.0, condition=None,
    )
    assert engine == "rule_based"


def test_missing_spo2_falls_back():
    score, level, engine = triage.calculate_risk_and_triage(
        age=30, pulse=80, spo2=None, temperature=37.0, condition=None,
    )
    assert engine == "rule_based"


def test_missing_temperature_falls_back():
    score, level, engine = triage.calculate_risk_and_triage(
        age=30, pulse=80, spo2=97.0, temperature=None, condition=None,
    )
    assert engine == "rule_based"


def test_no_condition_still_works():
    """condition=None must not crash -- a visit can be logged without
    a specific diagnosis selected."""
    score, level, engine = triage.calculate_risk_and_triage(
        age=30, pulse=80, spo2=97.0, temperature=37.0, condition=None,
    )
    assert 0 <= score <= 100


def test_rule_based_fallback_age_increases_risk():
    young_score, _, _ = triage.calculate_risk_and_triage(
        age=20, pulse=None, spo2=97.0, temperature=37.0, condition=None,
    )
    elderly_score, _, _ = triage.calculate_risk_and_triage(
        age=85, pulse=None, spo2=97.0, temperature=37.0, condition=None,
    )
    assert elderly_score >= young_score


def test_get_engine_status_reports_ml_model_when_loaded():
    status = triage.get_engine_status()
    assert status["engine"] in ("ml_model", "rule_based_fallback")
    if status["engine"] == "ml_model":
        assert "model_name" in status
        assert "features" in status
