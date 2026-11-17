"""Supabase CLI pin contract for GitHub Actions (ARCHITECTURE §46.2 / ST-OPS-10).

CI and deploy workflows must pin ``supabase/setup-cli`` to a semver — never
``latest`` — so a surprise CLI release cannot break migrations or pgTAP.
"""

from __future__ import annotations

import re
from pathlib import Path

ARTEFACT_ID = "OPS.CI.SUPABASE_CLI"
PINNED_SUPABASE_CLI_VERSION = "3.1.0"

_SETUP_CLI_STEP = re.compile(
    r"^\s*-\s+uses:\s+supabase/setup-cli@",
    re.MULTILINE,
)
_VERSION_INLINE = re.compile(
    r'version:\s*["\']?([^"\'\s#]+)',
)
_VERSION_FLOW = re.compile(
    r"^\s+version:\s*[\"']?([^\"'\s#]+)",
    re.MULTILINE,
)


class CiSupabaseCliPinError(ValueError):
    """Raised when a workflow violates the ST-OPS-10 Supabase CLI pin contract."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _extract_setup_cli_version(step_block: str) -> str | None:
    for pattern in (_VERSION_INLINE, _VERSION_FLOW):
        match = pattern.search(step_block)
        if match:
            return match.group(1).strip().strip("\"'")
    return None


def scan_workflow_supabase_cli_pins(
    workflow_path: Path,
    *,
    expected_version: str = PINNED_SUPABASE_CLI_VERSION,
) -> list[dict[str, str]]:
    """Return each ``supabase/setup-cli`` step and its declared version in one workflow file."""
    text = workflow_path.read_text(encoding="utf-8")
    pins: list[dict[str, str]] = []
    for match in _SETUP_CLI_STEP.finditer(text):
        start = match.start()
        next_step = text.find("\n      - uses:", start + 1)
        block = text[start : next_step if next_step != -1 else len(text)]
        version = _extract_setup_cli_version(block)
        pins.append(
            {
                "workflow": workflow_path.name,
                "version": version or "<missing>",
                "expected": expected_version,
            }
        )
    return pins


def assert_workflows_pin_supabase_cli(
    workflows_dir: Path | None = None,
    *,
    expected_version: str = PINNED_SUPABASE_CLI_VERSION,
) -> list[dict[str, str]]:
    """Verify every workflow using setup-cli pins ``expected_version`` (not ``latest``)."""
    root = workflows_dir or (_repo_root() / ".github" / "workflows")
    if not root.is_dir():
        msg = f"workflows directory missing: {root}"
        raise CiSupabaseCliPinError(msg)

    yml_files = sorted(root.glob("*.yml")) + sorted(root.glob("*.yaml"))
    all_pins: list[dict[str, str]] = []
    for path in yml_files:
        pins = scan_workflow_supabase_cli_pins(path, expected_version=expected_version)
        all_pins.extend(pins)

    if not all_pins:
        msg = "no supabase/setup-cli steps found in .github/workflows"
        raise CiSupabaseCliPinError(msg)

    errors: list[str] = []
    for pin in all_pins:
        version = pin["version"]
        if version.lower() == "latest":
            errors.append(f"{pin['workflow']}: version must not be 'latest' (ST-OPS-10)")
        elif version != expected_version:
            errors.append(
                f"{pin['workflow']}: version {version!r} != expected {expected_version!r}"
            )
        elif version == "<missing>":
            errors.append(f"{pin['workflow']}: supabase/setup-cli step missing version pin")

    if errors:
        raise CiSupabaseCliPinError("; ".join(errors))
    return all_pins


def ci_supabase_cli_manifest(*, seed: int = 42) -> dict[str, object]:
    pins = assert_workflows_pin_supabase_cli()
    workflows = sorted({p["workflow"] for p in pins})
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "pinned_version": PINNED_SUPABASE_CLI_VERSION,
        "workflow_count": len(workflows),
        "setup_cli_steps": len(pins),
        "workflows": workflows,
    }