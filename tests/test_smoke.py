"""Minimal smoke tests for the reconstructed project.

Run with:  python -m pytest tests/ -v
(or, without pytest installed:  python tests/test_smoke.py)

These check that the committed artifacts the thesis and the webapp depend
on are present and structurally sane — they do NOT re-verify the exact
numbers in Table 6.1 (those are documented as the original experiment's
results, not something this reconstructed code reproduces bit-for-bit).
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config


def test_data_file_exists():
    assert config.DATA_FILE.exists(), f"Missing dataset: {config.DATA_FILE}"


def test_final_model_files_exist():
    for f in (config.RF_MODEL_FILE, config.XGB_MODEL_FILE, config.AMOUNT_SCALER_FILE,
              config.X_TEST_FILE, config.Y_TEST_FILE):
        assert f.exists(), f"Missing expected artifact: {f}"


def test_final_models_load_and_predict():
    import joblib
    import pandas as pd
    rf = joblib.load(config.RF_MODEL_FILE)
    xgb = joblib.load(config.XGB_MODEL_FILE)
    X_test = pd.read_csv(config.X_TEST_FILE)
    for model in (rf, xgb):
        proba = model.predict_proba(X_test.head(5))
        assert proba.shape == (5, 2)


def test_thesis_reported_metrics_present():
    path = config.RESULTS_DIR / "thesis_reported_metrics.json"
    assert path.exists(), f"Missing {path}"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert "metrics" in data
    for model_name in ("Random Forest", "XGBoost", "Ensemble (Voting)"):
        assert model_name in data["metrics"]


def test_webapp_imports_and_routes():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "webapp"))
    import app as webapp_module
    client = webapp_module.app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    resp = client.get("/transactions")
    assert resp.status_code == 200
    resp = client.get("/api/metrics")
    assert resp.status_code == 200


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
        except Exception as e:
            failures += 1
            print(f"FAIL: {t.__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
