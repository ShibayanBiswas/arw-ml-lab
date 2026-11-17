"""TradingLab contract placeholder — real parity when vendor/tradinglab is vendored."""

from __future__ import annotations

import numpy as np
import pytest
from labcore.cv import PurgedKFold


def test_inlab_purged_kfold_smoke() -> None:
    """Until TradingLab submodule exists, assert in-lab purged API is importable."""
    X = np.arange(40).reshape(-1, 1)
    cv = PurgedKFold(n_splits=4, pct_embargo=0.01)
    folds = list(cv.split(X))
    assert len(folds) == 4


@pytest.mark.skip(
    reason="vendor/tradinglab missing — thin FS16–18 online; TradingLab parity only"
)
def test_tradinglab_purged_parity() -> None:
    raise AssertionError("pending TradingLab vendor submodule")
