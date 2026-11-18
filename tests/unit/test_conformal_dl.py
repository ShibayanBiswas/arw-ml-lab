"""Conformal DL residual wrapper — oneshot-c269."""

from __future__ import annotations

import numpy as np

from labcore.uncertainty.conformal_dl import (
    ARTEFACT_ID,
    conformal_qhat_from_residuals,
    predict_with_conformal_residual,
)


def test_conformal_dl_intervals() -> None:
    rng = np.random.default_rng(42)
    y = rng.normal(size=40)
    pred = y + rng.normal(scale=0.3, size=40)
    q = conformal_qhat_from_residuals(y, pred, confidence_level=0.9)
    assert q > 0
    out = predict_with_conformal_residual(pred[:5], q)
    assert out["id"] == ARTEFACT_ID
    assert out["refit"] is False
    widths = np.asarray(out["pred_upper"]) - np.asarray(out["pred_lower"])
    assert np.allclose(widths, 2 * q)
