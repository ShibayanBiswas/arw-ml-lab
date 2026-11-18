"""Conformal residual wrapper for torch regressors (Phase 2A) — oneshot-c269.

Fits only the residual quantile on a held-out calibration matrix; never calls
``fit`` / ``backward`` on the underlying network.
"""

from __future__ import annotations

from typing import Any

import numpy as np

ARTEFACT_ID = "UQ.CONFORMAL.DL"


def conformal_qhat_from_residuals(
    y_true: Any,
    y_pred: Any,
    *,
    confidence_level: float = 0.9,
) -> float:
    yt = np.asarray(y_true, dtype=float).ravel()
    yp = np.asarray(y_pred, dtype=float).ravel()
    mask = np.isfinite(yt) & np.isfinite(yp)
    if int(mask.sum()) < 2:
        raise ValueError("need ≥2 finite residuals")
    return float(np.quantile(np.abs(yt[mask] - yp[mask]), float(confidence_level)))


def predict_with_conformal_residual(
    y_pred: Any,
    qhat: float,
) -> dict[str, Any]:
    """Symmetric intervals around point predictions using a stored qhat."""
    yp = np.asarray(y_pred, dtype=float).ravel()
    q = float(qhat)
    lower = yp - q
    upper = yp + q
    return {
        "id": ARTEFACT_ID,
        "pred": yp.tolist(),
        "pred_lower": lower.tolist(),
        "pred_upper": upper.tolist(),
        "conformal_qhat": q,
        "pred_interval_method": "split_conformal_residual_dl",
        "refit": False,
    }
