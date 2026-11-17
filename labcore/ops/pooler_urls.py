"""Supabase pooler URL matrix — §39 / Phase 8.2 (oneshot-c202).

API → transaction pooler (``DATABASE_URL``).
Workers / Optuna / MLflow → session/direct (``DATABASE_URL_SESSION``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.POOLER.URLS"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_env_example_poolers(path: Path | None = None) -> dict[str, str]:
    p = path or (_repo_root() / ".env.example")
    text = p.read_text(encoding="utf-8")
    if "DATABASE_URL=" not in text:
        raise AssertionError(".env.example missing DATABASE_URL")
    if "DATABASE_URL_SESSION=" not in text:
        raise AssertionError(".env.example missing DATABASE_URL_SESSION")
    if "transaction" not in text.lower():
        raise AssertionError(".env.example must document transaction mode for DATABASE_URL")
    if "session" not in text.lower():
        raise AssertionError(".env.example must document session/direct for DATABASE_URL_SESSION")
    return {"file": p.name}


def assert_settings_fields(settings_src: str | None = None) -> dict[str, str]:
    src = settings_src or (_repo_root() / "backend" / "app" / "settings.py").read_text(
        encoding="utf-8"
    )
    if "DATABASE_URL" not in src or "DATABASE_URL_SESSION" not in src:
        raise AssertionError("settings.py must define both pooler URL fields")
    return {"module": "backend.app.settings"}


def assert_compose_worker_session(compose_src: str | None = None) -> dict[str, str]:
    src = compose_src or (_repo_root() / "docker-compose.prod.yml").read_text(encoding="utf-8")
    # Workers should receive both; Optuna uses session URL when set
    if "DATABASE_URL" not in src:
        raise AssertionError("compose must pass DATABASE_URL")
    if "DATABASE_URL_SESSION" not in src and "database_url_session" not in src.lower():
        # Accept x-app-env anchor listing — check .env is mounted
        if "env_file" not in src and ".env" not in src:
            raise AssertionError("compose must load .env with both pooler URLs")
    return {"compose": "docker-compose.prod.yml"}


def pooler_manifest(*, seed: int = 42) -> dict[str, Any]:
    checks = [
        assert_env_example_poolers(),
        assert_settings_fields(),
        assert_compose_worker_session(),
    ]
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "api": "DATABASE_URL (transaction)",
        "workers": "DATABASE_URL_SESSION (session/direct)",
        "checks": checks,
    }


def assert_pooler_contract() -> dict[str, object]:
    return pooler_manifest(seed=42)
