# Phase 3A report — Prediction Studio thin

**Date:** 2026-11-15 (IST)  
**Commit message target:** `phase 3a: prediction studio thin`

## Built

### Engine (`labcore/predict/`)
- `validate.py` — PV01 (extension), PV04–PV09; PV02/03/10–16 deferred stubs; `ValidationReport.to_dict()`.
- `template.py` — CSV/XLSX templates + sample row from contract; `predictions_to_safe_csv` (SEC-04 via `_safe_cell`).
- Train (`labcore/train/run.py`) — drop identifier-like columns; return `feature_contract`, `feature_names`, `champion_pipeline`.
- Worker train task registers champion into `MODEL_STORE` and sets `result.model_id`.

### API (`backend/app/routers/predict.py`)
- `GET /api/v1/models`, `…/template`, `…/sample-row`
- `POST /api/v1/predict/batch` (JSON), `/upload`, `/sample/{DS3|titanic}`
- Existing single/batch/explain routes kept

### Frontend
- Predict hub mode chooser; `BatchPredictPanel`; `CustomPredictForm` (numeric slider+number, categorical select, boolean; 300 ms debounce; reset; random row; SHAP list when explain works)

## Tests (real output)

```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_predict_samples.py tests/unit/test_phase3a_predict.py -q
.............................................                            [100%]
# 45 passed (38 predict samples + 7 Phase 3A)

.\.venv\Scripts\python.exe -m pytest tests/unit/test_phase3_explain_uq.py -q
.........                                                                [100%]
```

Thin ACs:
- DS3 template round-trip + `titanic_predict.csv` → 0 blocking PVs → scored
- PV04 / PV05 / PV06 / PV08 unit cases
- Single vs batch parity atol 1e-9 on 30 rows
- Feature contract schema-valid after train

## Deviations
- Full §45 / Playwright / 1M Celery chunking deferred to **3A-cont** (ADR-0013), matching thin phases 2/2A/3.
- Sync batch cap 5 000 rows (not 1 000 000).
- Predict home uses `PredictWorkbench` chooser instead of generic `ModuleHub`.

## TODOs (3A-cont)
- Full PV01–PV16, zip/XLSX bombs, Celery chunking + cancel + Idempotency-Key
- DS12/22/18/33 column suites, conformal columns in batch UI
- Playwright + axe; AI prediction prompt; sequential lookback

## Self-verification checklist (§000)
- [x] Phase 3A unit ACs + `test_predict_samples.py` green (commands above)
- [ ] Full `make test` / `make lint` — run in closeout with CI
- [x] No new stub `NotImplementedError` in shipped predict paths (deferred PV codes are explicit `severity=deferred` messages)
- [x] Endpoints align with §45.7 thin subset (aliases kept)
- [x] No secrets in diff
- [x] ADR-0013 + PROGRESS updated
- [ ] Push + Vercel `arw-ml-lab` READY only
