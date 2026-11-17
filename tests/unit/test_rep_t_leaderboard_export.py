"""REP.T.LEADERBOARD — ST-UX-02 leaderboard CSV/XLSX export (oneshot-c177)."""

from __future__ import annotations

from labcore.reports.leaderboard_export import (
    ARTEFACT_ID,
    STRESS_ID,
    build_leaderboard_export_manifest,
)
from labcore.train.export import leaderboard_fieldnames, leaderboard_to_xlsx_bytes


def test_leaderboard_export_manifest_seed_42() -> None:
    manifest = build_leaderboard_export_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["stress_test"] == STRESS_ID
    assert manifest["seed"] == 42
    assert manifest["formats"] == ["csv", "xlsx"]
    assert len(manifest["checks"]) == 2


def test_leaderboard_xlsx_flattens_metrics() -> None:
    rows = [
        {
            "rank": 1,
            "algorithm_key": "clf.logistic",
            "algorithm_id": "C1",
            "name": "Logistic",
            "library": "sklearn",
            "primary_metric": "balanced_accuracy",
            "cv_mean": {"balanced_accuracy": 0.7},
            "cv_std": {"balanced_accuracy": 0.01},
            "test": {"balanced_accuracy": 0.69},
        }
    ]
    fields = leaderboard_fieldnames(rows)
    assert "cv_mean_balanced_accuracy" in fields
    blob = leaderboard_to_xlsx_bytes(rows)
    assert blob[:2] == b"PK"
    assert len(blob) > 100