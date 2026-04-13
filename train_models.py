import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import pickle, os, json

DATA_PATH  = os.path.join(os.path.dirname(__file__), "data/student_performance.csv")
MODEL_DIR  = os.path.join(os.path.dirname(__file__), "models")

FEATURES = ["Study Hours (per day)", "Attendance (%)",
            "Midterm Scaled (0-20)", "Best Quiz (0-20)",
            "Lab + Viva (0-10)", "Project (0-10)"]
TARGET   = "End-Term Scaled (0-40)"
IMPUTE_TARGETS = ["Attendance (%)", "Midterm Scaled (0-20)",
                  "Best Quiz (0-20)", "Lab + Viva (0-10)", "Project (0-10)"]

def train_models():
    df = pd.read_csv(DATA_PATH)
    os.makedirs(MODEL_DIR, exist_ok=True)
    metrics = {}

    for subject in df["Subject"].unique():
        sub_df = df[df["Subject"] == subject].copy()
        safe   = subject.replace(" ", "_")

        # Main end-term prediction model
        X = sub_df[FEATURES].fillna(sub_df[FEATURES].mean())
        y = sub_df[TARGET]
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)
        model  = LinearRegression().fit(X_tr_s, y_tr)
        y_pred = model.predict(X_te_s)

        metrics[subject] = {
            "r2":  round(r2_score(y_te, y_pred), 3),
            "mae": round(mean_absolute_error(y_te, y_pred), 3)
        }

        with open(f"{MODEL_DIR}/{safe}_model.pkl",  "wb") as f: pickle.dump(model,  f)
        with open(f"{MODEL_DIR}/{safe}_scaler.pkl", "wb") as f: pickle.dump(scaler, f)

        # Imputation models: predict each optional feature from study_hours
        imp_models = {}
        for tgt in IMPUTE_TARGETS:
            imp_X = sub_df[["Study Hours (per day)"]].fillna(sub_df[["Study Hours (per day)"]].mean())
            imp_y = sub_df[tgt]
            imp_m = LinearRegression().fit(imp_X, imp_y)
            imp_models[tgt] = imp_m

        with open(f"{MODEL_DIR}/{safe}_impute.pkl", "wb") as f: pickle.dump(imp_models, f)

        # Store feature means for this subject
        feat_means = sub_df[FEATURES].mean().to_dict()
        with open(f"{MODEL_DIR}/{safe}_means.json", "w") as f:
            json.dump(feat_means, f, indent=2)

    with open(f"{MODEL_DIR}/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("✅ Models trained:")
    for s, m in metrics.items():
        print(f"   {s:<38} R²={m['r2']}  MAE={m['mae']}")
    return metrics

if __name__ == "__main__":
    train_models()
