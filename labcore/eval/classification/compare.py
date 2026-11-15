"""Statistical comparison — McNemar, 5×2cv, DeLong, CD, corrected-t (§41.10)."""

from __future__ import annotations

from typing import Any

import numpy as np


def corrected_resampled_t(
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    *,
    n_train: int,
    n_test: int,
) -> dict[str, Any]:
    """Nadeau–Bengio corrected resampled t-test on paired fold/resample scores.

    Reference: Nadeau & Bengio (2003); Bouckaert & Frank (2004).
    t = mean(d) / sqrt( (1/n + n_test/n_train) * var(d) )
    """
    from scipy import stats

    a = np.asarray(scores_a, dtype=float)
    b = np.asarray(scores_b, dtype=float)
    d = a - b
    n = len(d)
    if n < 2:
        return {
            "id": "CLE.T.COMPARE_CORRECTED_T",
            "t_statistic": None,
            "pvalue": None,
            "mean_diff": float(d.mean()) if n else None,
        }
    mean_d = float(np.mean(d))
    var_d = float(np.var(d, ddof=1))
    corr = (1.0 / n) + (n_test / n_train)
    denom = np.sqrt(max(corr * var_d, 1e-18))
    t_stat = mean_d / denom
    p = float(2 * stats.t.sf(abs(t_stat), df=n - 1))
    return {
        "id": "CLE.T.COMPARE_CORRECTED_T",
        "t_statistic": float(t_stat),
        "pvalue": p,
        "mean_diff": mean_d,
        "n": n,
        "n_train": n_train,
        "n_test": n_test,
    }


def critical_difference_nemenyi(
    fold_scores: dict[str, list[float]] | np.ndarray,
    *,
    model_names: list[str] | None = None,
) -> dict[str, Any]:
    """Friedman + Nemenyi CD via scikit-posthocs (synthetic/fold matrix OK)."""
    import pandas as pd
    import scikit_posthocs as sp
    from scipy.stats import friedmanchisquare

    if isinstance(fold_scores, dict):
        names = list(fold_scores.keys())
        mat = np.column_stack([np.asarray(fold_scores[n], dtype=float) for n in names])
    else:
        mat = np.asarray(fold_scores, dtype=float)
        names = model_names or [f"m{i}" for i in range(mat.shape[1])]

    # rows = folds/datasets, cols = models
    if mat.shape[0] < 2 or mat.shape[1] < 3:
        return {
            "id": "CLE.P.CD",
            "friedman_stat": None,
            "friedman_p": None,
            "models": names,
            "note": "need ≥2 folds and ≥3 models",
        }

    fr = friedmanchisquare(*[mat[:, j] for j in range(mat.shape[1])])
    df = pd.DataFrame(mat, columns=names)
    # posthoc expects data in long or matrix form — nemenyi_friedman on ranks
    ph = sp.posthoc_nemenyi_friedman(df)
    try:
        # optional diagram artefact (matplotlib → skip heavy; store ranks)
        avg_rank = (df.rank(axis=1, ascending=False).mean(axis=0)).to_dict()
    except Exception:
        avg_rank = {}

    return {
        "id": "CLE.P.CD",
        "friedman_stat": float(fr.statistic),
        "friedman_p": float(fr.pvalue),
        "models": names,
        "avg_rank": {str(k): float(v) for k, v in avg_rank.items()},
        "nemenyi_pvalues": ph.round(6).to_dict(),
    }


def mcnemar_test(y_true: np.ndarray, y_a: np.ndarray, y_b: np.ndarray) -> dict[str, Any]:
    """McNemar via statsmodels."""
    from statsmodels.stats.contingency_tables import mcnemar

    a_wrong_b_right = int(np.sum((y_a != y_true) & (y_b == y_true)))
    a_right_b_wrong = int(np.sum((y_a == y_true) & (y_b != y_true)))
    # Full 2x2 of agreements / disagreements
    both_right = int(np.sum((y_a == y_true) & (y_b == y_true)))
    both_wrong = int(np.sum((y_a != y_true) & (y_b != y_true)))
    table_arr = np.array(
        [[both_right, a_right_b_wrong], [a_wrong_b_right, both_wrong]],
        dtype=int,
    )
    res = mcnemar(table_arr, exact=False, correction=True)
    return {
        "id": "CLE.T.COMPARE_MCNEMAR",
        "statistic": float(res.statistic),
        "pvalue": float(res.pvalue),
        "table": table_arr.tolist(),
    }


def delong_test(y_true: np.ndarray, scores_a: np.ndarray, scores_b: np.ndarray) -> dict[str, Any]:
    """DeLong AUC comparison via MLstatkit."""
    try:
        from MLstatkit import Delong_test  # type: ignore[import-untyped]
    except Exception:
        from MLstatkit.stats import Delong_test  # type: ignore[import-untyped]

    result = Delong_test(y_true, scores_a, scores_b)
    z = float(result[0])
    p = float(result[1])
    return {
        "id": "CLE.T.COMPARE_DELONG",
        "z": z,
        "pvalue": p,
    }


def paired_5x2cv(
    estimator_a: Any,
    estimator_b: Any,
    X: Any,
    y: Any,
    *,
    scoring: str = "accuracy",
    seed: int = 42,
) -> dict[str, Any]:
    """5×2cv paired t-test via mlxtend."""
    from mlxtend.evaluate import paired_ttest_5x2cv

    t, p = paired_ttest_5x2cv(
        estimator1=estimator_a,
        estimator2=estimator_b,
        X=X,
        y=y,
        scoring=scoring,
        random_seed=seed,
    )
    return {
        "id": "CLE.T.COMPARE_5X2",
        "t_statistic": float(t),
        "pvalue": float(p),
        "scoring": scoring,
        "seed": seed,
    }
