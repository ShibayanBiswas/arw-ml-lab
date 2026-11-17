# Phase oneshot-c148 — SEC.EXPORT.FORMULA

## Built
- `labcore/security/formula_escape.py` — shared SEC-04 / PV15 escape (`= + - @` tab CR → leading `'`).
- `labcore/train/export.py`, `labcore/enterprise/audit.py`, `labcore/predict/validate.py` — route all export/escape paths through the helper.
- `docs/STRESS_TEST.md` — **ST-SEC-04** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_sec04_formula_escape.py tests\unit\test_enterprise_audit.py tests\unit\test_import_allowlist.py tests\unit\test_phase2_train.py::test_tuning_presets_and_csv_export tests\unit\test_pv_deepen.py::test_pv15_formula_sanitise -v --tb=short
============================== 18 passed in 8.27s ==============================
```

## Notes
- Closes **ST-SEC-04** (High) offline; audit CSV now escapes every column (not only `detail_json`).
- Distinct from oneshot-c147 **OPS.SENTRY.SCRUBBER**; OpenTelemetry FastAPI/Celery wiring remains Phase 8.2.
- Seed **42** unchanged; no Contabo / NVIDIA / TradingLab.

## Self-check (CURSOR_PROMPT §000)
- [x] Escape oracle covers all SEC-04 trigger prefixes; no fabricated metrics.
- [x] Import allowlist green.
- [x] Rule 70: stdlib-only helper in `labcore/security/`.

**Ship commit:** (filled after commit)