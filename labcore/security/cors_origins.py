"""CORS allow-list for Contabo lab-api — SEC-07 (oneshot-c213).

Production must include ``https://arw-ml-lab.vercel.app`` (no trailing slash).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "SEC.CORS.ORIGINS"
PROD_ORIGIN = "https://arw-ml-lab.vercel.app"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_deploy_contabo_cors() -> dict[str, str]:
    text = (_repo_root() / "docs" / "DEPLOY_CONTABO.md").read_text(encoding="utf-8")
    if "CORS_ALLOWED_ORIGINS" not in text:
        raise AssertionError("DEPLOY_CONTABO must document CORS_ALLOWED_ORIGINS")
    if PROD_ORIGIN not in text and "arw-ml-lab.vercel.app" not in text:
        raise AssertionError("DEPLOY_CONTABO must name the Vercel production origin")
    return {"doc": "DEPLOY_CONTABO", "origin": PROD_ORIGIN}


def assert_main_uses_settings_cors() -> dict[str, str]:
    main = (_repo_root() / "backend" / "app" / "main.py").read_text(encoding="utf-8")
    if "cors_allowed_origins" not in main:
        raise AssertionError("main.py must read settings.cors_allowed_origins")
    return {"main": "ok"}


def cors_manifest(*, seed: int = 42) -> dict[str, Any]:
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "production_origin": PROD_ORIGIN,
        "checks": [assert_deploy_contabo_cors(), assert_main_uses_settings_cors()],
    }


def assert_cors_origins_contract() -> dict[str, object]:
    return cors_manifest(seed=42)
