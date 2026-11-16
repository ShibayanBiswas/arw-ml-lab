"""Permutation importance via sklearn.inspection (ARCHITECTURE §17)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance


def permutation_explain(
    model: Any,
    X: pd.DataFrame | np.ndarray,
    y: np.ndarray | pd.Series,
    *,
    scoring: str | None = None,
    n_repeats: int = 10,
    seed: int = 42,
) -> dict[str, Any]:
    """Global permutation importance (mean ± std over repeats)."""
    feature_names = (
        list(X.columns)
        if isinstance(X, pd.DataFrame)
        else [f"f{i}" for i in range(np.asarray(X).shape[1])]
    )
    X_arr = np.asarray(X, dtype=float)
    y_arr = np.asarray(y).ravel()
    kwargs: dict[str, Any] = {
        "n_repeats": n_repeats,
        "random_state": seed,
        "n_jobs": 1,
    }
    if scoring is not None:
        kwargs["scoring"] = scoring
    result = permutation_importance(model, X_arr, y_arr, **kwargs)
    order = np.argsort(result.importances_mean)[::-1]
    return {
        "id": "EXPLAIN.T.PERMUTATION",
        "feature_names": feature_names,
        "importances_mean": result.importances_mean.tolist(),
        "importances_std": result.importances_std.tolist(),
        "ranking": [feature_names[i] for i in order],
        "seed": seed,
        "n_repeats": n_repeats,
    }
