"""JWT_SECRET must match Vercel BFF and Contabo lab-api — SEC (oneshot-c212).

Offline kit: ``.env.example`` documents a single ``JWT_SECRET`` for both;
``AUTH_MODE=bff`` is the Contabo/Vercel path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "SEC.JWT.PARITY"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_env_example_jwt() -> dict[str, str]:
    text = (_repo_root() / ".env.example").read_text(encoding="utf-8")
    if "JWT_SECRET=" not in text:
        raise AssertionError(".env.example missing JWT_SECRET")
    if "AUTH_MODE=" not in text:
        raise AssertionError(".env.example missing AUTH_MODE")
    return {"env": ".env.example"}


def assert_settings_jwt_fields() -> dict[str, str]:
    src = (_repo_root() / "backend" / "app" / "settings.py").read_text(encoding="utf-8")
    if "jwt_secret" not in src or "JWT_SECRET" not in src:
        raise AssertionError("settings must load JWT_SECRET")
    if "auth_mode" not in src:
        raise AssertionError("settings must load AUTH_MODE")
    return {"settings": "ok"}


def assert_deploy_docs_mention_match() -> dict[str, str]:
    contabo = (_repo_root() / "docs" / "DEPLOY_CONTABO.md").read_text(encoding="utf-8")
    if "JWT_SECRET" not in contabo:
        raise AssertionError("DEPLOY_CONTABO must mention JWT_SECRET parity with Vercel")
    return {"doc": "DEPLOY_CONTABO"}


def jwt_parity_manifest(*, seed: int = 42) -> dict[str, Any]:
    checks = [
        assert_env_example_jwt(),
        assert_settings_jwt_fields(),
        assert_deploy_docs_mention_match(),
    ]
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "rule": "JWT_SECRET identical on Vercel + /opt/arw-ml-lab/.env",
        "checks": checks,
        "hosted_verified": False,
    }


def assert_jwt_parity_contract() -> dict[str, object]:
    return jwt_parity_manifest(seed=42)
