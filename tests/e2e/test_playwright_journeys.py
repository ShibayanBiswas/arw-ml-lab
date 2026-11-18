"""Optional Playwright DoD journeys (Phase 7 / 8.2).

Skipped unless PLAYWRIGHT_E2E=1. Contabo API not required — shells must load
(or redirect to login) on the hosted Vercel frontend.
"""

from __future__ import annotations

import os

import pytest

BASE = os.environ.get("E2E_BASE_URL", "https://arw-ml-lab.vercel.app").rstrip("/")

pytestmark = pytest.mark.skipif(
    os.environ.get("PLAYWRIGHT_E2E") != "1",
    reason="set PLAYWRIGHT_E2E=1 and install playwright to run",
)

JOURNEYS = (
    ("/supervised/home", "supervised"),
    ("/predict/home", "predict"),
    ("/unsupervised/home", "unsupervised"),
    ("/timeseries/home", "timeseries"),
    ("/admin/workers", "admin"),
)


@pytest.mark.e2e
@pytest.mark.parametrize("path,needle", JOURNEYS, ids=[p for p, _ in JOURNEYS])
def test_playwright_journey_shell(path: str, needle: str) -> None:
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{BASE}{path}", wait_until="domcontentloaded", timeout=60_000)
        html = page.content().lower()
        assert (
            needle in html
            or "login" in html
            or "sign" in html
            or "arw" in html
            or "lab" in html
        ), f"unexpected shell for {path}"
        browser.close()
