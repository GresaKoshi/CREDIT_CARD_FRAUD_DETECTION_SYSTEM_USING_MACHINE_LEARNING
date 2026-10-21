# Credit Card Fraud Detection System — Machine Learning

Practical materials accompanying the Bachelor thesis *"Sistemi i Zbulimit të
Mashtrimeve me Kartë Krediti duke Përdorur Mësimin Makinerik"* (Gresa Koshi,
UNI — Universum International College).

## What this is

A fraud-detection pipeline trained on the public [Credit Card Fraud
Detection dataset](https://www.kaggle.com/mlg-ulb/creditcardfraud) (ULB
Machine Learning Group / Worldline, via Kaggle), plus a Flask web prototype
that serves the trained models over a static test set for demonstration.
**It is not a real banking system**: it does not connect to a live
transaction stream, and all data shown in the prototype comes from the
dataset's held-out test split.

## Two generations of code in this repo

- **`src/preprocess.py`, `src/train.py`** — the original exploratory
  scripts (StandardScaler fit before the split, SMOTE oversampling,
  `random_state=42`). These produced the early
  `models/random_forest.joblib`, `models/xgboost.joblib`,
  `models/ensemble.joblib` artifacts and `outputs/evaluation_results.json`.
- **`src/preprocess_final.py`, `src/train_final.py`** — a reconstructed
  pipeline matching the methodology described in the thesis (RobustScaler
  fit only on the training fold inside a `Pipeline`, class weighting
  instead of resampling, 5-fold stratified cross-validation with a
  hyperparameter grid search, `random_state=2026`). **The already-committed
  `models/rf_final.joblib`, `models/xgb_final.joblib`, and
  `outputs/evaluation_results_final.json` (which match Table 6.1 of the
  thesis) come from the original experiment run, not from re-running this
  reconstructed script** — the original code was not recovered, so this
  version documents the methodology and lets it be re-run, without
  overwriting the actual reported artifacts. See "Academic honesty" below.

## Project layout

```
config.py                  central paths, RANDOM_STATE=2026, TEST_SIZE
requirements.txt           pinned library versions used for the reconstructed code
data/creditcard.csv        raw dataset (not included in the repo — see below)
src/
  eda.py                   exploratory plots (Chapter IV/VI figures)
  preprocess.py             original exploratory preprocessing (StandardScaler + SMOTE)
  train.py                  original exploratory training
  evaluate.py                evaluation + plots for the exploratory models
  preprocess_final.py       reconstructed preprocessing (RobustScaler + Pipeline, no SMOTE)
  train_final.py            reconstructed training (class weighting, grid search + 5-fold CV)
  compare_baselines.py      OPTIONAL: rule-based + logistic-regression baselines vs.
                             McNemar's test — not part of the original experiment,
                             see the docstring in that file
models/                    trained model artifacts (.joblib) + test split (X_test.csv, y_test.csv)
outputs/                   EDA summaries, evaluation JSON, generated plots
results/thesis_reported_metrics.json   Table 6.1 numbers, explicitly labeled as
                             "reported in the thesis" (see file for details)
webapp/                    Flask prototype (app.py, templates/, static/)
tests/test_smoke.py        basic smoke tests (data/model/webapp presence + sanity)
```

## Setup

```bash
pip install -r requirements.txt
```

Place the dataset at `data/creditcard.csv` (not committed — download it
from Kaggle; the thesis documents the file as 284,807 transactions with
492 labeled fraud).

## Running things

```bash
# exploratory EDA plots
python src/eda.py

# reconstructed preprocessing + training (writes *_reconstructed.joblib,
# does NOT touch the existing rf_final.joblib / xgb_final.joblib)
python src/train_final.py

# optional baseline comparison + McNemar's test (see file docstring for
# what it does and does not prove)
python src/compare_baselines.py

# smoke tests
python -m pytest tests/ -v
# or, without pytest:
python tests/test_smoke.py

# web prototype
python webapp/app.py
```

## Academic honesty

The source code in `preprocess_final.py` / `train_final.py` was
reconstructed from the methodology, parameters, and results documented in
the thesis; it is not the original experiment's code, which was not
available when this repository was assembled. The metrics in
`results/thesis_reported_metrics.json` (and Table 6.1 / Table 5.4 of the
thesis) are the original run's reported results and are not claimed to be
reproduced by this reconstructed code. `requirements.txt` lists the
versions this reconstructed code was written and tested against, not the
original experiment's library versions, which are not documented in the
thesis.

## Limitations

- Running the full pipeline requires the original dataset, which is not
  distributed with this repository.
- The Flask prototype demonstrates the models on the static test split; it
  reports response times as a preliminary functional measurement on a
  local development machine, not a load/performance test, and its results
  should not be read as a claim about production-scale throughput.
- `compare_baselines.py` is optional and was added after the original
  experiment; see its docstring for exactly what it can and cannot be used
  to conclude.
