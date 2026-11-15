"""REE.M.* core metrics — sklearn / numpy wrappers (ARCHITECTURE §42)."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    explained_variance_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    median_absolute_error,
    r2_score,
)


def compute_ree_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    resid = y_true - y_pred
    out: dict[str, float] = {
        "REE.M.01": float(r2_score(y_true, y_pred)),
        "REE.M.02": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "REE.M.03": float(mean_absolute_error(y_true, y_pred)),
        "REE.M.04": float(median_absolute_error(y_true, y_pred)),
        "REE.M.05": float(np.max(np.abs(resid))),
        "REE.M.06": float(explained_variance_score(y_true, y_pred)),
        "REE.M.07": float(mean_squared_error(y_true, y_pred)),
    }
    try:
        out["REE.M.08"] = float(mean_absolute_percentage_error(y_true, y_pred))
    except Exception:
        out["REE.M.08"] = float("nan")
    # sMAPE thin arithmetic on library residuals
    denom = np.abs(y_true) + np.abs(y_pred)
    with np.errstate(invalid="ignore", divide="ignore"):
        smape = np.nanmean(2.0 * np.abs(resid) / denom)
    out["REE.M.09"] = float(smape)
    out["REE.M.10"] = float(np.mean(resid))
    out["REE.M.11"] = float(np.std(resid, ddof=1)) if len(resid) > 1 else 0.0
    return out
