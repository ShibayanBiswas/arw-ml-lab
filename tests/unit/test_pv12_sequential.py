"""PV12 sequential time / sort / dupes / lookback — oneshot-c246."""

from __future__ import annotations

import pandas as pd

from labcore.predict.validate import validate_predict_frame
from labcore.ux.pv_messages import IMPLEMENTED_PV_CODES, pv_message_for_code


def _base_contract(**extra: object) -> dict:
    c: dict = {
        "target": "y",
        "features": [{"name": "x1", "kind": "numeric", "nullable": True}],
        "time_column": "ts",
        "lookback": 2,
    }
    c.update(extra)
    return c


def test_pv12_deferred_without_time_column() -> None:
    contract = {
        "target": "y",
        "features": [{"name": "x1", "kind": "numeric", "nullable": True}],
    }
    df = pd.DataFrame({"x1": [1.0, 2.0]})
    report = validate_predict_frame(df, contract)
    assert any(i.code == "PV12" and i.severity == "deferred" for i in report.deferred)


def test_pv12_blocks_unparseable_time() -> None:
    df = pd.DataFrame({"x1": [1.0, 2.0], "ts": ["not-a-date", "also-bad"]})
    report = validate_predict_frame(df, _base_contract())
    assert any(i.code == "PV12" and i.severity == "block" for i in report.blocking)
    assert report.ok is False


def test_pv12_warns_unsorted_and_offers_autosort() -> None:
    df = pd.DataFrame(
        {
            "x1": [1.0, 2.0, 3.0, 4.0],
            "ts": ["2024-01-03", "2024-01-01", "2024-01-02", "2024-01-04"],
        }
    )
    report = validate_predict_frame(df, _base_contract(lookback=1))
    warn = next(i for i in report.warnings if i.code == "PV12" and i.details.get("auto_sort"))
    assert warn.severity == "warn"


def test_pv12_blocks_when_all_rows_lack_lookback() -> None:
    df = pd.DataFrame(
        {
            "x1": [1.0, 2.0],
            "ts": ["2024-01-01", "2024-01-02"],
        }
    )
    report = validate_predict_frame(df, _base_contract(lookback=5))
    block = next(i for i in report.blocking if i.code == "PV12")
    assert block.details.get("insufficient_history") is True
    assert report.ok is False


def test_pv12_warns_partial_insufficient_history() -> None:
    df = pd.DataFrame(
        {
            "x1": [1.0, 2.0, 3.0, 4.0, 5.0],
            "ts": pd.date_range("2024-01-01", periods=5, freq="D"),
        }
    )
    report = validate_predict_frame(df, _base_contract(lookback=2))
    assert not any(i.code == "PV12" for i in report.blocking)
    warn = next(
        i
        for i in report.warnings
        if i.code == "PV12" and i.details.get("insufficient_history")
    )
    assert warn.n_rows == 2


def test_pv12_ui_message_registered() -> None:
    assert "PV12" in IMPLEMENTED_PV_CODES
    msg = pv_message_for_code("PV12")
    assert "lookback" in msg["fix"].lower() or "time" in msg["fix"].lower()


def test_pv12_stores_insufficient_history_rows_on_report() -> None:
    df = pd.DataFrame(
        {
            "x1": [1.0, 2.0, 3.0, 4.0, 5.0],
            "ts": pd.date_range("2024-01-01", periods=5, freq="D"),
        }
    )
    report = validate_predict_frame(df, _base_contract(lookback=2))
    assert len(report.insufficient_history_rows) == 2
