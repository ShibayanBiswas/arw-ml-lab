# Phase oneshot-c139 — FE.WB.PREDICT_MONITOR_KS

## Built
- `MonitoringDriftPanel` on **Prediction Studio → Monitoring** — calls `POST /api/v1/monitoring/drift/ks` via `runMonitoringKsDrift`; renders per-feature KS statistic, p-value and drift flag; artefact id **`MON.T.KS_DRIFT`** cited in UI.
- `PredictWorkbench` — monitoring mode no longer blocked on model selection; mounts the drift panel directly.
- `frontend/src/lib/api.ts` — `monitoringKsDriftPath` + `runMonitoringKsDrift` client.
- Regression: `tests/unit/test_fe_predict_monitoring_wb.py`; vitest `monitoring-api.test.ts`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_predict_monitoring_wb.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
collected 4 items

tests\unit\test_fe_predict_monitoring_wb.py ...                          [ 75%]
tests\unit\test_import_allowlist.py .                                    [100%]

============================== 4 passed in 9.57s ==============================

cd frontend && pnpm exec vitest run src/lib/monitoring-api.test.ts
 Test Files  1 passed (1)
      Tests  1 passed (1)
```

## Notes
- Distinct from oneshot-c138 **`FE.WB.UNSUP_CLU_KSWEEP_MAP_REACH_KDIST`** (clustering catalogue completion).
- Backend from Phase 7 `labcore.monitoring.ks_drift_report` / `backend/app/routers/monitoring.py`; demo matrices are synthetic (no raw dataset rows in prompts).
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; table values come from API response only.
- [x] Backend report carries `seed: 42` metadata.
- [x] Import allowlist + vitest green.

**Ship commit:** `ac50a59`