# One-shot Chunk B.1 — deepen report

**Date:** 16 Nov 2026 (IST)  
**Scope:** PV02/03/10/14/15, purged K-fold + CPCV, Explain/Unsupervised/Suitability FS1–FS5 workbenches, DL leakage-safe scaler, registry expansion (prior)

## Built

| Area | Change |
|---|---|
| Predict PV | `labcore/predict/validate.py` — PV02 row/byte caps, PV03 encoding/delimiter/dup headers, PV10 contract-stat OOD, PV14 constant/all-NaN, PV15 formula sanitise, XLSX zip-bomb guard, `load_predict_table` returns meta |
| CV | `labcore/cv/purged.py` — `ml_get_train_times`, `PurgedKFold`, `CombinatorialPurgedKFold` (+ paths); wired into `build_splitter` as `purged_kfold` / `cpcv` |
| Explain | `labcore/explain/permutation.py`; API `method=shap\|permutation`; `ExplainWorkbench` |
| Unsupervised | `labcore/unsupervised/{clustering,dr,anomaly}.py` + API + `UnsupervisedWorkbench` |
| Suitability | `labcore/suitability/fs_checks.py` FS1–FS5 real; FS6–FS20 deferred; API + UI on preprocess/financial + supervised/backtest |
| Deep | Scaler fit on **train windows only** (`scaler_fit_on=train_windows_only`); `/api/v1/deep/sequential/smoke`; `DeepWorkbench` |
| Registry | Prior expand in `algorithms_extra.py` (~84 specs) + `test_registry_coverage.py` |

## Tests (real)

```
pytest tests/unit/test_purged_cv.py tests/unit/test_pv_deepen.py \
  tests/unit/test_unsupervised_suitability.py tests/unit/test_registry_coverage.py -q
→ 17 passed

pytest tests/unit/test_phase3a_predict.py -q → 7 passed
pytest tests/unit/test_phase2a_deep.py::test_window_purge_embargo_no_overlap → passed
fit_sequential smoke → scaler_fit_on=train_windows_only, n_train=65, val_mse=0.93078… (seed 42)
pnpm exec tsc --noEmit → exit 0
```

## Deferred / next in Chunk B→C

- PV11–13, PV16; Celery 1M batch + Idempotency-Key; full CLE.P/REE.P plot catalogues
- TradingLab submodule for FS6–FS20 + AFML parity goldens
- Full SHAP plot matrix, DiCE/Anchors, ONNX; Halving/Hyperband/NSGA-II UX
- Phases 4A → 8.2

## Self-check (§000)

- [x] Seed 42
- [x] No fabricated metrics (library scores only)
- [x] NVIDIA key not on client
- [x] Thin wrappers / AFML-cited purged CV (TradingLab not vendored yet)
- [ ] Full `make test` + Deploy watch — run on commit push
