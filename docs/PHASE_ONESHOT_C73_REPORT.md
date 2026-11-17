# Phase oneshot-c73 — REE.P.RESID_FITTED

## Built
- `plot_resid_fitted` in `labcore/eval/regression/plots.py` — residuals vs fitted scatter plus `statsmodels.nonparametric.smoothers_lowess.lowess` trend (default `frac=2/3`); artefact id `REE.P.RESID_FITTED`; `numbers` carries LOWESS coordinates for FACTS/oracle checks.
- `run_regression_eval` suite uses `plot_resid_fitted` instead of the legacy scatter helper; `plot_residual_scatter` remains a thin alias.

## Tests
```
uv run pytest tests/unit/test_ree_resid_fitted.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_resid_fitted.py .                                    [100%]

============================== 1 passed in 9.83s ==============================
```

## Notes
- Seed 42 on synthetic `y_pred` / residual fixture; oracle compares `numbers.lowess_*` to a direct `lowess` call at `frac=0.45` (1e-12 atol).
- Next gap: `CLE.P.PVALUE_HEATMAP`, `REE.P.ERR_FEATURE_BIN`, or MAPIE interval plots (`REE.P.PI_BAND`, etc.) per ARCHITECTURE §41–§42.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; statsmodels LOWESS only (no hand-rolled smoother).
- [x] Thin wrapper; Plotly layout on library coordinates.
- [x] Imports within pinned stack (statsmodels, plotly, numpy).