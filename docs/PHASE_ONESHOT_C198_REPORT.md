# Phase oneshot-c198 — SEC.RATE.LIMIT + OPS.RESTORE.DRILL

## Built
- `labcore/security/rate_limit_policy.py` — documents slowapi defaults (120/min, healthz 60/min).
- `labcore/ops/restore_drill.py` — offline restore-drill checklist ready until Contabo secrets land.
- Unit tests for both.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_sec_rate_limit.py tests\unit\test_ops_restore_drill.py -v --tb=line
============================= 4 passed in 21.61s ==============================
```

## Deviations
Restore drill **hosted_executed=false** until Contabo + rclone remote available (Blocked).

## TODOs
Execute RD1–RD5 on the VPS; set `hosted_executed=True` in PHASE_8_1_REPORT.
