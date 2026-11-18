# Phase oneshot-c275 — JSON logs + OTLP + Celery OTel

## Built
- `labcore/observability/json_logging.py` (OPS.JSON.LOGS): structlog JSON + ContextVar `job_id` / `run_id` / `workspace_id`.
- OTel: pin `opentelemetry-exporter-otlp-proto-http==1.45.2`; OTLP HTTP exporter when endpoint set, else console; `instrument_celery()` from `celery_app.py`.
- Locks recompiled (api, worker-light, worker-train). §44 matrix row added.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_ops_otel_stub.py tests/unit/test_ops_json_logging.py -q --tb=short
.........                                                                [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing; Actions billing still kills CI in ~2s. Live OTLP collector prove stays hosted.
