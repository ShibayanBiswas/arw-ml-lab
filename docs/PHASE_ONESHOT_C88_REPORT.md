# Phase oneshot-c88 — REE.P.ALPHA_CV

## Built
- `plot_alpha_cv` in `labcore/eval/regression/plots.py` — CV mean MSE vs log10(α) with ±1 std error bars; **Lasso** / **ElasticNet** via sklearn `LassoCV` / `ElasticNetCV` (`mse_path_`); **Ridge** via `RidgeCV` for `alpha_` plus `validation_curve` on `Ridge` with `neg_mean_squared_error` (sklearn 1.9 `RidgeCV` with explicit `cv` does not expose `mse_path_`); gold vertical line at chosen α; artefact id **`REE.P.ALPHA_CV`**; on-demand regularised-linear diagnostic (not wired into default `run_regression_eval` suite).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_ree_alpha_cv.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_import_allowlist.py .                                    [ 33%]
tests\unit\test_ree_alpha_cv.py ..                                       [100%]

============================== 3 passed in 7.71s ==============================
```

## Notes
- Seed 42 `make_regression` fixtures; oracles match `LassoCV.mse_path_` / `validation_curve` + `RidgeCV.alpha_`.
- Distinct from c86 **`REE.P.REG_PATH`** (coefficient paths, no CV score curve).
- Next gap: MAPIE interval plots (`REE.P.PI_BAND`, `REE.P.COVERAGE_BIN`), `REE.P.BLAND_ALTMAN`, or remaining §42 per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; sklearn CV estimators + `validation_curve` only.
- [x] Thin wrapper; Plotly layout on library-computed numbers.
- [x] Imports within pinned stack (sklearn, plotly, numpy); import allowlist green.