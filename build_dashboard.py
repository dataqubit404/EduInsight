"""
build_dashboard.py  —  Injects dataset + model coefficients into the HTML template.
"""
import json, os, pickle
import pandas as pd
import numpy as np

BASE   = os.path.dirname(__file__)
DATA   = pd.read_csv(os.path.join(BASE, "data/student_performance.csv"))
MODEL_DIR = os.path.join(BASE, "models")

# ── 1. Build flat dataset for JS ─────────────────────────────────────────────
records = []
for _, row in DATA.iterrows():
    records.append({
        "name":           row["Student Name"],
        "subject":        row["Subject"],
        "study":          round(row["Study Hours (per day)"], 1),
        "attendance":     round(row["Attendance (%)"], 1),
        "midterm_scaled": round(row["Midterm Scaled (0-20)"], 1),
        "best_quiz":      round(row["Best Quiz (0-20)"], 1),
        "lab_viva":       round(row["Lab + Viva (0-10)"], 1),
        "project":        round(row["Project (0-10)"], 1),
        "endterm":        round(row["End-Term Scaled (0-40)"], 1),
        "total":          round(row["Total Marks (0-100)"], 1),
        "grade":          row["Grade"],
    })

# ── 2. Model metrics ─────────────────────────────────────────────────────────
with open(os.path.join(MODEL_DIR, "metrics.json")) as f:
    metrics = json.load(f)

# ── 3. Imputation coefficients (slope, intercept) per subject ────────────────
IMPUTE_KEYS = {
    "attendance":     "Attendance (%)",
    "midterm_raw":    "Midterm Marks (0-50)",
    "midterm_scaled": "Midterm Scaled (0-20)",
    "best_quiz":      "Best Quiz (0-20)",
    "quiz1":          "Quiz 1 (0-20)",
    "lab_viva":       "Lab + Viva (0-10)",
    "project":        "Project (0-10)",
}

impute_coeffs = {}
for subject in DATA["Subject"].unique():
    sub = DATA[DATA["Subject"] == subject]
    X = sub[["Study Hours (per day)"]].values
    impute_coeffs[subject] = {}
    for js_key, col in IMPUTE_KEYS.items():
        if col not in sub.columns:
            continue
        y = sub[col].values
        from sklearn.linear_model import LinearRegression
        lr = LinearRegression().fit(X, y)
        impute_coeffs[subject][js_key] = [round(float(lr.coef_[0]),4),
                                           round(float(lr.intercept_),4)]

# ── 4. Inject into template ──────────────────────────────────────────────────
tmpl_path = os.path.join(BASE, "dashboard_template.html")
out_path  = os.path.join(BASE, "dashboard.html")

with open(tmpl_path) as f:
    html = f.read()

html = html.replace("__DATASET_JSON__",  json.dumps(records))
html = html.replace("__METRICS_JSON__",  json.dumps(metrics))
html = html.replace("__IMPUTE_JSON__",   json.dumps(impute_coeffs))

with open(out_path, "w") as f:
    f.write(html)

print(f"✅ Dashboard built → {out_path}")
print(f"   Records injected: {len(records)}")
print(f"   Subjects: {list(impute_coeffs.keys())}")
