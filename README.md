# AI-Powered Emergency Decision Support Platform

A backend + React dashboard for logging patient emergency visits, scoring clinical risk with a trained ML model, and assigning triage priority (P1–P4).

![CI](https://github.com/YOUR_USERNAME/emergency-platform/actions/workflows/ci.yml/badge.svg)

---

## What this project is — and what it honestly isn't

This is a **portfolio project demonstrating an end-to-end ML + backend + frontend engineering pipeline**. It is not a clinically validated medical device and should never be used as one.

Specifically:
- The risk model is trained on a **synthetic dataset** generated from documented heuristic rules (`ml/generate_dataset.py`), not real patient data.
- The "ground truth" risk labels are formulas I designed myself, loosely inspired by common triage heuristics. They are intentional simplifications.
- The goal is to demonstrate: synthetic data generation with documented assumptions, feature engineering, model training and evaluation with proper methodology, model comparison, and full-stack integration of a trained model with validation, persistence, auth, tests, and CI.

This is stated openly because being able to articulate what a model *cannot* do is part of the skill being demonstrated.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend API | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite (dev) → Postgres-ready (one env var change) |
| ML | scikit-learn, XGBoost, pandas, joblib |
| Frontend | React, Vite, Tailwind CSS, Recharts |
| Auth | API key (X-API-Key header) |
| Tests | pytest, 39 tests, FastAPI TestClient |
| CI | GitHub Actions (runs on every push) |
| Deployment | Docker, docker-compose |

---

## Project Structure

```
emergency-platform/
├── .github/workflows/ci.yml     # GitHub Actions CI
├── docker-compose.yml            # one command to run the whole stack
├── backend/
│   ├── app/
│   │   ├── main.py               # app entrypoint, CORS, auth, router wiring
│   │   ├── auth.py               # API key authentication dependency
│   │   ├── models/               # SQLAlchemy ORM (patients, visits, conditions)
│   │   ├── schemas/              # Pydantic validation (rejects bad input at boundary)
│   │   ├── routers/              # HTTP route handlers (patients, visits, conditions)
│   │   ├── db/                   # session, CRUD functions, seed script
│   │   ├── services/triage.py    # ML risk engine + rule-based fallback
│   │   └── ml_models/risk_model.pkl
│   ├── tests/                    # 39 pytest tests (auth, patients, visits, triage)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.js         # single source of truth for all backend calls
│   │   ├── components/           # TriageBadge, RiskEngineTag
│   │   └── pages/                # Dashboard, PatientDetail, NewPatient, Analytics
│   ├── Dockerfile
│   └── nginx.conf
└── ml/
    ├── generate_dataset.py       # synthetic data with documented ground-truth rules
    ├── train.py                  # LogisticRegression vs XGBoost, proper evaluation
    └── data/synthetic_emergency_data.csv
```

---

## Quickstart — Docker (recommended)

```bash
git clone https://github.com/YOUR_USERNAME/emergency-platform
cd emergency-platform
mkdir -p data
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend API docs → http://localhost:8000/docs
- All API requests require header: `X-API-Key: dev-secret`

> For production, set `API_KEY` in your environment to something secret before running `docker compose up`.

---

## Quickstart — Local dev (two terminals)

**Terminal 1 — Backend:**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m app.db.seed
uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open http://localhost:5173

---

## Running Tests

```bash
cd backend
python -m pytest -v
```

39 tests covering: API auth (missing/wrong/correct key), patient CRUD, visit creation and validation, ML engine vs fallback switching, triage scoring direction, and all 404 edge cases.

---

## ML Risk Engine — honest explanation

The risk engine lives in `backend/app/services/triage.py`. It:

1. Loads a trained XGBoost model from `risk_model.pkl` at startup
2. Takes age, pulse, SpO2, temperature, condition severity, and three symptom flags as input
3. Predicts a risk band (LOW / MODERATE / HIGH / CRITICAL) mapped to a 0–100 score and a triage level (P1–P4)
4. **Falls back** to a simple rule-based calculation (and reports `risk_engine: "rule_based"`) if vitals are incomplete or the model file is unavailable — so the API never crashes silently

**Why two models were trained** (see `ml/train.py` output): XGBoost scored higher on weighted F1 (0.844 vs 0.796) but had worse recall on the rare CRITICAL class due to class imbalance. XGBoost was selected by the aggregate metric — but for a real triage system, optimizing for CRITICAL-class recall would be the correct criterion. This tradeoff is intentionally documented, not hidden.

---

## NEWS2 — a real, published clinical score (not our invention)

`backend/app/services/news2.py` implements **NEWS2 (National Early Warning Score 2)**, a standardised scoring system developed by the **Royal College of Physicians (UK)** and used across NHS England and NHS Scotland to detect patient deterioration. This is a real, citable clinical tool — not something built for this project.

**Why it exists alongside the ML model, not instead of it:** the ML risk engine above tries to predict risk for the specific conditions in our `conditions` table. NEWS2 deliberately does *not* try to diagnose anything — it scores general physiological deterioration from six vitals (respiration rate, SpO2, blood pressure, pulse, temperature, consciousness), which is exactly why it's valid as a fallback or sanity-check across virtually any presenting condition, unlike a disease-specific model.

**What's implemented exactly as published:**
- All six core parameters, scored 0–3 each per the official RCP scoring bands
- The "red score" rule: a single parameter scoring 3 escalates the risk level even if the total score is otherwise low — this is NEWS2's actual safety design, not ours
- Risk thresholds: 0–4 LOW, single-param-3 → LOW-MEDIUM minimum, 5–6 MEDIUM, 7+ HIGH

**What's deliberately not implemented** (documented simplification, not hidden): the +2 "on supplemental oxygen" modifier, and the alternate SpO2 Scale 2 used for COPD/chronic hypercapnic patients — our data model doesn't currently capture oxygen therapy status or chronic respiratory diagnosis.

**Verification:** `backend/tests/test_news2.py` includes a test reproducing a real documented clinical worked example (an 82-year-old COVID-19 patient case from published clinical trial protocol literature) — our implementation's component scores and total match the published reference exactly.

Every visit stores both `risk_score`/`risk_engine` (the ML side) and `news2_score`/`news2_risk_level` (the NEWS2 side) independently, so they can be compared rather than one silently overriding the other.

---

## Symptom Checker — disease prediction (separate feature)

`backend/app/services/disease_prediction.py`, exposed via `/symptoms/*` endpoints and the **Symptom Checker** page in the frontend nav.

This is a **completely separate feature** from triage/risk scoring — it doesn't touch patient records, doesn't affect triage priority, and isn't tied to any visit. It takes a checklist of symptoms and returns the top-5 statistically closest diseases from a 41-disease, 132-symptom public dataset.

**Read `ml/disease_prediction/README.md` before treating any number from this feature as meaningful** — it documents that 94% of the training data are exact duplicates of just 304 unique symptom patterns, which means the near-100% accuracy reflects the dataset's near-deterministic construction, not genuine diagnostic capability. The disclaimer shown in the app every time a prediction appears says exactly this, in plain language.

---

## Roadmap / what's not built (and why)

| Feature | Decision |
|---|---|
| AI chatbot | Cut — wrapping an LLM API is not a differentiator; everyone's 2026 project has one |
| Voice assistant | Cut — high effort, zero engineering depth for the portfolio |
| Hospital recommendation | Cut — Maps API integration, not meaningfully related to the ML/backend work |
| SMS/email alerts | Could add in ~1 hour (Twilio); left as a documented extension point |
| Alembic migrations | `Base.metadata.create_all()` is fine for SQLite dev; Alembic is the real path for schema changes in production |
| PostgreSQL | One env var change from SQLite; left undone because it adds ops complexity without adding learning value |
| NEWS2 oxygen modifier / Scale 2 | Requires tracking O2 therapy status and chronic respiratory diagnosis, not yet in the data model |
