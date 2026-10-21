# Credit Card Fraud Detection System Using Machine Learning

A machine learning project that detects fraudulent credit card transactions, built on the public [Credit Card Fraud Detection dataset](https://www.kaggle.com/mlg-ulb/creditcardfraud) from the ULB Machine Learning Group / Worldline (via Kaggle).

The project covers data preprocessing, exploratory data analysis, model training and evaluation, and a Flask web prototype that demonstrates fraud detection with the trained models.

> **Note:** This is a demonstration prototype, not a real banking system. It does not connect to live transaction streams. All transactions shown in the web prototype come from the held-out test set.

## Features

- Exploratory data analysis and visualizations
- Preprocessing for highly imbalanced transaction data
- Random Forest and XGBoost classifiers
- Soft-voting ensemble model
- Evaluation with metrics suited to imbalanced classification
- Reconstructed training pipeline with scaling, class weighting, hyperparameter search, and stratified cross-validation
- Flask web prototype for interactive demonstration
- Basic smoke tests

## Dataset

The original dataset contains **284,807 transactions**, of which **492 are fraudulent** (about **0.173%**).

It includes anonymized numerical features (`V1`–`V28`), a `Time` field, an `Amount` field, and a `Class` label (1 = fraud, 0 = legitimate).

The dataset is **not included** in this repository. Download it from [Kaggle](https://www.kaggle.com/mlg-ulb/creditcardfraud) and place it at:

```
data/creditcard.csv
```

## Project Structure

```
.
├── config.py
├── requirements.txt
├── data/
│   └── creditcard.csv          (download separately)
├── src/
│   ├── eda.py
│   ├── preprocess.py
│   ├── train.py
│   ├── evaluate.py
│   ├── preprocess_final.py
│   ├── train_final.py
│   └── compare_baselines.py
├── models/
│   ├── rf_final.joblib
│   ├── xgb_final.joblib
│   ├── ensemble.joblib
│   ├── X_test.csv
│   └── y_test.csv
├── outputs/
│   ├── plots/
│   ├── screenshots/
│   ├── evaluation_results.json
│   └── evaluation_results_final.json
├── results/
│   └── thesis_reported_metrics.json
├── webapp/
│   ├── app.py
│   └── templates/
└── tests/
    └── test_smoke.py
```

## Installation

Requires Python and `pip`. Using a virtual environment is recommended.

**1. Clone the repository**

```bash
git clone https://github.com/GresaKoshi/CREDIT_CARD_FRAUD_DETECTION_SYSTEM_USING_MACHINE_LEARNING.git
cd CREDIT_CARD_FRAUD_DETECTION_SYSTEM_USING_MACHINE_LEARNING
```

**2. Create and activate a virtual environment**

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The versions in `requirements.txt` match the reconstructed implementation. They are not verified records of the original experiment's environment.

**4. Download the dataset**

Download `creditcard.csv` from [Kaggle](https://www.kaggle.com/mlg-ulb/creditcardfraud) and save it as `data/creditcard.csv`.

## Usage

Run all commands from the repository root.

### Exploratory data analysis

```bash
python src/eda.py
```

Generates summary statistics and visualizations.

### Model training

```bash
python src/train_final.py
```

Runs the reconstructed training workflow (preprocessing and model training). It saves its artifacts separately, so the existing final model files are not overwritten. See `config.py` and `src/train_final.py` for exact output paths.

### Baseline comparison (optional)

```bash
python src/compare_baselines.py
```

Compares model predictions with selected baseline approaches, including McNemar's test. This script was added after the original experiment. Its conclusions apply only to its data, evaluation design, and assumptions, and do not by themselves prove general superiority over traditional fraud-detection systems.

### Tests

```bash
python -m pytest tests/ -v
```

or, without `pytest`:

```bash
python tests/test_smoke.py
```

These are basic smoke tests, not a full validation suite, load test, or proof of production readiness. Tests that depend on the dataset or model files need those files to be present.

### Web prototype

```bash
python webapp/app.py
```

Then open **http://127.0.0.1:5057** in your browser.

The prototype makes predictions with the trained models on static test data. It is not connected to a bank, payment processor, or live transaction stream.

## Models

- **Random Forest:** an ensemble of decision trees that classifies transactions based on learned patterns.
- **XGBoost:** a gradient-boosting algorithm that builds trees sequentially to improve predictive performance.
- **Soft-voting ensemble:** combines the predicted probabilities of multiple models into a final prediction.

## Evaluation Metrics

Accuracy alone is misleading for fraud detection: a model that labels every transaction as legitimate would still score above 99.8%. This project therefore uses:

- **Precision:** the share of flagged transactions that are actually fraudulent.
- **Recall:** the share of actual frauds that are correctly detected.
- **F1-score:** the harmonic mean of precision and recall.
- **Average Precision (PR-AUC):** summarizes the precision-recall trade-off; especially useful for rare positive classes.
- **ROC-AUC:** how well the model separates the two classes across all thresholds.
- **Confusion matrix:** counts of true/false positives and negatives.

The metrics in `results/thesis_reported_metrics.json` are previously reported experiment results. They should not be described as independently reproduced by the reconstructed pipeline unless that pipeline has been run and its results verified.

## Data Processing and Leakage Prevention

The reconstructed pipeline fits all preprocessing on training data only, using a scikit-learn `Pipeline`. Fitting a scaler on the full dataset before splitting would leak test-set information into training.

The reconstructed workflow handles class imbalance with **class weighting**, while the earlier exploratory workflow used **SMOTE**. These are different approaches, and their results should not be mixed or presented as coming from the same configuration.

For reproducible experiments, record the dataset version, split strategy, random seed, preprocessing configuration, library versions, model parameters, and evaluation outputs.

## Reproducibility and Provenance

`src/preprocess_final.py` and `src/train_final.py` were reconstructed from the documented methodology, parameters, and reported results, because the original experiment's source code was unavailable when this repository was assembled.

`results/thesis_reported_metrics.json` and `outputs/evaluation_results_final.json` preserve the results reported from the original experiment. They are not claimed to have been reproduced by the reconstructed code.

This separation makes it clear which results come from the original experiment, the earlier exploratory scripts, and the reconstructed workflow.

## Limitations

- The dataset must be downloaded separately from Kaggle.
- The full pipeline requires the dataset and all dependencies.
- The original source code and exact software environment were not recovered.
- Reconstructed outputs may differ from the reported metrics.
- The optional baseline comparison was added later and must be interpreted within its own assumptions.
- The web app is a demonstration using static test data, not a real-time fraud detection service.
- The project has not undergone comprehensive security, scalability, or operational testing.
- Response times measured in the prototype are preliminary local measurements, not performance benchmarks.

## Future Improvements

- Re-run and document the full pipeline in a clean environment
- Add automated tests for preprocessing, training, evaluation, and web endpoints
- Record verified experiment configurations and results in machine-readable reports
- Tune classification thresholds against explicit false-positive and false-negative costs
- Add model monitoring and drift detection for real-world deployment
- Strengthen security and operational testing before any production use

## Dataset Attribution

Dataset: [Credit Card Fraud Detection](https://www.kaggle.com/mlg-ulb/creditcardfraud), ULB Machine Learning Group / Worldline, via Kaggle.

Review the dataset's terms and licensing before redistributing the data. No ownership of the original dataset is claimed.
