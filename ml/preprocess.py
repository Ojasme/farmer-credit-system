import pandas as pd
from sklearn.preprocessing import LabelEncoder
import json
import os
from sklearn.utils import resample

print("📥 Loading raw datasets...")

# Load datasets
loans = pd.read_csv("data/kiva_loans.csv")
mpi = pd.read_csv("data/kiva_mpi_region_locations.csv")
themes_region = pd.read_csv("data/loan_themes_by_region.csv")
themes_ids = pd.read_csv("data/loan_theme_ids.csv")

# ------------------------------
# Merge loan themes
# ------------------------------
loans = loans.merge(
    themes_ids[['id', 'Loan Theme ID', 'Loan Theme Type']],
    on='id',
    how='left'
)
loans.rename(columns={
    'Loan Theme ID': 'loan_theme_id',
    'Loan Theme Type': 'loan_theme_type'
}, inplace=True)

# ------------------------------
# Keep Agriculture loans only
# ------------------------------
loans = loans[loans['sector'] == 'Agriculture']

# ------------------------------
# Select required columns
# ------------------------------
df = loans[[
    "loan_amount",
    "term_in_months",
    "repayment_interval",
    "borrower_genders",
    "country",
    "activity",
    "region",
    "loan_theme_id",
    "loan_theme_type",
    "funded_amount"
]].dropna()

# ------------------------------
# Target: Approved / Rejected
# ------------------------------
df["funded_ratio"] = df["funded_amount"] / df["loan_amount"]
df["funded"] = (df["funded_ratio"] >= 0.9).astype(int)
df.drop(["funded_amount", "funded_ratio"], axis=1, inplace=True)

# ------------------------------
# Balance target: 60% accepted, 40% rejected
# ------------------------------
# ------------------------------
# Balance target: 60% accepted, 40% rejected
# ------------------------------
# ------------------------------
# Balance target: 60% accepted, 40% rejected
# ------------------------------
df_accepted = df[df['funded'] == 1]
df_rejected = df[df['funded'] == 0]

n_total = len(df)
n_accepted = int(n_total * 0.6)
n_rejected = n_total - n_accepted

# Resample
df_accepted_resampled = resample(
    df_accepted, n_samples=n_accepted, random_state=42, replace=False
)
df_rejected_resampled = resample(
    df_rejected, n_samples=n_rejected, random_state=42, replace=True  # oversample minority
)

df = pd.concat([df_accepted_resampled, df_rejected_resampled]) \
       .sample(frac=1, random_state=42) \
       .reset_index(drop=True)



# ------------------------------
# Merge MPI (poverty index)
# ------------------------------
mpi_country = mpi.groupby("country")["MPI"].mean().reset_index()
mpi_country.rename(columns={"MPI": "mpi"}, inplace=True)
df = df.merge(mpi_country, on="country", how="left")
df["mpi"] = df["mpi"].fillna(df["mpi"].median())


# ------------------------------
# Theme loan density
# ------------------------------
theme_density = themes_region.groupby(
    ["country", "Loan Theme ID"]
).size().reset_index(name="theme_loan_density")
theme_density.rename(columns={"Loan Theme ID": "loan_theme_id"}, inplace=True)

df = df.merge(theme_density, on=["country", "loan_theme_id"], how="left")
df["theme_loan_density"] = df["theme_loan_density"].clip(
    upper=df["theme_loan_density"].quantile(0.95)
)
df["theme_loan_density"] = df["theme_loan_density"].fillna(
    df["theme_loan_density"].median()
)
df.drop("loan_theme_id", axis=1, inplace=True)

# ------------------------------
# Borrower gender counts
# ------------------------------
df["borrower_genders"] = df["borrower_genders"].fillna("")
df["num_female_borrowers"] = df["borrower_genders"].str.count("female")
df["num_male_borrowers"] = df["borrower_genders"].str.count("male")
df.drop("borrower_genders", axis=1, inplace=True)

# ------------------------------
# Label Encoding
# ------------------------------
label_mappings = {}
categorical_cols = [
    "repayment_interval",
    "country",
    "activity",
    "region",
    "loan_theme_type"
]

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_mappings[col] = {label: int(idx) for idx, label in enumerate(le.classes_)}

# ------------------------------
# Save processed data
# ------------------------------
os.makedirs("data", exist_ok=True)
df.to_csv("data/processed_kiva.csv", index=False)

with open("data/label_mappings.json", "w") as f:
    json.dump(label_mappings, f, indent=2)

print("✅ Preprocessing complete")
print("Funded distribution (60/40):")
print(df["funded"].value_counts())
