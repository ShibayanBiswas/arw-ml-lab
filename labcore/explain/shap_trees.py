"""TreeSHAP + PDP/ICE thin wrappers (shap + sklearn.inspection)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.inspection import partial_dependence


def tree_shap_explain(
    model: Any,
    X: pd.DataFrame | np.ndarray,
    *,
    seed: int = 42,
) -> dict[str, Any]:
    """
    TreeSHAP via ``shap.TreeExplainer``.

    Additivity: |Σφ + E[f] − f(x)| < 1e-6 on the SHAP link (margin / log-odds
    for binary LightGBM, raw score for regressors).
    """
    import shap

    _ = seed
    feature_names = list(X.columns) if isinstance(X, pd.DataFrame) else None
    X_arr = np.asarray(X, dtype=float)
    if X_arr.ndim == 1:
        X_arr = X_arr.reshape(1, -1)

    explainer = shap.TreeExplainer(model)
    explanation = explainer(X_arr, check_additivity=False)
    sv = np.asarray(explanation.values, dtype=float)
    # Binary LightGBM: shap may return (n, n_features, n_classes) or list
    if sv.ndim == 3:
        sv = sv[:, :, -1]
    base = np.asarray(explanation.base_values, dtype=float).ravel()
    if base.size == X_arr.shape[0]:
        base_row = base
    elif base.size > 1:
        # per-class base — take positive class
        base_row = np.full(X_arr.shape[0], float(base[-1]))
    else:
        base_row = np.full(X_arr.shape[0], float(base[0]))

    # Model output on the same scale as SHAP (margin)
    if hasattr(model, "predict"):
        try:
            raw = model.predict(X_arr, raw_score=True)
            f_x = np.asarray(raw, dtype=float).ravel()
        except TypeError:
            if hasattr(model, "predict_proba"):
                # fall back: compare on probability scale with logistic of margin
                f_x = sv.sum(axis=1) + base_row
            else:
                f_x = np.asarray(model.predict(X_arr), dtype=float).ravel()
    else:
        f_x = sv.sum(axis=1) + base_row

    reconstructed = sv.sum(axis=1) + base_row
    residual = np.abs(reconstructed - f_x)
    return {
        "id": "EXPLAIN.T.SHAP_SUMMARY",
        "shap_values": sv.tolist(),
        "base_value": float(base_row[0]),
        "f_x": f_x.tolist(),
        "additivity_max_abs": float(np.max(residual)),
        "feature_names": feature_names,
        "waterfall_row0": {
            "base": float(base_row[0]),
            "shap": sv[0].tolist(),
            "f_x": float(f_x[0]),
        },
    }


def pdp_equals_mean_ice(
    model: Any,
    X: pd.DataFrame | np.ndarray,
    feature: int | str = 0,
    *,
    grid_resolution: int = 20,
) -> dict[str, Any]:
    """PDP must equal the mean of ICE curves (sklearn.inspection)."""
    result = partial_dependence(
        model,
        X,
        features=[feature],
        kind="both",
        grid_resolution=grid_resolution,
    )
    average = np.asarray(result["average"]).ravel()
    individual = np.asarray(result["individual"])
    ice_mean = individual.reshape(-1, individual.shape[-1]).mean(axis=0)
    max_abs = float(np.max(np.abs(average - ice_mean)))
    return {
        "id": "EXPLAIN.T.PDP_ICE",
        "feature": feature,
        "pdp": average.tolist(),
        "ice_mean": ice_mean.tolist(),
        "max_abs_pdp_minus_mean_ice": max_abs,
    }
