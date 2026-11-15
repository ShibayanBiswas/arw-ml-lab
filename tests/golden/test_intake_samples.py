"""Golden intake expectations — ARCHITECTURE §33.14."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from labcore.data.samples import load_sample_frame
from labcore.intake.pipeline import run_intake

ROOT = Path(__file__).resolve().parents[2]


def _run(ds_id: str):
    df, _, _ = load_sample_frame(ds_id)
    return run_intake(df)["merged"]


def test_intake_ds3_titanic():
    m = _run("DS3")
    assert m["family"]["proposed"] == "supervised_non_sequential"
    assert m["family"]["scores"]["supervised_non_sequential"] >= 0.7
    assert m["targets"][0]["column"] == "Survived"
    assert m["roles"]["PassengerId"]["role"] == "row_id"
    assert m["roles"]["Name"]["role"] in {"pii", "text"}
    assert m["roles"]["Name"]["hard_exclude"] is True
    assert "high_missing" in m["roles"]["Cabin"]["tags"]
    assert m["roles"]["Cabin"]["included"] is False


def test_intake_ds12_housing():
    try:
        m = _run("DS12")
    except KeyError as exc:
        pytest.skip(f"DS12 source unavailable: {exc}")
    assert m["family"]["proposed"] == "supervised_non_sequential"
    assert m["targets"][0]["column"] == "median_house_value"
    assert (m.get("task") or {}).get("type") == "regression"


def test_intake_ds18_unsupervised():
    m = _run("DS18")
    assert m["family"]["proposed"] == "unsupervised"
    assert m["roles"]["CustomerID"]["role"] == "row_id"


def test_intake_ds22_airline():
    m = _run("DS22")
    assert m["family"]["proposed"] == "time_series"
    assert m["family"]["scores"]["time_series"] >= 0.8
    assert m["time_index"] and (
        m["time_index"].get("column") == "Month" or m["time_index"].get("column")
    )
    alias = (m.get("frequency") or {}).get("alias") or ""
    assert alias.startswith("M") or "M" in alias or alias in {"MS", "ME", "M"}
    periods = (m.get("frequency") or {}).get("seasonal_periods") or []
    assert 12 in periods or 12.0 in periods
    assert m["targets"][0]["column"] == "Passengers"
    assert m.get("horizon") and m["horizon"]["h_max"] == 24


def test_intake_ds24_daily():
    m = _run("DS24")
    assert m["family"]["proposed"] == "time_series"
    alias = ((m.get("frequency") or {}).get("alias") or "").upper()
    assert alias.startswith("D") or alias == "D"
    periods = (m.get("frequency") or {}).get("seasonal_periods") or []
    assert any(abs(p - 7) < 0.1 or abs(p - 365.25) < 0.1 for p in periods)


def test_intake_ds27_quarterly_composite():
    m = _run("DS27")
    assert m["family"]["proposed"] == "time_series"
    ti = m.get("time_index") or {}
    assert ti.get("composite_of") and set(ti["composite_of"]) >= {"year", "quarter"}
    alias = ((m.get("frequency") or {}).get("alias") or "").upper()
    assert alias.startswith("Q") or "Q" in alias


def test_intake_ds28_hourly_ot():
    m = _run("DS28")
    assert m["family"]["proposed"] == "time_series"
    alias = ((m.get("frequency") or {}).get("alias") or "").upper()
    assert alias.startswith("H") or alias == "H"
    assert m["targets"][0]["column"] == "OT"


def test_intake_ds30_nifty_financial():
    m = _run("DS30")
    assert m["family"]["proposed"] == "supervised_sequential"
    assert m["family"]["financial"] is True
    assert m["family"]["scores"]["supervised_sequential"] >= 0.7
    freq = m.get("frequency") or {}
    alias = str(freq.get("alias") or "")
    assert "trading" in alias.lower() or "XNSE" in alias or alias in {"B", "C"}
    roles = m["roles"]
    assert any(r["role"] == "price_close" for r in roles.values())
    assert any(r["role"] == "volume" for r in roles.values())
    # raw Close not a target
    for t in m["targets"]:
        assert t.get("column") != "Close"
        if t.get("column") == "__derived__":
            assert t.get("derived", {}).get("builder") == "triple_barrier" or t.get("derived")
    assert m["targets"][0].get("derived", {}).get("builder") == "triple_barrier"


def test_intake_synthetic_leakage():
    path = ROOT / "data" / "samples" / "synthetic" / "leakage_intake.csv"
    df = pd.read_csv(path, parse_dates=["order_date", "ship_date"])
    m = run_intake(df)["merged"]
    rules = {(s["column"], s["rule"], s["severity"]) for s in m["leakage_suspects"]}
    assert any(c == "y_copy" and sev == "critical" for c, _, sev in rules)
    assert any(c == "ship_date" and r == "later_event_timestamp" for c, r, _ in rules)
    assert any(r in {"centred_rolling_future", "lead_lag_future_info"} for _, r, _ in rules)
