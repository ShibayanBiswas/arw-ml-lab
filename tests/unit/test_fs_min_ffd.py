"""FS.P.MIN_FFD — fractional-difference d* vs ADF."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.finance.ffd import frac_diff_ffd, scan_min_ffd
from labcore.suitability import plot_min_ffd

ROOT = Path(__file__).resolve().parents[2]


def test_frac_diff_d1_near_first_difference():
    rng = np.random.default_rng(42)
    s = np.cumsum(rng.normal(0, 1, size=200))
    d1 = frac_diff_ffd(s, 1.0)
    diff = np.diff(s, prepend=np.nan)
    mask = np.isfinite(d1) & np.isfinite(diff)
    err = np.abs(d1[mask] - diff[mask])
    assert float(np.nanmax(err)) < 1e-10


def test_plot_min_ffd_nifty_artefact():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    art = plot_min_ffd(df, price_col="close", seed=42)
    assert art["id"] == "FS.P.MIN_FFD"
    assert art["numbers"]["seed"] == 42
    assert art["numbers"]["n_obs"] >= 50
    d_star = art["numbers"]["d_star"]
    assert d_star is None or 0 < d_star <= 0.6
    scan = scan_min_ffd(
        np.log(df["close"].astype(float).clip(lower=1e-12).to_numpy()), d_step=0.05
    )
    assert scan["d_star"] == d_star