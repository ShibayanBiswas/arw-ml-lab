# Phase oneshot-c156 — OPS.PREDICTION.RETENTION

## Built
- `labcore/ops/prediction_retention_contract.py` — **ST-OPS-07** contract: `prediction_jobs.expires_at` (30 days), `expired_prediction_jobs()`, maintenance Storage purge before DELETE, `prediction_results` cap 1 000; artefact **`OPS.PREDICTION.RETENTION`**, seed **42**.
- `tests/unit/test_ops_prediction_retention_contract.py` — kit scanner + negative maintenance fixture.
- `docs/STRESS_TEST.md` — **ST-OPS-07** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_prediction_retention_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 6 passed in 3.63s ==============================
```

## Notes
- Closes **ST-OPS-07** (Medium) offline — builds on c110 worker purge and c155 `lab-beat`; live Supabase Storage purge proof stays Phase 8.2.
- Distinct from oneshot-c155 **OPS.LAB_BEAT** (**ST-OPS-05**), oneshot-c154 **OPS.JOB.RELIABILITY** (**ST-OPS-03**), oneshot-c152 **SEC.MODEL.LOAD** (**ST-SEC-06**).
- Seed **42**; no Contabo / NVIDIA / TradingLab / Actions billing.

## Self-check (CURSOR_PROMPT §000)
- [x] Contract reads real migrations and `maintenance.py`; no fabricated purge metrics.
- [x] Import allowlist green.
- [x] Rule 70: stdlib-only in new `labcore` module.