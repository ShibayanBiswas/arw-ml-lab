"""Calibration thin wrappers — sklearn CalibratedClassifierCV + netcal ECE."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split


def expected_calibration_error(
    y_true: np.ndarray,
    scores: np.ndarray,
    *,
    n_bins: int = 15,
) -> float:
    try:
        from netcal.metrics import ECE

        return float(ECE(n_bins).measure(np.asarray(scores), np.asarray(y_true)))
    except Exception:
        y = np.asarray(y_true).ravel()
        p = np.asarray(scores).ravel()
        bins = np.linspace(0.0, 1.0, n_bins + 1)
        ece = 0.0
        for i in range(n_bins):
            mask = (p >= bins[i]) & (p < bins[i + 1] if i < n_bins - 1 else p <= bins[i + 1])
            if not np.any(mask):
                continue
            ece += float(mask.mean()) * abs(float(y[mask].mean()) - float(p[mask].mean()))
        return float(ece)


def calibrate_binary(
    estimator: Any,
    X: np.ndarray | Any,
    y: np.ndarray,
    *,
    method: Literal["sigmoid", "isotonic"] = "isotonic",
    seed: int = 42,
) -> dict[str, Any]:
    """
    Three-way split: fit raw on train, calibrate on cal, compare ECE on test.

    sklearn ≥1.6 removed ``cv='prefit'`` — wrap with ``FrozenEstimator``.
    """
    X_tmp, X_te, y_tmp, y_te = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    X_tr, X_cal, y_tr, y_cal = train_test_split(
        X_tmp, y_tmp, test_size=0.33, random_state=seed, stratify=y_tmp
    )

    raw = clone(estimator)
    raw.fit(X_tr, y_tr)
    ece_before = expected_calibration_error(y_te, np.asarray(raw.predict_proba(X_te))[:, 1])

    from sklearn.frozen import FrozenEstimator

    base = clone(estimator)
    base.fit(X_tr, y_tr)
    cal = CalibratedClassifierCV(FrozenEstimator(base), method=method)
    cal.fit(X_cal, y_cal)
    ece_after = expected_calibration_error(y_te, np.asarray(cal.predict_proba(X_te))[:, 1])

    return {
        "id": "CLE.T.COMPARE_CALIBRATION",
        "method": method,
        "ece_before": ece_before,
        "ece_after": ece_after,
        "ece_reduced": bool(ece_after < ece_before - 1e-12),
        "calibrator": cal,
    }
