"""PV13 HorizonGuard on predict validate — oneshot-c245."""

from __future__ import annotations

import pandas as pd

from labcore.predict.validate import validate_predict_frame


def test_pv13_blocks_over_h_max() -> None:
    contract = {
        "target": "y",
        "features": [{"name": "x1", "kind": "numeric", "nullable": True}],
        "timeseries": {"n": 144, "freq": "MS", "h_request": 100},
    }
    df = pd.DataFrame({"x1": [1.0, 2.0, 3.0]})
    report = validate_predict_frame(df, contract)
    assert any(i.code == "PV13" and i.severity == "block" for i in report.blocking)
    assert report.ok is False


def test_pv13_allows_within_h_max() -> None:
    contract = {
        "target": "y",
        "features": [{"name": "x1", "kind": "numeric", "nullable": True}],
        "timeseries": {"n": 144, "freq": "MS"},
    }
    df = pd.DataFrame({"x1": [1.0, 2.0, 3.0]})
    report = validate_predict_frame(df, contract, h_request=12)
    assert any(i.code == "PV13" and i.severity == "info" for i in report.info)
    assert not any(i.code == "PV13" for i in report.blocking)
