# EduPredict
# 🎓 Student Performance Prediction Dashboard

## Project Structure

```
student_dashboard/
├── generate_dataset.py      ← Creates Excel + CSV dataset (160 students)
├── train_models.py          ← Trains Linear Regression models per subject
├── prediction_engine.py     ← Core prediction + imputation logic
├── build_dashboard.py       ← Injects data into HTML dashboard
├── dashboard.html           ← 🌐 Open this in browser!
├── data/
│   ├── student_performance.xlsx   ← Color-coded Excel dataset
│   ├── student_performance.csv    ← Raw CSV for ML
│   ├── heatmap.png                ← Correlation heatmap
│   └── study_vs_performance.png   ← Scatter charts
├── models/
│   ├── *_model.pkl          ← Trained LinearRegression per subject
│   ├── *_scaler.pkl         ← StandardScaler per subject
│   ├── *_impute.pkl         ← Imputation models
│   ├── *_means.json         ← Feature means
│   └── metrics.json         ← R² and MAE per subject
└── notebooks/
    └── analysis.ipynb       ← Jupyter analysis notebook
```

## Quick Start

### 1. Install Dependencies
```bash
pip install pandas numpy scikit-learn matplotlib seaborn openpyxl
```

### 2. Generate Dataset
```bash
python generate_dataset.py
```

### 3. Train Models
```bash
python train_models.py
```

### 4. Build Dashboard
```bash
python build_dashboard.py
```

### 5. Open Dashboard
Open `dashboard.html` in any modern browser — **no server needed!**

### 6. Run Jupyter Notebook
```bash
jupyter notebook notebooks/analysis.ipynb
```

## Subjects
- 🔬 Essentials Of Data Science
- 💻 Software Engineering
- 🧠 Deep Learning
- ⚙️ Technical Training

## Marking Scheme
| Component | Raw | Scaled |
|-----------|-----|--------|
| Midterm | 0–50 | 0–20 |
| Best Quiz (Q1 or Q2) | — | 0–20 |
| Lab + Viva | — | 0–10 |
| Project | — | 0–10 |
| End-Term | 0–100 | **0–40** |
| **Total** | | **100** |

## Input Rule
- ✅ Study Hours is **MANDATORY**
- ✅ At least **ONE** of: Quiz, Midterm, Lab+Viva, Project, Attendance
- 🪄 Missing values are predicted from Study Hours via imputation models
- ❌ Only Study Hours → Error shown

## Grade System
| Grade | Marks |
|-------|-------|
| A+ | ≥ 85 |
| A  | ≥ 75 |
| B+ | ≥ 65 |
| B  | ≥ 55 |
| C+ | ≥ 45 |
| C  | ≥ 35 |
| D  | ≥ 30 |
| F  | < 30 |

## VS Code Setup
Recommended extensions:
- Python (ms-python.python)
- Jupyter (ms-toolsai.jupyter)
- Excel Viewer (GrapeCity.gc-excelviewer)
- Live Preview (ms-vscode.live-preview)  ← Open dashboard.html live
