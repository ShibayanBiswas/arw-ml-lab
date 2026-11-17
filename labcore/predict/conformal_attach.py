"""Attach split-conformal residual quantile from OOF residuals (never refits)."""

from __future__ import annotations

from typing import Any

import numpy as np


def oof_absolute_residual_qhat(
    y_true: Any,
    y_pred: Any,
    *,
    confidence_level: float = 0.9,
) -> float:
    """``q_hat`` = empirical quantile of |y − ŷ| at ``confidence_level`` (OOF only)."""
    yt = np.asarray(y_true, dtype=float).ravel()
    yp = np.asarray(y_pred, dtype=float).ravel()
    mask = np.isfinite(yt) & np.isfinite(yp)
    if int(mask.sum()) < 2:
        raise ValueError("need ≥2 finite OOF residuals for conformal qhat")
    resid = np.abs(yt[mask] - yp[mask])
    return float(np.quantile(resid, float(confidence_level)))


def attach_oof_residual_qhat(
    pipeline: Any,
    y_true: Any,
    y_pred: Any,
    *,
    confidence_level: float = 0.9,
) -> Any:
    """Set ``pipeline.conformal_qhat_`` from OOF residuals for predict-time intervals."""
    qhat = oof_absolute_residual_qhat(y_true, y_pred, confidence_level=confidence_level)
    try:
        setattr(pipeline, "conformal_qhat_", qhat)
    except Exception:
        # Some estimators reject setattr; wrap in a thin holder
        class _ConformalHolder:
            def __init__(self, inner: Any, q: float) -> None:
                self._inner = inner
                self.conformal_qhat_ = q

            def predict(self, X: Any) -> Any:
                return self._inner.predict(X)

            def predict_proba(self, X: Any) -> Any:
                return self._inner.predict_proba(X)

            def __getattr__(self, name: str) -> Any:
                return getattr(self._inner, name)

        return _ConformalHolder(pipeline, qhat)
    return pipeline
