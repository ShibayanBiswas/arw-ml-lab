# Phase oneshot-c192 — OPS.MEMORY.ENQUEUE

## Built
- `labcore/ops/memory_enqueue.py` — Contabo 3584 MiB train-worker cap + MI-09 decision helper.
- `backend/app/routers/experiments.py` — HTTP 422 when estimated RAM > 1.2× worker limit (train + tune).
- `tests/unit/test_ops_memory_enqueue.py`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_memory_enqueue.py -v --tb=short
============================== 3 passed in 4.68s ==============================
```

## Notes
- Seed **42**. Contabo / Actions billing still blocked.
