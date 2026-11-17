"""OPS.DEPLOY.ORDERING — ST-OPS-04 migrate-before-deploy contract (oneshot-c157)."""

from __future__ import annotations

from pathlib import Path

import pytest

from labcore.ops.deploy_ordering_contract import (
    ARTEFACT_ID,
    DeployOrderingContractError,
    assert_deploy_ordering_contract,
    assert_deploy_workflow_ordering,
    assert_render_auto_deploy_off,
    deploy_ordering_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def test_repo_deploy_ordering_contract() -> None:
    checks = assert_deploy_ordering_contract()
    assert len(checks) == 2
    assert checks[0]["policy"] == "off"
    assert "migrate" in checks[1]["order"]


def test_render_and_deploy_individually() -> None:
    render = assert_render_auto_deploy_off(ROOT / "render.yaml")
    workflow = assert_deploy_workflow_ordering(ROOT / ".github" / "workflows" / "deploy.yml")
    assert render["auto_deploy_services"] == "3"
    assert workflow["workflow"] == "deploy.yml"


def test_rejects_checks_pass_autodeploy(tmp_path: Path) -> None:
    bad = tmp_path / "render.yaml"
    bad.write_text(
        'services:\n  - type: web\n    autoDeployTrigger: "checksPass"\n',
        encoding="utf-8",
    )
    with pytest.raises(DeployOrderingContractError, match="checksPass"):
        assert_render_auto_deploy_off(bad)


def test_rejects_deploy_without_migrate_needs(tmp_path: Path) -> None:
    bad = tmp_path / "deploy.yml"
    bad.write_text(
        "jobs:\n  migrate:\n    steps: []\n  deploy:\n    needs: [build]\n  smoke:\n    needs: deploy\n",
        encoding="utf-8",
    )
    with pytest.raises(DeployOrderingContractError, match="needs"):
        assert_deploy_workflow_ordering(bad)


def test_manifest_contract_seed_42() -> None:
    manifest = deploy_ordering_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["stress_id"] == "ST-OPS-04"
    assert len(manifest["checks"]) == 2