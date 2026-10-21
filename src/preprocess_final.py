"""Reconstructed preprocessing pipeline matching the methodology described in
the thesis (Chapters IV and VII / Appendix A):

  - remove exact duplicate rows
  - convert Time (seconds since first transaction) into Hour-of-day
  - standardise Amount with RobustScaler, fit ONLY on the training fold
    (wrapped in a scikit-learn Pipeline so no test-set information leaks
    into the transform, unlike the earlier exploratory preprocess.py which
    fit its scaler on the full dataset before splitting)
  - stratified 80/20 train/test split
  - class imbalance handled via class weighting at model level
    (RandomForestClassifier(class_weight=...), XGBClassifier(scale_pos_weight=...))
    rather than by resampling; SMOTE/undersampling are intentionally NOT
    applied here, matching the thesis's framing of them as discussed
    alternatives rather than methods actually used for the final models.

This script is provided for reproducibility and is not required to
regenerate the "_final" model files already committed to models/ — those
were produced by the original (unrecovered) experiment code, and the
numbers reported in Table 6.1 / Table 5.4 of the thesis are documented as
that original run's results, not as output of this reconstructed script
(see the "Ndershmëria akademike" / academic honesty note in Appendix A).
"""
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline
import joblib

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import DATA_FILE, MODELS_DIR, RANDOM_STATE, TEST_SIZE


def load_and_prepare():
    df = pd.read_csv(DATA_FILE)

    n_before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    n_removed = n_before - len(df)
    print(f"Removed {n_removed} duplicate rows ({n_before} -> {len(df)}).")

    # Time -> Hour of day (0-23), replacing the raw seconds-since-start feature
    df["Hour"] = (df["Time"] // 3600) % 24

    feature_cols = [c for c in df.columns if c not in ("Time", "Class")]
    X = df[feature_cols]
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # RobustScaler for Amount only, fit strictly on the training fold via a
    # Pipeline so evaluate/train code never has to remember to avoid leakage.
    amount_pipeline = Pipeline([("amount_scaler", RobustScaler())])
    amount_pipeline.fit(X_train[["Amount"]])

    X_train = X_train.copy()
    X_test = X_test.copy()
    X_train["Amount"] = amount_pipeline.transform(X_train[["Amount"]])
    X_test["Amount"] = amount_pipeline.transform(X_test[["Amount"]])

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(amount_pipeline.named_steps["amount_scaler"], MODELS_DIR / "amount_scaler.joblib")

    print("Train shape:", X_train.shape, "Test shape:", X_test.shape)
    print("Fraud in train:", int(y_train.sum()), "/ Fraud in test:", int(y_test.sum()))

    return X_train, X_test, y_train, y_test, feature_cols


if __name__ == "__main__":
    load_and_prepare()
