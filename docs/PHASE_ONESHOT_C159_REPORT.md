# Phase oneshot-c159 — Chunk C / ST-ML-02 offline

## Built
- `labcore/deep/gpu_guard_contract.py` — **DEEP.GPU.GUARD**: catalogue GPU-only keys, `validate_train_gpu_guard` → HTTP **422** when `LAB_GPU_WORKER` unset; wired in `backend/app/routers/experiments.py`.
- `labcore/integrity/nested_cv_contract.py` — **MI.NESTED.CV** / **MI-03**: manifest for nested CV auto-default (`n_train < 2000`); emitted from `run_supervised_cv`.
- `docs/STRESS_TEST.md` — **ST-ML-02** notes offline **MI.NESTED.CV** + **DEEP.GPU.GUARD** (remainder still 2/4/5).

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_deep_gpu_guard.py tests\unit\test_mi_nested_cv.py tests\unit\test_import_allowlist.py -v --tb=short
======================= 8 passed, 5 warnings in 56.99s ========================
```

## Notes
- Distinct from oneshot-c158 (**OPS.OTEL.STUB**, **MI.HOLDOUT.REUSE**, **SEC.FEATURE_CONTRACT.IDENTIFIER**).
- HorizonGuard table/API tests unchanged (`test_horizon_guard.py`, `test_timeseries_api.py`).
- Seed **42**; no Contabo / NVIDIA / TradingLab.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; nested manifest from real `run_supervised_cv`; GPU 422 from live `TestClient`.
- [x] Import allowlist green.
- [x] Rule 70: thin wrappers over sklearn registry + existing `assert_gpu_allowed`.

**Ship commit:** _(fill after commit)_