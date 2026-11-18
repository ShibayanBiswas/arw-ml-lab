"""Module journey HTTP smoke (Phase 7 / 8.2) — httpx against hosted Vercel.

Covers DoD journey landing pages without a Contabo API (pages must render shell).
Skipped softly when the frontend is unreachable unless E2E_STRICT=1.
"""

from __future__ import annotations

import os

import httpx
import pytest

BASE = os.environ.get("E2E_BASE_URL", "https://arw-ml-lab.vercel.app").rstrip("/")
STRICT = os.environ.get("E2E_STRICT", "").lower() in {"1", "true", "yes"}

# DoD journeys → module shells that must not 404 on the hosted frontend
JOURNEY_PATHS: tuple[tuple[str, str], ...] = (
    ("Titanic / classification", "/supervised/home"),
    ("California Housing / regression", "/supervised/setup"),
    ("Airline / forecast", "/timeseries/home"),
    ("NIFTY financial", "/supervised/backtest"),
    ("Mall clustering", "/unsupervised/home"),
    ("Prediction Studio", "/predict/home"),
    ("Admin workers", "/admin/workers"),
    ("Reports bundle", "/reports/templates"),
)


def _get(path: str) -> httpx.Response:
    try:
        with httpx.Client(timeout=12.0, follow_redirects=True) as client:
            return client.get(f"{BASE}{path}")
    except (
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.TimeoutException,
        httpx.RemoteProtocolError,
    ) as exc:
        if STRICT:
            raise
        pytest.skip(f"hosted frontend unreachable ({exc.__class__.__name__})")


@pytest.mark.e2e
@pytest.mark.parametrize("label,path", JOURNEY_PATHS, ids=[p for _, p in JOURNEY_PATHS])
def test_journey_module_shell_reachable(label: str, path: str) -> None:
    _ = label
    res = _get(path)
    # Auth may redirect to /login — both are acceptable for shell reachability
    assert res.status_code in {200, 307, 308, 302}, (path, res.status_code)
    if res.status_code == 200:
        body = res.text.lower()
        assert "arw" in body or "lab" in body or "login" in body or "sign" in body
