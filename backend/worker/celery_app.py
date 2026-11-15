"""Celery application — all queues from ARCHITECTURE §8 / §45."""

from __future__ import annotations

from celery import Celery

from backend.app.settings import get_settings

settings = get_settings()

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
    ],
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=20,
    task_default_queue="q.demo",
    task_create_missing_queues=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    # Known queue names (ARCHITECTURE §8 + q.predict.heavy + q.demo)
    task_routes={
        "lab.demo.progress": {"queue": "q.demo"},
        "lab.ingest.parse": {"queue": "q.ingest"},
        "lab.ingest.sample": {"queue": "q.ingest"},
        "lab.eda.run": {"queue": "q.eda"},
    },
)
# Expose queue catalogue for workers / docs
celery_app.conf.broker_transport_options = {"queue_order_strategy": "priority"}
celery_app.conf.worker_direct = False
_ = QUEUES  # documented queue set; workers select via -Q
