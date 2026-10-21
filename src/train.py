"""Train Random Forest, XGBoost, and a soft-voting ensemble for fraud detection."""
import time
import json
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

from preprocess import load_and_prepare

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
MODELS.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


def main():
    X_train, X_test, y_train, y_test, feature_cols = load_and_prepare()

    joblib.dump((X_test, y_test), MODELS / "test_set.joblib")

    timings = {}

    print("Training Logistic Regression (baseline)...")
    t0 = time.time()
    lr = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    lr.fit(X_train, y_train)
    timings["logistic_regression"] = round(time.time() - t0, 2)
    joblib.dump(lr, MODELS / "logistic_regression.joblib")

    print("Training Random Forest...")
    t0 = time.time()
    rf = RandomForestClassifier(
        n_estimators=200, max_depth=12, random_state=RANDOM_STATE, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    timings["random_forest"] = round(time.time() - t0, 2)
    joblib.dump(rf, MODELS / "random_forest.joblib")

    print("Training XGBoost...")
    t0 = time.time()
    xgb = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    xgb.fit(X_train, y_train)
    timings["xgboost"] = round(time.time() - t0, 2)
    joblib.dump(xgb, MODELS / "xgboost.joblib")

    print("Training Voting Ensemble (RF + XGBoost + LogReg)...")
    t0 = time.time()
    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("xgb", xgb), ("lr", lr)],
        voting="soft",
        n_jobs=-1,
    )
    ensemble.fit(X_train, y_train)
    timings["ensemble"] = round(time.time() - t0, 2)
    joblib.dump(ensemble, MODELS / "ensemble.joblib")

    with open(MODELS / "training_timings.json", "w") as f:
        json.dump(timings, f, indent=2)

    print("Training complete.")
    print(json.dumps(timings, indent=2))


if __name__ == "__main__":
    main()
