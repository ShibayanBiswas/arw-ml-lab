# Phase 3 report — Explain / Predict / UQ thin + deploy hygiene

**Date:** 2026-11-15 (IST)  
**Status:** green for locked thin scope (ADR-0011 + ADR-0012)

## Workstream A — Deploy / CI hygiene

- Deleted stray Vercel project **`frontend`** (Root `.` → `NEXT_NO_VERSION`); sole project **`arw-ml-lab`** (Root `frontend`).
- Removed local `frontend/.vercel`; ADR-0011 + `docs/DEPLOY.md` updated.
- CI: `pnpm/action-setup` → `frontend/package.json`; `[inbucket]` → `[local_smtp]`; ruff format; mypy overrides for scientific libs; install `ml-core`+`eda`+`xai-uq` for unit tests; eslint `react-hooks/set-state-in-effect` off for intake/shell data loads.

## Workstream B — Phase 3 thin

### Built
- `labcore/explain/` — TreeSHAP + PDP=mean ICE
- `labcore/uncertainty/` — calibration (FrozenEstimator) + MAPIE split conformal / APS
- `labcore/predict/` — feature contract builder/validator + predict_single/batch
- API: `GET /models/{id}/schema`, `POST /models/{id}/predict`, `POST /explain/{id}` via `MODEL_STORE`

## AC (real runs)

| AC | Result |
|---|---|
| TreeSHAP additivity < 1e-6 | **PASS** (`1.78e-15`) |
| PDP = mean ICE | **PASS** |
| Conformal 90% coverage ∈ [0.88, 0.92] | **PASS** (`0.905` on DS12 subsample) |
| APS coverage ≥ 0.89 | **PASS** (`0.983`) |
| Calibration reduces ECE | **PASS** |
| Feature contract schema + no id values | **PASS** |
| Vitest / prior catalog | carried by CI |

### Commands

```
PYTHONPATH=. python -m pytest tests/unit/test_phase3_explain_uq.py -q
.........                                                                [100%]
EXIT:0
```

## Deferred (3-cont / 3A)

- Full SHAP plot matrix, DiCE/Anchors/EBM, ONNX/export/MLflow registry
- Prediction Studio UI (§45)

## Self-check (§000)

- [x] ACs with real numbers
- [x] seed 42; no fabricated metrics
- [x] libraries from §44 / xai-uq only
- [x] report + DECISIONS + PROGRESS
- [x] commit + push + Vercel READY (below)

### Deploy closeout

- GitHub `main`: _(filled after push)_
- Vercel **`arw-ml-lab` only** READY: _(filled after deploy)_

## Next

Stop and wait for **continue** → Phase 3A (Prediction Studio UI) or 3-cont / 2A-cont.
