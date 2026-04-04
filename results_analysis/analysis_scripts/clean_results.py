import pandas as pd 
import os
import numpy as np
import string 
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument(
    "--security", 
    action="store_true",   # If flag present, True; if absent, False
    help="Enable security mode"
)
args=parser.parse_args() 

security_enabled = args.security

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

for results_file in os.listdir(results_dir): 
    file_path = os.path.join(results_dir, results_file)
    df_file = pd.read_csv(file_path)
    print(df_file.head())
    df = pd.concat([df, df_file])    


# Replace empty/whitespace strings with NaN
df = df.replace(r"^\s*$", np.nan, regex=True)
df = df.loc[:, ~df.columns.str.lower().str.startswith("unnamed")]
df = df.dropna(how="all")

import re

# Step 0: Define valid CASE ID pattern
pattern = r"^[A-Z]+-\d+$"  # e.g., ABC-123

# Step 1: Keep only the first word of each CASE ID
df['CASE ID'] = df['CASE ID'].astype(str).str.split().str[0]

# Step 2: Blank out any value that doesn't match the pattern, assign it as NA otherwise for filling later
df['CASE ID'] = df['CASE ID'].where(df['CASE ID'].str.match(pattern), pd.NA)

# Step 3: Forward-fill to propagate valid CASE IDs to subsequent rows
# df['CASE ID'] = df['CASE ID'].replace("", pd.NA).ffill()

df[['CASE ID', 'Model']] = df[['CASE ID', 'Model']].ffill()

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
df['success'] = encode_yn_partial(df['successyn'])
df = df.drop("successyn", axis=1)
df['timeout'] = encode_yn_partial(df['timeout'])
df = df.drop("timeout", axis=1)
df['llm_refused'] = encode_yn_partial(df['llmrefused'])
df = df.drop("llmrefused", axis=1)
df['user_input_req'] = encode_yn_partial(df['userinterventionreq'])
df = df.drop("userinterventionreq", axis=1)
df['failed_to_run'] = encode_yn_partial(df['failuretorun'])
df = df.drop("failuretorun", axis=1)

df.rename(columns={"importantthinghappenwhilerunning":"notes"}, inplace=True)
df.rename(columns={"resultfilename":"result_file_name"}, inplace=True)
df.rename(columns={"caseid":"case_id"}, inplace=True)


print(df.info())

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
    df.to_csv(os.path.join(cleaned_results_with_sec_dir, 'cleaned_results'))

else:
    cleaned_results_no_sec_dir = os.path.join(cleaned_results_dir_base, 'no_security')
    os.makedirs(cleaned_results_no_sec_dir, exist_ok=True)
    df.to_csv(os.path.join(cleaned_results_no_sec_dir, 'cleaned_results'))
    