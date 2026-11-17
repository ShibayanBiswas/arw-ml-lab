"""LAB_AUTH_BYPASS / NEXT_PUBLIC_LAB_AUTH_BYPASS must stay false in prod — oneshot-c220."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "SEC.LAB_AUTH.BYPASS"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_env_example_lab_auth_false() -> dict[str, str]:
    text = (_repo_root() / ".env.example").read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.strip().startswith("LAB_AUTH_BYPASS")]
    if not lines:
        raise AssertionError(".env.example must document LAB_AUTH_BYPASS")
    if "=true" in lines[0].lower().replace(" ", ""):
        raise AssertionError("LAB_AUTH_BYPASS must default false in .env.example")
    return {"env": lines[0].strip()}


def assert_deploy_docs_forbid_lab_auth() -> dict[str, str]:
    text = (_repo_root() / "docs" / "DEPLOY.md").read_text(encoding="utf-8")
    if "LAB_AUTH_BYPASS" not in text:
        raise AssertionError("DEPLOY.md must forbid LAB_AUTH_BYPASS in production")
    return {"doc": "DEPLOY.md"}


def assert_no_next_public_lab_auth_default_true() -> dict[str, int]:
    """Frontend env templates must not default NEXT_PUBLIC_LAB_AUTH_BYPASS=true."""
    root = _repo_root()
    hits = 0
    for rel in (
        "frontend/.env.example",
        "frontend/.env.local.example",
        ".env.example",
    ):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for ln in text.splitlines():
            if "NEXT_PUBLIC_LAB_AUTH_BYPASS" in ln and "=true" in ln.lower().replace(" ", ""):
                if ln.strip().startswith("#"):
                    continue
                hits += 1
    if hits:
        raise AssertionError("NEXT_PUBLIC_LAB_AUTH_BYPASS must not default true in env templates")
    return {"bad_defaults": 0}


def lab_auth_bypass_manifest(*, seed: int = 42) -> dict[str, Any]:
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "checks": [
            assert_env_example_lab_auth_false(),
            assert_deploy_docs_forbid_lab_auth(),
            assert_no_next_public_lab_auth_default_true(),
        ],
    }


def assert_lab_auth_bypass_contract() -> dict[str, object]:
    return lab_auth_bypass_manifest(seed=42)
