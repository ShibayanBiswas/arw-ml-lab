"""PV16 identifier_like warning — oneshot-c243."""

from __future__ import annotations

import pandas as pd

from labcore.predict.validate import validate_predict_frame


def test_pv16_warns_on_identifier_like() -> None:
    contract = {
        "target": "y",
        "features": [
            {"name": "x1", "kind": "numeric", "nullable": True},
            {"name": "passenger_name", "kind": "identifier_like", "nullable": True},
        ],
    }
    df = pd.DataFrame({"x1": [1.0, 2.0], "passenger_name": ["Ada", "Bob"]})
    report = validate_predict_frame(df, contract)
    pv16 = [i for i in report.warnings if i.code == "PV16"]
    assert pv16
    assert "passenger_name" in (pv16[0].details or {}).get("columns", [])


def test_pv16_info_when_clean() -> None:
    contract = {
        "target": "y",
        "features": [{"name": "x1", "kind": "numeric", "nullable": True}],
    }
    df = pd.DataFrame({"x1": [1.0, 2.0]})
    report = validate_predict_frame(df, contract)
    assert any(i.code == "PV16" and i.severity == "info" for i in report.info)
