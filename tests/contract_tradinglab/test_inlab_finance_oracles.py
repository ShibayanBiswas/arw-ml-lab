"""Offline TradingLab-adjacent contracts — no vendor/tradinglab required.

Parity vs TradingLab submodule stays skip-gated in ``test_contract_placeholder``.
These tests pin in-lab purged CV / CPCV / PBO surfaces used by Phase 5.
"""

from __future__ import annotations

import numpy as np
from labcore.cv import CombinatorialPurgedKFold, PurgedKFold
from labcore.finance import probability_of_backtest_overfitting


def test_purged_kfold_embargo_shapes() -> None:
    X = np.arange(100).reshape(-1, 1)
    cv = PurgedKFold(n_splits=5, pct_embargo=0.02)
    folds = list(cv.split(X))
    assert len(folds) == 5
    for tr, te in folds:
        assert len(tr) > 0 and len(te) > 0
        assert len(np.intersect1d(tr, te)) == 0


def test_cpcv_import_smoke() -> None:
    X = np.arange(80).reshape(-1, 1)
    cv = CombinatorialPurgedKFold(n_splits=4, n_test_splits=2, pct_embargo=0.01)
    folds = list(cv.split(X))
    assert len(folds) >= 1
    tr, te = folds[0]
    assert len(tr) > 0 and len(te) > 0


def test_pbo_contract_callable() -> None:
    """PBO helper must exist for financial champion gates (ARCHITECTURE §15)."""
    # thin smoke: matrix of strategy returns across trials
    mat = np.random.default_rng(42).normal(size=(16, 6))
    out = probability_of_backtest_overfitting(mat)
    if isinstance(out, dict):
        val = float(out.get("pbo", out.get("value", out.get("PBO", 0.0))))
    else:
        val = float(out)
    assert 0.0 <= val <= 1.0
