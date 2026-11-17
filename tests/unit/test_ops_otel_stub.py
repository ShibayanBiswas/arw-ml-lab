"""OPS.OTEL.STUB — ST-OPS-09 OpenTelemetry offline stub (oneshot-c158)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI

from labcore.observability.otel_stub import (
    ARTEFACT_ID,
    OtelStubContractError,
    assert_api_txt_opentelemetry_pins,
    init_opentelemetry,
    instrument_fastapi_app,
    otel_stub_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def test_api_txt_pins() -> None:
    pins = assert_api_txt_opentelemetry_pins(ROOT / "backend" / "requirements" / "api.txt")
    assert len(pins) == 3


def test_rejects_missing_pin(tmp_path: Path) -> None:
    bad = tmp_path / "api.txt"
    bad.write_text("fastapi==0.1\n", encoding="utf-8")
    with pytest.raises(OtelStubContractError, match="opentelemetry-sdk"):
        assert_api_txt_opentelemetry_pins(bad)


def test_init_disabled() -> None:
    assert init_opentelemetry(enabled=False, service_name="lab-api") is False


def test_init_enables_console_exporter() -> None:
    active = init_opentelemetry(enabled=True, service_name="test-lab-api", otlp_endpoint="")
    assert active is True
    app = FastAPI()

    assert instrument_fastapi_app(app) is True


def test_manifest_seed_42() -> None:
    manifest = otel_stub_manifest(seed=42)
    assert manifest["id"] == ARTEFACT_ID
    assert manifest["seed"] == 42
    assert len(manifest["pins"]) == 3