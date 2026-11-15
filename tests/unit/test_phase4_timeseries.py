"""Phase 4 thin: DS22/DS23 backtest ACs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from labcore.timeseries.analysis import analyse_series
from labcore.timeseries.backtest import rolling_origin_backtest
from labcore.timeseries.horizon_guard import compute_horizon_guard, seasonal_allowed

ROOT = Path(__file__).resolve().parents[2]
AIRLINE = ROOT / "data" / "samples" / "airline_passengers.csv"
SHAMPOO = ROOT / "data" / "samples" / "shampoo.csv"


@pytest.fixture(scope="module")
def airline_y() -> pd.Series:
    df = pd.read_csv(AIRLINE)
    return df["Passengers"].astype(float)


@pytest.fixture(scope="module")
def shampoo_y() -> pd.Series:
    df = pd.read_csv(SHAMPOO)
    return df["Sales"].astype(float)


def test_ds22_horizon_and_sarima_beats_naive(airline_y):
    n = len(airline_y)
    assert n == 144
    guard = compute_horizon_guard(n, "MS", m=12, w=4)
    assert guard["h_max"] == 24
    h = 12  # within h_max; faster than h=24 for CI wall-time while still W=4
    # AC also allows full h_max path — use h=12 for speed; assert formula separately
    bt = rolling_origin_backtest(airline_y, h=h, w=4, m=12, freq="MS", seed=42)
    assert bt["ok"], bt
    sn = bt["models"]["seasonal_naive"]
    sa = bt["models"]["sarima_airline"]
    assert sn["ok"] and sa["ok"], bt["models"]
    assert sa["cv_mean"]["mase"] < sn["cv_mean"]["mase"], (
        sa["cv_mean"]["mase"],
        sn["cv_mean"]["mase"],
    )
    lb = sa.get("ljung_box") or {}
    assert lb.get("pvalue") is not None and lb["pvalue"] > 0.05, lb


def test_ds22_h_max_full_guard():
    """Structural AC: DS22 h_max = 24 with W=4, n_min_train=24."""
    assert compute_horizon_guard(144, "MS", m=12, w=4)["h_max"] == 24


def test_ds23_seasonal_disabled(shampoo_y):
    n = len(shampoo_y)
    assert n == 36
    guard = compute_horizon_guard(n, "MS", m=12, w=4)
    assert guard["h_max"] <= 9
    ok, reason = seasonal_allowed(n, 12.0, h=12)
    assert not ok and reason
    # Force check via models API at h requiring 2m+h ≥ n
    from labcore.timeseries.models import forecast_sarima_airline

    with pytest.raises(ValueError, match="2m\\+h|seasonal"):
        forecast_sarima_airline(shampoo_y.to_numpy(), h=12, m=12)


def test_analysis_airline(airline_y):
    out = analyse_series(airline_y, m=12)
    assert "acf" in out and len(out["acf"]) > 5
    assert out.get("stl") and "error" not in out["stl"]
