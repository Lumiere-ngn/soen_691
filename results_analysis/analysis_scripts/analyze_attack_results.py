import argparse
import pandas as pd
import os

# ----------------------------
# ARGPARSE
# ----------------------------
parser = argparse.ArgumentParser(description="Compute success/failure stats for LLM models.")
parser.add_argument("--results", type=str, required=True, help="Path to the results CSV file")
parser.add_argument("--output_dir", type=str, required=True, help="Directory to save CSVs")
args = parser.parse_args()
results_file = args.results
output_dir = args.output_dir

os.makedirs(output_dir, exist_ok=True)

# ----------------------------
# LOAD DATA
# ----------------------------
df = pd.read_csv(results_file)

# Allowed models
allowed_models = [
    "ollama/kamekichi128/qwen3-4b-instruct-2507",
    "openai/gpt-4o",
    "ollama/llama3.1:8b"
]

df = df[df['model'].isin(allowed_models)]

# ----------------------------
# Ensure numeric columns and flags
# ----------------------------
for col in ['success', 'llm_refused', 'user_input_req', 'failed_to_run']:
    df[col] = pd.to_numeric(df[col], errors='coerce')


# TAKE OUT FAILURES 
df = df[df['failed_to_run'] == 0]

# Flags (match lines 34–40)
df['attack_success'] = df['success'].astype(int)
df['attack_full_success'] = (df['success'] == 1).astype(int)
df['attack_partial_success'] = (df['success'] == 2).astype(int)
df['attack_failure'] = (df['success'] == 0).astype(int)
df['llm_refused_flag'] = (df['llm_refused'] == 1).astype(int)
df['ignored'] = ((df['attack_success'] == 0) &
                 (df['failed_to_run'] == 0) &
                 (df['llm_refused_flag'] == 0)).astype(int)

# ----------------------------
# 1) Overall results
# ----------------------------
total_trials = len(df)
overall_table = pd.DataFrame({
    'Metric': ['Total Trials', 'Attack Full Success', 'Attack Partial Success', 'Attack Failed', 
               'Attack Refused',  'Attack Ignored', 'Agent Failure'],
    'Count': [
        total_trials,
        df['attack_full_success'].sum(),
        df['attack_partial_success'].sum(),
        df['attack_failure'].sum(), 
        df['llm_refused_flag'].sum(),
        df['ignored'].sum(),
        df['failed_to_run'].sum()
    ],
    'Percentage': [
        100,
        df['attack_full_success'].mean() * 100,
        df['attack_partial_success'].mean() * 100,
        df['attack_failure'].mean() * 100,
        df['llm_refused_flag'].mean() * 100,
        df['ignored'].mean() * 100,
        df['failed_to_run'].mean() * 100
    ]
})
overall_table['Percentage'] = overall_table['Percentage'].map(lambda x: f"{x:.2f}%")
overall_table.to_csv(f"{output_dir}/overall_results.csv", index=False)
print("=== Overall Results ===")
print(overall_table.to_string(index=False))

# ----------------------------
# 2) Results per model
# ----------------------------
per_model_table = df.groupby('model').agg(
    total_trials=('attack_success', 'count'),
    attack_full_success=('attack_full_success', 'sum'),
    attack_partial_success=('attack_partial_success', 'sum'),
    attack_failure=('attack_failure', 'sum'),
    llm_refused=('llm_refused_flag', 'sum'),
    ignored=('ignored', 'sum'),
    agent_failure=('failed_to_run', 'sum')
).reset_index()

for col in ['attack_full_success', 'attack_partial_success', 'attack_failure', 'llm_refused', 'ignored', 'agent_failure']:
    per_model_table[col + '_pct'] = (per_model_table[col] / per_model_table['total_trials'] * 100).map(lambda x: f"{x:.2f}%")

per_model_table.to_csv(f"{output_dir}/results_per_model.csv", index=False)
print("\n=== Results Per Model ===")
print(per_model_table.to_string(index=False))

# ----------------------------
# 3) Results per attack scenario (case_id)
# ----------------------------
per_case_table = df.groupby('case_id').agg(
    total_trials=('attack_success', 'count'),
    attack_full_success=('attack_full_success', 'sum'),
    attack_partial_success=('attack_partial_success', 'sum'),
    attack_failure=('attack_failure', 'sum'),
    llm_refused=('llm_refused_flag', 'sum'),
    ignored=('ignored', 'sum'),
    agent_failure=('failed_to_run', 'sum')
).reset_index()

for col in ['attack_full_success', 'attack_partial_success', 'attack_failure', 'llm_refused', 'ignored', 'agent_failure']:
    per_case_table[col + '_pct'] = (per_case_table[col] / per_case_table['total_trials'] * 100).map(lambda x: f"{x:.2f}%")

per_case_table.to_csv(f"{output_dir}/results_per_case.csv", index=False)
print("\n=== Results Per Case (Attack Scenario) ===")
print(per_case_table.to_string(index=False))

# ----------------------------
# 4) Results per model per attack scenario
# ----------------------------
per_model_case_table = df.groupby(['case_id', 'model']).agg(
    total_trials=('attack_success', 'count'),
    attack_full_success=('attack_full_success', 'sum'),
    attack_partial_success=('attack_partial_success', 'sum'),
    attack_failure=('attack_failure', 'sum'),
    llm_refused=('llm_refused_flag', 'sum'),
    ignored=('ignored', 'sum'),
    agent_failure=('failed_to_run', 'sum')
).reset_index()

for col in ['attack_full_success', 'attack_partial_success', 'attack_failure', 'llm_refused', 'ignored', 'agent_failure']:
    per_model_case_table[col + '_pct'] = (per_model_case_table[col] / per_model_case_table['total_trials'] * 100).map(lambda x: f"{x:.2f}%")

per_model_case_table.to_csv(f"{output_dir}/results_per_model_per_case.csv", index=False)
print("\n=== Results Per Model Per Case ===")
print(per_model_case_table.to_string(index=False))

# ----------------------------
# Optional: highlight unexpected trial counts
# ----------------------------
unexpected_trials = per_model_case_table[per_model_case_table['total_trials'] != 3]
if not unexpected_trials.empty:
    print("\n=== Cases with unexpected trial counts (should be 3) ===")
    print(unexpected_trials.to_string(index=False))