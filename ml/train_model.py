import pandas as pd
import joblib
import os
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, f1_score
import numpy as np

print("📥 Loading processed data...")
df = pd.read_csv("data/processed_kiva.csv")

# ------------------------------
# Feature Engineering
# ------------------------------
df['loan_amount_per_borrower'] = (
    df['loan_amount'] / df[['num_female_borrowers','num_male_borrowers']].sum(axis=1).replace(0,1)
)
df['short_term'] = (df['term_in_months'] <= 6).astype(int)
df['high_mpi'] = (df['mpi'] >= 0.6).astype(int)

FEATURES = [
    "loan_amount",
    "term_in_months",
    "repayment_interval",
    "country",
    "activity",
    "region",
    "loan_theme_type",
    "mpi",
    "theme_loan_density",
    "num_female_borrowers",
    "num_male_borrowers",
    "loan_amount_per_borrower",
    "short_term",
    "high_mpi"
]

X = df[FEATURES]
y = df["funded"]

# ------------------------------
# Train/Test Split
# ------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=True, stratify=y, random_state=42
)

# ------------------------------
# Compute scale_pos_weight for XGBoost
# ------------------------------
neg = (y_train == 0).sum()
pos = (y_train == 1).sum()
scale_pos_weight = neg / pos
print(f"Scale_pos_weight: {scale_pos_weight:.2f}")

# ------------------------------
# XGBoost Model
# ------------------------------
model = XGBClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=5,
    min_child_weight=5,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=1.0,
    scale_pos_weight=scale_pos_weight,
    objective="binary:logistic",
    eval_metric="auc",
    random_state=42,
    n_jobs=-1
)

print("🚀 Training XGBoost model...")
model.fit(X_train, y_train)

# ------------------------------
# Optimize threshold for rejected loans (class 0)
# ------------------------------
y_prob = model.predict_proba(X_test)[:,1]
best_threshold = 0.5
best_f1 = 0

for t in np.arange(0.3, 0.8, 0.01):
    y_pred_t = (y_prob >= t).astype(int)
    f1 = f1_score(y_test, y_pred_t, pos_label=0)  # optimize for rejections
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = t

print(f"Best threshold for rejected loans (class 0): {best_threshold:.2f}")

# ------------------------------
# Final predictions using best threshold
# ------------------------------
y_pred = (y_prob >= best_threshold).astype(int)

print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"AUC: {roc_auc_score(y_test, y_prob):.4f}")
print("Classification Report:")
print(classification_report(y_test, y_pred))

# ------------------------------
# Save model
# ------------------------------
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/credit_xgb_balanced.pkl")
print("💾 Model saved successfully!")
