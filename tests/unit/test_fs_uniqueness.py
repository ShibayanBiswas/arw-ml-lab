"""FS.P.UNIQUENESS — per-event uniqueness histogram and concurrency series."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.suitability import plot_uniqueness_concurrency, run_suitability
from labcore.suitability.fs_checks import compute_trial_uniqueness_profile

ROOT = Path(__file__).resolve().parents[2]


def test_uniqueness_profile_matches_fs12():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    report = run_suitability(df, time_col="date", asset="NIFTY")
    fs12 = next(c for c in report["checks"] if c["code"] == "FS12")
    prof = compute_trial_uniqueness_profile(df, "close")
    assert prof["ok"]
    assert fs12["details"]["mean_uniqueness"] == prof["mean_uniqueness"]
    assert fs12["details"]["n_spans"] == prof["n_spans"]


def test_plot_uniqueness_concurrency_artefact():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    art = plot_uniqueness_concurrency(df, price_col="close", time_col="date", seed=42)
    assert art["id"] == "FS.P.UNIQUENESS"
    assert art["numbers"]["seed"] == 42
    assert art["numbers"]["mean_uniqueness"] is not None
    assert art["numbers"]["n_spans"] >= 20
    assert len(art["plotly"]["data"]) >= 2