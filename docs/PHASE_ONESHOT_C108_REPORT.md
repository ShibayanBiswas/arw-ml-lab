# Phase oneshot-c108 — OPS-03 Celery job heartbeat

## Built
- `backend/worker/heartbeat.py` — OPS-03 worker path: `touch_job_heartbeat` updates in-memory `JOB_STORE` and Postgres `jobs.heartbeat_at` every **30 s** via Celery `task_prerun` / `task_postrun` / `task_failure` signals; closes the gap left after oneshot-c101 (reaper-only).
- `backend/app/jobs_store.py` — `touch_heartbeat()` for periodic bumps without progress events.
- `backend/worker/celery_app.py` — imports heartbeat module so signals register on worker boot.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check backend/worker/heartbeat.py backend/worker/celery_app.py backend/app/jobs_store.py tests/unit/test_job_heartbeat.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_job_heartbeat.py tests/unit/test_maintenance.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 15 items

tests\unit\test_job_heartbeat.py .....                                   [ 33%]
tests\unit\test_maintenance.py .........                                 [ 93%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 15 passed in 6.02s ==============================
```

## Notes
- Seed **42** on `HEARTBEAT_SEED` (metadata; aligns with maintenance `MAINTENANCE_SEED`).
- Distinct from c101 (reaper/retention CLI), c106 `DR.P.CUMVAR`, c105 `FS.P.GRID`.
- Next gap: DR biplot / loadings, remaining FS.P.* / CLU·DR plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] psycopg via existing maintenance connect helper (rule 70).
- [x] Import allowlist green; c101 maintenance regression green.