# Phase oneshot-c147 — OPS.SENTRY.SCRUBBER

## Built
- `labcore/observability/sentry_scrub.py` — pure `before_send` scrubber: auth headers, cookies, secret-like keys, email / Bearer / JWT-shaped substrings (`[REDACTED]`).
- `backend/app/observability.py` — `init_sentry` with `send_default_pii=False`, lazy `sentry_sdk` import (api image pin).
- `backend/app/settings.py` — `SENTRY_DSN`, `SENTRY_ENVIRONMENT`; `main.py` lifespan calls `init_sentry`.
- `docs/STRESS_TEST.md` — **ST-OPS-09** → `fixed + tested (Sentry scrubber; OTel traces Phase 8.2)`.
- `pyproject.toml` dev extra — `sentry-sdk==2.75.0` for local pytest parity with `api.txt`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_sentry_scrubber.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 5 passed in 3.15s ==============================
```

## Notes
- Closes **ST-OPS-09** (Medium) offline; OpenTelemetry FastAPI/Celery wiring remains Phase 8.2.
- Distinct from oneshot-c146 **REP.T.FORMULAS** (KaTeX formula sheet reports).
- Distinct from oneshot-c145 **SEC.ZAP.BASELINE** (OWASP ZAP configs only).
- Seed **42** unchanged (global `LAB_DEFAULT_SEED`); no Contabo / NVIDIA / TradingLab.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated Sentry events; scrubber tested on synthetic dicts only.
- [x] Import allowlist green.
- [x] Rule 70: `sentry_sdk` already in `backend/requirements/api.txt`.

**Ship commit:** `676e0c1`