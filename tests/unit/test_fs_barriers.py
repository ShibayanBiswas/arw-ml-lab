"""FS.P.BARRIERS — sample triple-barrier event panels."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from labcore.suitability import plot_sample_barriers, run_suitability
from labcore.suitability.fs_checks import enumerate_trial_tb_events, sample_trial_tb_events

ROOT = Path(__file__).resolve().parents[2]


def test_barriers_sample_reproducible_seed_42():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    sample_a = sample_trial_tb_events(df, "close", seed=42)
    sample_b = sample_trial_tb_events(df, "close", seed=42)
    assert sample_a["ok"] and sample_b["ok"]
    assert sample_a["sampled_events"] == sample_b["sampled_events"]
    labels = {int(e["label"]) for e in sample_a["sampled_events"]}
    assert -1 in labels or 0 in labels or 1 in labels


def test_plot_sample_barriers_artefact():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    enum = enumerate_trial_tb_events(df, "close")
    assert enum["ok"]
    art = plot_sample_barriers(df, price_col="close", time_col="date", seed=42)
    assert art["id"] == "FS.P.BARRIERS"
    assert art["numbers"]["seed"] == 42
    assert 1 <= art["numbers"]["n_panels"] <= 6
    assert len(art["numbers"]["sampled_events"]) == art["numbers"]["n_panels"]
    assert art["plotly"]["data"]
    report = run_suitability(df, time_col="date", asset="NIFTY")
    fs10 = next(c for c in report["checks"] if c["code"] == "FS10")
    assert fs10["details"]["n_labels"] == enum["n_labels"]