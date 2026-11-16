"""E2E smoke placeholder — Playwright suite expands in Phase 7."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Playwright e2e lands in Phase 7")
def test_playwright_suite_pending() -> None:
    raise AssertionError("pending Phase 7")
