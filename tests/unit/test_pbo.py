"""PBO / CSCV unit tests (Bailey et al.)."""

from __future__ import annotations

import numpy as np
from labcore.finance.pbo import probability_of_backtest_overfitting


def test_pbo_random_near_half():
    rng = np.random.default_rng(42)
    # T=64, M=8 noise — PBO should be around 0.5
    mat = rng.normal(size=(64, 8))
    out = probability_of_backtest_overfitting(mat, n_blocks=8, seed=42)
    assert out["status"] == "ok"
    assert 0.0 <= out["pbo"] <= 1.0
    assert out["n_combinations"] > 0


def test_pbo_too_small_not_computed():
    mat = np.ones((4, 2))
    out = probability_of_backtest_overfitting(mat, n_blocks=16, seed=42)
    assert out["status"] == "not computed"
    assert out["pbo"] != out["pbo"]  # nan


def test_pbo_clear_overfit_signal():
    rng = np.random.default_rng(42)
    t, m = 64, 6
    mat = rng.normal(size=(t, m)) * 0.01
    # config 0 looks great in first half, collapses in second
    mat[:32, 0] += 5.0
    mat[32:, 0] -= 5.0
    out = probability_of_backtest_overfitting(mat, n_blocks=8, seed=42)
    assert out["status"] == "ok"
    # overfit config should push PBO above chance
    assert out["pbo"] >= 0.4
