"""Observability wiring for lab-api (OPS-12 / ST-OPS-09)."""

from __future__ import annotations

from typing import Any

from labcore.observability.otel_stub import init_opentelemetry, instrument_fastapi_app
from labcore.observability.sentry_scrub import scrub_event


def _before_send(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
    _ = hint
    return scrub_event(event)


def init_otel(
    *,
    enabled: bool,
    service_name: str,
    otlp_endpoint: str,
    app: Any | None = None,
) -> bool:
    active = init_opentelemetry(
        enabled=enabled,
        service_name=service_name,
        otlp_endpoint=otlp_endpoint,
    )
    if active and app is not None:
        instrument_fastapi_app(app)
    return active


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