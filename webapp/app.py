"""
Flask web dashboard for the Credit Card Fraud Detection System.
Implements the 'web application for real-time monitoring and reporting'
component described in the thesis (Chapter VII).

Uses the final Random Forest / XGBoost / Ensemble models trained and
evaluated in Chapters V-VI (rf_final.joblib, xgb_final.joblib), so the
numbers shown here match Table 6.1 exactly.
"""
import json
import random
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
OUTPUTS = ROOT / "outputs"
PLOTS = OUTPUTS / "plots"

app = Flask(__name__)


class EnsembleModel:
    """Soft-voting ensemble: averages RF and XGBoost predicted probabilities (see 5.3)."""

    def __init__(self, rf, xgb):
        self.rf = rf
        self.xgb = xgb

    def predict_proba(self, X):
        p_rf = self.rf.predict_proba(X)[:, 1]
        p_xgb = self.xgb.predict_proba(X)[:, 1]
        p = (p_rf + p_xgb) / 2.0
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


# --- Load model + data once at startup ---
rf_model = joblib.load(MODELS / "rf_final.joblib")
xgb_model = joblib.load(MODELS / "xgb_final.joblib")
ensemble = EnsembleModel(rf_model, xgb_model)
scaler = joblib.load(MODELS / "amount_scaler.joblib")

X_test = pd.read_csv(MODELS / "X_test.csv")
y_test = pd.read_csv(MODELS / "y_test.csv").iloc[:, 0] if (MODELS / "y_test.csv").exists() else None
if y_test is None:
    y_test = pd.Series(np.load(MODELS / "y_test.npy"), name="Class")
feature_cols = X_test.columns.tolist()

with open(OUTPUTS / "evaluation_results_final.json", encoding="utf-8") as f:
    EVAL_RESULTS = json.load(f)

with open(OUTPUTS / "eda_summary_final.json", encoding="utf-8") as f:
    EDA_SUMMARY = json.load(f)

# Live-computed predictions on the held-out test set (real-time scoring, not cached)
_y_proba = ensemble.predict_proba(X_test)[:, 1]
_y_pred = ensemble.predict(X_test)

TX_TABLE = X_test.copy()
TX_TABLE = TX_TABLE.rename(columns={"Amount": "Amount_scaled"})
TX_TABLE["actual"] = y_test.values
TX_TABLE["predicted"] = _y_pred
TX_TABLE["fraud_probability"] = _y_proba
TX_TABLE = TX_TABLE.reset_index(drop=True)
TX_TABLE.insert(0, "transaction_id", [f"TXN-{100000+i}" for i in range(len(TX_TABLE))])


def risk_level(p):
    if p >= 0.75:
        return "High"
    if p >= 0.3:
        return "Medium"
    return "Low"


@app.route("/")
def dashboard():
    best_model = "Ensemble (Voting)"
    metrics = EVAL_RESULTS[best_model]
    flagged = TX_TABLE[TX_TABLE.predicted == 1].sort_values("fraud_probability", ascending=False).head(8)
    stats = {
        "total_transactions": EDA_SUMMARY["n_transactions"],
        "fraud_transactions": EDA_SUMMARY["n_fraud"],
        "fraud_rate": EDA_SUMMARY["fraud_rate_pct"],
        "test_set_size": len(TX_TABLE),
        "flagged_in_test": int((TX_TABLE.predicted == 1).sum()),
    }
    return render_template(
        "dashboard.html",
        stats=stats,
        metrics=metrics,
        all_results=EVAL_RESULTS,
        flagged=flagged.to_dict(orient="records"),
    )


@app.route("/transactions")
def transactions():
    filter_flag = request.args.get("filter", "all")
    page = int(request.args.get("page", 1))
    per_page = 25

    df = TX_TABLE
    if filter_flag == "flagged":
        df = df[df.predicted == 1]
    elif filter_flag == "fraud":
        df = df[df.actual == 1]

    total = len(df)
    start = (page - 1) * per_page
    page_df = df.iloc[start:start + per_page].copy()
    page_df["risk"] = page_df["fraud_probability"].apply(risk_level)

    cols = ["transaction_id", "Amount_scaled", "actual", "predicted", "fraud_probability", "risk"]
    records = page_df[cols].to_dict(orient="records")

    total_pages = max(1, (total + per_page - 1) // per_page)
    return render_template(
        "transactions.html",
        records=records,
        page=page,
        total_pages=total_pages,
        filter_flag=filter_flag,
        total=total,
    )


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    result = None
    sample = None
    if request.method == "POST":
        idx = request.form.get("sample_idx")
        if idx is not None and idx != "":
            row = TX_TABLE.iloc[int(idx)]
            proba = float(row["fraud_probability"])
            result = {
                "transaction_id": row["transaction_id"],
                "probability": round(proba * 100, 2),
                "prediction": "FRAUD" if row["predicted"] == 1 else "LEGITIMATE",
                "actual": "FRAUD" if row["actual"] == 1 else "LEGITIMATE",
                "risk": risk_level(proba),
            }
            sample = row.to_dict()

    flagged_idx = TX_TABLE.index[TX_TABLE.predicted == 1].tolist()
    highlight_idx = random.sample(flagged_idx, min(4, len(flagged_idx)))
    remaining = [i for i in range(len(TX_TABLE)) if i not in highlight_idx]
    random_idx = highlight_idx + random.sample(remaining, 6)
    samples = TX_TABLE.iloc[random_idx][["transaction_id"]].to_dict(orient="records")
    sample_indices = list(zip(random_idx, [s["transaction_id"] for s in samples]))

    return render_template("analyze.html", result=result, sample_indices=sample_indices)


@app.route("/reports")
def reports():
    plot_files = sorted(p.name for p in PLOTS.glob("*.png"))
    return render_template("reports.html", plot_files=plot_files, all_results=EVAL_RESULTS)


@app.route("/plots/<path:filename>")
def serve_plot(filename):
    return send_from_directory(PLOTS, filename)


@app.route("/api/metrics")
def api_metrics():
    return jsonify(EVAL_RESULTS)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5057, debug=False)
