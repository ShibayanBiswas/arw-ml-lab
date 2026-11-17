"""PV11 batch drift when reference_df provided — oneshot-c242."""

from __future__ import annotations

import numpy as np
import pandas as pd

from labcore.predict.validate import validate_predict_frame


def _contract() -> dict:
    return {
        "target": "y",
        "features": [
            {"name": "x1", "kind": "numeric", "nullable": True},
            {"name": "x2", "kind": "numeric", "nullable": True},
        ],
    }


def test_pv11_deferred_without_reference() -> None:
    rng = np.random.default_rng(42)
    df = pd.DataFrame({"x1": rng.normal(size=50), "x2": rng.normal(size=50)})
    report = validate_predict_frame(df, _contract())
    codes = {i.code for i in report.deferred}
    assert "PV11" in codes


def test_pv11_computes_when_reference_supplied() -> None:
    rng = np.random.default_rng(42)
    ref = pd.DataFrame({"x1": rng.normal(size=200), "x2": rng.normal(size=200)})
    # Shifted batch → should flag drift
    cur = pd.DataFrame({"x1": rng.normal(loc=3.0, size=80), "x2": rng.normal(loc=-2.0, size=80)})
    report = validate_predict_frame(cur, _contract(), reference_df=ref)
    pv11 = [i for i in report.warnings if i.code == "PV11"]
    assert pv11, report.deferred
    assert "ks" in (pv11[0].details or {})
    assert int((pv11[0].details or {})["ks"].get("n_drifted", 0)) >= 1
