# Phase oneshot-c187 — OPS.SOFT.TIME_LIMIT (tune)

## Built
- `backend/worker/tasks/tune.py` — soft time-limit → `save_best_so_far` (mirrors train).
- `labcore/ops/soft_time_limit_contract.py` — asserts tune task wiring (5 checks).

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_soft_time_limit.py -v --tb=short
============================== 1 passed in 0.23s ==============================
```

## Notes
- Seed **42**. Contabo still blocked.

## Self-check
- [x] Tune task catches SoftTimeLimitExceeded via shared helper.
