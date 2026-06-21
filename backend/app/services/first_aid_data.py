"""
First-aid / supportive-care guidance for the 41 diseases in the
disease-prediction dataset.

CLASSIFICATION METHODOLOGY (documented, not arbitrary):
Each disease is tagged "common" or "serious".

- "common": everyday conditions where general supportive care (rest,
  fluids, OTC-category guidance like "paracetamol not aspirin for
  fever") is the actual standard first-line advice, not a substitute
  for specialist treatment. These get slightly more specific guidance,
  including OTC medicine CATEGORIES (never exact drug names+doses).

- "serious": conditions requiring diagnosis-specific medical treatment
  (AIDS, Hepatitis, Tuberculosis, Heart attack, Paralysis, etc.) where
  approximating treatment advice would be irresponsible regardless of
  how it's worded. These get ONLY general safe guidance: what to do
  while awaiting care, and why a doctor is necessary -- never any
  medicine category or dosage.

This file does NOT contain specific drug names or dosages for ANY
disease, common or serious. "OTC category" guidance (e.g. "fever
reducer" rather than "paracetamol 500mg") is the most specific this
gets, and only for the "common" tier.
"""

FIRST_AID = {
    "Common Cold": {
        "tier": "common",
        "advice": (
            "Rest and stay well hydrated (water, warm fluids, soup). "
            "A fever reducer / pain reliever (e.g. paracetamol-type OTC "
            "medicine, not aspirin for children) can ease aches and fever -- "
            "follow the package instructions for your age and weight. "
            "Saltwater gargle can soothe a sore throat. Usually resolves in "
            "7-10 days; see a doctor if fever is high/persistent or breathing "
            "becomes difficult."
        ),
    },
    "Migraine": {
        "tier": "common",
        "advice": (
            "Rest in a dark, quiet room. Cold compress on the forehead or "
            "neck. Stay hydrated. An OTC pain reliever taken early in an "
            "attack can help. Avoid known personal triggers (certain foods, "
            "bright light, strong smells). See a doctor if this is the "
            "worst headache of your life, or comes with confusion, vision "
            "loss, or weakness -- those need urgent evaluation."
        ),
    },
    "Acne": {
        "tier": "common",
        "advice": (
            "Gently cleanse the skin twice daily, avoid harsh scrubbing or "
            "picking at lesions. OTC topical treatments containing benzoyl "
            "peroxide or salicylic acid (as a category) can help mild cases. "
            "See a dermatologist for persistent or severe acne, as "
            "prescription treatment is often more effective."
        ),
    },
    "Allergy": {
        "tier": "common",
        "advice": (
            "Remove/avoid the suspected trigger if known. An OTC "
            "antihistamine (as a category) can relieve mild symptoms like "
            "sneezing, itching, or hives. Seek EMERGENCY care immediately "
            "if there is swelling of the face/throat, difficulty breathing, "
            "or dizziness -- this can indicate anaphylaxis, which is "
            "life-threatening."
        ),
    },
    "Gastroenteritis": {
        "tier": "common",
        "advice": (
            "Stay hydrated with small, frequent sips of water or oral "
            "rehydration solution (ORS) -- dehydration is the main danger. "
            "Eat bland food once tolerated (rice, toast, bananas). Rest. "
            "See a doctor if there is blood in stool/vomit, signs of severe "
            "dehydration (very little urine, dizziness), or symptoms last "
            "more than a couple of days."
        ),
    },
    "Fungal infection": {
        "tier": "common",
        "advice": (
            "Keep the affected area clean and dry. OTC antifungal cream "
            "(as a category) is generally effective for mild skin/nail "
            "fungal infections. Avoid sharing towels/footwear. See a doctor "
            "if it spreads, doesn't improve after a couple of weeks, or "
            "affects nails/scalp significantly."
        ),
    },
    "GERD": {
        "tier": "common",
        "advice": (
            "Avoid lying down right after eating; eat smaller meals. Avoid "
            "trigger foods (spicy, fatty, caffeine, alcohol). An OTC antacid "
            "(as a category) can relieve occasional symptoms. See a doctor "
            "if symptoms are frequent/severe, as long-term GERD needs proper "
            "evaluation and treatment."
        ),
    },
    "Dimorphic hemmorhoids(piles)": {
        "tier": "common",
        "advice": (
            "Increase fiber and water intake to soften stool. Warm sitz "
            "baths can ease discomfort. OTC hemorrhoid creams (as a "
            "category) may relieve symptoms. See a doctor if there is "
            "significant bleeding or pain that doesn't improve."
        ),
    },
    "Drug Reaction": {
        "tier": "common",
        "advice": (
            "Stop the suspected medication if safe to do so, and contact "
            "the prescriber or a doctor promptly. Seek EMERGENCY care "
            "immediately if there is difficulty breathing, facial/throat "
            "swelling, or widespread rash with fever -- these can indicate "
            "a severe reaction."
        ),
    },
    "Varicose veins": {
        "tier": "common",
        "advice": (
            "Elevate the legs when resting, avoid prolonged standing/"
            "sitting, and consider compression stockings. Regular walking "
            "helps circulation. See a doctor for persistent pain, skin "
            "changes, or if veins worsen, as procedures are available for "
            "more significant cases."
        ),
    },
    "Impetigo": {
        "tier": "common",
        "advice": (
            "Keep the affected area clean and covered to prevent spread to "
            "others (this is contagious). Avoid sharing towels/bedding. "
            "Mild cases sometimes respond to OTC antiseptic cleaning, but "
            "this often requires a doctor-prescribed antibiotic cream -- "
            "see a doctor, especially for children or spreading lesions."
        ),
    },
    "Psoriasis": {
        "tier": "common",
        "advice": (
            "Keep skin moisturized; avoid known triggers (stress, certain "
            "skin injuries). OTC moisturizing creams can ease dryness and "
            "scaling. This is a chronic condition best managed with a "
            "dermatologist for proper long-term treatment."
        ),
    },
    "Chicken pox": {
        "tier": "common",
        "advice": (
            "Isolate to prevent spreading to others (highly contagious). "
            "Keep nails short and avoid scratching to prevent scarring/"
            "infection. Cool baths and calamine-type lotion can ease "
            "itching. Use a fever reducer / pain reliever if needed -- "
            "AVOID aspirin in children/teenagers with viral illness "
            "(linked to Reye's syndrome). See a doctor if very high fever, "
            "difficulty breathing, or signs of skin infection develop."
        ),
    },
    "Dengue": {
        "tier": "common",
        "advice": (
            "Rest and stay well hydrated. Use a fever reducer / pain "
            "reliever from the paracetamol category ONLY -- AVOID aspirin "
            "and ibuprofen, as these increase bleeding risk in dengue. "
            "Watch closely for warning signs (severe abdominal pain, "
            "persistent vomiting, bleeding gums, difficulty breathing) and "
            "seek EMERGENCY care immediately if any appear, as dengue can "
            "progress to a severe, life-threatening stage."
        ),
    },
    "Typhoid": {
        "tier": "common",
        "advice": (
            "Stay hydrated, rest, and eat easily digestible food. Typhoid "
            "requires a doctor-prescribed antibiotic course to actually "
            "clear the infection -- this is supportive care while you seek "
            "medical treatment, not a substitute for it. See a doctor "
            "promptly; untreated typhoid can become serious."
        ),
    },
    "Urinary tract infection": {
        "tier": "common",
        "advice": (
            "Drink plenty of water to help flush the urinary tract. "
            "Avoid holding in urine. See a doctor for a proper diagnosis "
            "and antibiotic treatment -- UTIs generally need prescription "
            "antibiotics to fully clear, especially if fever, back pain, "
            "or blood in urine appear, which can indicate the infection "
            "has spread to the kidneys."
        ),
    },
    "Hypoglycemia": {
        "tier": "common",
        "advice": (
            "If conscious and able to swallow: give fast-acting sugar "
            "immediately (fruit juice, regular soda, glucose tablets, or "
            "candy), followed by a longer-acting snack once symptoms ease. "
            "Seek EMERGENCY care immediately if the person is unconscious, "
            "confused, or unable to swallow safely -- do not give food or "
            "drink by mouth in that case."
        ),
    },
    "Peptic ulcer diseae": {
        "tier": "common",
        "advice": (
            "Avoid NSAIDs (like ibuprofen/aspirin), spicy food, alcohol, "
            "and smoking, all of which worsen ulcers. Eating smaller, "
            "frequent meals may help. See a doctor for proper diagnosis and "
            "treatment, as ulcers often need prescription medication to "
            "heal. Seek EMERGENCY care for severe abdominal pain, vomiting "
            "blood, or black stools -- signs of bleeding."
        ),
    },
    "Arthritis": {
        "tier": "common",
        "advice": (
            "Rest the affected joint but maintain gentle movement to avoid "
            "stiffness. Cold packs for acute swelling, warmth for chronic "
            "stiffness. OTC pain relievers (as a category) may ease mild "
            "discomfort. See a doctor for proper long-term management, as "
            "treatment varies significantly by arthritis type."
        ),
    },

    # ---------- SERIOUS TIER: general safe guidance only ----------
    "AIDS": {
        "tier": "serious",
        "advice": (
            "This requires specialist medical care and ongoing antiretroviral "
            "treatment managed by a doctor -- there is no safe self-care "
            "substitute. Seek medical evaluation promptly if this is "
            "suspected. A doctor can arrange proper testing, counseling, "
            "and treatment."
        ),
    },
    "Alcoholic hepatitis": {
        "tier": "serious",
        "advice": (
            "Stop alcohol consumption immediately and seek medical care -- "
            "this is a serious liver condition that needs professional "
            "evaluation and monitoring. Do not attempt to self-treat."
        ),
    },
    "Bronchial Asthma": {
        "tier": "serious",
        "advice": (
            "If this is a known asthma diagnosis with a prescribed rescue "
            "inhaler, use it as directed by your doctor. For a first-time "
            "or worsening breathing difficulty, seek EMERGENCY care "
            "immediately -- asthma attacks can become life-threatening "
            "quickly and need proper medical assessment."
        ),
    },
    "Cervical spondylosis": {
        "tier": "serious",
        "advice": (
            "Avoid sudden neck movements and heavy lifting. This requires "
            "proper medical evaluation (often imaging) to assess severity "
            "and guide treatment -- see a doctor rather than self-managing "
            "persistent neck pain or any arm weakness/numbness."
        ),
    },
    "Chronic cholestasis": {
        "tier": "serious",
        "advice": (
            "This is a liver-related condition requiring proper medical "
            "diagnosis and monitoring. See a doctor promptly for evaluation "
            "-- self-treatment is not appropriate for this condition."
        ),
    },
    "Heart attack": {
        "tier": "serious",
        "advice": (
            "Call emergency services IMMEDIATELY. While waiting: have the "
            "person sit down and rest, loosen tight clothing, and stay "
            "calm. If they are prescribed their own nitroglycerin, they may "
            "take it as previously directed by their doctor. Do not drive "
            "yourself to the hospital if symptoms are severe -- call for "
            "emergency transport. This is a medical emergency requiring "
            "immediate professional care."
        ),
    },
    "Hepatitis B": {
        "tier": "serious",
        "advice": (
            "Seek medical evaluation promptly -- hepatitis B requires "
            "proper testing and monitoring by a doctor, and in some cases "
            "specific antiviral treatment. Avoid alcohol. Do not attempt "
            "self-treatment."
        ),
    },
    "Hepatitis C": {
        "tier": "serious",
        "advice": (
            "Seek medical evaluation promptly -- hepatitis C requires "
            "proper testing and is treatable with doctor-prescribed "
            "antiviral medication. Avoid alcohol. Do not attempt "
            "self-treatment."
        ),
    },
    "Hepatitis D": {
        "tier": "serious",
        "advice": (
            "Seek medical evaluation promptly -- this requires proper "
            "diagnosis and specialist monitoring by a doctor. Avoid "
            "alcohol. Do not attempt self-treatment."
        ),
    },
    "Hepatitis E": {
        "tier": "serious",
        "advice": (
            "Seek medical evaluation promptly. Rest and stay hydrated while "
            "awaiting care, and avoid alcohol, but this requires proper "
            "medical monitoring, especially in pregnancy where it can be "
            "more serious."
        ),
    },
    "hepatitis A": {
        "tier": "serious",
        "advice": (
            "Rest, stay hydrated, and avoid alcohol while seeking medical "
            "evaluation. Hepatitis A usually resolves on its own but needs "
            "proper diagnosis and monitoring by a doctor, and care to avoid "
            "spreading it to others."
        ),
    },
    "Hypertension ": {
        "tier": "serious",
        "advice": (
            "This requires ongoing medical management, not self-treatment. "
            "Seek a doctor for proper evaluation and a treatment plan. "
            "Seek EMERGENCY care immediately for a sudden severe headache, "
            "chest pain, vision changes, or very high readings with "
            "symptoms -- these can indicate a hypertensive emergency."
        ),
    },
    "Hyperthyroidism": {
        "tier": "serious",
        "advice": (
            "This requires proper medical diagnosis (blood tests) and "
            "treatment plan from a doctor. Do not attempt to self-treat "
            "with supplements or medication."
        ),
    },
    "Hypothyroidism": {
        "tier": "serious",
        "advice": (
            "This requires proper medical diagnosis (blood tests) and "
            "treatment plan from a doctor. Do not attempt to self-treat "
            "with supplements or medication."
        ),
    },
    "Jaundice": {
        "tier": "serious",
        "advice": (
            "Jaundice is a sign of an underlying liver or blood condition "
            "that needs medical evaluation to identify the cause. Seek "
            "medical care promptly -- do not self-treat."
        ),
    },
    "Malaria": {
        "tier": "serious",
        "advice": (
            "Seek medical care promptly -- malaria requires proper "
            "diagnosis (blood test) and prescription antimalarial "
            "treatment, which varies by malaria type and region. Rest and "
            "stay hydrated while seeking care, but this is not a "
            "substitute for treatment. Seek EMERGENCY care for confusion, "
            "difficulty breathing, or very high fever."
        ),
    },
    "Osteoarthristis": {
        "tier": "serious",
        "advice": (
            "Maintain gentle activity and avoid overloading the joint, but "
            "long-term management needs a doctor's evaluation to guide "
            "appropriate treatment, which varies by severity and joint "
            "involved."
        ),
    },
    "Paralysis (brain hemorrhage)": {
        "tier": "serious",
        "advice": (
            "Call emergency services IMMEDIATELY -- this is a medical "
            "emergency. Keep the person still, do not give food or water, "
            "and note the time symptoms started, as this affects treatment "
            "options. Do not delay seeking emergency care."
        ),
    },
    "Pneumonia": {
        "tier": "serious",
        "advice": (
            "Seek medical care promptly -- pneumonia often requires "
            "prescription antibiotics and proper assessment of severity. "
            "Rest and stay hydrated while seeking care. Seek EMERGENCY care "
            "immediately for difficulty breathing, bluish lips/face, or "
            "confusion."
        ),
    },
    "Tuberculosis": {
        "tier": "serious",
        "advice": (
            "Seek medical evaluation promptly -- TB requires a specific, "
            "supervised long-term antibiotic treatment course from a "
            "doctor. If confirmed, take precautions to avoid spreading it "
            "to others until cleared by a medical professional."
        ),
    },
    "Diabetes ": {
        "tier": "serious",
        "advice": (
            "This requires ongoing medical management and monitoring -- "
            "see a doctor for proper diagnosis and a treatment plan. Seek "
            "EMERGENCY care immediately for confusion, difficulty "
            "breathing, fruity-smelling breath, or loss of consciousness, "
            "which can indicate a diabetic emergency."
        ),
    },
    "(vertigo) Paroymsal  Positional Vertigo": {
        "tier": "serious",
        "advice": (
            "Sit or lie down immediately when dizziness occurs to avoid "
            "falls. Avoid sudden head movements. See a doctor for proper "
            "evaluation, as treatment (including specific repositioning "
            "maneuvers) is most effective when guided by a professional."
        ),
    },
}


def get_first_aid(disease_name: str) -> dict:
    """
    Returns first-aid guidance for a disease name. Falls back to a
    generic safe response if the disease isn't in our table (shouldn't
    happen for the 41 known diseases, but defensive nonetheless).
    """
    entry = FIRST_AID.get(disease_name)
    if entry is None:
        return {
            "tier": "unknown",
            "advice": (
                "No specific guidance available for this prediction. "
                "Seek medical evaluation for proper diagnosis and care."
            ),
        }
    return entry
