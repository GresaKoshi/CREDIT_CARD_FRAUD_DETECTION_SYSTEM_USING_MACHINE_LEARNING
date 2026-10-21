"""Evaluate trained models: accuracy, precision, recall, F1, ROC-AUC, confusion
matrices, ROC/PR curves, and feature importance. Produces the plots and the
results table used in Chapter 6 (Results) of the thesis.
"""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve,
    average_precision_score, classification_report,
)

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
PLOTS = ROOT / "outputs" / "plots"
PLOTS.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

MODEL_FILES = {
    "Logistic Regression": "logistic_regression.joblib",
    "Random Forest": "random_forest.joblib",
    "XGBoost": "xgboost.joblib",
    "Ensemble (Voting)": "ensemble.joblib",
}

COLORS = {
    "Logistic Regression": "#888888",
    "Random Forest": "#2b7fb8",
    "XGBoost": "#d9534f",
    "Ensemble (Voting)": "#5b8c5a",
}


def main():
    X_test, y_test = joblib.load(MODELS / "test_set.joblib")
    feature_cols = joblib.load(MODELS / "feature_cols.joblib")

    results = {}
    roc_fig, roc_ax = plt.subplots(figsize=(7, 6))
    pr_fig, pr_ax = plt.subplots(figsize=(7, 6))

    fig_cm, axes_cm = plt.subplots(1, 4, figsize=(20, 5))

    for i, (name, fname) in enumerate(MODEL_FILES.items()):
        model = joblib.load(MODELS / fname)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        ap = average_precision_score(y_test, y_proba)
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "avg_precision": round(ap, 4),
            "confusion_matrix": cm.tolist(),
            "false_positives": int(cm[0][1]),
            "false_negatives": int(cm[1][0]),
            "true_positives": int(cm[1][1]),
            "true_negatives": int(cm[0][0]),
        }

        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.4f})", color=COLORS[name])

        prc, rcl, _ = precision_recall_curve(y_test, y_proba)
        pr_ax.plot(rcl, prc, label=f"{name} (AP={ap:.4f})", color=COLORS[name])

        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=axes_cm[i],
                    xticklabels=["Legit", "Fraud"], yticklabels=["Legit", "Fraud"], cbar=False)
        axes_cm[i].set_title(name)
        axes_cm[i].set_xlabel("Predicted")
        axes_cm[i].set_ylabel("Actual")

        print(f"\n=== {name} ===")
        print(classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))

    roc_ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random")
    roc_ax.set_xlabel("False Positive Rate")
    roc_ax.set_ylabel("True Positive Rate")
    roc_ax.set_title("ROC Curves - Model Comparison")
    roc_ax.legend(loc="lower right", fontsize=9)
    roc_fig.tight_layout()
    roc_fig.savefig(PLOTS / "06_roc_curves.png", dpi=150)

    pr_ax.set_xlabel("Recall")
    pr_ax.set_ylabel("Precision")
    pr_ax.set_title("Precision-Recall Curves - Model Comparison")
    pr_ax.legend(loc="lower left", fontsize=9)
    pr_fig.tight_layout()
    pr_fig.savefig(PLOTS / "07_precision_recall_curves.png", dpi=150)

    fig_cm.suptitle("Confusion Matrices by Model")
    fig_cm.tight_layout()
    fig_cm.savefig(PLOTS / "08_confusion_matrices.png", dpi=150)

    # Feature importance (Random Forest + XGBoost)
    rf = joblib.load(MODELS / "random_forest.joblib")
    xgb = joblib.load(MODELS / "xgboost.joblib")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, model, name in [(axes[0], rf, "Random Forest"), (axes[1], xgb, "XGBoost")]:
        importances = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False).head(10)
        sns.barplot(x=importances.values, y=importances.index, ax=ax, color=COLORS[name])
        ax.set_title(f"Top 10 Feature Importances - {name}")
    fig.tight_layout()
    fig.savefig(PLOTS / "09_feature_importance.png", dpi=150)

    # Metric comparison bar chart
    metrics_df = pd.DataFrame(results).T[["accuracy", "precision", "recall", "f1_score", "roc_auc"]]
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics_df.plot(kind="bar", ax=ax, colormap="viridis")
    ax.set_title("Model Performance Comparison")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right", fontsize=8)
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(PLOTS / "10_metric_comparison.png", dpi=150)

    with open(ROOT / "outputs" / "evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n\nSummary table:")
    print(metrics_df.round(4).to_string())
    print("\nEvaluation complete. Plots saved to", PLOTS)


if __name__ == "__main__":
    main()
