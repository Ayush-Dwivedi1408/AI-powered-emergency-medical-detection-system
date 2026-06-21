"""
Trains and evaluates two models on the synthetic risk dataset:
  1. Logistic Regression -- explainable baseline (can show feature weights)
  2. XGBoost             -- stronger non-linear model for comparison

Saves the better-performing model (by weighted F1) to models/risk_model.pkl
along with the feature scaler, for use by the FastAPI backend.

WHY COMPARE TWO MODELS (interview talking point):
Logistic regression gives interpretable coefficients -- you can say
"a 1-unit increase in condition_severity increases log-odds of higher
risk by X" and defend it. XGBoost usually scores higher on imbalanced,
non-linear data but is harder to explain directly (we use feature
importance instead of coefficients). Showing you evaluated both and
made a reasoned choice is worth more than just picking the "fancier"
model by default.
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
)
from xgboost import XGBClassifier

FEATURES = [
    "age", "pulse", "spo2", "temperature",
    "condition_severity", "has_chest_pain", "has_breathing_diff", "has_bleeding",
]
TARGET = "risk_band"
BAND_NAMES = {0: "LOW", 1: "MODERATE", 2: "HIGH", 3: "CRITICAL"}


def load_data():
    df = pd.read_csv("data/synthetic_emergency_data.csv")
    X = df[FEATURES]
    y = df[TARGET]
    return X, y


def evaluate(name, model, X_test, y_test, scaled=False, scaler=None):
    X_eval = scaler.transform(X_test) if scaled else X_test
    preds = model.predict(X_eval)

    f1 = f1_score(y_test, preds, average="weighted")
    print(f"\n--- {name} ---")
    print(f"Weighted F1: {f1:.3f}")
    print(classification_report(
        y_test, preds, target_names=[BAND_NAMES[i] for i in sorted(BAND_NAMES)],
        zero_division=0,
    ))
    print("Confusion matrix (rows=actual, cols=predicted):")
    print(confusion_matrix(y_test, preds))
    return f1


def main():
    X, y = load_data()

    # stratify keeps the same class proportions in train/test splits --
    # important here because CRITICAL is rare (~0.4% of data)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ---------- Logistic Regression ----------
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    logreg = LogisticRegression(
        max_iter=1000, class_weight="balanced"
    )
    logreg.fit(X_train_scaled, y_train)
    f1_logreg = evaluate("Logistic Regression", logreg, X_test, y_test, scaled=True, scaler=scaler)

    print("\nLogistic Regression coefficients (per class, standardized features):")
    coef_df = pd.DataFrame(logreg.coef_, columns=FEATURES, index=[BAND_NAMES[i] for i in sorted(BAND_NAMES)])
    print(coef_df.round(2))

    # ---------- XGBoost ----------
    xgb = XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.1,
        objective="multi:softprob",
        num_class=4,
        eval_metric="mlogloss",
        random_state=42,
    )
    # class weighting via sample_weight since XGBClassifier doesn't take class_weight directly
    class_counts = y_train.value_counts()
    sample_weight = y_train.map(lambda c: len(y_train) / (len(class_counts) * class_counts[c]))
    xgb.fit(X_train, y_train, sample_weight=sample_weight)
    f1_xgb = evaluate("XGBoost", xgb, X_test, y_test, scaled=False)

    print("\nXGBoost feature importances:")
    importance_df = pd.Series(xgb.feature_importances_, index=FEATURES).sort_values(ascending=False)
    print(importance_df.round(3))

    # ---------- Pick winner, save artifacts ----------
    if f1_xgb >= f1_logreg:
        winner_name, winner_model, needs_scaling = "xgboost", xgb, False
    else:
        winner_name, winner_model, needs_scaling = "logistic_regression", logreg, True

    print(f"\n=== Selected model: {winner_name} (F1: {max(f1_xgb, f1_logreg):.3f}) ===")

    joblib.dump({
        "model": winner_model,
        "model_name": winner_name,
        "scaler": scaler if needs_scaling else None,
        "needs_scaling": needs_scaling,
        "features": FEATURES,
        "band_names": BAND_NAMES,
    }, "models/risk_model.pkl")
    print("Saved to models/risk_model.pkl")


if __name__ == "__main__":
    main()
