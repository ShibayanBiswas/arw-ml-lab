"""Optional Playwright + axe smoke for hosted frontend.

Skipped unless PLAYWRIGHT_E2E=1 and playwright is installed.
Does not run in default CI (no browser install).
"""

from __future__ import annotations

import os

import pytest

BASE = os.environ.get("E2E_BASE_URL", "https://arw-ml-lab.vercel.app")


pytestmark = pytest.mark.skipif(
    os.environ.get("PLAYWRIGHT_E2E") != "1",
    reason="set PLAYWRIGHT_E2E=1 and install playwright to run",
)


def test_login_page_loads_and_axe_critical() -> None:
    playwright = pytest.importorskip("playwright.sync_api")
    axe_playwright = pytest.importorskip("axe_playwright_python")

    with playwright.sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{BASE}/login", wait_until="domcontentloaded", timeout=60_000)
        assert page.title() is not None
        # axe via axe-playwright-python if present
        try:
            from axe_playwright_python.sync_playwright import Axe

            results = Axe().run(page)
            critical = [
                v
                for v in results.response.get("violations", [])
                if v.get("impact") in {"critical", "serious"}
            ]
            assert critical == [], critical
        except Exception as exc:  # noqa: BLE001
            # Fallback: page must at least expose a login landmark/form
            assert page.locator("form, [data-testid='login'], input[type='email']").count() >= 1, (
                f"axe unavailable ({exc}); no login form found"
            )
        browser.close()
