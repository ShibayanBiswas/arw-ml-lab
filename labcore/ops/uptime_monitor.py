"""External uptime check contract — DEPLOY_CONTABO §11 (oneshot-c199).

External monitor must hit public ``https://<LAB_API_HOSTNAME>/healthz`` from
*outside* the VPS so a host outage is visible. Offline kit check: runbook +
smoke job + healthz route exist.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.UPTIME.EXTERNAL"
HEALTH_PATH = "/healthz"
_UPTIME_SECTION = re.compile(r"Uptime|UptimeRobot|healthchecks\.io|Uptime Kuma", re.I)
_HEALTHZ = re.compile(r"/healthz")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_uptime_runbook(doc_path: Path | None = None) -> dict[str, str]:
    path = doc_path or (_repo_root() / "docs" / "DEPLOY_CONTABO.md")
    text = path.read_text(encoding="utf-8")
    if "## 11." not in text and "Uptime" not in text:
        raise AssertionError("DEPLOY_CONTABO must document uptime monitoring")
    section = text
    if "## 11." in text:
        section = text.split("## 11.", 1)[1].split("## 12.", 1)[0]
    if not _UPTIME_SECTION.search(section):
        raise AssertionError("§11 must name an external uptime provider")
    if not _HEALTHZ.search(section):
        raise AssertionError("§11 must monitor /healthz")
    if "outside" not in section.lower() and "external" not in section.lower():
        raise AssertionError("monitor must run outside the VPS")
    return {"runbook": path.name, "path": HEALTH_PATH}


def assert_smoke_healthz(workflow_path: Path | None = None) -> dict[str, str]:
    path = workflow_path or (_repo_root() / ".github" / "workflows" / "deploy.yml")
    text = path.read_text(encoding="utf-8")
    if "healthz" not in text:
        raise AssertionError("deploy.yml smoke must curl /healthz")
    return {"workflow": path.name, "check": "healthz"}


def uptime_manifest(*, seed: int = 42, hosted_configured: bool = False) -> dict[str, Any]:
    checks = [assert_uptime_runbook(), assert_smoke_healthz()]
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "health_path": HEALTH_PATH,
        "interval_hint": "1 min",
        "checks": checks,
        "hosted_configured": hosted_configured,
        "status": "ready_offline" if not hosted_configured else "configured",
    }


def assert_uptime_contract() -> dict[str, object]:
    return uptime_manifest(seed=42, hosted_configured=False)
