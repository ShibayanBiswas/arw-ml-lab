"""OPS.JSON.LOGS — structured logs with job_id/run_id/workspace_id (oneshot-c275)."""

from __future__ import annotations

from labcore.observability.json_logging import (
    ARTEFACT_ID,
    STRESS_ID,
    assert_json_log_shape,
    bind_context,
    clear_context,
    configure_json_logging,
    current_context,
)


def test_bind_context_roundtrip() -> None:
    clear_context()
    bind_context(job_id="j1", run_id="r1", workspace_id="w1")
    ctx = current_context()
    assert ctx == {"job_id": "j1", "run_id": "r1", "workspace_id": "w1"}
    assert assert_json_log_shape(ctx)["ok"] is True
    clear_context()


def test_configure_json_logging_returns_logger() -> None:
    log = configure_json_logging(service="test-lab")
    assert log is not None
    # structlog bound logger or stdlib Logger
    assert hasattr(log, "info")


def test_artefact_ids() -> None:
    assert ARTEFACT_ID == "OPS.JSON.LOGS"
    assert STRESS_ID == "ST-OPS-09"
