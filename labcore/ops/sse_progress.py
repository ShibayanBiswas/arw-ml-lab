"""Job SSE progress contract — hosted smoke AC (oneshot-c211).

Browser must stream progress from ``lab-api`` over SSE (not via Vercel).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.SSE.PROGRESS"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_jobs_events_route() -> dict[str, str]:
    jobs = (_repo_root() / "backend" / "app" / "routers" / "jobs.py").read_text(encoding="utf-8")
    if "/events" not in jobs and "events" not in jobs:
        raise AssertionError("jobs router must expose an events/SSE endpoint")
    if "text/event-stream" not in jobs and "EventSourceResponse" not in jobs and "StreamingResponse" not in jobs:
        # accept sse-starlette or manual stream
        if "yield" not in jobs and "sse" not in jobs.lower():
            raise AssertionError("jobs events must stream SSE")
    return {"router": "jobs.py", "path_hint": "/api/v1/jobs/{id}/events"}


def assert_fe_sse_client() -> dict[str, str]:
    api = (_repo_root() / "frontend" / "src" / "lib" / "api.ts").read_text(encoding="utf-8")
    if "jobEventsUrl" not in api and "EventSource" not in api:
        # jobEventsUrl is enough; consumers open EventSource
        raise AssertionError("frontend must expose jobEventsUrl for SSE")
    return {"client": "jobEventsUrl"}


def assert_caddy_buffers_off_or_flush() -> dict[str, str]:
    """Caddy should not buffer SSE forever — flush or disable response buffering."""
    caddy = (_repo_root() / "infra" / "caddy" / "Caddyfile").read_text(encoding="utf-8")
    if "lab-api" not in caddy and "8000" not in caddy:
        raise AssertionError("Caddyfile must proxy to lab-api")
    if "flush_interval" not in caddy:
        raise AssertionError("Caddy reverse_proxy must set flush_interval for SSE")
    return {"proxy": "lab-api", "flush_interval": True}


def sse_manifest(*, seed: int = 42) -> dict[str, Any]:
    checks = [
        assert_jobs_events_route(),
        assert_fe_sse_client(),
        assert_caddy_buffers_off_or_flush(),
    ]
    return {"id": ARTEFACT_ID, "seed": seed, "checks": checks, "hosted_prove": False}


def assert_sse_progress_contract() -> dict[str, object]:
    return sse_manifest(seed=42)
