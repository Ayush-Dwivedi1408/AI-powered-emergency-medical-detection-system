"""
Quick end-to-end smoke test for Phase 1, using FastAPI's TestClient
(no need for a separately-running server process).
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== Root ===")
r = client.get("/")
print(r.status_code, r.json())

print("\n=== List conditions ===")
r = client.get("/conditions/")
conditions = r.json()
print(r.status_code, f"{len(conditions)} conditions")
heart_attack = next(c for c in conditions if c["name"] == "Heart Attack")
print("Heart Attack condition id:", heart_attack["id"])

print("\n=== Create patient (valid) ===")
r = client.post("/patients/", json={"name": "John Doe", "age": 30})
print(r.status_code, r.json())
patient_id = r.json()["id"]

print("\n=== Create patient (invalid age -> should 422) ===")
r = client.post("/patients/", json={"name": "Bad Age", "age": -5})
print(r.status_code, r.json()["detail"][0]["msg"])

print("\n=== Create patient (missing name -> should 422) ===")
r = client.post("/patients/", json={"age": 40})
print(r.status_code)

print("\n=== Log a visit: Heart Attack, abnormal pulse ===")
r = client.post("/visits/", json={
    "patient_id": patient_id,
    "condition_id": heart_attack["id"],
    "pulse": 130,
    "spo2": 89,
    "temperature": 37.0,
    "notes": "Chest pain, shortness of breath"
})
print(r.status_code, r.json())

print("\n=== Log a visit: invalid spo2 (>100) -> should 422 ===")
r = client.post("/visits/", json={
    "patient_id": patient_id,
    "spo2": 150,
})
print(r.status_code)

print("\n=== Get patient detail (with visit history) ===")
r = client.get(f"/patients/{patient_id}")
print(r.status_code)
detail = r.json()
print("Name:", detail["name"], "| Visits logged:", len(detail["visits"]))
for v in detail["visits"]:
    print(" ->", v["risk_score"], v["triage_level"])

print("\n=== Get non-existent patient -> should 404 ===")
r = client.get("/patients/9999")
print(r.status_code, r.json())

print("\n=== Model info (Phase 2: which risk engine is active) ===")
r = client.get("/visits/model-info")
print(r.status_code, r.json())

print("\n=== Log a visit with symptom flags -> should use ML model ===")
r = client.post("/visits/", json={
    "patient_id": patient_id,
    "condition_id": heart_attack["id"],
    "pulse": 135,
    "spo2": 86.0,
    "temperature": 38.2,
    "has_chest_pain": True,
    "has_breathing_diff": True,
    "has_bleeding": False,
    "notes": "Severe presentation, testing ML path"
})
print(r.status_code, r.json())
assert r.json()["risk_engine"] == "ml_model", "Expected ML model to be used!"

print("\n=== Log a visit with missing vitals -> should fall back to rule-based ===")
r = client.post("/visits/", json={
    "patient_id": patient_id,
    "condition_id": heart_attack["id"],
    "notes": "No vitals recorded"
})
print(r.status_code, r.json())
assert r.json()["risk_engine"] == "rule_based", "Expected rule-based fallback when vitals missing!"

print("\n=== Mild case (low vitals/symptoms) -> should predict lower risk band ===")
r = client.post("/visits/", json={
    "patient_id": patient_id,
    "condition_id": next(c for c in conditions if c["name"] == "Minor Cut")["id"],
    "pulse": 75,
    "spo2": 98.0,
    "temperature": 36.8,
})
print(r.status_code, r.json())

print("\nAll smoke tests ran.")
