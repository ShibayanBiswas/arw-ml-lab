"""Hosted frontend smoke (Phase 7 thin) — httpx, no Playwright browser."""

from __future__ import annotations

import os

import httpx
import pytest

BASE = os.environ.get("E2E_BASE_URL", "https://arw-ml-lab.vercel.app").rstrip("/")
STRICT = os.environ.get("E2E_STRICT", "").lower() in {"1", "true", "yes"}


def _get(path: str, *, follow_redirects: bool = True) -> httpx.Response:
    try:
        with httpx.Client(timeout=45.0, follow_redirects=follow_redirects) as client:
            return client.get(f"{BASE}{path}")
    except (
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.TimeoutException,
    ) as exc:
        if STRICT:
            raise
        pytest.skip(f"hosted frontend unreachable ({exc.__class__.__name__})")


@pytest.mark.e2e
def test_login_page_returns_200() -> None:
    res = _get("/login")
    assert res.status_code == 200, res.status_code
    body = res.text.lower()
    assert "login" in body or "sign" in body or "otp" in body or "magic" in body or "email" in body


@pytest.mark.e2e
def test_root_redirects_or_serves() -> None:
    res = _get("/", follow_redirects=False)
    assert res.status_code in {200, 307, 308, 302}
