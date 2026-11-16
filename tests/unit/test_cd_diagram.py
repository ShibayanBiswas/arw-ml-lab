"""Friedman–Nemenyi / CD diagram tests (seed 42)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from labcore.eval.cd_diagram import friedman_nemenyi, plot_cd_ranks


def test_friedman_detects_difference():
    rng = np.random.default_rng(42)
    # model A clearly better
    data = {
        "A": rng.normal(0.9, 0.02, size=12),
        "B": rng.normal(0.5, 0.05, size=12),
        "C": rng.normal(0.55, 0.05, size=12),
    }
    df = pd.DataFrame(data)
    out = friedman_nemenyi(df)
    assert out["status"] == "ok"
    assert out["mean_ranks"]["A"] < out["mean_ranks"]["B"]
    assert out["critical_difference"] > 0
    fig = plot_cd_ranks(out)
    assert fig["data"]
