"""Sentry wiring for lab-api (OPS-12 / ST-OPS-09)."""

from __future__ import annotations

from typing import Any

from labcore.observability.sentry_scrub import scrub_event


def _before_send(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
    _ = hint
    return scrub_event(event)


def init_sentry(*, dsn: str, environment: str) -> None:
    if not dsn.strip():
        return

    import sentry_sdk  # pinned in backend/requirements/api.txt; lazy for local dev venv

    sentry_sdk.init(
        dsn=dsn.strip(),
        environment=environment or "development",
        send_default_pii=False,
        before_send=_before_send,
    )