"""
Tests for /patients/ endpoints.

Covers: happy path, validation boundaries (the exact thing the original
C++ version had zero of), and 404 behavior.
"""


def test_create_patient_valid(client):
    r = client.post("/patients/", json={"name": "Alice", "age": 30})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Alice"
    assert body["age"] == 30
    assert "id" in body
    assert "created_at" in body


def test_create_patient_negative_age_rejected(client):
    r = client.post("/patients/", json={"name": "Bad Age", "age": -5})
    assert r.status_code == 422


def test_create_patient_zero_age_rejected(client):
    # age must be > 0 (gt=0 in schema) -- boundary check
    r = client.post("/patients/", json={"name": "Newborn Edge Case", "age": 0})
    assert r.status_code == 422


def test_create_patient_age_above_max_rejected(client):
    r = client.post("/patients/", json={"name": "Too Old", "age": 200})
    assert r.status_code == 422


def test_create_patient_age_at_max_boundary_accepted(client):
    # le=130 in schema -- 130 itself should be valid
    r = client.post("/patients/", json={"name": "Edge Case", "age": 130})
    assert r.status_code == 201


def test_create_patient_empty_name_rejected(client):
    r = client.post("/patients/", json={"name": "", "age": 30})
    assert r.status_code == 422


def test_create_patient_missing_name_rejected(client):
    r = client.post("/patients/", json={"age": 30})
    assert r.status_code == 422


def test_create_patient_missing_age_rejected(client):
    r = client.post("/patients/", json={"name": "No Age"})
    assert r.status_code == 422


def test_list_patients_empty(client):
    r = client.get("/patients/")
    assert r.status_code == 200
    assert r.json() == []


def test_list_patients_returns_created(client, sample_patient):
    r = client.get("/patients/")
    assert r.status_code == 200
    names = [p["name"] for p in r.json()]
    assert "Test Patient" in names


def test_get_patient_by_id(client, sample_patient):
    r = client.get(f"/patients/{sample_patient['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Test Patient"
    assert r.json()["visits"] == []  # no visits logged yet


def test_get_nonexistent_patient_404(client):
    r = client.get("/patients/99999")
    assert r.status_code == 404


def test_delete_patient(client, sample_patient):
    r = client.delete(f"/patients/{sample_patient['id']}")
    assert r.status_code == 204

    r = client.get(f"/patients/{sample_patient['id']}")
    assert r.status_code == 404


def test_delete_nonexistent_patient_404(client):
    r = client.delete("/patients/99999")
    assert r.status_code == 404
