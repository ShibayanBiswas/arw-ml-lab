"""lab-beat deployment contract (ARCHITECTURE §39.3 / §46.2 OPS / ST-OPS-05).

Retention cleanup and the stale-heartbeat reaper must run hourly via
``python -m backend.worker.maintenance --all`` on Render (cron) and Contabo
(compose loop). Postgres exposes ``expired_prediction_jobs()`` for retention.
"""

from __future__ import annotations

import re
from pathlib import Path

ARTEFACT_ID = "OPS.LAB_BEAT"
MAINTENANCE_MODULE = "backend.worker.maintenance"
MAINTENANCE_CLI = f"python -m {MAINTENANCE_MODULE} --all"
HOURLY_SLEEP_SECONDS = 3600
LAB_BEAT_SERVICE_NAME = "lab-beat"

_RENDER_LAB_BEAT_BLOCK = re.compile(
    r"-\s+type:\s+cron\s*\n\s+name:\s+lab-beat\b",
    re.MULTILINE,
)
_RENDER_DOCKER_CMD = re.compile(
    r"dockerCommand:\s*python -m backend\.worker\.maintenance --all",
)
_RENDER_SCHEDULE = re.compile(r'schedule:\s*["\']?[^\s"\']+', re.MULTILINE)

_COMPOSE_LAB_BEAT = re.compile(r"^\s+lab-beat:\s*$", re.MULTILINE)
_COMPOSE_MAINTENANCE = re.compile(
    r"python -m backend\.worker\.maintenance --all",
)
_COMPOSE_SLEEP = re.compile(r"sleep\s+3600")

_EXPIRED_FN = re.compile(
    r"create or replace function public\.expired_prediction_jobs\(\)",
    re.IGNORECASE,
)


class LabBeatContractError(ValueError):
    """Raised when a deployment file violates the ST-OPS-05 lab-beat contract."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_render_yaml_lab_beat(render_path: Path | None = None) -> dict[str, str]:
    """Verify ``render.yaml`` defines the hourly ``lab-beat`` cron with ``--all``."""
    path = render_path or (_repo_root() / "render.yaml")
    if not path.is_file():
        msg = f"render.yaml missing: {path}"
        raise LabBeatContractError(msg)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not _RENDER_LAB_BEAT_BLOCK.search(text):
        errors.append("render.yaml: missing cron service lab-beat")
    if not _RENDER_DOCKER_CMD.search(text):
        errors.append(f"render.yaml: lab-beat must use {MAINTENANCE_CLI!r}")
    if not _RENDER_SCHEDULE.search(text):
        errors.append("render.yaml: lab-beat must declare an hourly schedule")
    if errors:
        raise LabBeatContractError("; ".join(errors))
    return {"blueprint": path.name, "command": MAINTENANCE_CLI}


def assert_compose_prod_lab_beat(compose_path: Path | None = None) -> dict[str, str]:
    """Verify ``docker-compose.prod.yml`` runs maintenance hourly in ``lab-beat``."""
    path = compose_path or (_repo_root() / "docker-compose.prod.yml")
    if not path.is_file():
        msg = f"docker-compose.prod.yml missing: {path}"
        raise LabBeatContractError(msg)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not _COMPOSE_LAB_BEAT.search(text):
        errors.append("docker-compose.prod.yml: missing lab-beat service")
    if not _COMPOSE_MAINTENANCE.search(text):
        errors.append(f"compose: lab-beat must invoke {MAINTENANCE_CLI!r}")
    if not _COMPOSE_SLEEP.search(text):
        errors.append(f"compose: lab-beat loop must sleep {HOURLY_SLEEP_SECONDS}")
    if errors:
        raise LabBeatContractError("; ".join(errors))
    return {
        "compose": path.name,
        "command": MAINTENANCE_CLI,
        "interval_seconds": str(HOURLY_SLEEP_SECONDS),
    }


def assert_hardening_expired_prediction_jobs(
    migration_path: Path | None = None,
) -> dict[str, str]:
    """Verify the hardening migration defines ``expired_prediction_jobs()`` (ST-OPS-05)."""
    root = _repo_root()
    path = migration_path or (
        root / "supabase" / "migrations" / "20261115000100_hardening.sql"
    )
    if not path.is_file():
        msg = f"hardening migration missing: {path}"
        raise LabBeatContractError(msg)
    text = path.read_text(encoding="utf-8")
    if not _EXPIRED_FN.search(text):
        msg = f"{path.name}: missing function expired_prediction_jobs()"
        raise LabBeatContractError(msg)
    return {"migration": path.name, "function": "expired_prediction_jobs"}


def assert_lab_beat_contract(
    *,
    render_path: Path | None = None,
    compose_path: Path | None = None,
    migration_path: Path | None = None,
) -> list[dict[str, str]]:
    """Run all ST-OPS-05 lab-beat deployment checks."""
    return [
        assert_render_yaml_lab_beat(render_path),
        assert_compose_prod_lab_beat(compose_path),
        assert_hardening_expired_prediction_jobs(migration_path),
    ]


def lab_beat_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_lab_beat_contract()
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "service": LAB_BEAT_SERVICE_NAME,
        "maintenance_cli": MAINTENANCE_CLI,
        "hourly_sleep_seconds": HOURLY_SLEEP_SECONDS,
        "checks": checks,
    }