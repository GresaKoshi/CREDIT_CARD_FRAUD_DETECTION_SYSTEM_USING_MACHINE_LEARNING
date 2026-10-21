"""Preprocessing pipeline: scaling + train/test split + SMOTE balancing."""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import joblib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "creditcard.csv"
MODELS = ROOT / "models"
MODELS.mkdir(parents=True, exist_ok=True)


def load_and_prepare(test_size=0.2, random_state=42):
    df = pd.read_csv(DATA)

    scaler = StandardScaler()
    df["Amount_scaled"] = scaler.fit_transform(df[["Amount"]])
    df["Time_scaled"] = scaler.fit_transform(df[["Time"]])

    feature_cols = [c for c in df.columns if c not in ("Time", "Amount", "Class")]
    X = df[feature_cols]
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    print("Before SMOTE:", y_train.value_counts().to_dict())
    smote = SMOTE(random_state=random_state)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    print("After SMOTE:", pd.Series(y_train_res).value_counts().to_dict())

    joblib.dump(scaler, MODELS / "scaler.joblib")
    joblib.dump(feature_cols, MODELS / "feature_cols.joblib")

    return X_train_res, X_test, y_train_res, y_test, feature_cols


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, cols = load_and_prepare()
    print("Train shape:", X_train.shape, "Test shape:", X_test.shape)
