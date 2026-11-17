"""FS.P.LABEL_BALANCE — trial financial label share bar."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from labcore.suitability import plot_label_balance, run_suitability
from labcore.suitability.fs_checks import compute_trial_tb_label_balance

ROOT = Path(__file__).resolve().parents[2]


def test_label_balance_matches_fs10_details():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    report = run_suitability(df, time_col="date", asset="NIFTY")
    fs10 = next(c for c in report["checks"] if c["code"] == "FS10")
    bal = compute_trial_tb_label_balance(df, "close")
    assert bal["ok"]
    assert fs10["details"]["pos"] == bal["counts"][1]
    assert fs10["details"]["neg"] == bal["counts"][-1]
    assert fs10["details"]["minority_share"] == bal["minority_signed_share"]
    assert fs10["details"]["zero_share"] == bal["shares"][0]


def test_plot_label_balance_artefact_and_shares():
    path = ROOT / "data" / "samples" / "nifty50_daily_5y.csv"
    df = pd.read_csv(path)
    art = plot_label_balance(df, price_col="close", method="triple_barrier")
    assert art["id"] == "FS.P.LABEL_BALANCE"
    shares = [float(art["numbers"]["shares"][k]) for k in ("-1", "0", "1")]
    assert abs(sum(shares) - 1.0) < 1e-9
    assert art["numbers"]["n_labels"] == sum(int(art["numbers"]["counts"][k]) for k in ("-1", "0", "1"))
    assert art["plotly"]["data"]