"""
Tests for API key authentication.

These are intentionally simple -- the point is to verify that the guard
actually fires, not to test cryptography. A recruiter asking "what
security does this have?" should get "API key auth verified by tests
that confirm unauthenticated requests are rejected."
"""
from fastapi.testclient import TestClient
from app.main import app


def test_missing_api_key_returns_403():
    # No headers at all
    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/patients/")
    assert r.status_code == 403


def test_wrong_api_key_returns_403():
    client = TestClient(app, headers={"X-API-Key": "not-the-right-key"}, raise_server_exceptions=False)
    r = client.get("/patients/")
    assert r.status_code == 403


def test_correct_api_key_passes():
    client = TestClient(app, headers={"X-API-Key": "dev-secret"})
    r = client.get("/patients/")
    assert r.status_code == 200


def test_auth_error_message_is_clear():
    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/patients/")
    assert "API key" in r.json()["detail"]
