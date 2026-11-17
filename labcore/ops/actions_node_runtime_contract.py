"""GitHub Actions must not pin Node-20-era action majors — OPS.ACTIONS.NODE (oneshot-c224)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.ACTIONS.NODE"

# Majors known to still ship on the Node 20 Actions runtime (deprecated).
FORBIDDEN = (
    ("actions/checkout", {1, 2, 3, 4}),
    ("actions/setup-node", {1, 2, 3, 4}),
    ("actions/setup-python", {1, 2, 3, 4, 5}),
    ("docker/login-action", {1, 2, 3}),
    ("docker/setup-buildx-action", {1, 2, 3}),
    ("docker/build-push-action", {1, 2, 3, 4, 5, 6}),
    ("pnpm/action-setup", {1, 2, 3, 4}),
)

_USE_RE = re.compile(
    r"uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@v(\d+)",
)


def assert_actions_off_node20() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2] / ".github" / "workflows"
    hits: list[str] = []
    forbidden_map = {name: majors for name, majors in FORBIDDEN}
    for path in sorted(root.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        for m in _USE_RE.finditer(text):
            action, major_s = m.group(1), m.group(2)
            major = int(major_s)
            banned = forbidden_map.get(action)
            if banned is not None and major in banned:
                hits.append(f"{path.name}: {action}@v{major}")
    if hits:
        raise AssertionError("Node-20-era action pins remain: " + "; ".join(hits))
    return {"id": ARTEFACT_ID, "seed": 42, "hits": 0}


def assert_actions_node_contract() -> dict[str, object]:
    return assert_actions_off_node20()
