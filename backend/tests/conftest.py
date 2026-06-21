"""
Shared pytest fixtures.

KEY DECISION: each test gets its own in-memory SQLite database, completely
isolated from your real emergency.db and from other tests. This is the
correct pattern -- without it, tests would either corrupt your real data
or fail unpredictably depending on what ran before them (a classic
"works on my machine, flaky in CI" bug).

We override FastAPI's `get_db` dependency rather than touching the
app's real session.py, so production code is never aware tests exist.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import Base, get_db
from app.models import models


@pytest.fixture()
def db_session():
    """Fresh in-memory SQLite DB for a single test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # keeps the same in-memory DB across connections in one test
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """TestClient wired to the isolated in-memory DB instead of the real one.
    Passes the dev API key header so auth doesn't block tests."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    # "dev-secret" matches the default in auth.py for local/test environments
    yield TestClient(app, headers={"X-API-Key": "dev-secret"})
    app.dependency_overrides.clear()


@pytest.fixture()
def seeded_condition(db_session):
    """One condition row, enough for most visit-related tests."""
    condition = models.Condition(
        name="Heart Attack",
        base_severity="CRITICAL",
        base_risk_score=10,
        first_aid="Call ambulance immediately.",
        medicine="Aspirin 325mg.",
    )
    db_session.add(condition)
    db_session.commit()
    db_session.refresh(condition)
    return condition


@pytest.fixture()
def sample_patient(client):
    """A persisted patient via the real API, for tests that need one to exist."""
    response = client.post("/patients/", json={"name": "Test Patient", "age": 40})
    return response.json()
