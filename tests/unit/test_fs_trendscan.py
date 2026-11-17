"""FS.P.TRENDSCAN — trend-scan slope t-stat diagnostic plot."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.finance.trendscan import compute_trendscan_series
from labcore.suitability import plot_trendscan

ROOT = Path(__file__).resolve().parents[2]


def _synthetic_uptrend_log_prices(n: int = 180, *, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    log_px = np.zeros(n)
    for t in range(1, n):
        if 40 <= t < 120:
            log_px[t] = log_px[t - 1] + 0.012 + rng.normal(0, 0.003)
        else:
            log_px[t] = log_px[t - 1] + rng.normal(0, 0.006)
    return log_px


def test_trendscan_higher_t_during_trend_segment() -> None:
    log_px = _synthetic_uptrend_log_prices()
    out = compute_trendscan_series(log_px, l_min=5, l_max=15, step=2)
    trend_mid = 80
    near = min(range(len(out["origins"])), key=lambda i: abs(out["origins"][i] - trend_mid))
    quiet = min(range(len(out["origins"])), key=lambda i: abs(out["origins"][i] - 10))
    assert abs(out["t_value"][near]) > abs(out["t_value"][quiet])


def test_plot_trendscan_nifty_artefact() -> None:
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    art = plot_trendscan(df, price_col="close", step=3, seed=42)
    assert art["id"] == "FS.P.TRENDSCAN"
    assert art["numbers"]["seed"] == 42
    assert art["numbers"]["n_obs"] >= 50
    assert len(art["numbers"]["series"]) >= 50
    share = float(art["numbers"]["share_abs_t_gt_2"])
    assert 0.0 <= share <= 1.0