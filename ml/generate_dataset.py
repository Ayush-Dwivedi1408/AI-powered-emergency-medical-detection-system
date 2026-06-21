"""
Synthetic dataset generator for the emergency risk model.

WHY SYNTHETIC, AND WHY THIS IS HONEST:
Real labeled emergency-triage data is sensitive, hard to get, and not
something a student project should claim to have. Instead, we generate
data from clinically-informed but simplified rules that WE define and can
fully explain. The model then learns to approximate these rules from
raw features -- which is a legitimate ML exercise (the model doesn't see
the rules directly, only age/pulse/spo2/temperature/symptom flags, and
has to learn the relationship), even though the ground truth itself is
not from real patients.

State this openly in interviews: "I generated a synthetic dataset using
documented clinical heuristics, then trained a model to predict risk
band from raw vitals -- this demonstrates the ML pipeline end-to-end,
not a clinically validated diagnostic tool."

FEATURES:
- age                 : int, 0-100
- pulse               : int, bpm
- spo2                : float, % blood oxygen saturation
- temperature         : float, Celsius
- condition_severity  : int, 0-3 (LOW/MODERATE/HIGH/CRITICAL encoded, mirrors
                         the `conditions` table's base_severity)
- has_chest_pain      : 0/1 symptom flag
- has_breathing_diff  : 0/1 symptom flag
- has_bleeding        : 0/1 symptom flag

TARGET:
- risk_score (0-100, continuous)   -- used for regression-style framing
- risk_band  (0=LOW,1=MODERATE,2=HIGH,3=CRITICAL) -- used for classification
"""
import numpy as np
import pandas as pd

RNG_SEED = 42
N_SAMPLES = 5000


def generate_dataset(n=N_SAMPLES, seed=RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    age = rng.integers(1, 95, size=n)
    pulse = rng.normal(80, 20, size=n).clip(30, 200).round().astype(int)
    spo2 = rng.normal(96, 4, size=n).clip(70, 100).round(1)
    temperature = rng.normal(37.0, 1.2, size=n).clip(34, 41.5).round(1)
    condition_severity = rng.integers(0, 4, size=n)  # 0=LOW .. 3=CRITICAL

    has_chest_pain = rng.binomial(1, 0.15, size=n)
    has_breathing_diff = rng.binomial(1, 0.15, size=n)
    has_bleeding = rng.binomial(1, 0.10, size=n)

    # ---- Ground-truth risk score formula (documented, not hidden) ----
    # This mirrors the same logic family as the Phase 1 rule-based stub,
    # but with continuous, slightly noisy relationships so the model has
    # something non-trivial to learn instead of just memorizing thresholds.
    risk = np.zeros(n)

    # Condition severity is the dominant factor (0-30 points)
    risk += condition_severity * 10

    # Vitals abnormality (graded, not just a hard cutoff)
    pulse_abnormality = np.abs(pulse - 80) / 10          # bigger deviation = more risk
    risk += np.clip(pulse_abnormality, 0, 15)

    spo2_deficit = np.clip(96 - spo2, 0, None)            # below-normal spo2 only
    risk += spo2_deficit * 3

    temp_abnormality = np.clip(temperature - 37.5, 0, None)
    risk += temp_abnormality * 8

    # Age risk multiplier -- elderly and very young patients are higher risk
    age_risk = np.where(age >= 60, (age - 60) * 0.4, 0)
    age_risk += np.where(age <= 5, (5 - age) * 1.0, 0)
    risk += age_risk

    # Symptom flags add fixed risk contributions
    risk += has_chest_pain * 12
    risk += has_breathing_diff * 10
    risk += has_bleeding * 8

    # Small random noise so the relationship isn't perfectly deterministic
    # (real-world data is never perfectly clean -- this keeps the exercise honest)
    risk += rng.normal(0, 4, size=n)

    risk_score = np.clip(risk, 0, 100).round().astype(int)

    # Risk band thresholds (mirrors triage bands from Phase 1)
    risk_band = pd.cut(
        risk_score,
        bins=[-1, 24, 49, 74, 100],
        labels=[0, 1, 2, 3],  # LOW, MODERATE, HIGH, CRITICAL
    ).astype(int)

    df = pd.DataFrame({
        "age": age,
        "pulse": pulse,
        "spo2": spo2,
        "temperature": temperature,
        "condition_severity": condition_severity,
        "has_chest_pain": has_chest_pain,
        "has_breathing_diff": has_breathing_diff,
        "has_bleeding": has_bleeding,
        "risk_score": risk_score,
        "risk_band": risk_band,
    })
    return df


if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv("data/synthetic_emergency_data.csv", index=False)
    print(f"Generated {len(df)} rows -> data/synthetic_emergency_data.csv")
    print("\nRisk band distribution:")
    print(df["risk_band"].value_counts().sort_index())
    print("\nSample rows:")
    print(df.head())
