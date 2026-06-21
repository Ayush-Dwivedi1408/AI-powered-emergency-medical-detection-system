"""
Disease prediction model trainer.

DATA SOURCE: Training.csv / Testing.csv, originally from a Kaggle dataset
("Disease Prediction Using Machine Learning"), traceable to a Columbia
University DBMI Disease-Symptom Knowledge Base project. NOT real patient
records -- see README.md in this directory for the full honesty disclosure.

CRITICAL HONESTY NOTE, READ BEFORE TRUSTING ANY ACCURACY NUMBER BELOW:
This dataset is almost perfectly deterministic. Of 4920 training rows,
only 304 are unique symptom combinations -- the rest are exact duplicates
(each disease repeats ~7-8 unique patterns ~15x to pad to 120 rows).
This means ANY reasonable classifier will score 95-100% accuracy, not
because it learned medicine, but because the mapping symptoms->disease
is nearly a lookup table by construction. A high accuracy score here is
NOT evidence of genuine diagnostic skill -- it's a property of how the
dataset was built. State this explicitly anywhere this model's results
are shown or discussed.
"""
import joblib
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.preprocessing import LabelEncoder


def load_data():
    train = pd.read_csv("Training.csv")
    test = pd.read_csv("Testing.csv")

    # Training.csv has a trailing empty "Unnamed: 133" column -- a CSV
    # export artifact from the original dataset, not real data. Drop it.
    if "Unnamed: 133" in train.columns:
        train = train.drop(columns=["Unnamed: 133"])

    symptom_cols = [c for c in train.columns if c != "prognosis"]

    X_train, y_train = train[symptom_cols], train["prognosis"]
    X_test, y_test = test[symptom_cols], test["prognosis"]

    return X_train, y_train, X_test, y_test, symptom_cols


def main():
    X_train, y_train, X_test, y_test, symptom_cols = load_data()

    print(f"Training rows: {len(X_train)} ({X_train.drop_duplicates().shape[0]} unique symptom patterns)")
    print(f"Test rows: {len(X_test)}")
    print(f"Symptoms: {len(symptom_cols)}")
    print(f"Diseases: {y_train.nunique()}")
    print()

    le = LabelEncoder()
    y_train_enc = le.fit_transform(y_train)
    y_test_enc = le.transform(y_test)

    # ---------- Decision Tree (simple, explainable baseline) ----------
    dt = DecisionTreeClassifier(random_state=42, max_depth=15)
    dt.fit(X_train, y_train_enc)
    dt_preds = dt.predict(X_test)
    dt_acc = accuracy_score(y_test_enc, dt_preds)
    dt_f1 = f1_score(y_test_enc, dt_preds, average="weighted")

    print("=== Decision Tree ===")
    print(f"Accuracy: {dt_acc:.4f}  |  Weighted F1: {dt_f1:.4f}")
    print()

    # ---------- Random Forest (ensemble, typically more robust) ----------
    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15)
    rf.fit(X_train, y_train_enc)
    rf_preds = rf.predict(X_test)
    rf_acc = accuracy_score(y_test_enc, rf_preds)
    rf_f1 = f1_score(y_test_enc, rf_preds, average="weighted")

    print("=== Random Forest ===")
    print(f"Accuracy: {rf_acc:.4f}  |  Weighted F1: {rf_f1:.4f}")
    print()

    print("--- HONEST CONTEXT FOR THE NUMBERS ABOVE ---")
    print("These accuracy scores are expected to be very high (95-100%)")
    print("because of how this dataset is constructed (see module docstring).")
    print("This is NOT a sign of strong diagnostic modeling -- it reflects")
    print("near-deterministic symptom-to-disease mapping in the source data.")
    print()

    # Pick the better model by weighted F1 (same selection principle as
    # the vitals risk engine in ml/train.py, for consistency)
    if rf_f1 >= dt_f1:
        winner_name, winner_model = "random_forest", rf
    else:
        winner_name, winner_model = "decision_tree", dt

    print(f"Selected model: {winner_name}")

    print()
    print("Full classification report (winner):")
    winner_preds = winner_model.predict(X_test)
    print(classification_report(y_test_enc, winner_preds, target_names=le.classes_, zero_division=0))

    joblib.dump({
        "model": winner_model,
        "model_name": winner_name,
        "label_encoder": le,
        "symptom_columns": symptom_cols,
        "disease_classes": list(le.classes_),
    }, "disease_model.pkl")
    print("Saved to disease_model.pkl")


if __name__ == "__main__":
    main()
