# Phase oneshot-c87 — REE.P.PRED_ACTUAL_FOLDS

## Built
- `plot_pred_actual_folds` in `labcore/eval/regression/plots.py` — accepts `fold_preds` (`y_true` / `y_pred` per fold, same shape as `run_regression_eval`); each panel uses `sklearn.metrics.PredictionErrorDisplay.from_predictions` for aligned inputs then Plotly scatter (actual vs predicted) with y=x reference; subplot titles show per-fold R² and RMSE from `compute_ree_metrics`; artefact id **`REE.P.PRED_ACTUAL_FOLDS`**; `numbers.per_fold` stores fold index, n, R², RMSE, and coordinates for FACTS/oracle checks.
- On-demand CV diagnostic (not wired into default `run_regression_eval` suite; same pattern as `REE.P.METRIC_FOLDS`).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_ree_pred_actual_folds.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 2 items

tests\unit\test_import_allowlist.py .                                    [ 50%]
tests\unit\test_ree_pred_actual_folds.py .                               [100%]

============================= 2 passed in 16.74s ==============================
```

## Notes
- Seed 42 synthetic three-fold data; oracle matches `compute_ree_metrics` (sklearn R² / RMSE) per fold.
- Distinct from oneshot-c84 **`REE.P.PARTIAL_RESID`** (CCPR linear) and pooled **`REE.P.PRED_VS_ACTUAL`**.
- Next gap: `REE.P.REG_PATH`, `REE.P.ALPHA_CV`, or remaining §42 uncertainty plots per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; sklearn `PredictionErrorDisplay` + metrics wrapper only.
- [x] Thin wrapper; Plotly layout on library-computed numbers.
- [x] Imports within pinned stack (sklearn, plotly, numpy); import allowlist green.