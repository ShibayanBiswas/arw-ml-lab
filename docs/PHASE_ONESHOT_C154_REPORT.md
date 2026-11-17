# Phase oneshot-c154 — OPS.JOB.RELIABILITY

## Built
- `labcore/ops/job_reliability_contract.py` — **ST-OPS-03** offline contract: migrations (`jobs` / `prediction_jobs` idempotency + `heartbeat_at`), Celery `acks_late` / `task_reject_on_worker_lost`, 30 s heartbeat and 10 min reaper timing, in-memory idempotency store; artefact **`OPS.JOB.RELIABILITY`**, seed **42**.
- `tests/unit/test_ops_job_reliability_contract.py` — kit scanner + negative Celery ack case.
- `docs/STRESS_TEST.md` — **ST-OPS-03** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_job_reliability_contract.py tests\unit\test_job_heartbeat.py tests\unit\test_maintenance.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 23 passed in 6.04s ==============================
```

## Notes
- Closes **ST-OPS-03** (High) offline — fold/result upserts and broker `visibility_timeout` remain Phase 8.2.
- Distinct from oneshot-c155 **OPS.LAB_BEAT** (**ST-OPS-05**), oneshot-c153 **OPS.CI.SUPABASE_CLI** (**ST-OPS-10**), oneshot-c152 **SEC.MODEL.LOAD** (**ST-SEC-06**).
- Builds on oneshot-c101 (reaper) and c108 (Celery heartbeat); no live Redis/Postgres.
- Seed **42**; no Contabo / NVIDIA / TradingLab.

## Self-check (CURSOR_PROMPT §000)
- [x] Contract reads real repo files; timings match `heartbeat.py` / `maintenance.py`.
- [x] Import allowlist green.
- [x] Rule 70: stdlib-only in new `labcore` module.

**Ship commit:** _(pending)_