# Phase oneshot-c85 — REE.P.COEF_FOREST

## Built
- `plot_coef_forest` in `labcore/eval/regression/plots.py` — horizontal coefficient forest with asymmetric Plotly error bars from statsmodels `conf_int`; artefact id **`REE.P.COEF_FOREST`**; on-demand linear-model diagnostic (not wired into default `run_regression_eval` suite).

## Tests
```
uv run pytest tests/unit/test_ree_coef_forest.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_coef_forest.py .                                     [100%]

============================== 1 passed in 9.51s ==============================
```

## Notes
- Seed 42 OLS fixture; oracle compares `numbers` to `sm.OLS(...).fit().conf_int()`.
- Distinct from planned c84 lane **`REE.P.PARTIAL_RESID`** (CCPR per feature) and c83 **`REE.P.RESID_FEATURE`** (residual vs feature LOWESS).
- Next gap: `REE.P.PARTIAL_RESID`, `REE.P.REG_PATH`, or `REE.P.PRED_ACTUAL_FOLDS` per ARCHITECTURE §42.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; oracle aligns with statsmodels CI bounds.
- [x] Thin wrapper; Plotly layout on library CI only.
- [x] Imports within pinned stack (plotly, numpy, statsmodels in tests).