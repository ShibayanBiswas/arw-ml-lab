"""Leaderboard export manifest — REP.T.LEADERBOARD / ST-UX-02 (ARCHITECTURE §46.4)."""

from __future__ import annotations

import zipfile
from io import BytesIO
from typing import Any

from labcore.security.formula_escape import escape_formula_export_cell
from labcore.train.export import leaderboard_to_csv, leaderboard_to_xlsx_bytes

ARTEFACT_ID = "REP.T.LEADERBOARD"
STRESS_ID = "ST-UX-02"
LAB_DEFAULT_SEED = 42


def _demo_rows() -> list[dict[str, Any]]:
    return [
        {
            "rank": 1,
            "algorithm_key": "=evil",
            "algorithm_id": "C1",
            "name": "+leader",
            "library": "sklearn",
            "primary_metric": "balanced_accuracy",
            "cv_mean": {"balanced_accuracy": 0.71},
            "cv_std": {"balanced_accuracy": 0.02},
            "test": {"balanced_accuracy": 0.69},
        },
        {
            "rank": 2,
            "algorithm_key": "clf.logistic",
            "algorithm_id": "C2",
            "name": "Logistic regression",
            "library": "sklearn",
            "primary_metric": "balanced_accuracy",
            "cv_mean": {"balanced_accuracy": 0.68},
            "cv_std": {"balanced_accuracy": 0.03},
            "test": {"balanced_accuracy": 0.67},
        },
    ]


def assert_rep_leaderboard_csv_escapes(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    rows = _demo_rows()
    csv_text = leaderboard_to_csv(rows)
    for ch in ("'=evil", "'+leader"):
        if ch not in csv_text:
            raise ValueError(f"REP.T.LEADERBOARD: CSV must SEC-04 escape triggers, missing {ch!r}")
    return {"format": "csv", "byte_len": len(csv_text.encode("utf-8")), "seed": seed}


def assert_rep_leaderboard_xlsx_escapes(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    data = leaderboard_to_xlsx_bytes(_demo_rows())
    if not data.startswith(b"PK"):
        raise ValueError("REP.T.LEADERBOARD: XLSX must be a zip (PK header)")
    with zipfile.ZipFile(BytesIO(data)) as zf:
        sheet_xml = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")
    for raw in ("=evil", "+leader"):
        escaped = escape_formula_export_cell(raw)
        if escaped not in sheet_xml:
            raise ValueError(f"REP.T.LEADERBOARD: XLSX sheet must contain escaped {escaped!r}")
    return {"format": "xlsx", "byte_len": len(data), "seed": seed}


def assert_leaderboard_export_contract(*, seed: int = LAB_DEFAULT_SEED) -> list[dict[str, object]]:
    return [
        assert_rep_leaderboard_csv_escapes(seed=seed),
        assert_rep_leaderboard_xlsx_escapes(seed=seed),
    ]


def build_leaderboard_export_manifest(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    checks = assert_leaderboard_export_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "seed": seed,
        "formats": ["csv", "xlsx"],
        "checks": checks,
    }