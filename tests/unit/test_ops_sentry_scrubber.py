"""OPS.SENTRY.SCRUBBER — Sentry before_send PII scrub (ST-OPS-09 / oneshot-c147)."""

from __future__ import annotations

from labcore.observability.sentry_scrub import REDACTED, scrub_event, scrub_string


def test_scrub_string_masks_email_bearer_and_jwt() -> None:
    s = "contact alice@corp.com token Bearer sk-live-abc eyJhbGciOiJIUzI1NiJ9.a.b"
    out = scrub_string(s)
    assert "alice@corp.com" not in out
    assert "sk-live-abc" not in out
    assert REDACTED in out
    assert "example.invalid" in out


def test_scrub_event_redacts_auth_headers_and_secrets() -> None:
    event = {
        "request": {
            "headers": {
                "Authorization": "Bearer top-secret",
                "Content-Type": "application/json",
            },
            "cookies": "session=evil",
        },
        "extra": {"NVIDIA_API_KEY": "nvkey-123", "note": "reach me@home.io"},
        "user": {"email": "user@example.com", "id": "u1"},
    }
    out = scrub_event(event)
    assert out["request"]["headers"]["Authorization"] == REDACTED
    assert out["request"]["headers"]["Content-Type"] == "application/json"
    assert out["request"]["cookies"] == REDACTED
    assert out["extra"]["NVIDIA_API_KEY"] == REDACTED
    assert "home.io" not in str(out["extra"]["note"])
    assert "user@example.com" not in str(out["user"]["email"])


def test_init_sentry_noop_on_empty_dsn() -> None:
    from backend.app.observability import init_sentry

    init_sentry(dsn="  ", environment="test")


def test_init_sentry_accepts_dsn_when_sdk_present(monkeypatch) -> None:
    calls: list[dict] = []
    fake_sdk = type(
        "S",
        (),
        {
            "init": staticmethod(lambda **kwargs: calls.append(kwargs)),
        },
    )

    import sys

    monkeypatch.setitem(sys.modules, "sentry_sdk", fake_sdk)
    from backend.app.observability import init_sentry

    init_sentry(dsn="https://example@o0.ingest/1", environment="staging")
    assert len(calls) == 1
    assert calls[0]["send_default_pii"] is False
    assert calls[0]["environment"] == "staging"
    assert calls[0]["before_send"].__name__ == "_before_send"