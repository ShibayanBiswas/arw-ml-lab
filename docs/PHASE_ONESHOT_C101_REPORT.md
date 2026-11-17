# Phase oneshot-c101 — OPS-03 lab-beat maintenance (reaper + retention)

## Built
- `backend/worker/maintenance.py` — Postgres-backed §46.2 OPS-03 stale-heartbeat reaper (`jobs.heartbeat_at` / `started_at` fallback), OPS-07 `prediction_jobs` expiry deletes via `expires_at`, OPS-06 trim of `prediction_results` beyond 1 000 rows per job; psycopg when `DATABASE_URL` is up, in-memory `JOB_STORE` / `MODEL_STORE` fallback for local dev.
- `backend/app/jobs_store.py` — `heartbeat_at` on `JobRecord`, bumped on progress/running updates (demo path aligned with OPS-03).
- `backend/app/model_store.py` — `created_at` on `StoredModel` for dev retention tests.
- `tests/unit/test_maintenance.py` — memory reaper/retention, mocked Postgres reaper, SQL contract checks, CLI smoke.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check backend/worker/maintenance.py backend/app/jobs_store.py backend/app/model_store.py tests/unit/test_maintenance.py
# All checks passed

.\.venv\Scripts\python.exe -m pytest tests/unit/test_maintenance.py tests/unit/test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 10 items

tests\unit\test_maintenance.py .........                                 [ 90%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 10 passed in 0.35s ==============================
```

## Notes
- Seed 42 recorded in `run_all()` payload (`MAINTENANCE_SEED`).
- Supabase Storage object deletion for expired `predictions/` paths remains worker-side (8.2-cont); DB rows are purged here.
- Celery worker periodic heartbeat writes to `jobs.heartbeat_at` (full OPS-03 closure) still TODO in task base — schema + reaper ready.
- Next gap: worker heartbeat task, `FS.P.GRID`, remaining FS.P.* / CLU·DR·ANO plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] psycopg only (pinned `api.txt` / rule 70).
- [x] Import allowlist green.