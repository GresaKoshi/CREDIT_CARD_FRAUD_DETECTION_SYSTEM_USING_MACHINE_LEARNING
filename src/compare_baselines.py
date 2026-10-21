"""Optional comparison between the ensemble model and two traditional
baselines, using McNemar's test for paired binary classifier comparison.

This module is NOT part of the original thesis experiment. It was added to
the reconstructed codebase to give the author the option of computing an
actual statistical comparison against traditional methods, if she chooses
to include one — the thesis text itself makes no H0/H1 statistical claim
about superiority over traditional methods, because no such test was run
on the original results (see Chapter VIII and Appendix A).

Baselines:
  1. Rule-based: flags a transaction as fraud if its (RobustScaler-scaled)
     Amount is an extreme outlier (> 3x the IQR above Q3) — a simple
     proxy for the kind of fixed-threshold rule traditional systems use.
     This is illustrative, not a claim about any real bank's actual rules.
  2. Logistic Regression: a standard linear baseline, trained with
     class_weight="balanced" on the same training split as the ensemble.

Usage:
    python src/compare_baselines.py

Requires: the reconstructed train/test split from preprocess_final.py
(loads it fresh — it does not reuse models/X_test.csv, since that file's
matching X_train is not available; results here compare against a
freshly-split baseline test set, NOT the exact original test set behind
Table 6.1. This script's output must not be described as a statistical
test of the thesis's actual reported models unless that limitation is
stated alongside it.)
"""
import sys
from pathlib import Path
import numpy as np
from scipy.stats import binomtest, chi2
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import RANDOM_STATE
from preprocess_final import load_and_prepare


def mcnemar_test(n01, n10):
    """McNemar's test from the two discordant-pair counts.

    n01 = count where classifier A is wrong and classifier B is right
    n10 = count where classifier A is right and classifier B is wrong

    Uses the exact binomial form (recommended when n01 + n10 < 25) and
    falls back to the chi-square approximation with continuity correction
    otherwise. Implemented directly with scipy (no statsmodels dependency).
    """
    n = n01 + n10
    if n == 0:
        return 1.0, None
    if n < 25:
        p = binomtest(min(n01, n10), n, 0.5, alternative="two-sided").pvalue
        return p, None
    statistic = (abs(n01 - n10) - 1) ** 2 / n
    p = 1 - chi2.cdf(statistic, df=1)
    return p, statistic


def rule_based_predict(X):
    amt = X["Amount"]
    q1, q3 = amt.quantile(0.25), amt.quantile(0.75)
    iqr = q3 - q1
    threshold = q3 + 3 * iqr
    return (amt > threshold).astype(int).values


def run_mcnemar(y_true, pred_a, pred_b, label_a, label_b):
    both_wrong = int(np.sum((pred_a != y_true) & (pred_b != y_true)))
    a_right_b_wrong = int(np.sum((pred_a == y_true) & (pred_b != y_true)))
    a_wrong_b_right = int(np.sum((pred_a != y_true) & (pred_b == y_true)))
    both_right = int(np.sum((pred_a == y_true) & (pred_b == y_true)))
    table = [[both_right, a_right_b_wrong], [a_wrong_b_right, both_wrong]]
    pvalue, statistic = mcnemar_test(n01=a_wrong_b_right, n10=a_right_b_wrong)
    print(f"\nMcNemar's test: {label_a} vs {label_b}")
    print("Contingency table [[both_right, A_right_B_wrong],[A_wrong_B_right, both_wrong]]:", table)
    if statistic is not None:
        print(f"statistic={statistic:.4f}, p-value={pvalue:.6f}")
    else:
        print(f"(exact binomial form, n<25) p-value={pvalue:.6f}")
    return pvalue


def main():
    X_train, X_test, y_train, y_test, feature_cols = load_and_prepare()

    print("\nTraining Logistic Regression baseline (class_weight='balanced')...")
    logreg = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)
    logreg.fit(X_train, y_train)
    logreg_pred = logreg.predict(X_test)

    print("Applying rule-based Amount-outlier baseline...")
    rule_pred = rule_based_predict(X_test)

    # NOTE: the ensemble model bundled in models/ (ensemble.joblib) was
    # trained on the OLD preprocess.py split (StandardScaler + SMOTE,
    # random_state=42), not this reconstructed split. It is intentionally
    # NOT loaded and compared here, to avoid comparing predictions across
    # two different, non-aligned test sets. To compare a specific trained
    # ensemble against these baselines, retrain it inside this same script
    # on this same split, or adapt this script to load a model that was
    # fit on this exact X_train/y_train.
    print("\nBaseline standalone metrics on this reconstructed split:")
    for name, pred in [("Rule-based", rule_pred), ("Logistic Regression", logreg_pred)]:
        print(f"  {name}: accuracy={accuracy_score(y_test, pred):.4f}, "
              f"f1={f1_score(y_test, pred):.4f}")

    run_mcnemar(y_test.values, rule_pred, logreg_pred, "Rule-based", "Logistic Regression")

    print("\nTo compare against the ensemble model itself, train it on "
          "X_train/y_train from this script (see src/train_final.py) and "
          "pass its predictions into run_mcnemar() alongside a baseline's.")


if __name__ == "__main__":
    main()
