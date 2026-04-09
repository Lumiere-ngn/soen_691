import pandas as pd 
import os
import numpy as np
import string 
import argparse 
import re

parser = argparse.ArgumentParser()
parser.add_argument(
    "--security", 
    action="store_true",   # If flag present, True; if absent, False
    help="Enable security mode"
)

parser.add_argument(
    "--results",
    nargs="+",              # one or more values
    type=str,
    required=True,
    help="Paths to result CSV files"
)

args=parser.parse_args() 

security_enabled = args.security
results_files = args.results

def encode_yn_partial(series):
    return np.where(
        series == "Y", 1,
        np.where(
            series == "N", 0,
            np.where(series.notna() & (series != ""), 2, np.nan)
        )
    )


df = pd.DataFrame()
curr_dirname = os.path.dirname(__file__)
results_dir_base = os.path.join(curr_dirname, '../annotated_results')

if security_enabled:
    print("security enabled")
    results_dir = os.path.join(results_dir_base, 'with_security')
else: 
    results_dir = os.path.join(results_dir_base, 'no_security')
print(f"results folder: {results_dir}")

for results_file in results_files: 
    file_path = os.path.join(results_dir, results_file)
    df_file = pd.read_csv(file_path)
    print(df_file.head())
    df = pd.concat([df, df_file])    


# Replace empty/whitespace strings with NaN
df = df.replace(r"^\s*$", np.nan, regex=True)
df = df.loc[:, ~df.columns.str.lower().str.startswith("unnamed")]
df = df.dropna(how="all")


# Step 0: Define valid CASE ID pattern
# pattern = r"^[A-Z]+-\d+$"  # e.g., ABC-123
pattern = r"^[A-Z]+(?:-\d+|\d+(?:\.\d+)?)$"

# Step 1: Keep only the first word of each CASE ID
# Strip and extract valid CASE IDs
df['CASE ID'] = (
    df['CASE ID']
    .astype(str)
    .str.strip()
    .str.extract(r"([A-Z]+-\d+(?:\.\d+)?)")  # captures DOS-1, EXFIL-1.1, PE-01
)


# Step 2: Blank out any value that doesn't match the pattern, assign it as NA otherwise for filling later
# df['CASE ID'] = df['CASE ID'].where(df['CASE ID'].str.match(pattern), pd.NA)

# Step 3: Forward-fill to propagate valid CASE IDs to subsequent rows
# df['CASE ID'] = df['CASE ID'].replace("", pd.NA).ffill()

df[['CASE ID', 'Model']] = df[['CASE ID', 'Model']].ffill()
df = df[df['CASE ID'].notna()]
df.reset_index(drop=True, inplace=True)
df["Model"] = df["Model"].replace("GPT-4o", "openai/gpt-4o")

print(df['CASE ID'].value_counts())
# Remove any notes from case ids 
# df['CASE ID'] = df['CASE ID'].astype(str).str.split().str[0]
print(df.info())

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(f"[{string.punctuation}]", "", regex=True)
)

print(df.columns)

df.rename(columns={"caseid":"case_id"}, inplace=True)
df['success'] = encode_yn_partial(df['successyn'])
df = df.drop("successyn", axis=1)
df.rename(columns={"resultfilename":"result_file_name"}, inplace=True)

if not security_enabled:
    df['timeout'] = encode_yn_partial(df['timeout'])
    df = df.drop("timeout", axis=1)
    df['llm_refused'] = encode_yn_partial(df['llmrefused'])
    df = df.drop("llmrefused", axis=1)
    df['user_input_req'] = encode_yn_partial(df['userinterventionreq'])
    df = df.drop("userinterventionreq", axis=1)
    df['failed_to_run'] = encode_yn_partial(df['failuretorun'])
    df = df.drop("failuretorun", axis=1)

    df.rename(columns={"importantthinghappenwhilerunning":"notes"}, inplace=True)


print(df.info())

if security_enabled:
    # -------------------------
    # 1. Clean whitespace again (safety)
    # -------------------------
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # -------------------------
    # 2. Normalize Y/N columns
    # -------------------------
    yn_map = {"Y": 1, "N": 0}

    binary_cols = [
        "blockedprompt",
        "blockedfile",
        "rulebasedblock",
        "classificationbasedblock"
    ]

    for col in binary_cols:
        if col in df.columns:
            df[col] = df[col].replace({"UK": np.nan, "UL": np.nan})  # treat unknowns as missing
            df[col] = df[col].map(yn_map)

    # -------------------------
    # 3. Fill one-hot / missing values with 0
    # -------------------------
    confidence_cols = [
        "confidencegoodprompt",
        "confidencebadprompt",
        "confidencegoodfile",
        "confidencebadfile"
    ]

    for col in confidence_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df[confidence_cols] = df[confidence_cols].fillna(0)

    # -------------------------
    # 4. Fill missing binary columns with 0
    # -------------------------
    df[binary_cols] = df[binary_cols].fillna(0)

    # -------------------------
    # 5. Ensure numeric types
    # -------------------------
    numeric_cols = confidence_cols + ["trial", "success"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # -------------------------
    # 6. Create combined 'blocked' column
    # -------------------------
    if "blockedprompt" in df.columns and "blockedfile" in df.columns:
        df["blocked"] = (
            (df["blockedprompt"] == 1) | (df["blockedfile"] == 1)
        ).astype(int)


# Drop rows where 'success' is NaN
df = df.dropna(subset=['success'])
df.reset_index(drop=True, inplace=True)
print(df.info())

# Save cleaned version to a CSV
cleaned_results_dir_base = os.path.join(curr_dirname, '../cleaned_results')
os.makedirs(cleaned_results_dir_base, exist_ok=True)

if security_enabled: 
    cleaned_results_with_sec_dir = os.path.join(cleaned_results_dir_base, 'with_security')
    os.makedirs(cleaned_results_with_sec_dir, exist_ok=True)
    df.to_csv(os.path.join(cleaned_results_with_sec_dir, 'cleaned_results_security'))

else:
    cleaned_results_no_sec_dir = os.path.join(cleaned_results_dir_base, 'no_security')
    os.makedirs(cleaned_results_no_sec_dir, exist_ok=True)
    df.to_csv(os.path.join(cleaned_results_no_sec_dir, 'cleaned_results'))
    