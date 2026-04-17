import pandas as pd
import os
import numpy as np
import string
import argparse

# -------------------------
# Args
# -------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--security", action="store_true", help="Enable security mode")
parser.add_argument("--results", nargs="+", type=str, required=True)
parser.add_argument(
    "--output",
    type=str,
    default=None,
    help="Output filename (e.g., results.csv). Defaults depend on security mode."
)

args = parser.parse_args()
security_enabled = args.security
results_files = args.results

# -------------------------
# Helpers
# -------------------------
def safe_numeric(df, cols):
    """Convert to numeric and fill NaN with 0 (for binary/count columns)."""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def safe_numeric_no_fill(df, cols):
    """Convert to numeric but keep NaN (for confidence columns)."""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def safe_fillna(df, cols, value=0):
    existing = [c for c in cols if c in df.columns]
    if existing:
        df[existing] = df[existing].fillna(value)
    return df

def encode_yn_partial(series):
    return np.where(
        series == "Y", 1,
        np.where(
            series == "N", 0,
            np.where(series.notna() & (series != ""), 2, np.nan)
        )
    )

# -------------------------
# Constants
# -------------------------
confidence_cols = [
    "confidencegoodprompt",
    "confidencebadprompt",
    "confidencegoodfile",
    "confidencebadfile"
]

binary_cols_security = [
    "blockedprompt",
    "blockedfile",
    "rulebasedblock",
    "classificationbasedblock"
]

binary_cols_nonsec = [
    "timeout", "llm_refused", "user_input_req",
    "failed_to_run", "success"
]

# -------------------------
# Load data
# -------------------------
df = pd.DataFrame()
curr_dir = os.path.dirname(__file__)

results_dir = os.path.join(
    curr_dir,
    "../annotated_results",
    "with_security" if security_enabled else "no_security"
)

print(f"Security enabled: {security_enabled}")
print(f"Results dir: {results_dir}")

for f in results_files:
    path = os.path.join(results_dir, f)
    df = pd.concat([df, pd.read_csv(path)], ignore_index=True)

# -------------------------
# Basic cleaning
# -------------------------
df = df.replace(r"^\s*$", np.nan, regex=True)
df = df.loc[:, ~df.columns.str.lower().str.startswith("unnamed")]
df = df.dropna(how="all")

# Normalize column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(f"[{string.punctuation}]", "", regex=True)
)

# Rename known variants
df = df.rename(columns={
    "caseid": "case_id",
    "resultfilename": "result_file_name"
})

# -------------------------
# CASE ID cleaning
# -------------------------
df["case_id"] = (
    df["case_id"]
    .astype(str)
    .str.strip()
    .str.extract(r"([A-Z]+-\d+(?:\.\d+)?)")
)

# Forward fill identifiers
for col in ["case_id", "model"]:
    if col in df.columns:
        df[col] = df[col].ffill()

df = df[df["case_id"].notna()].reset_index(drop=True)

# Normalize model names
if "model" in df.columns:
    df["model"] = df["model"].replace("GPT-4o", "openai/gpt-4o")

# -------------------------
# NON-SECURITY MODE
# -------------------------
if not security_enabled:
    mapping = {
        "timeout": "timeout",
        "llmrefused": "llm_refused",
        "userinterventionreq": "user_input_req",
        "failuretorun": "failed_to_run",
        "successyn": "success"
    }

    for raw, new in mapping.items():
        if raw in df.columns:
            df[new] = encode_yn_partial(df[raw])
            df.drop(columns=[raw], inplace=True)

    # Drop rows where success missing (if present)
    if "success" in df.columns:
        df = df.dropna(subset=["success"]).reset_index(drop=True)

    # Rename notes
    if "importantthinghappenwhilerunning" in df.columns:
        df = df.rename(columns={"importantthinghappenwhilerunning": "notes"})

    # Convert binary columns → int
    for col in binary_cols_nonsec:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# -------------------------
# SECURITY MODE
# -------------------------
else:
    # Strip whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    yn_map = {"Y": 1, "N": 0}

    # Convert Y/N → 1/0
    for col in binary_cols_security:
        if col in df.columns:
            df[col] = df[col].replace({"UK": np.nan, "UL": np.nan})
            df[col] = df[col].map(yn_map)

    # Fill missing binary values → 0
    df = safe_fillna(df, binary_cols_security, 0)

    # Cast binary → int
    for col in binary_cols_security:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # Convert confidence → float (keep NaN)
    df = safe_numeric_no_fill(df, confidence_cols)

    # Create combined blocked column
    if all(c in df.columns for c in ["blockedprompt", "blockedfile"]):
        df["blocked"] = (
            (df["blockedprompt"] == 1) |
            (df["blockedfile"] == 1)
        ).astype(int)

# -------------------------
# Final numeric normalization
# -------------------------
common_numeric = ["trial"]

numeric_cols = common_numeric.copy()
numeric_cols += (
    binary_cols_security if security_enabled else binary_cols_nonsec
)

df = safe_numeric(df, numeric_cols)

# Ensure confidence columns remain float with NaN
df = safe_numeric_no_fill(df, confidence_cols)

# -------------------------
# Save
# -------------------------
out_base = os.path.join(curr_dir, "../cleaned_results")
subdir = "with_security" if security_enabled else "no_security"
out_dir = os.path.join(out_base, subdir)

os.makedirs(out_dir, exist_ok=True)

# Determine filename
if args.output:
    output_file = os.path.basename(args.output)
else:
    output_file = (
        "cleaned_results_security.csv"
        if security_enabled
        else "cleaned_results.csv"
    )

output_path = os.path.join(out_dir, output_file)

print(df.info())

df.to_csv(output_path, index=False)

print(f"Saved cleaned results to: {output_path}")