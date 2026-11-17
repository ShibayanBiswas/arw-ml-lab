"""OPS.CI.SUPABASE_CLI — ST-OPS-10 Supabase CLI pin in GitHub Actions (oneshot-c153)."""

from __future__ import annotations

from pathlib import Path

import pytest

from labcore.ops.ci_supabase_cli_pin import (
    ARTEFACT_ID,
    PINNED_SUPABASE_CLI_VERSION,
    CiSupabaseCliPinError,
    assert_workflows_pin_supabase_cli,
    ci_supabase_cli_manifest,
    scan_workflow_supabase_cli_pins,
)

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_repo_workflows_pin_supabase_cli() -> None:
    pins = assert_workflows_pin_supabase_cli(WORKFLOWS)
    assert len(pins) >= 2
    assert all(p["version"] == PINNED_SUPABASE_CLI_VERSION for p in pins)


def test_scan_ci_and_deploy_yml() -> None:
    ci_pins = scan_workflow_supabase_cli_pins(WORKFLOWS / "ci.yml")
    deploy_pins = scan_workflow_supabase_cli_pins(WORKFLOWS / "deploy.yml")
    assert len(ci_pins) == 1
    assert len(deploy_pins) == 1
    assert ci_pins[0]["version"] == PINNED_SUPABASE_CLI_VERSION


def test_rejects_latest_in_temp_workflow(tmp_path: Path) -> None:
    wf = tmp_path / "bad.yml"
    wf.write_text(
        "jobs:\n  supabase:\n    steps:\n"
        "      - uses: supabase/setup-cli@v1\n"
        "        with: { version: latest }\n",
        encoding="utf-8",
    )
    pins = scan_workflow_supabase_cli_pins(wf)
    assert pins[0]["version"] == "latest"
    with pytest.raises(CiSupabaseCliPinError, match="latest"):
        assert_workflows_pin_supabase_cli(tmp_path)


def test_manifest_contract_seed_42() -> None:
    manifest = ci_supabase_cli_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert manifest["pinned_version"] == PINNED_SUPABASE_CLI_VERSION
    assert manifest["setup_cli_steps"] >= 2