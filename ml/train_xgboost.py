import pandas as pd
import joblib
import os

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from imblearn.over_sampling import SMOTE

print("📥 Loading processed data...")
df = pd.read_csv("data/processed_kiva.csv")

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
    "num_male_borrowers"
]

X = df[FEATURES]
y = df["funded"]

# Time-safe split (NO shuffle)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

# Handle imbalance
smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

# XGBoost Model (CONTROLLED CONFIDENCE)
model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=5,
    min_child_weight=3,
    subsample=0.75,
    colsample_bytree=0.75,
    gamma=0.5,
    objective="binary:logistic",
    eval_metric="auc",
    random_state=42,
    n_jobs=-1
)

print("🚀 Training XGBoost...")
model.fit(X_train_res, y_train_res)

# Evaluation
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
print(f"AUC: {roc_auc_score(y_test, y_prob):.3f}")
print(classification_report(y_test, y_pred))

# Save model
os.makedirs("../backend/model", exist_ok=True)
joblib.dump(model, "../backend/model/credit_xgb.pkl")

print("💾 Model saved successfully")
