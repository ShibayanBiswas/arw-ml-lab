"""SEC-04 — shared formula escape for CSV/XLSX exports (ST-SEC-04)."""

from __future__ import annotations

import pytest

from labcore.enterprise.audit import audit_rows_to_csv, demo_audit_rows
from labcore.predict.template import predictions_to_safe_csv
from labcore.security.formula_escape import escape_formula_export_cell, is_formula_trigger
from labcore.train.export import leaderboard_to_csv

WS = "00000000-0000-0000-0000-000000000010"


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("=1+1", "'=1+1"),
        ("+SUM(A1)", "'+SUM(A1)"),
        ("-2+3", "'-2+3"),
        ("@SUM(A1:A2)", "'@SUM(A1:A2)"),
        ("\tcmd", "'\tcmd"),
        ("\rcmd", "'\rcmd"),
        ("safe", "safe"),
        ("", ""),
        (None, ""),
        (42, "42"),
    ],
)
def test_escape_formula_export_cell(raw: object, expected: str) -> None:
    assert escape_formula_export_cell(raw) == expected
    if isinstance(raw, str):
        assert is_formula_trigger(raw) == (escape_formula_export_cell(raw) != raw)


def test_leaderboard_csv_all_triggers_seed_42() -> None:
    csv_text = leaderboard_to_csv(
        [
            {
                "rank": 1,
                "algorithm_key": "=evil",
                "algorithm_id": "C1",
                "name": "+x",
                "library": "sklearn",
                "primary_metric": "balanced_accuracy",
                "cv_mean": {"balanced_accuracy": 0.7},
                "cv_std": {"balanced_accuracy": 0.01},
                "test": {"balanced_accuracy": 0.69},
            }
        ]
    )
    for ch in ("'=evil", "'+x"):
        assert ch in csv_text


def test_audit_export_escapes_action_and_detail() -> None:
    rows = demo_audit_rows(WS, seed=42, count=1)
    rows[0]["action"] = "=HYPERLINK()"
    rows[0]["detail"] = {"note": "+cmd"}
    csv_text = audit_rows_to_csv(rows)
    assert "'=HYPERLINK()" in csv_text
    assert '"+cmd"' in csv_text or "'+cmd" in csv_text


def test_predictions_export_reuses_escape() -> None:
    import pandas as pd

    df = pd.DataFrame({"y_pred": ["=1+1", "ok"]})
    csv_text = predictions_to_safe_csv(df).decode("utf-8")
    assert "'=1+1" in csv_text
    assert "ok" in csv_text