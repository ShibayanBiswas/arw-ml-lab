"""FS.P.SADF — supremum ADF bubble diagnostic plot."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.finance.sadf import compute_sadf_series
from labcore.suitability import plot_sadf

ROOT = Path(__file__).resolve().parents[2]


def _synthetic_bubble_log_prices(n: int = 220, *, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    log_px = np.zeros(n)
    for t in range(1, n):
        if 80 <= t < 130:
            log_px[t] = log_px[t - 1] + 0.018 + rng.normal(0, 0.004)
        else:
            log_px[t] = log_px[t - 1] + rng.normal(0, 0.008)
    return log_px


def test_sadf_higher_during_explosive_segment() -> None:
    log_px = _synthetic_bubble_log_prices()
    out = compute_sadf_series(
        log_px, min_window=25, max_lookback=55, maxlag=0, end_step=2
    )
    bubble_mid = 105
    near = min(
        range(len(out["end_indices"])),
        key=lambda i: abs(out["end_indices"][i] - bubble_mid),
    )
    quiet = min(
        range(len(out["end_indices"])),
        key=lambda i: abs(out["end_indices"][i] - 25),
    )
    assert out["sadf"][near] > out["sadf"][quiet]


def test_plot_sadf_nifty_artefact() -> None:
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    art = plot_sadf(df, price_col="close", end_step=5, seed=42)
    assert art["id"] == "FS.P.SADF"
    assert art["numbers"]["seed"] == 42
    assert art["numbers"]["n_obs"] >= 50
    assert len(art["numbers"]["series"]) >= 50
    peak = float(art["numbers"]["peak_sadf"])
    assert -5 < peak < 10