"""AUTH_TEST_BYPASS must be false in Contabo prod — SEC (oneshot-c218)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "SEC.AUTH.BYPASS"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_env_example_bypass_false() -> dict[str, str]:
    text = (_repo_root() / ".env.example").read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.strip().startswith("AUTH_TEST_BYPASS")]
    if not lines:
        raise AssertionError(".env.example must document AUTH_TEST_BYPASS")
    if "=true" in lines[0].lower().replace(" ", ""):
        raise AssertionError("AUTH_TEST_BYPASS must default false in .env.example")
    return {"env": lines[0].strip()}


def assert_deploy_contabo_mentions_bypass() -> dict[str, str]:
    text = (_repo_root() / "docs" / "DEPLOY_CONTABO.md").read_text(encoding="utf-8")
    if "AUTH_TEST_BYPASS=false" not in text:
        raise AssertionError("DEPLOY_CONTABO must set AUTH_TEST_BYPASS=false for prod")
    return {"doc": "DEPLOY_CONTABO"}


def assert_compose_prod_bypass_false() -> dict[str, str]:
    text = (_repo_root() / "docker-compose.prod.yml").read_text(encoding="utf-8")
    if "AUTH_TEST_BYPASS: \"false\"" not in text and "AUTH_TEST_BYPASS=false" not in text:
        raise AssertionError("docker-compose.prod.yml must force AUTH_TEST_BYPASS=false")
    return {"compose": "AUTH_TEST_BYPASS=false"}


def auth_bypass_manifest(*, seed: int = 42) -> dict[str, Any]:
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "checks": [
            assert_env_example_bypass_false(),
            assert_deploy_contabo_mentions_bypass(),
            assert_compose_prod_bypass_false(),
        ],
    }


def assert_auth_bypass_contract() -> dict[str, object]:
    return auth_bypass_manifest(seed=42)
