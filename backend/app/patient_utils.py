import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .config import settings
from .schemas import PatientReport


DIAGNOSES = [
    "Chronic Kidney Disease Stage 3",
    "Acute Kidney Injury",
    "Nephrotic Syndrome",
    "Hypertensive Nephrosclerosis",
    "Diabetic Nephropathy",
]

MEDICATION_POOL = [
    "ACE inhibitor",
    "ARB",
    "Diuretic",
    "Erythropoietin",
    "Vitamin D",
    "Phosphate binder",
]

DIET_POOL = [
    "Low sodium",
    "Low potassium",
    "Fluid restriction",
    "Low phosphorus",
]

FOLLOW_UP_POOL = [
    "Check BMP in 1 week",
    "Follow up with nephrology in 2 weeks",
    "Monitor blood pressure daily",
    "Bring medication list to next visit",
]

WARNINGS_POOL = [
    "Shortness of breath",
    "Swelling in legs or face",
    "Decreased urine output",
    "Chest pain",
]

DISCHARGE_POOL = [
    "Take medications as prescribed",
    "Record daily weight",
    "Avoid NSAIDs",
    "Keep low-salt diet",
]


def _ensure_patient_db() -> None:
    os.makedirs(os.path.dirname(settings.patient_reports_path), exist_ok=True)
    if not os.path.exists(settings.patient_reports_path):
        seed_dummy_patients(30)
    else:
        with open(settings.patient_reports_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            seed_dummy_patients(30)
        else:
            data = json.loads(content)
            if len(data) < settings.min_patient_records:
                seed_dummy_patients(settings.min_patient_records)


def seed_dummy_patients(n: int = 30) -> None:
    first_names = ["Alex", "Sam", "Taylor", "Jordan", "Morgan", "Riley", "Casey", "Jamie", "Avery", "Quinn"]
    last_names = ["Smith", "Johnson", "Lee", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson"]
    today = datetime.utcnow()
    records: List[Dict[str, Any]] = []
    for i in range(n):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        report = PatientReport(
            patient_name=name,
            discharge_date=(today - timedelta(days=random.randint(1, 60))).date().isoformat(),
            diagnosis=random.choice(DIAGNOSES),
            medications=random.sample(MEDICATION_POOL, k=random.randint(2, 4)),
            dietary_restrictions=random.sample(DIET_POOL, k=random.randint(1, 3)),
            follow_up_instructions=random.sample(FOLLOW_UP_POOL, k=random.randint(2, 3)),
            warning_signs=random.sample(WARNINGS_POOL, k=random.randint(2, 3)),
            discharge_instructions=random.sample(DISCHARGE_POOL, k=random.randint(2, 3)),
        )
        records.append(report.dict())

    with open(settings.patient_reports_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def load_patient_reports() -> List[PatientReport]:
    _ensure_patient_db()
    with open(settings.patient_reports_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [PatientReport(**r) for r in raw]


def lookup_patient_by_name(name: str) -> List[PatientReport]:
    name_norm = name.strip().lower()
    reports = load_patient_reports()
    return [r for r in reports if name_norm in r.patient_name.lower()]


