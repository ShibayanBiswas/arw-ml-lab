"""Deploy ordering contract (ARCHITECTURE §46.2 OPS-11 / ST-OPS-04).

Schema migrations must finish before application images roll out. On Render,
``autoDeployTrigger`` must stay ``off`` so ``deploy.yml`` is the only deploy
path. On Contabo, ``deploy`` still ``needs: [migrate, build]`` then ``smoke``.
"""

from __future__ import annotations

import re
from pathlib import Path

ARTEFACT_ID = "OPS.DEPLOY.ORDERING"
RENDER_FORBIDDEN_CHECKS_PASS = "checksPass"
DEPLOY_NEEDS_MIGRATE_BUILD = re.compile(
    r"^\s+needs:\s*\[migrate,\s*build\]",
    re.MULTILINE,
)
SMOKE_NEEDS_DEPLOY = re.compile(r"^\s+needs:\s*deploy\b", re.MULTILINE)
MIGRATE_JOB = re.compile(r"^\s+migrate:\s*$", re.MULTILINE)
DEPLOY_JOB = re.compile(r"^\s+deploy:\s*$", re.MULTILINE)
DB_PUSH_REMOTE = re.compile(r"supabase db push --remote", re.MULTILINE)


class DeployOrderingContractError(ValueError):
    """Raised when deploy ordering violates ST-OPS-04 / OPS-11."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_render_auto_deploy_off(render_path: Path | None = None) -> dict[str, str]:
    """Every Render service with ``autoDeployTrigger`` must set it to ``off``."""
    path = render_path or (_repo_root() / "render.yaml")
    if not path.is_file():
        msg = f"render.yaml missing: {path}"
        raise DeployOrderingContractError(msg)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if RENDER_FORBIDDEN_CHECKS_PASS in text:
        errors.append('render.yaml: must not use autoDeployTrigger "checksPass" (ST-OPS-04)')
    triggers = list(re.finditer(r"autoDeployTrigger:\s*[\"']?(\w+)", text))
    if not triggers:
        errors.append("render.yaml: expected autoDeployTrigger on web/worker services")
    for match in triggers:
        value = match.group(1)
        if value != "off":
            errors.append(f"render.yaml: autoDeployTrigger must be off, got {value!r}")
    if errors:
        raise DeployOrderingContractError("; ".join(errors))
    return {
        "blueprint": path.name,
        "auto_deploy_services": str(len(triggers)),
        "policy": "off",
    }


def assert_deploy_workflow_ordering(
    workflow_path: Path | None = None,
) -> dict[str, str]:
    """``deploy.yml``: migrate → deploy (after build) → smoke."""
    path = workflow_path or (_repo_root() / ".github" / "workflows" / "deploy.yml")
    if not path.is_file():
        msg = f"deploy workflow missing: {path}"
        raise DeployOrderingContractError(msg)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not MIGRATE_JOB.search(text):
        errors.append("deploy.yml: missing migrate job")
    if not DEPLOY_JOB.search(text):
        errors.append("deploy.yml: missing deploy job")
    if not DEPLOY_NEEDS_MIGRATE_BUILD.search(text):
        errors.append("deploy.yml: deploy job must needs: [migrate, build]")
    if not SMOKE_NEEDS_DEPLOY.search(text):
        errors.append("deploy.yml: smoke job must needs: deploy")
    if not DB_PUSH_REMOTE.search(text):
        errors.append("deploy.yml: migrate must run supabase db push --remote")
    if errors:
        raise DeployOrderingContractError("; ".join(errors))
    return {
        "workflow": path.name,
        "order": "migrate → build → deploy → smoke",
    }


def assert_deploy_ordering_contract(
    *,
    render_path: Path | None = None,
    workflow_path: Path | None = None,
) -> list[dict[str, str]]:
    """Run all ST-OPS-04 deploy-ordering checks."""
    return [
        assert_render_auto_deploy_off(render_path),
        assert_deploy_workflow_ordering(workflow_path),
    ]


def deploy_ordering_manifest(*, seed: int = 42) -> dict[str, object]:
    checks = assert_deploy_ordering_contract()
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "stress_id": "ST-OPS-04",
        "ops_rule": "OPS-11",
        "checks": checks,
    }