"""Statistical comparison — McNemar, 5×2cv, DeLong (ARCHITECTURE §41.10)."""

from __future__ import annotations

from typing import Any

import numpy as np


def mcnemar_test(y_true: np.ndarray, y_a: np.ndarray, y_b: np.ndarray) -> dict[str, Any]:
    """McNemar via statsmodels."""
    from statsmodels.stats.contingency_tables import mcnemar

    a_wrong_b_right = int(np.sum((y_a != y_true) & (y_b == y_true)))
    a_right_b_wrong = int(np.sum((y_a == y_true) & (y_b != y_true)))
    table = [[0, a_right_b_wrong], [a_wrong_b_right, 0]]
    # Better: full 2x2 of disagreements
    both_right = int(np.sum((y_a == y_true) & (y_b == y_true)))
    both_wrong = int(np.sum((y_a != y_true) & (y_b != y_true)))
    table = np.array([[both_right, a_right_b_wrong], [a_wrong_b_right, both_wrong]])
    res = mcnemar(table, exact=False, correction=True)
    return {
        "id": "CLE.T.COMPARE_MCNEMAR",
        "statistic": float(res.statistic),
        "pvalue": float(res.pvalue),
        "table": table.tolist(),
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
