import argparse
import pandas as pd
import os

# ----------------------------
# ARGPARSE
# ----------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--results", type=str, required=True)
parser.add_argument("--output_dir", type=str, required=True)
args = parser.parse_args()

os.makedirs(args.output_dir, exist_ok=True)

# ----------------------------
# LOAD DATA
# ----------------------------
df = pd.read_csv(args.results)

# ----------------------------
# Ensure numeric
# ----------------------------
num_cols = [
    "blockedprompt", "blockedfile",
    "rulebasedblock", "classificationbasedblock",
    "confidencegoodprompt", "confidencebadprompt",
    "confidencegoodfile", "confidencebadfile", "blocked"
]

for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# ----------------------------
# BASIC DERIVED FLAGS
# ----------------------------
df["is_blocked"] = (df["blocked"] == 1).astype(int)

df["rule_block"] = (df["rulebasedblock"] == 1).astype(int)
df["ml_block"] = (df["classificationbasedblock"] == 1).astype(int)

df["prompt_block"] = (df["blockedprompt"] == 1).astype(int)
df["file_block"] = (df["blockedfile"] == 1).astype(int)

# ----------------------------
# 1) OVERALL STATS
# ----------------------------
total = len(df)

overall = pd.DataFrame({
    "Metric": [
        "Total",
        "Blocked",
        "Blocking Rate",
        "Rule-based Blocks",
        "ML-based Blocks",
        "Prompt-based Blocks",
        "File-based Blocks"
    ],
    "Value": [
        total,
        df["is_blocked"].sum(),
        df["is_blocked"].mean() * 100,
        df["rule_block"].sum(),
        df["ml_block"].sum(),
        df["prompt_block"].sum(),
        df["file_block"].sum()
    ]
})

overall.to_csv(f"{args.output_dir}/overall_blocking_stats.csv", index=False)

# ----------------------------
# 2) CONFIDENCE STATS
# ----------------------------
confidence_cols = [
    "confidencegoodprompt",
    "confidencebadprompt",
    "confidencegoodfile",
    "confidencebadfile"
]

confidence_stats = df[confidence_cols].describe().T.reset_index()
confidence_stats.rename(columns={"index": "metric"}, inplace=True)

confidence_stats.to_csv(
    f"{args.output_dir}/confidence_stats.csv",
    index=False
)


# ----------------------------
# 3) BREAKDOWN BY CASE
# ----------------------------
case_stats = df.groupby("case_id").agg(
    total=("is_blocked", "count"),
    blocked=("is_blocked", "sum"),
    rule_block=("rule_block", "sum"),
    ml_block=("ml_block", "sum"),
    prompt_block=("prompt_block", "sum"),
    file_block=("file_block", "sum")
).reset_index()

case_stats["blocking_rate_pct"] = case_stats["blocked"] / case_stats["total"] * 100

case_stats.to_csv(f"{args.output_dir}/case_breakdown.csv", index=False)

# ----------------------------
# PRINT SUMMARY
# ----------------------------
print("\n=== OVERALL ===")
print(overall.to_string(index=False))

print("\n=== CONFIDENCE STATS ===")
print(confidence_stats.to_string(index=False))
