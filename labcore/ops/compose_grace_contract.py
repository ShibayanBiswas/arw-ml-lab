"""docker-compose.prod.yml workers need 300s stop grace — OPS.COMPOSE.GRACE (oneshot-c232)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.COMPOSE.GRACE"


def assert_compose_stop_grace() -> dict[str, Any]:
    text = (Path(__file__).resolve().parents[2] / "docker-compose.prod.yml").read_text(
        encoding="utf-8"
    )
    for svc in ("worker-light:", "worker-train:"):
        if svc not in text:
            raise AssertionError(f"missing service {svc}")
    # Both workers must declare stop_grace_period: 300s (§39.3 / maxShutdownDelaySeconds)
    if text.count("stop_grace_period: 300s") < 2:
        raise AssertionError("worker-light and worker-train need stop_grace_period: 300s")
    return {"id": ARTEFACT_ID, "seed": 42, "stop_grace_period": "300s"}
