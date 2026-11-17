"""OPS.LAB_BEAT — ST-OPS-05 lab-beat cron / compose contract (oneshot-c155)."""

from __future__ import annotations

from pathlib import Path

import pytest

from labcore.ops.lab_beat_contract import (
    ARTEFACT_ID,
    HOURLY_SLEEP_SECONDS,
    MAINTENANCE_CLI,
    LabBeatContractError,
    assert_compose_prod_lab_beat,
    assert_hardening_expired_prediction_jobs,
    assert_lab_beat_contract,
    assert_render_yaml_lab_beat,
    lab_beat_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def test_repo_lab_beat_contract() -> None:
    checks = assert_lab_beat_contract()
    assert len(checks) == 3
    assert checks[0]["command"] == MAINTENANCE_CLI


def test_render_and_compose_individually() -> None:
    render = assert_render_yaml_lab_beat(ROOT / "render.yaml")
    compose = assert_compose_prod_lab_beat(ROOT / "docker-compose.prod.yml")
    assert render["blueprint"] == "render.yaml"
    assert compose["interval_seconds"] == str(HOURLY_SLEEP_SECONDS)


def test_hardening_migration_function() -> None:
    meta = assert_hardening_expired_prediction_jobs()
    assert meta["function"] == "expired_prediction_jobs"


def test_rejects_compose_without_sleep(tmp_path: Path) -> None:
    bad = tmp_path / "docker-compose.prod.yml"
    bad.write_text(
        "services:\n  lab-beat:\n    command: sh -c 'python -m backend.worker.maintenance --all'\n",
        encoding="utf-8",
    )
    with pytest.raises(LabBeatContractError, match="sleep"):
        assert_compose_prod_lab_beat(bad)


def test_manifest_contract_seed_42() -> None:
    manifest = lab_beat_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["maintenance_cli"] == MAINTENANCE_CLI
    assert len(manifest["checks"]) == 3