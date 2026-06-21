"""
Seeds the `conditions` table with the same 10 emergency types from the
original C++ HeartAttack/Stroke/.../MinorCut subclasses. This is the
"extract content from code into data" step -- the medical text is now a
table you can query, edit, or extend without touching application code.

Run with: python -m app.db.seed
"""
from app.db.session import SessionLocal, engine, Base
from app.models import models

CONDITIONS = [
    {
        "name": "Heart Attack",
        "base_severity": "CRITICAL",
        "base_risk_score": 10,
        "first_aid": (
            "1. Call ambulance (108) RIGHT NOW.\n"
            "2. Make patient sit or lie down comfortably.\n"
            "3. Loosen tight clothing around chest and neck.\n"
            "4. If unconscious, start CPR (30 compressions + 2 breaths).\n"
            "5. Give Aspirin 325mg to chew (if not allergic).\n"
            "6. Do NOT give food or water."
        ),
        "medicine": "Aspirin 325mg (chew if not allergic). Rush to hospital for ECG.",
    },
    {
        "name": "Stroke",
        "base_severity": "CRITICAL",
        "base_risk_score": 10,
        "first_aid": (
            "F - Face drooping? Ask to smile.\n"
            "A - Arm weakness? Ask to raise both arms.\n"
            "S - Speech slurred? Ask to repeat a sentence.\n"
            "T - Time to call 108 immediately!\n"
            "Lay patient on side if vomiting.\n"
            "Do NOT give any food, water or medicine."
        ),
        "medicine": "No self-medication. Must reach hospital within 4.5 hours.",
    },
    {
        "name": "Snake Bite",
        "base_severity": "CRITICAL",
        "base_risk_score": 10,
        "first_aid": (
            "1. Keep patient calm and still (panic spreads venom faster).\n"
            "2. Immobilize bitten limb below heart level.\n"
            "3. Remove rings/watches near bite area.\n"
            "4. Do NOT cut, suck or apply tourniquet.\n"
            "5. Rush to hospital for anti-venom immediately."
        ),
        "medicine": "Anti-venom only at hospital. No home remedies work.",
    },
    {
        "name": "Asthma Attack",
        "base_severity": "HIGH",
        "base_risk_score": 8,
        "first_aid": (
            "1. Help patient sit upright and stay calm.\n"
            "2. Give prescribed inhaler (2-4 puffs).\n"
            "3. Wait 5 minutes. If no relief, repeat inhaler.\n"
            "4. If no improvement after 3 times, call 108.\n"
            "5. Loosen tight clothing."
        ),
        "medicine": "Salbutamol inhaler (Ventolin). Hospital for nebulizer if severe.",
    },
    {
        "name": "Seizure",
        "base_severity": "HIGH",
        "base_risk_score": 8,
        "first_aid": (
            "1. Clear area of sharp objects.\n"
            "2. Cushion head with pillow or folded cloth.\n"
            "3. Turn patient gently on their side.\n"
            "4. Do NOT restrain or put anything in mouth.\n"
            "5. Time the seizure. If >5 minutes, call 108.\n"
            "6. Stay with patient until fully awake."
        ),
        "medicine": "Diazepam (only if prescribed). Consult doctor after seizure.",
    },
    {
        "name": "Severe Bleeding",
        "base_severity": "HIGH",
        "base_risk_score": 9,
        "first_aid": (
            "1. Apply firm pressure with clean cloth.\n"
            "2. Do NOT remove first cloth if soaked - add more layers.\n"
            "3. Elevate injured area above heart level.\n"
            "4. Apply tourniquet 2 inches above wound if needed.\n"
            "5. Call 108 immediately."
        ),
        "medicine": "No oral medicine. Tranexamic acid given only in hospital.",
    },
    {
        "name": "Minor Burn",
        "base_severity": "MODERATE",
        "base_risk_score": 4,
        "first_aid": (
            "1. Cool burn under running cold water for 10-20 minutes.\n"
            "2. Do NOT use ice, butter or toothpaste.\n"
            "3. Cover loosely with sterile bandage.\n"
            "4. Do NOT pop blisters."
        ),
        "medicine": "Burnol or Silver sulfadiazine cream. Paracetamol for pain.",
    },
    {
        "name": "Sprain",
        "base_severity": "MODERATE",
        "base_risk_score": 4,
        "first_aid": (
            "R - Rest the injured area.\n"
            "I - Ice for 20 min every 2-3 hours.\n"
            "C - Compress with elastic bandage.\n"
            "E - Elevate above heart level.\n"
            "Avoid weight on area for 48 hours."
        ),
        "medicine": "Ibuprofen or Volini gel. Consult doctor if no improvement.",
    },
    {
        "name": "Fever",
        "base_severity": "LOW",
        "base_risk_score": 3,
        "first_aid": (
            "1. Rest in a cool room.\n"
            "2. Drink plenty of fluids (water/ORS).\n"
            "3. Apply cool damp cloth on forehead.\n"
            "4. Wear light clothes.\n"
            "5. If fever >103F or lasts >3 days, see doctor."
        ),
        "medicine": "Paracetamol 500mg. ORS for hydration.",
    },
    {
        "name": "Minor Cut",
        "base_severity": "LOW",
        "base_risk_score": 2,
        "first_aid": (
            "1. Rinse under clean running water.\n"
            "2. Apply gentle pressure to stop bleeding.\n"
            "3. Clean with antiseptic.\n"
            "4. Cover with sterile bandage.\n"
            "5. Change dressing daily."
        ),
        "medicine": "Betadine/Dettol + Neosporin ointment. Tetanus shot if deep.",
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(models.Condition).count()
        if existing > 0:
            print(f"Conditions table already has {existing} rows. Skipping seed.")
            return
        for c in CONDITIONS:
            db.add(models.Condition(**c))
        db.commit()
        print(f"Seeded {len(CONDITIONS)} conditions.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
