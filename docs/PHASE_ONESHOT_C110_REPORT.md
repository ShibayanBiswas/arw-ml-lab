# Phase oneshot-c110 — ST-OPS-07 prediction storage purge

## Built
- `backend/worker/maintenance.py` — before deleting expired `prediction_jobs` rows, fetch `input_path` / `output_path`, normalize keys under bucket `predictions`, purge via Supabase Storage (service role) or local `.cache/uploads` dev copies; counts `storage_removed` in retention stats (closes c101 TODO for worker-side Storage cleanup).
- `tests/unit/test_maintenance.py` — key normalization, dedupe, Postgres purge order (storage before DELETE), local file removal.

## Tests
```
.\.venv\Scripts\python.exe -m ruff check backend/worker/maintenance.py tests/unit/test_maintenance.py
# All checks passed!

.\.venv\Scripts\python.exe -m pytest tests/unit/test_maintenance.py tests/unit/test_import_allowlist.py tests/unit/test_job_heartbeat.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 20 items

tests\unit\test_maintenance.py ..............                            [ 70%]
tests\unit\test_import_allowlist.py .                                    [ 75%]
tests\unit\test_job_heartbeat.py .....                                   [100%]

============================= 20 passed in 10.02s ==============================
```

## Notes
- Seed **42** unchanged (`MAINTENANCE_SEED` in `run_all()`).
- Distinct from c109 (intended `DR.P.LOADINGS` heatmap + API route — not in this commit), c108 `OPS-03.CELERY_HEARTBEAT`, c101 DB-only retention.
- Uncommitted working-tree edits for DR loadings remain for a separate oneshot-c109 commit.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] `supabase` imported lazily inside purge helper (pinned via `api.txt` / worker `-r api.txt`).
- [x] Import allowlist + c108 heartbeat regression green.