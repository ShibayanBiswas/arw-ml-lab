"""Celery application — all queues from ARCHITECTURE §8 / §45."""

from __future__ import annotations

from celery import Celery

from backend.app.settings import get_settings
from labcore.ops.queue_time_limits import (
    celery_task_annotations,
    visibility_timeout_floor_s,
)
from labcore.ops.worker_recycle import celery_recycle_settings

settings = get_settings()
_RECYCLE = celery_recycle_settings(settings.service_role)

QUEUES = (
    "q.ingest",
    "q.eda",
    "q.train.cpu",
    "q.train.gpu",
    "q.tune",
    "q.explain",
    "q.forecast",
    "q.insights",
    "q.report",
    "q.predict.batch",
    "q.predict.heavy",
    "q.demo",
)

celery_app = Celery(
    "arw_ml_lab",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "backend.worker.tasks.demo",
        "backend.worker.tasks.ingest",
        "backend.worker.tasks.eda",
        "backend.worker.tasks.intake",
        "backend.worker.tasks.train",
        "backend.worker.tasks.tune",
        "backend.worker.tasks.predict",
    ],
)

_TASK_ANNOTATIONS = celery_task_annotations()

_celery_update: dict = {
    "task_acks_late": True,
    "task_reject_on_worker_lost": True,
    "worker_prefetch_multiplier": 1,
    "worker_max_tasks_per_child": int(_RECYCLE["worker_max_tasks_per_child"]),
    "task_default_queue": "q.demo",
    "task_create_missing_queues": True,
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "Asia/Kolkata",
    "enable_utc": True,
    # OPS-03 / §39.3: soft → SoftTimeLimitExceeded; hard → kill
    "task_annotations": _TASK_ANNOTATIONS,
}
if _RECYCLE.get("worker_max_memory_per_child"):
    _celery_update["worker_max_memory_per_child"] = int(_RECYCLE["worker_max_memory_per_child"])
celery_app.conf.update(
    **_celery_update,
    # Known queue names (ARCHITECTURE §8 + q.predict.heavy + q.demo)
    task_routes={
        "lab.demo.progress": {"queue": "q.demo"},
        "lab.ingest.parse": {"queue": "q.ingest"},
        "lab.ingest.sample": {"queue": "q.ingest"},
        "lab.eda.run": {"queue": "q.eda"},
        "lab.train.run": {"queue": "q.train.cpu"},
        "lab.tune.run": {"queue": "q.tune"},
        "lab.predict.batch": {"queue": "q.predict.batch"},
    },
)
# Expose queue catalogue for workers / docs
# OPS-04: visibility_timeout must exceed max hard limit
celery_app.conf.broker_transport_options = {
    "queue_order_strategy": "priority",
    "visibility_timeout": visibility_timeout_floor_s(),
}
celery_app.conf.worker_direct = False
_ = QUEUES  # documented queue set; workers select via -Q

# OPS-03: register heartbeat signal handlers (import side effect).
from backend.worker import heartbeat as _heartbeat  # noqa: E402, F401

_ = _heartbeat.HEARTBEAT_SEED

# OPS-12 / ST-OPS-09: structured logs + Celery OTel when enabled
from labcore.observability.json_logging import configure_json_logging  # noqa: E402

configure_json_logging(service=f"lab-worker-{settings.service_role}")
if settings.otel_enabled:
    from labcore.observability.otel_stub import (  # noqa: E402
        init_opentelemetry,
        instrument_celery,
    )

    init_opentelemetry(
        enabled=True,
        service_name=settings.otel_service_name or f"lab-worker-{settings.service_role}",
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
    )
    instrument_celery()
