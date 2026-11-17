# Phase oneshot-c96 — REE.P.WIDTH_FITTED

## Built
- `plot_width_fitted` in `labcore/eval/regression/plots.py` — scatter of interval width (upper − lower) vs ŷ; `statsmodels.nonparametric.smoothers_lowess.lowess` overlay; horizontal mean width from MAPIE `regression_mean_width_score`; artefact id **`REE.P.WIDTH_FITTED`**; on-demand uncertainty diagnostic (not wired into default `run_regression_eval` suite).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_ree_width_fitted.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_import_allowlist.py .                                    [ 33%]
tests\unit\test_ree_width_fitted.py ..                                   [100%]

============================= 3 passed in 17.09s ==============================
```

(Combined local run with oneshot-c95 `test_cle_roc_cv.py`: **4 passed in 17.09s**.)

## Notes
- Seed 42 synthetic width–ŷ pattern + MAPIE `SplitConformalRegressor` integration test; LOWESS oracle matches `statsmodels` on the same inputs.
- Distinct from oneshot-c95 **`CLE.P.ROC_CV`** (classification CV ROC lane) and c91 **`REE.P.COVERAGE_BIN`** (decile coverage bars).
- Next gap: `REE.P.PIT`, `FS.P.LABEL_BALANCE`, F60 `pmdarima_auto_arima` (train image / `ts.txt`), or F10 generic SARIMA per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; MAPIE + statsmodels LOWESS only.
- [x] Thin wrapper; Plotly layout on library-computed widths.
- [x] Imports within pinned stack; import allowlist green.