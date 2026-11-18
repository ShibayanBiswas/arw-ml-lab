"""OpenTelemetry offline stub — OPS-12 / ST-OPS-09 (Phase 8.2 hardening).

Configures tracing only when explicitly enabled. Full OTLP/collector wiring is
proved offline via pin contract tests; ``lab-api`` calls ``init_opentelemetry``
from ``backend.app.observability``.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ARTEFACT_ID = "OPS.OTEL.STUB"
_PINNED_PACKAGES: tuple[str, ...] = (
    "opentelemetry-sdk",
    "opentelemetry-instrumentation-fastapi",
    "opentelemetry-instrumentation-celery",
    "opentelemetry-exporter-otlp-proto-http",
)

_PIN_LINE = re.compile(r"^opentelemetry[^\s=]+==", re.MULTILINE)


class OtelStubContractError(ValueError):
    """Raised when OTel pins or stub wiring violate OPS-12."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_api_txt_opentelemetry_pins(api_txt: Path | None = None) -> list[dict[str, str]]:
    path = api_txt or (_repo_root() / "backend" / "requirements" / "api.txt")
    if not path.is_file():
        raise OtelStubContractError(f"api.txt missing: {path}")
    text = path.read_text(encoding="utf-8")
    checks: list[dict[str, str]] = []
    for pkg in _PINNED_PACKAGES:
        if f"{pkg}==" not in text:
            raise OtelStubContractError(f"api.txt: missing pin for {pkg}")
        checks.append({"package": pkg, "requirements": path.name})
    if not _PIN_LINE.search(text):
        raise OtelStubContractError("api.txt: no opentelemetry pins found")
    return checks


def _build_exporter(otlp_endpoint: str) -> Any:
    """OTLP HTTP when endpoint set and exporter pinned; else console spans."""
    endpoint = (otlp_endpoint or "").strip()
    if endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            return OTLPSpanExporter(endpoint=endpoint)
        except Exception:  # noqa: BLE001 — console fallback if exporter missing
            pass
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter

    return ConsoleSpanExporter()


def init_opentelemetry(
    *,
    enabled: bool,
    service_name: str,
    otlp_endpoint: str = "",
) -> bool:
    """Configure a TracerProvider when enabled; return whether tracing is active."""
    if not enabled:
        return False

    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create({"service.name": service_name.strip() or "lab-api"})
    provider = TracerProvider(resource=resource)
    exporter = _build_exporter(otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return True


def instrument_fastapi_app(app: Any) -> bool:
    """Instrument a FastAPI app when a TracerProvider is registered."""
    from opentelemetry import trace
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    if trace.get_tracer_provider().__class__.__name__ == "ProxyTracerProvider":
        return False
    FastAPIInstrumentor.instrument_app(app)
    return True


def instrument_celery() -> bool:
    """Register Celery auto-instrumentation (worker entrypoint, Phase 8.2)."""
    from opentelemetry import trace
    from opentelemetry.instrumentation.celery import CeleryInstrumentor

    if trace.get_tracer_provider().__class__.__name__ == "ProxyTracerProvider":
        return False
    CeleryInstrumentor().instrument()
    return True


def otel_stub_manifest(*, seed: int = 42) -> dict[str, object]:
    return {
        "id": ARTEFACT_ID,
        "seed": seed,
        "pinned_packages": list(_PINNED_PACKAGES),
        "pins": assert_api_txt_opentelemetry_pins(),
    }