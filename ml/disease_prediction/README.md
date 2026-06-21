# Disease Prediction Module

## What this is

A symptom-checker demo that predicts likely diseases from a checklist of
132 symptoms, trained on a real public dataset (not invented data).

**This is explicitly NOT a diagnostic tool.** See the disclaimer that
appears every time a prediction is shown in the app, and read the
honesty section below before trusting any number this model produces.

## Data source and provenance

- Files: `Training.csv` (4,920 rows) / `Testing.csv` (42 rows)
- Originally a Kaggle dataset: "Disease Prediction Using Machine Learning"
- Traceable to a Columbia University DBMI (Department of Biomedical
  Informatics) Disease-Symptom Knowledge Base project
- **132 binary symptom columns, 41 disease labels**

## Critical honesty disclosure — read this before trusting any accuracy number

We inspected the actual data, not just the dataset's description. Here's
what we found:

- **94% of training rows are exact duplicates.** Of 4,920 rows, only 304
  are unique symptom combinations. Each disease has roughly 7-8 unique
  symptom patterns, each repeated ~15 times to pad the dataset to a
  perfectly even 120 rows per disease.
- **The 120-rows-per-disease balance is itself a signal of synthetic
  construction.** Real clinical data is never this evenly distributed
  across conditions.
- **This means the symptom→disease mapping is nearly deterministic by
  construction**, not because the relationships are medically simple.

### What this means for the model's accuracy

Our trained Random Forest scores ~97.6% accuracy on the test set. **This
high number does not indicate strong diagnostic modeling.** It reflects
the fact that the underlying task is close to a lookup table: most
diseases in this dataset are distinguished by fixed, non-overlapping
symptom clusters with very little real-world noise or ambiguity.

For comparison, we also trained a single Decision Tree, which scored
only **45% accuracy** on the same test set — because a single tree
overfits to one specific decision path through the 304 unique patterns
and fails to generalize even slightly. The Random Forest's much higher
score comes from averaging 100 such trees, which smooths out that
overfitting — a real, observable difference in model behavior, and a
useful thing to be able to explain, even though neither number should
be read as "this model understands medicine."

## What's implemented

- `train_disease_model.py` — trains and compares Decision Tree vs.
  Random Forest using the dataset's own provided train/test split
  (not a custom split), selects the winner by weighted F1
- `backend/app/services/disease_prediction.py` — loads the trained
  model, returns **ranked top-5 candidates with probabilities**, never
  a single bare answer, with a disclaimer field on every response
- `backend/app/routers/disease_prediction.py` — a deliberately separate
  `/symptoms/*` API, architecturally isolated from `/visits/` and
  `/patients/` — this feature does not write to the database and does
  not affect triage priority in any way
- Frontend: `SymptomChecker.jsx` page with a checklist UI. The
  disclaimer component (`DiseaseDisclaimer.jsx`) is rendered twice on
  this page — once before any interaction, and again directly next to
  any result — so it's structurally impossible to see a prediction
  without seeing the caveat in the same view.

## Why probabilities are shown as a ranked list, not a single verdict

Showing "Top 5: Common Cold 89%, Chicken pox 0.5%, ..." is a more honest
framing than "You have Common Cold" or even "73% chance of X" alone.
A ranked list with visibly low secondary probabilities communicates
"these are statistically closest matches in a limited dataset," which
is what the model is actually doing — not "this is a diagnosis."

## First-aid guidance — what's included and what's deliberately left out

`backend/app/services/first_aid_data.py` provides general supportive-care
guidance for each of the 41 diseases, shown only for the **top-ranked**
prediction (lower-ranked candidates are too uncertain to attach care
advice to).

**Every disease is classified into one of two tiers, by explicit, documented rule:**

- **"common" (19 diseases)** — everyday conditions (Common Cold, Migraine,
  Allergy, Gastroenteritis, Dengue, etc.) where general supportive care
  and OTC medicine **categories** (e.g. "fever reducer," never an exact
  drug name or dose) are genuinely the standard first-line advice.
- **"serious" (22 diseases)** — conditions requiring diagnosis-specific
  treatment (AIDS, all Hepatitis types, Tuberculosis, Heart attack,
  Paralysis, Diabetes, Hypertension, etc.) where the guidance is
  intentionally limited to "what to do while seeking care" and "why a
  doctor is necessary" — **no medicine category, no dosage, ever.**

**Verification:** `test_serious_tier_advice_contains_no_specific_drug_names`
and `test_all_41_diseases_have_first_aid_coverage` in
`backend/tests/test_disease_prediction.py` enforce this at the test
level — not just by convention, but checked automatically on every run.

No disease, in either tier, ever receives a specific drug name or
dosage from this system. The most specific guidance given is an OTC
medicine *category* (e.g. "antihistamine," "fever reducer") for the
common tier only.

## Running it

```bash
cd ml/disease_prediction
python train_disease_model.py
cp disease_model.pkl ../../backend/app/ml_models/
```

Restart the backend afterward to pick up a retrained model.
