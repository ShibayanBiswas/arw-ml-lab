"""DEPLOY_CONTABO §7 must list OPTUNA_STORAGE_URL — OPS.CONTABO.OPTUNA (oneshot-c231)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.CONTABO.OPTUNA"


def assert_contabo_env_optuna() -> dict[str, Any]:
    text = (Path(__file__).resolve().parents[2] / "docs" / "DEPLOY_CONTABO.md").read_text(
        encoding="utf-8"
    )
    section = text.split("## 7. Server env file", 1)[-1].split("## 8.", 1)[0]
    if "OPTUNA_STORAGE_URL" not in section:
        raise AssertionError("DEPLOY_CONTABO §7 must list OPTUNA_STORAGE_URL")
    if "HEALTHCHECK_PING_URL" not in section:
        raise AssertionError("DEPLOY_CONTABO §7 must list HEALTHCHECK_PING_URL")
    return {"id": ARTEFACT_ID, "seed": 42}
