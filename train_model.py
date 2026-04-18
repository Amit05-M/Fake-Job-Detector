import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
from imblearn.over_sampling import SMOTE

# ─────────────────────────────────────────
# STEP 1 — Load Dataset 1 (EMSCAD Global)
# ─────────────────────────────────────────
print("Loading EMSCAD dataset...")
emscad = pd.read_csv("fake_job_postings.csv")

# Combine all text columns into one
emscad["text"] = (
    emscad["title"].fillna("") + " " +
    emscad["company_profile"].fillna("") + " " +
    emscad["description"].fillna("") + " " +
    emscad["requirements"].fillna("") + " " +
    emscad["benefits"].fillna("")
)

emscad_df = pd.DataFrame({
    "text": emscad["text"],
    "label": emscad["fraudulent"]  # 0 = real, 1 = fake
})

print(f"EMSCAD loaded: {len(emscad_df)} rows")
print(f"  Real: {(emscad_df['label'] == 0).sum()}")
print(f"  Fake: {(emscad_df['label'] == 1).sum()}")

# ─────────────────────────────────────────
# STEP 2 — Load Dataset 2 (Naukri India)
# ─────────────────────────────────────────
print("\nLoading Naukri India dataset...")

import glob

# Read all 3 CSV files from the naukri_jobs.csv folder
naukri_files = glob.glob("naukri_jobs.csv/*.csv")
print(f"Found {len(naukri_files)} Naukri files: {naukri_files}")

naukri_frames = []
for f in naukri_files:
    try:
        temp = pd.read_csv(f, encoding="utf-8")
    except UnicodeDecodeError:
        temp = pd.read_csv(f, encoding="latin-1")
    naukri_frames.append(temp)
    print(f"  Loaded: {f} — {len(temp)} rows | Columns: {temp.columns.tolist()}")

naukri = pd.concat(naukri_frames, ignore_index=True)
print(f"Total Naukri rows: {len(naukri)}")

# Auto-detect text columns
text_cols = []
for col in naukri.columns:
    if any(keyword in col.lower() for keyword in
           ["title", "description", "company", "skill", "role",
            "profile", "requirement", "job", "key", "location"]):
        text_cols.append(col)

print(f"Using Naukri columns: {text_cols}")

if not text_cols:
    # fallback — use all string columns
    text_cols = naukri.select_dtypes(include="object").columns.tolist()
    print(f"Fallback — using all text columns: {text_cols}")

naukri["text"] = naukri[text_cols].fillna("").astype(str).agg(" ".join, axis=1)

naukri_df = pd.DataFrame({
    "text": naukri["text"],
    "label": 0  # all Naukri posts are real
})

print(f"Naukri loaded: {len(naukri_df)} rows (all labeled as real)")
# ─────────────────────────────────────────
# STEP 3 — Merge Both Datasets
# ─────────────────────────────────────────
print("\nMerging datasets...")
df = pd.concat([emscad_df, naukri_df], ignore_index=True)

# Clean text
df["text"] = df["text"].str.lower()
df["text"] = df["text"].str.replace(r"[^a-zA-Z0-9\s₹]", " ", regex=True)
df["text"] = df["text"].str.strip()

# Drop empty rows
df = df[df["text"].str.len() > 20]
df = df.dropna(subset=["text", "label"])
df = df.reset_index(drop=True)

print(f"\nFinal merged dataset: {len(df)} rows")
print(f"  Real jobs: {(df['label'] == 0).sum()}")
print(f"  Fake jobs: {(df['label'] == 1).sum()}")

# ─────────────────────────────────────────
# STEP 4 — TF-IDF Vectorization
# ─────────────────────────────────────────
print("\nRunning TF-IDF vectorization...")
vectorizer = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),   # single words + word pairs
    stop_words="english",
    min_df=2
)

X = vectorizer.fit_transform(df["text"])
y = df["label"].values

print(f"Feature matrix shape: {X.shape}")

# ─────────────────────────────────────────
# STEP 5 — Train / Test Split
# ─────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTrain size: {X_train.shape[0]}")
print(f"Test size:  {X_test.shape[0]}")

# ─────────────────────────────────────────
# STEP 6 — Handle Class Imbalance (SMOTE)
# ─────────────────────────────────────────
print("\nApplying SMOTE to balance classes...")
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)

print(f"After SMOTE:")
print(f"  Real: {(y_train_bal == 0).sum()}")
print(f"  Fake: {(y_train_bal == 1).sum()}")

# ─────────────────────────────────────────
# STEP 7 — Train Logistic Regression
# ─────────────────────────────────────────
print("\nTraining Logistic Regression...")
lr_model = LogisticRegression(max_iter=1000, random_state=42)
lr_model.fit(X_train_bal, y_train_bal)

lr_pred = lr_model.predict(X_test)
lr_acc  = accuracy_score(y_test, lr_pred)
lr_f1   = f1_score(y_test, lr_pred)

print(f"Logistic Regression — Accuracy: {lr_acc:.4f} | F1: {lr_f1:.4f}")

# ─────────────────────────────────────────
# STEP 8 — Train Random Forest
# ─────────────────────────────────────────
print("\nTraining Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_bal, y_train_bal)

rf_pred = rf_model.predict(X_test)
rf_acc  = accuracy_score(y_test, rf_pred)
rf_f1   = f1_score(y_test, rf_pred)

print(f"Random Forest       — Accuracy: {rf_acc:.4f} | F1: {rf_f1:.4f}")

# ─────────────────────────────────────────
# STEP 9 — Compare & Pick Best Model
# ─────────────────────────────────────────
print("\n" + "="*50)
print("MODEL COMPARISON")
print("="*50)
print(f"Logistic Regression  →  Accuracy: {lr_acc:.2%}  |  F1: {lr_f1:.4f}")
print(f"Random Forest        →  Accuracy: {rf_acc:.2%}  |  F1: {rf_f1:.4f}")

if rf_f1 >= lr_f1:
    best_model = rf_model
    best_name  = "Random Forest"
    best_f1    = rf_f1
else:
    best_model = lr_model
    best_name  = "Logistic Regression"
    best_f1    = lr_f1

print(f"\nBest model: {best_name} (F1: {best_f1:.4f})")
print("="*50)

# Detailed report for best model
best_pred = best_model.predict(X_test)
print(f"\nDetailed report for {best_name}:")
print(classification_report(y_test, best_pred,
      target_names=["Real", "Fake"]))

# ─────────────────────────────────────────
# STEP 10 — Save Model & Vectorizer
# ─────────────────────────────────────────
print("\nSaving model and vectorizer...")
joblib.dump(best_model,  "model.pkl")
joblib.dump(vectorizer,  "vectorizer.pkl")

print("Saved: model.pkl")
print("Saved: vectorizer.pkl")
print("\nTraining complete!")