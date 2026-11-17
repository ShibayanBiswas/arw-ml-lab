"""FS.P.PRICE — close series with CUSUM event markers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.suitability import plot_price_cusum, run_suitability
from labcore.suitability.fs_checks import compute_cusum_filter_events

ROOT = Path(__file__).resolve().parents[2]


def test_cusum_events_match_fs9():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    report = run_suitability(df, time_col="date", asset="NIFTY")
    fs9 = next(c for c in report["checks"] if c["code"] == "FS9")
    comp = compute_cusum_filter_events(df, "close")
    assert comp["ok"]
    assert fs9["details"]["events"] == comp["n_events"]
    assert fs9["details"]["h"] == comp["h"]


def test_plot_price_cusum_artefact():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    art = plot_price_cusum(df, price_col="close", time_col="date", seed=42)
    assert art["id"] == "FS.P.PRICE"
    assert art["numbers"]["seed"] == 42
    assert art["numbers"]["n_events"] == art["numbers"]["n_up"] + art["numbers"]["n_down"]
    assert art["numbers"]["n_events"] >= 100
    assert art["numbers"]["h"] > 0
    assert art["plotly"]["data"]
    assert len(art["plotly"]["data"][0]["y"]) == len(df)