# Phase oneshot-c197 — OPS.WORKER.RECYCLE

## Built
- `labcore/ops/worker_recycle.py` — max_tasks=20, Contabo memory caps (light 1400 / train 3200 MiB), stop_grace 300s.
- `backend/worker/celery_app.py` applies recycle settings from `SERVICE_ROLE`.
- `docker-compose.prod.yml` worker-train `--max-tasks-per-child` aligned to 20.
- `tests/unit/test_ops_worker_recycle.py`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_worker_recycle.py -v --tb=line
============================== 4 passed in 2.37s ==============================
```

## Deviations
None. Contabo/Actions still blocked.

## TODOs
Hosted prove recycle under load on Contabo.
