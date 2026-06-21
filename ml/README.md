# ML Pipeline

This directory is the model training pipeline. It's run **separately**
from the backend -- you only need to re-run this if you want to
regenerate the dataset or retrain the model. The backend just consumes
the resulting `.pkl` file.

## 1. Install dependencies
```bash
pip install pandas numpy scikit-learn xgboost joblib
```

## 2. Generate the synthetic dataset
```bash
python generate_dataset.py
```
Writes `data/synthetic_emergency_data.csv` (5,000 rows). Read the
docstring at the top of this file -- it documents exactly how the
ground-truth risk scores are constructed, which you should be able to
explain in an interview.

## 3. Train and evaluate models
```bash
python train.py
```
This trains Logistic Regression and XGBoost, prints a full evaluation
(classification report, confusion matrix, feature importances/
coefficients) for both, and saves the better-performing one to
`models/risk_model.pkl`.

## 4. Deploy the model to the backend
```bash
cp models/risk_model.pkl ../backend/app/ml_models/risk_model.pkl
```
Restart the backend (or it'll pick up the new file on next startup,
since it's loaded once at import time).

## Things worth experimenting with (good for learning, good for interview talking points)
- Change `RNG_SEED` or `N_SAMPLES` in `generate_dataset.py` and see how
  model performance shifts with more/less data.
- Try `class_weight` variations or `SMOTE`-style oversampling for the
  rare CRITICAL class instead of just `class_weight="balanced"`.
- Add a feature (e.g. `respiratory_rate`) end-to-end: dataset generator
  → train.py → triage.py → schemas.py → smoke_test.py, to practice
  extending the full pipeline.
- Try selecting the "winning" model by CRITICAL-class recall instead of
  weighted F1, and see how the choice changes -- this directly explores
  the limitation documented in the main README.
