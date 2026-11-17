"""FS.P.HOLDING — triple-barrier holding-period distribution."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.suitability import plot_holding_period_distribution
from labcore.suitability.fs_checks import compute_trial_holding_profile, enumerate_trial_tb_events

ROOT = Path(__file__).resolve().parents[2]


def test_holding_profile_matches_tb_events():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    base = enumerate_trial_tb_events(df, "close", horizon=5, vol_span=100)
    prof = compute_trial_holding_profile(df, "close", horizon=5, vol_span=100)
    assert base["ok"] and prof["ok"]
    manual = [int(ev["t1"]) - int(ev["t0"]) for ev in base["events"]]
    assert prof["holding_bars"] == manual
    assert prof["n_events"] == len(manual)
    assert 0 <= prof["min_holding"] <= prof["median_holding"] <= prof["max_holding"]


def test_plot_holding_period_artefact():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    art = plot_holding_period_distribution(df, price_col="close", seed=42)
    assert art["id"] == "FS.P.HOLDING"
    assert art["numbers"]["seed"] == 42
    assert art["numbers"]["n_events"] >= 20
    assert art["numbers"]["mean_holding"] is not None
    assert sum(art["numbers"]["by_label_counts"].values()) == art["numbers"]["n_events"]
    assert len(art["plotly"]["data"]) >= 1