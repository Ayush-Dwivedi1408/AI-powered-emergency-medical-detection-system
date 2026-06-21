# Backend Setup

## 1. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

## 2. Install dependencies
```bash
pip install -r requirements.txt
```

## 3. Seed the database
Creates `emergency.db` (SQLite) and loads the 10 emergency condition types.
```bash
python -m app.db.seed
```

## 4. Run the server
```bash
uvicorn app.main:app --reload
```

## 5. Explore the API
Open http://localhost:8000/docs for the interactive Swagger UI -- you can
create patients, log visits, and see the model's risk/triage output
directly from the browser.

Check `GET /visits/model-info` to confirm the ML model loaded correctly
(it should report `"engine": "ml_model"`, not `"rule_based_fallback"`).

## 6. Run the smoke test
```bash
python smoke_test.py
```
This exercises every endpoint, validation rule, and both the ML and
rule-based-fallback code paths.

## Notes
- The model file at `app/ml_models/risk_model.pkl` is already trained and
  included -- you don't need to retrain to run the backend. See
  `ml/README.md` if you want to regenerate or retrain it.
- `emergency.db` is created fresh by the seed script; delete it and
  re-seed any time you want a clean slate.
