"""
Tests for disease prediction -- both the service layer (no HTTP) and the
API endpoints. Verifies: real predictions work, disclaimer is ALWAYS
present, invalid/unknown symptoms are handled gracefully, and the
feature is correctly isolated from /visits/ (doesn't touch the DB).
"""
from app.services import disease_prediction


def test_get_available_symptoms_returns_132():
    symptoms = disease_prediction.get_available_symptoms()
    assert len(symptoms) == 132
    assert "itching" in symptoms
    assert "high_fever" in symptoms


def test_predict_with_real_training_pattern_matches_expected_disease():
    """Uses symptoms from an actual training row (Common Cold) -- the
    model should predict correctly on in-distribution data."""
    symptoms = [
        "continuous_sneezing", "chills", "fatigue", "cough", "high_fever",
        "headache", "swelled_lymph_nodes", "malaise", "phlegm",
        "throat_irritation", "redness_of_eyes", "sinus_pressure",
        "runny_nose", "congestion", "chest_pain", "loss_of_smell", "muscle_pain",
    ]
    result = disease_prediction.predict_disease(symptoms)
    assert result.available is True
    assert result.symptoms_provided == len(symptoms)
    assert len(result.top_predictions) > 0
    top_disease = result.top_predictions[0].disease
    assert top_disease == "Common Cold"


def test_disclaimer_always_present_on_successful_prediction():
    result = disease_prediction.predict_disease(["itching", "skin_rash"])
    assert result.disclaimer  # never empty/None
    assert "not a medical diagnosis" in result.disclaimer.lower() or "not a" in result.disclaimer.lower()


def test_disclaimer_always_present_even_with_no_valid_symptoms():
    result = disease_prediction.predict_disease(["this_is_not_a_real_symptom"])
    assert result.disclaimer
    assert result.symptoms_provided == 0
    assert result.top_predictions == []


def test_unknown_symptoms_are_filtered_not_errored():
    """Passing a mix of valid and invalid symptom names shouldn't crash --
    invalid ones are silently filtered, not rejected with an error,
    since the frontend checklist only ever sends valid names anyway."""
    result = disease_prediction.predict_disease(["itching", "not_a_real_symptom", "skin_rash"])
    assert result.available is True
    assert result.symptoms_provided == 2  # only the 2 valid ones counted


def test_get_model_status_reports_provenance():
    status = disease_prediction.get_model_status()
    assert status["available"] is True
    assert status["num_symptoms"] == 132
    assert status["num_diseases"] == 41
    assert "Kaggle" in status["data_source"] or "Columbia" in status["data_source"]


# ---------- API-level tests ----------

def test_list_available_symptoms_endpoint(client):
    r = client.get("/symptoms/available")
    assert r.status_code == 200
    assert len(r.json()["symptoms"]) == 132


def test_model_info_endpoint(client):
    r = client.get("/symptoms/model-info")
    assert r.status_code == 200
    assert r.json()["available"] is True


def test_predict_endpoint_returns_disclaimer(client):
    r = client.post("/symptoms/predict", json={"symptoms": ["itching", "skin_rash"]})
    assert r.status_code == 200
    body = r.json()
    assert body["disclaimer"]
    assert isinstance(body["top_predictions"], list)


def test_predict_endpoint_rejects_empty_symptom_list(client):
    r = client.post("/symptoms/predict", json={"symptoms": []})
    assert r.status_code == 422  # min_length=1 on the schema


def test_predict_endpoint_does_not_require_patient_or_visit(client):
    """Confirms this feature is correctly isolated -- no patient_id,
    no visit creation, no DB write needed to get a prediction."""
    r = client.post("/symptoms/predict", json={"symptoms": ["headache", "nausea"]})
    assert r.status_code == 200
    # Verify it didn't accidentally create any visits
    visits_r = client.get("/visits/")
    assert visits_r.json() == []


def test_all_41_diseases_have_first_aid_coverage():
    """Every disease the model can predict must have first-aid guidance --
    no silent fallback to the generic 'unknown' response for a real,
    expected disease name."""
    from app.services.first_aid_data import FIRST_AID
    assert len(FIRST_AID) == 41
    for entry in FIRST_AID.values():
        assert entry["tier"] in ("common", "serious")
        assert len(entry["advice"]) > 20  # not an empty/placeholder string


def test_serious_tier_advice_contains_no_specific_drug_names():
    """Spot-check: serious-tier advice should never name a specific
    medicine -- only general guidance and 'see a doctor' framing."""
    from app.services.first_aid_data import FIRST_AID
    banned_terms = ["mg", "tablet", "antiretroviral drug", "specific dose"]
    serious_entries = [v for v in FIRST_AID.values() if v["tier"] == "serious"]
    assert len(serious_entries) > 0
    for entry in serious_entries:
        advice_lower = entry["advice"].lower()
        for term in banned_terms:
            assert term not in advice_lower, f"Found '{term}' in serious-tier advice"


def test_predict_endpoint_includes_first_aid_for_top_prediction(client):
    """Common Cold pattern should return first-aid advice tagged 'common'
    tier alongside the prediction."""
    r = client.post("/symptoms/predict", json={"symptoms": [
        "continuous_sneezing", "chills", "fatigue", "cough", "high_fever",
        "headache", "swelled_lymph_nodes", "malaise", "phlegm",
        "throat_irritation", "redness_of_eyes", "sinus_pressure",
        "runny_nose", "congestion", "chest_pain", "loss_of_smell", "muscle_pain",
    ]})
    assert r.status_code == 200
    body = r.json()
    top = body["top_predictions"][0]
    assert top["disease"] == "Common Cold"
    assert top["first_aid_tier"] == "common"
    assert len(top["first_aid_advice"]) > 20
    assert "not a substitute" in body["disclaimer"].lower() or "not a medical diagnosis" in body["disclaimer"].lower()
