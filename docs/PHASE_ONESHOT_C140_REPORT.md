# Phase oneshot-c140 — FE.WB.PREDICT_MONITOR_PSI

## Built
- `labcore.monitoring.psi_drift_report` — per-feature PSI on reference quantile bins (reuses `labcore.intake.d8_drift._psi`); artefact id **`MON.T.PSI_DRIFT`**, amber/red flags, `drift` when PSI > threshold (default 0.2).
- `POST /api/v1/monitoring/drift/psi` on `backend/app/routers/monitoring.py`.
- `MonitoringDriftPanel` — second section for PSI beside KS (c139); `runMonitoringPsiDrift` in `frontend/src/lib/api.ts`.
- Regression: `tests/unit/test_drift_psi.py`; extended `test_fe_predict_monitoring_wb.py`; vitest `monitoring-api.test.ts`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_drift_psi.py tests\unit\test_drift_ks.py tests\unit\test_fe_predict_monitoring_wb.py tests\unit\test_import_allowlist.py -v --tb=short
============================= test session starts =============================
collected 10 items
tests\unit\test_drift_psi.py ..                                          [ 20%]
tests\unit\test_drift_ks.py ..                                           [ 40%]
tests\unit\test_fe_predict_monitoring_wb.py .....                        [ 90%]
tests\unit\test_import_allowlist.py .                                    [100%]
============================= 10 passed in 47.31s =============================

cd frontend && pnpm exec vitest run src/lib/monitoring-api.test.ts
 Test Files  1 passed (1)
      Tests  2 passed (2)
```

## Notes
- Distinct from oneshot-c139 **`FE.WB.PREDICT_MONITOR_KS`** (KS p-value lane); pairs with ARCHITECTURE PV11 / D8 PSI thresholds.
- Demo matrices unchanged (synthetic 40×3); no raw dataset rows in FE.
- No Contabo changes.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; table values come from API response only.
- [x] Backend report carries `seed: 42` metadata.
- [x] Import allowlist + vitest green.

**Ship commit:** `264a556`