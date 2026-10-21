"""Central configuration for the "final" (thesis-reported) pipeline.

This module documents the parameters used for the methodology described in
the thesis (RobustScaler inside a scikit-learn Pipeline, class weighting
instead of resampling, and a fixed random_state). The thesis itself does not
specify a seed; RANDOM_STATE below is a value fixed for this reconstructed,
reproducible version of the project and is not claimed to be the exact seed
of the original experiment.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
OUTPUTS_DIR = ROOT / "outputs"
RESULTS_DIR = ROOT / "results"

DATA_FILE = DATA_DIR / "creditcard.csv"

RANDOM_STATE = 2026
TEST_SIZE = 0.20

# Final ("_final") model artifact filenames, as consumed by webapp/app.py
RF_MODEL_FILE = MODELS_DIR / "rf_final.joblib"
XGB_MODEL_FILE = MODELS_DIR / "xgb_final.joblib"
AMOUNT_SCALER_FILE = MODELS_DIR / "amount_scaler.joblib"
X_TEST_FILE = MODELS_DIR / "X_test.csv"
Y_TEST_FILE = MODELS_DIR / "y_test.csv"

CROSS_VAL_FOLDS = 5
