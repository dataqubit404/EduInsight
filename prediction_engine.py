"""
prediction_engine.py — Core prediction logic for the dashboard.
"""
import os, json, pickle
import numpy as np
import pandas as pd

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data/student_performance.csv")

FEATURES = ["Study Hours (per day)", "Attendance (%)",
            "Midterm Scaled (0-20)", "Best Quiz (0-20)",
            "Lab + Viva (0-10)", "Project (0-10)"]

GRADE_THRESHOLDS = [
    (85, "A+"), (75, "A"), (65, "B+"), (55, "B"),
    (45, "C+"), (35, "C"), (30, "D"), (0,  "F")
]

def _safe(subject: str) -> str:
    return subject.replace(" ", "_")

def get_grade(total: float) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if total >= threshold:
            return grade
    return "F"

def load_artifacts(subject: str):
    s = _safe(subject)
    with open(f"{MODEL_DIR}/{s}_model.pkl",  "rb") as f: model  = pickle.load(f)
    with open(f"{MODEL_DIR}/{s}_scaler.pkl", "rb") as f: scaler = pickle.load(f)
    with open(f"{MODEL_DIR}/{s}_impute.pkl", "rb") as f: impute = pickle.load(f)
    with open(f"{MODEL_DIR}/{s}_means.json", "r") as f: means  = json.load(f)
    return model, scaler, impute, means

def predict(subject: str, inputs: dict) -> dict:
    """
    inputs keys (all optional except study_hours):
      study_hours, attendance, midterm_raw (0-50), quiz1, quiz2,
      lab_viva, project
    Returns dict with prediction results and imputed values.
    """
    study_hours = inputs.get("study_hours")
    if study_hours is None:
        raise ValueError("Study Hours is mandatory.")

    model, scaler, impute, means = load_artifacts(subject)

    # Convert midterm raw 0-50 → 0-20
    midterm_scaled = None
    if inputs.get("midterm_raw") is not None:
        midterm_scaled = round(float(inputs["midterm_raw"]) * 20 / 50, 2)

    # Best quiz
    best_quiz = None
    q1, q2 = inputs.get("quiz1"), inputs.get("quiz2")
    if q1 is not None and q2 is not None:
        best_quiz = max(float(q1), float(q2))
    elif q1 is not None:
        best_quiz = float(q1)
    elif q2 is not None:
        best_quiz = float(q2)

    attendance = inputs.get("attendance")
    lab_viva   = inputs.get("lab_viva")
    project    = inputs.get("project")

    provided = [attendance, midterm_scaled, best_quiz, lab_viva, project]
    if all(v is None for v in provided):
        raise ValueError("Provide at least one field besides Study Hours "
                         "(Quiz, Midterm, Lab+Viva, Project, or Attendance).")

    # Impute missing via study-hours model
    imp_X = pd.DataFrame({"Study Hours (per day)": [study_hours]})
    imputed = {}

    def _imp(val, key):
        if val is None:
            pred = float(impute[key].predict(imp_X)[0])
            # Clamp to range
            limits = {"Attendance (%)": (50, 100),
                      "Midterm Scaled (0-20)": (0, 20),
                      "Best Quiz (0-20)": (0, 20),
                      "Lab + Viva (0-10)": (0, 10),
                      "Project (0-10)": (0, 10)}
            lo, hi = limits.get(key, (0, 100))
            pred = round(np.clip(pred, lo, hi), 2)
            imputed[key] = pred
            return pred
        return float(val)

    attendance    = _imp(attendance,    "Attendance (%)")
    midterm_scaled= _imp(midterm_scaled,"Midterm Scaled (0-20)")
    best_quiz     = _imp(best_quiz,     "Best Quiz (0-20)")
    lab_viva      = _imp(lab_viva,      "Lab + Viva (0-10)")
    project       = _imp(project,       "Project (0-10)")

    # Predict end-term
    feat_vec = pd.DataFrame([{
        "Study Hours (per day)": study_hours,
        "Attendance (%)":        attendance,
        "Midterm Scaled (0-20)": midterm_scaled,
        "Best Quiz (0-20)":      best_quiz,
        "Lab + Viva (0-10)":     lab_viva,
        "Project (0-10)":        project,
    }])
    feat_scaled = scaler.transform(feat_vec[FEATURES])
    endterm = float(model.predict(feat_scaled)[0])
    endterm = round(np.clip(endterm, 0, 40), 2)

    total = round(midterm_scaled + best_quiz + lab_viva + project + endterm, 2)
    total = min(total, 100)
    grade = get_grade(total)

    return {
        "subject":         subject,
        "study_hours":     study_hours,
        "attendance":      round(attendance, 2),
        "midterm_scaled":  round(midterm_scaled, 2),
        "best_quiz":       round(best_quiz, 2),
        "lab_viva":        round(lab_viva, 2),
        "project":         round(project, 2),
        "endterm_pred":    endterm,
        "total_marks":     total,
        "grade":           grade,
        "imputed":         imputed,
    }

def get_subject_data(subject: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    return df[df["Subject"] == subject].copy()

def get_all_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)

def get_model_metrics() -> dict:
    with open(f"{MODEL_DIR}/metrics.json") as f:
        return json.load(f)

if __name__ == "__main__":
    result = predict("Deep Learning", {
        "study_hours": 5,
        "midterm_raw": 35,
        "quiz1": 14,
    })
    for k, v in result.items():
        print(f"  {k}: {v}")
