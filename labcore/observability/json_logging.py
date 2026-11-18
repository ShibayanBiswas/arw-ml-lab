"""Structured JSON logs with job_id / run_id / workspace_id — OPS-12 / ST-OPS-09."""

from __future__ import annotations

import logging
from contextvars import ContextVar
from typing import Any

ARTEFACT_ID = "OPS.JSON.LOGS"
STRESS_ID = "ST-OPS-09"

_job_id: ContextVar[str | None] = ContextVar("lab_job_id", default=None)
_run_id: ContextVar[str | None] = ContextVar("lab_run_id", default=None)
_workspace_id: ContextVar[str | None] = ContextVar("lab_workspace_id", default=None)

REQUIRED_KEYS = ("job_id", "run_id", "workspace_id")


def bind_context(
    *,
    job_id: str | None = None,
    run_id: str | None = None,
    workspace_id: str | None = None,
) -> None:
    """Bind correlation ids for the current task/request (ContextVar)."""
    if job_id is not None:
        _job_id.set(job_id)
    if run_id is not None:
        _run_id.set(run_id)
    if workspace_id is not None:
        _workspace_id.set(workspace_id)


def clear_context() -> None:
    _job_id.set(None)
    _run_id.set(None)
    _workspace_id.set(None)


def current_context() -> dict[str, str | None]:
    return {
        "job_id": _job_id.get(),
        "run_id": _run_id.get(),
        "workspace_id": _workspace_id.get(),
    }


class ContextFilter(logging.Filter):
    """Inject job_id / run_id / workspace_id onto every LogRecord."""

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = current_context()
        for key in REQUIRED_KEYS:
            if not hasattr(record, key):
                setattr(record, key, ctx.get(key))
        return True


def configure_json_logging(*, level: int = logging.INFO, service: str = "lab-api") -> Any:
    """Configure logging via structlog JSON renderer (stdlib fallback)."""
    try:
        import structlog

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                _structlog_lab_context,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        return structlog.get_logger(service).bind(service=service)
    except Exception:  # noqa: BLE001 — stdlib JSON-ish fallback
        logger = logging.getLogger(service)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter(
                    '{"service":"%(name)s","level":"%(levelname)s","msg":"%(message)s",'
                    '"job_id":"%(job_id)s","run_id":"%(run_id)s","workspace_id":"%(workspace_id)s"}'
                )
            )
            handler.addFilter(ContextFilter())
            logger.addHandler(handler)
        logger.setLevel(level)
        return logger


def _structlog_lab_context(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    _ = logger, method_name
    ctx = current_context()
    for key in REQUIRED_KEYS:
        event_dict.setdefault(key, ctx.get(key))
    return event_dict


def assert_json_log_shape(payload: dict[str, Any]) -> dict[str, object]:
    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        raise ValueError(f"OPS.JSON.LOGS missing keys: {missing}")
    return {"ok": True, "keys": list(REQUIRED_KEYS)}
