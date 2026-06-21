"""
Tests for /visits/ -- the core feature of the project.

These tests specifically verify the engine-switching behavior documented
in services/triage.py: full vitals -> ML model; missing vitals -> graceful
rule-based fallback. This is the single most important behavior to have
test coverage on, since it's the centerpiece of the "AI risk engine"
claim in the README.
"""


def test_create_visit_requires_existing_patient(client, seeded_condition):
    r = client.post("/visits/", json={
        "patient_id": 99999,
        "condition_id": seeded_condition.id,
        "pulse": 90, "spo2": 97.0, "temperature": 37.0,
    })
    assert r.status_code == 404


def test_create_visit_requires_existing_condition(client, sample_patient):
    r = client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "condition_id": 99999,
        "pulse": 90, "spo2": 97.0, "temperature": 37.0,
    })
    assert r.status_code == 404


def test_create_visit_with_full_vitals_uses_ml_model(client, sample_patient, seeded_condition):
    r = client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "condition_id": seeded_condition.id,
        "pulse": 130, "spo2": 86.0, "temperature": 38.5,
        "has_chest_pain": True, "has_breathing_diff": True, "has_bleeding": False,
    })
    assert r.status_code == 201
    body = r.json()
    assert body["risk_engine"] == "ml_model"
    assert 0 <= body["risk_score"] <= 100
    assert body["triage_level"] in (
        "P1 - IMMEDIATE", "P2 - URGENT", "P3 - LESS URGENT", "P4 - ROUTINE"
    )


def test_create_visit_missing_vitals_falls_back_to_rule_based(client, sample_patient, seeded_condition):
    r = client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "condition_id": seeded_condition.id,
        # no pulse/spo2/temperature provided
    })
    assert r.status_code == 201
    body = r.json()
    assert body["risk_engine"] == "rule_based"


def test_create_visit_partial_vitals_falls_back_to_rule_based(client, sample_patient, seeded_condition):
    # only pulse provided, spo2/temperature missing -- model needs all three
    r = client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "condition_id": seeded_condition.id,
        "pulse": 90,
    })
    assert r.status_code == 201
    assert r.json()["risk_engine"] == "rule_based"


def test_severe_case_scores_higher_than_mild_case(client, sample_patient, seeded_condition):
    """
    Sanity check on model behavior direction (not exact values, since those
    depend on the trained model): a clearly severe presentation should not
    score lower than a clearly mild one. This guards against, e.g., a future
    retrain accidentally inverting a feature's sign.
    """
    severe = client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "condition_id": seeded_condition.id,
        "pulse": 140, "spo2": 82.0, "temperature": 39.5,
        "has_chest_pain": True, "has_breathing_diff": True, "has_bleeding": True,
    }).json()

    mild = client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "pulse": 75, "spo2": 98.0, "temperature": 36.8,
    }).json()

    assert severe["risk_score"] >= mild["risk_score"]


def test_invalid_spo2_above_100_rejected(client, sample_patient):
    r = client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "spo2": 150.0,
    })
    assert r.status_code == 422


def test_invalid_pulse_out_of_range_rejected(client, sample_patient):
    r = client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "pulse": 1000,
    })
    assert r.status_code == 422


def test_get_patient_visits(client, sample_patient, seeded_condition):
    client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "condition_id": seeded_condition.id,
        "pulse": 90, "spo2": 97.0, "temperature": 37.0,
    })
    r = client.get(f"/visits/patient/{sample_patient['id']}")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_visits_for_nonexistent_patient_404(client):
    r = client.get("/visits/patient/99999")
    assert r.status_code == 404


def test_model_info_endpoint_reports_active_engine(client):
    r = client.get("/visits/model-info")
    assert r.status_code == 200
    body = r.json()
    assert "engine" in body
    assert body["engine"] in ("ml_model", "rule_based_fallback")


def test_create_visit_returns_news2_score_alongside_ml_score(client, sample_patient, seeded_condition):
    """
    NEWS2 is calculated and stored independently of the ML risk engine --
    both should be present on the same visit, since they're two different,
    independently meaningful scores (not one replacing the other).
    """
    r = client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "condition_id": seeded_condition.id,
        "pulse": 109, "spo2": 95.0, "temperature": 39.0,
        "respiration_rate": 26, "systolic_bp": 95, "is_alert": False,
    })
    assert r.status_code == 201
    body = r.json()
    assert body["risk_engine"] == "ml_model"      # ML engine still ran
    assert body["news2_score"] == 11               # real NEWS2 score, independent of ML
    assert body["news2_risk_level"] == "HIGH"


def test_create_visit_news2_works_even_without_news2_specific_fields(client, sample_patient):
    """NEWS2 fields (respiration_rate, systolic_bp, is_alert) are optional --
    a visit logged with only the original vitals should still get a partial
    NEWS2 score, not an error."""
    r = client.post("/visits/", json={
        "patient_id": sample_patient["id"],
        "pulse": 80, "spo2": 97.0, "temperature": 37.0,
    })
    assert r.status_code == 201
    body = r.json()
    assert body["news2_score"] is not None
    assert body["news2_risk_level"] is not None
