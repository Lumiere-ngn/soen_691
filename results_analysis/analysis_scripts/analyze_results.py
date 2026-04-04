import argparse
import pandas as pd

# ----------------------------
# ARGPARSE
# ----------------------------
parser = argparse.ArgumentParser(description="Compute success/failure stats for LLM models.")
parser.add_argument("--results", type=str, required=True, help="Path to the results CSV file")
args = parser.parse_args()
results_file = args.results

# ----------------------------
# LOAD DATA
# ----------------------------
df = pd.read_csv(results_file)

# Allowed models
allowed_models = [
    "ollama/kamekichi128/qwen3-4b-instruct-2507",
    # "openai/gpt-4o",
    "ollama/llama3.1:8b"
]

# Filter DataFrame by allowed models
df = df[df['model'].isin(allowed_models)]
df = df[df['case_id'] != "PE-17"]
# Ensure numeric columns
for col in ['success', 'llm_refused', 'user_input_req', 'failed_to_run']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Keep only binary success/failure rows
df_binary = df[df['success'].isin([0, 1])]

# ----------------------------
# 1. Overall statistics
# ----------------------------
total_trials = len(df_binary)
overall_success_rate = df_binary['success'].mean() * 100
overall_failure_rate = 100 - overall_success_rate
model_failure_pct = df_binary['failed_to_run'].mean() * 100

print("=== Overall Statistics ===")
print(f"Total trials (0/1 only): {total_trials}")
print(f"Overall success rate: {overall_success_rate:.2f}%")
print(f"Overall failure rate: {overall_failure_rate:.2f}%")
print(f"Model failure percentage: {model_failure_pct:.2f}%")

# ----------------------------
# 2. Per-model statistics
# ----------------------------
per_model = df_binary.groupby('model').agg(
    total_trials=('success', 'count'),
    success_rate=('success', 'mean'),
    failed_to_run_pct=('failed_to_run', 'mean')
).reset_index()

# Convert to percentages
per_model['success_rate'] = per_model['success_rate'] * 100
per_model['failed_to_run_pct'] = per_model['failed_to_run_pct'] * 100

# Format nicely
per_model['success_rate'] = per_model['success_rate'].map(lambda x: f"{x:.2f}%")
per_model['failed_to_run_pct'] = per_model['failed_to_run_pct'].map(lambda x: f"{x:.2f}%")

print("\n=== Per Model Statistics ===")
print(per_model.to_string(index=False))

# ----------------------------
# 3. Per-case statistics
# ----------------------------
per_case = df_binary.groupby('case_id').agg(
    total_trials=('success', 'count'),
    success_rate=('success', 'mean'),
    failed_to_run_pct=('failed_to_run', 'mean')
).reset_index()

# Convert to percentages
per_case['success_rate'] = per_case['success_rate'] * 100
per_case['failed_to_run_pct'] = per_case['failed_to_run_pct'] * 100

# Format nicely
per_case['success_rate'] = per_case['success_rate'].map(lambda x: f"{x:.2f}%")
per_case['failed_to_run_pct'] = per_case['failed_to_run_pct'].map(lambda x: f"{x:.2f}%")

print("\n=== Per Case Statistics ===")
print(per_case.to_string(index=False))

# ----------------------------
# 4. Conditional on failure (success == 0)
# ----------------------------
fail_rows = df_binary[df_binary['success'] == 0]
num_failures = len(fail_rows)

print("\n=== Conditional Statistics on Failures ===")
if num_failures > 0:
    llm_refused_bool = fail_rows['llm_refused'].astype(bool)
    failed_to_run_bool = fail_rows['failed_to_run'].astype(bool)
    
    refusal_rate = llm_refused_bool.mean() * 100
    failed_to_run_rate = failed_to_run_bool.mean() * 100
    refusal_or_failed_rate = (llm_refused_bool | failed_to_run_bool).mean() * 100
    
    print(f"Number of failures: {num_failures}")
    print(f"Refusal rate among failures: {refusal_rate:.2f}%")
    print(f"Failed_to_run rate among failures: {failed_to_run_rate:.2f}%")
    print(f"Refusal or failed_to_run among failures: {refusal_or_failed_rate:.2f}%")
else:
    print("No failure rows to compute conditional statistics.")