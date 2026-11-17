# Phase oneshot-c186 — OPS.SOFT.TIME_LIMIT

## Built
- `labcore/ops/soft_time_limit.py` — truncated best-so-far payload + `save_best_so_far` + SoftTimeLimitExceeded detector.
- `labcore/ops/soft_time_limit_contract.py` — offline artefact **`OPS.SOFT.TIME_LIMIT`**.
- `backend/worker/tasks/train.py` — catches soft limit and persists truncated result instead of failing hard.
- `tests/unit/test_ops_soft_time_limit.py`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_soft_time_limit.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 2 passed in 1.66s ==============================
```

## Notes
- Seed **42**. Contabo / Actions billing still blocked.
- Tune/predict soft-limit wiring can mirror the same helper later.

## Self-check (CURSOR_PROMPT §000)
- [x] Soft limit → truncated=True payload, job marked done.
- [x] Train task imports helper.
- [x] Import allowlist green.
