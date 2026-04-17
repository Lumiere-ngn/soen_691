import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.patches as mpatches
# --- 1. Load the CSV file ---
csv_file = "/home/emsha/projects/soen_691/results_analysis/saved_results/results_per_model_per_case.csv"  # replace with your CSV filename
df = pd.read_csv(csv_file)


# Convert percentages to floats
for col in ["attack_full_success_pct", "attack_partial_success_pct", "attack_failure_pct"]:
    df[col] = df[col].str.rstrip('%').astype(float)

# Compute median and mean ASR per tactic
# We'll assume 'case_id' maps to tactics via a simple dictionary
tactic_map = {
    "PE-01":"Command and Scripting Interpreter",
    "PE-02":"Command and Scripting Interpreter",
    "PE-03":"Command and Scripting Interpreter",
    "PE-04":"LLM Jailbreak",
    "PE-05":"Denial of AI Service",
    "PE-06":"User Execution",
    "PE-07":"Command and Scripting Interpreter",
    "PE-08":"LLM Prompt Injection",
    "PE-09":"User Execution",
    "PE-10":"LLM Prompt Injection",
    "PE-11":"Data Destruction via AI Agent Tool Invocation",
    "PE-12":"Exfiltration via AI Agent Tool Invocation",
    "PE-13":"User Execution",
    "PE-14":"LLM Jailbreak",
    "PE-15":"LLM Prompt Injection",
    "PE-16":"Data from Local System",
    "PE-4.1":"LLM Jailbreak",
    "DOS-1":"Denial of AI Service",
    "DOS-2":"Denial of AI Service",
    "DOS-3":"Denial of AI Service",
    "EXFIL-1.1":"Exfiltration via AI Agent Tool Invocation",
    "EXFIL-1.2":"Exfiltration via AI Agent Tool Invocation",
    "EXFIL-2.1":"Exfiltration via AI Agent Tool Invocation"
}

df['tactic'] = df['case_id'].map(tactic_map)

# Compute median and mean ASR per tactic
df['ASR'] = df['attack_full_success_pct'] + df['attack_partial_success_pct']
summary = df.groupby('tactic')['ASR'].agg(['median','mean']).sort_values('median', ascending=False).reset_index()

# Plot
sns.set_style("whitegrid")
plt.figure(figsize=(14,7))
bar_plot = sns.barplot(data=summary, x='tactic', y='median', color='steelblue', alpha=0.8)
plt.scatter(x=range(len(summary)), y=summary['mean'], color='darkorange', s=120, label='Mean ASR', zorder=5)

# Annotate bars
for idx, row in summary.iterrows():
    bar_plot.text(idx, row['median']+1, f"{row['median']:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
    plt.text(idx, row['mean']+1, f"{row['mean']:.1f}%", ha='center', va='bottom', fontsize=10, color='darkorange')

# Improve legibility
plt.xticks(rotation=30, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.ylabel("Attack Success Rate (%)", fontsize=14)
plt.xlabel("")
plt.title("Median and Mean Attack Success Rate per MITRE Tactic", fontsize=16, fontweight='bold')
plt.legend(fontsize=12)
# Custom legend
median_patch = mpatches.Patch(color='steelblue', alpha=0.8, label='Median ASR')
mean_patch = plt.Line2D([], [], marker='o', color='darkorange', linestyle='None', markersize=10, label='Mean ASR')
plt.legend(handles=[median_patch, mean_patch], fontsize=12)
plt.tight_layout()
plt.savefig("/home/emsha/projects/soen_691/results_analysis/saved_results/mean_median_asr_per_technique.png")


# Load the per model CSV
df = pd.read_csv("/home/emsha/projects/soen_691/results_analysis/saved_results/results_per_model.csv")

# Convert percentage columns to numeric (remove %)
pct_cols = ['attack_full_success_pct', 'attack_partial_success_pct', 'attack_failure_pct', 
            'llm_refused_pct', 'ignored_pct', 'agent_failure_pct']
for col in pct_cols:
    df[col] = df[col].str.rstrip('%').astype(float)

# Aggregate by model across all cases
agg_df = df.groupby("model")[pct_cols].mean()

# Plot
colors = ["#4caf50", "#ffeb3b", "#f44336", "#2196f3", "#9e9e9e", "#ff9800"]  # full, partial, failure, refused, ignored, agent_fail
agg_df.plot(kind='bar', stacked=True, color=colors, figsize=(12,6))

plt.ylabel("Average %")
plt.title("Average Attack Outcomes per Model")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Outcome", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("/home/emsha/projects/soen_691/results_analysis/saved_results/results_per_model.png")
