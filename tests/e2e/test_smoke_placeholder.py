"""E2E suite entry — hosted httpx smoke is the thin Phase 7 gate."""

from __future__ import annotations

from pathlib import Path


def test_e2e_suite_has_hosted_smoke() -> None:
    smoke = Path(__file__).with_name("test_hosted_frontend_smoke.py")
    assert smoke.is_file()
    text = smoke.read_text(encoding="utf-8")
    assert "test_login_page_returns_200" in text
