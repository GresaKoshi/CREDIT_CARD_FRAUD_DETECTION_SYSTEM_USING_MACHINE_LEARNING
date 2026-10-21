"""Exploratory Data Analysis for the credit card fraud dataset.
Generates the plots referenced in Chapter 4/6 of the thesis (class imbalance,
correlation structure, amount/time distributions).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "creditcard.csv"
PLOTS = ROOT / "outputs" / "plots"
PLOTS.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

df = pd.read_csv(DATA)
print("Shape:", df.shape)
print(df["Class"].value_counts())

fraud_rate = df["Class"].mean() * 100
print(f"Fraud rate: {fraud_rate:.4f}%")

# 1. Class distribution
fig, ax = plt.subplots(figsize=(6, 5))
counts = df["Class"].value_counts().sort_index()
bars = ax.bar(["Legitimate (0)", "Fraud (1)"], counts.values, color=["#2b7fb8", "#d9534f"])
ax.set_ylabel("Number of transactions")
ax.set_title(f"Class Distribution\n({fraud_rate:.3f}% of transactions are fraudulent)")
for b, v in zip(bars, counts.values):
    ax.text(b.get_x() + b.get_width() / 2, v, f"{v:,}", ha="center", va="bottom")
ax.set_yscale("log")
fig.tight_layout()
fig.savefig(PLOTS / "01_class_distribution.png", dpi=150)
plt.close(fig)

# 2. Transaction amount distribution by class
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.histplot(df[df.Class == 0]["Amount"], bins=50, ax=axes[0], color="#2b7fb8")
axes[0].set_title("Amount Distribution - Legitimate")
axes[0].set_xlim(0, 2000)
sns.histplot(df[df.Class == 1]["Amount"], bins=50, ax=axes[1], color="#d9534f")
axes[1].set_title("Amount Distribution - Fraud")
axes[1].set_xlim(0, 2000)
fig.tight_layout()
fig.savefig(PLOTS / "02_amount_distribution.png", dpi=150)
plt.close(fig)

# 3. Transactions over time by class
fig, ax = plt.subplots(figsize=(10, 5))
df["Hour"] = (df["Time"] // 3600) % 24
sns.histplot(data=df, x="Hour", hue="Class", bins=24, multiple="dodge",
             palette={0: "#2b7fb8", 1: "#d9534f"}, stat="density", common_norm=False, ax=ax)
ax.set_title("Transaction Frequency by Hour of Day (normalized)")
ax.set_xlabel("Hour")
fig.tight_layout()
fig.savefig(PLOTS / "03_time_distribution.png", dpi=150)
plt.close(fig)

# 4. Correlation heatmap
fig, ax = plt.subplots(figsize=(14, 11))
corr = df.drop(columns=["Hour"]).corr()
sns.heatmap(corr, cmap="coolwarm", center=0, ax=ax, cbar_kws={"shrink": 0.7})
ax.set_title("Feature Correlation Matrix")
fig.tight_layout()
fig.savefig(PLOTS / "04_correlation_heatmap.png", dpi=150)
plt.close(fig)

# 5. Top correlated features with Class
fig, ax = plt.subplots(figsize=(8, 6))
top_corr = corr["Class"].drop("Class").abs().sort_values(ascending=False).head(12)
sns.barplot(x=top_corr.values, y=top_corr.index, ax=ax, color="#5b8c5a")
ax.set_title("Top 12 Features Most Correlated with Fraud (|r|)")
ax.set_xlabel("Absolute correlation with Class")
fig.tight_layout()
fig.savefig(PLOTS / "05_top_correlated_features.png", dpi=150)
plt.close(fig)

summary = {
    "n_transactions": int(df.shape[0]),
    "n_features": int(df.shape[1] - 1),
    "n_fraud": int(df["Class"].sum()),
    "n_legit": int((df["Class"] == 0).sum()),
    "fraud_rate_pct": round(fraud_rate, 4),
    "amount_mean_legit": round(df[df.Class == 0]["Amount"].mean(), 2),
    "amount_mean_fraud": round(df[df.Class == 1]["Amount"].mean(), 2),
}
import json
with open(ROOT / "outputs" / "eda_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(summary, indent=2))
print("EDA complete. Plots saved to", PLOTS)
