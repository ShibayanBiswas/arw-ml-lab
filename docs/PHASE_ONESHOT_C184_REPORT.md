# Phase oneshot-c184 — OPS.QUEUE.TIME_LIMITS

## Built
- `labcore/ops/queue_time_limits.py` — §39.3 / OPS-03 soft/hard seconds table + Celery task annotations + `visibility_timeout` floor.
- `labcore/ops/queue_time_limits_contract.py` — offline artefact **`OPS.QUEUE.TIME_LIMITS`**.
- `backend/worker/celery_app.py` — wires `task_annotations` and broker `visibility_timeout`.
- `tests/unit/test_ops_queue_time_limits.py`.
- `docs/STRESS_TEST.md` — **ST-OPS-03** notes time limits + visibility_timeout.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_queue_time_limits.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 4 passed in 4.98s ==============================
```

## Notes
- Seed **42**. SoftTimeLimitExceeded handlers that persist best-so-far remain Phase 8.2 task-body work.
- Contabo / Actions billing still blocked.

## Self-check (CURSOR_PROMPT §000)
- [x] Limits match §39.3 minutes for eda/train/tune/ingest/predict.heavy.
- [x] visibility_timeout > max hard limit.
- [x] Import allowlist green.
