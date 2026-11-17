"""FS.P.VOL — EWMA daily volatility series."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.suitability import plot_daily_volatility, run_suitability
from labcore.suitability.fs_checks import compute_daily_ewma_vol

ROOT = Path(__file__).resolve().parents[2]


def test_daily_vol_matches_fs7_median():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    report = run_suitability(df, time_col="date", asset="NIFTY")
    fs7 = next(c for c in report["checks"] if c["code"] == "FS7")
    comp = compute_daily_ewma_vol(df, "close", span=100)
    assert comp["ok"]
    assert fs7["details"]["median_vol"] == comp["median_vol"]


def test_plot_daily_volatility_artefact():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    art = plot_daily_volatility(df, price_col="close", time_col="date", seed=42)
    assert art["id"] == "FS.P.VOL"
    assert art["numbers"]["seed"] == 42
    assert art["numbers"]["span"] == 100
    assert art["numbers"]["median_vol"] is not None and art["numbers"]["median_vol"] > 0
    assert art["plotly"]["data"]
    assert len(art["plotly"]["data"][0]["y"]) == len(df)