from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import json
import os
import shap   # ✅ ADDED

# ===============================
# Create FastAPI app
# ===============================
app = FastAPI(title="Farmer Credit Scoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# Resolve BASE DIRECTORY
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR, "..", "ml", "model", "credit_xgb_balanced.pkl"
)

LABEL_PATH = os.path.join(
    BASE_DIR, "..", "ml", "data", "label_mappings.json"
)

FEATURE_PATH = os.path.join(
    BASE_DIR, "..", "ml", "model", "feature_names.pkl"
)

# ===============================
# Load Model
# ===============================
try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Model loading failed:", e)
    raise e

# ===============================
# Load SHAP (FAST VERSION)
# ===============================
try:
    explainer = shap.TreeExplainer(model)   # ✅ FAST FIX
    feature_names = joblib.load(FEATURE_PATH)
    print("✅ SHAP explainer ready")
except Exception as e:
    print("❌ SHAP loading failed:", e)
    explainer = None
    feature_names = None

# ===============================
# Load Label Mappings
# ===============================
with open(LABEL_PATH, "r") as f:
    label_mappings = json.load(f)

print("✅ Label mappings loaded")

# ===============================
# Request Schema
# ===============================
class CreditInput(BaseModel):
    loan_amount: float
    term_in_months: float
    repayment_interval: str
    country: str
    activity: str
    region: str
    loan_theme_type: str
    mpi: float
    theme_loan_density: float
    num_female_borrowers: int
    num_male_borrowers: int


# ===============================
# Root Endpoint
# ===============================
@app.get("/")
def root():
    return {"status": "Farmer Credit API running 🚜"}


# ===============================
# Prediction Endpoint
# ===============================
@app.post("/predict")
def predict_credit(data: CreditInput):

    input_data = data.dict()

    # ---------------------------
    # Encode categorical features
    # ---------------------------
    for col, mapping in label_mappings.items():
        if col in input_data:
            input_data[col] = mapping.get(str(input_data[col]), 0)

    # ---------------------------
    # Feature Engineering (UNCHANGED)
    # ---------------------------
    total_borrowers = max(
        input_data["num_female_borrowers"] +
        input_data["num_male_borrowers"],
        1
    )

    # ---------------------------
    # Create DataFrame
    # ---------------------------
    df = pd.DataFrame([input_data])

    # ✅ Ensure correct feature order (IMPORTANT)
    if feature_names:
        df = df[feature_names]

    # ---------------------------
    # Predict Probability
    # ---------------------------
    prob = float(model.predict_proba(df)[0][1])

    # ---------------------------
    # Credit Score (300–900)
    # ---------------------------
    credit_score = int(300 + (prob ** 0.75) * 600)
    credit_score = min(max(credit_score, 300), 900)

    # ---------------------------
    # Decision Logic
    # ---------------------------
    decision = "Approved" if prob >= 0.65 else "Rejected"

    # ---------------------------
    # SHAP Explanation (FAST + FIXED)
    # ---------------------------
    shap_values_output = {}

    if explainer is not None and feature_names is not None:
        try:
            shap_values = explainer.shap_values(df)

            shap_values_output = {
                feature: float(value)
                for feature, value in zip(feature_names, shap_values[0])
            }
        except Exception as e:
            print("⚠️ SHAP error:", e)

    return {
        "credit_score": credit_score,
        "approval_probability": round(prob * 100, 2),
        "decision": decision,
        "shap_values": shap_values_output   # ✅ ADDED
    }


# ===============================
# Run Server
# ===============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)