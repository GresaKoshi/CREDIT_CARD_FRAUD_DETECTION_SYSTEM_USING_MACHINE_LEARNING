"""Reconstructed training script for the "final" models referenced in the
thesis (rf_final.joblib, xgb_final.joblib), using:

  - class weighting for the imbalance (class_weight="balanced" for Random
    Forest; scale_pos_weight for XGBoost) instead of SMOTE/undersampling
  - a hyperparameter grid search combined with 5-fold stratified
    cross-validation (GridSearchCV(..., cv=5))
  - random_state = 2026 throughout (see config.py and the reproducibility
    note in the thesis for why this value, not the original experiment's
    seed, is used here)

NOTE: this script is provided for reproducibility of the described
methodology. Running it will NOT reproduce the exact numbers in Table 6.1
of the thesis bit-for-bit, since the original experiment's code and split
are not available (see Appendix A, "Ndershmëria akademike"). The
already-committed models/rf_final.joblib and models/xgb_final.joblib are
the actual artifacts behind the thesis's reported results and are not
overwritten by simply having this script present.
"""
import sys
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from xgboost import XGBClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MODELS_DIR, RANDOM_STATE, CROSS_VAL_FOLDS
from preprocess_final import load_and_prepare


def main():
    X_train, X_test, y_train, y_test, feature_cols = load_and_prepare()

    cv = StratifiedKFold(n_splits=CROSS_VAL_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    print("Grid-searching Random Forest (class_weight='balanced')...")
    rf_grid = {
        "n_estimators": [200, 300],
        "max_depth": [10, 12, None],
    }
    rf_search = GridSearchCV(
        RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
        rf_grid, scoring="average_precision", cv=cv, n_jobs=-1,
    )
    rf_search.fit(X_train, y_train)
    rf = rf_search.best_estimator_
    print("Best RF params:", rf_search.best_params_)

    scale_pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
    print(f"Grid-searching XGBoost (scale_pos_weight={scale_pos_weight:.1f})...")
    xgb_grid = {
        "n_estimators": [200, 300],
        "max_depth": [4, 6],
        "learning_rate": [0.05, 0.1],
    }
    xgb_search = GridSearchCV(
        XGBClassifier(
            scale_pos_weight=scale_pos_weight, eval_metric="logloss",
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
        xgb_grid, scoring="average_precision", cv=cv, n_jobs=-1,
    )
    xgb_search.fit(X_train, y_train)
    xgb = xgb_search.best_estimator_
    print("Best XGB params:", xgb_search.best_params_)

    print("Fitting soft-voting ensemble (RF + XGBoost)...")
    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("xgb", xgb)], voting="soft", n_jobs=-1,
    )
    ensemble.fit(X_train, y_train)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf, MODELS_DIR / "rf_final_reconstructed.joblib")
    joblib.dump(xgb, MODELS_DIR / "xgb_final_reconstructed.joblib")
    joblib.dump(ensemble, MODELS_DIR / "ensemble_final_reconstructed.joblib")
    X_test.to_csv(MODELS_DIR / "X_test_reconstructed.csv", index=False)
    y_test.to_csv(MODELS_DIR / "y_test_reconstructed.csv", index=False)
    print("Saved reconstructed models with a '_reconstructed' suffix so the "
          "thesis-reported rf_final.joblib / xgb_final.joblib are never overwritten.")


if __name__ == "__main__":
    main()
