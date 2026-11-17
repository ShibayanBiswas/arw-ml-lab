"""Maintenance uses DATABASE_URL_SESSION when set (oneshot-c207)."""

from pathlib import Path

SRC = Path("backend/worker/maintenance.py")


def test_maintenance_prefers_session_dsn() -> None:
    text = SRC.read_text(encoding="utf-8")
    assert "database_url_session" in text
    assert "database_url" in text
