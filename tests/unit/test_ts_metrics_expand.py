"""§35.7 thin metric expansions — hand-checked values (seed 42)."""

from __future__ import annotations

import numpy as np
import pytest
from labcore.timeseries.metrics import (
    directional_accuracy,
    mape,
    me,
    point_metrics,
    theil_u2,
    wape,
)


def test_me_mae_mape_wape_hand():
    y = np.array([10.0, 20.0, 30.0])
    p = np.array([11.0, 18.0, 33.0])
    # errors: -1, +2, -3 → mean -2/3
    assert me(y, p) == pytest.approx(-2.0 / 3.0)
    assert mape(y, p) == pytest.approx(100.0 * ((1 / 10) + (2 / 20) + (3 / 30)) / 3)
    assert wape(y, p) == pytest.approx((1 + 2 + 3) / (10 + 20 + 30))


def test_point_metrics_keys():
    rng = np.random.default_rng(42)
    train = rng.normal(size=50) + 10
    true = train[-12:] + rng.normal(scale=0.1, size=12)
    pred = true + 0.2
    out = point_metrics(true, pred, train[:-12], m=12)
    for k in (
        "me",
        "mae",
        "rmse",
        "mape",
        "wape",
        "smape",
        "mase",
        "directional_accuracy",
        "theil_u2",
    ):
        assert k in out
        assert np.isfinite(out[k])


def test_directional_and_theil():
    y_prev = np.array([1.0, 2.0, 3.0])
    y_true = np.array([2.0, 1.0, 4.0])
    y_pred = np.array([2.5, 0.5, 3.5])
    assert directional_accuracy(y_true, y_pred, y_prev) == 1.0
    assert theil_u2(y_true, y_pred, y_prev) >= 0
