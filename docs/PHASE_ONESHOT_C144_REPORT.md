# Phase oneshot-c144 — LOAD.P.HEALTHZ_CATALOG

## Built
- `tests/load/locustfile.py` — `LabApiPublicUser` hits `GET /healthz` (asserts `seed` 42) and public catalogue routes; scenario id **`LOAD.P.HEALTHZ_CATALOG`**; no auth headers or POSTs.
- `tests/unit/test_load_locust_api.py` — locust contract + FastAPI mirror of the same paths.
- Removed skipped `tests/load/test_load_placeholder.py`; updated `tests/security/README.md` Locust row.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_load_locust_api.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
collected 3 items
tests\unit\test_load_locust_api.py ..                                    [ 66%]
tests\unit\test_import_allowlist.py .                                    [100%]
======================== 3 passed, 1 warning in 31.72s ========================
```

## Notes
- Chose **Locust public API** over **REP.T.FORMULAS** (formula sheet report not yet wired; load skeleton was deferred at c143).
- Distinct from oneshot-c143 **FE.WB.ADMIN_AUDIT** and c15 frontend-only Locust skeleton.
- Locust headless against a live host remains manual/CI-optional; pytest proves contract offline.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated load metrics; headless p95 not claimed.
- [x] `/healthz` returns `seed: 42`.
- [x] Import allowlist green.

**Ship commit:** (filled after commit)