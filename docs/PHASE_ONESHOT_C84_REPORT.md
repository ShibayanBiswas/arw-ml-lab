# Phase oneshot-c84 — REE.P.PARTIAL_RESID

## Built
- `plot_partial_resid` in `labcore/eval/regression/plots.py` — OLS on `y` vs `add_constant(X)`; per-feature CCPR panels mirror `statsmodels.graphics.regressionplots.plot_ccpr` (scatter of `βⱼ·xⱼ + resid` vs `xⱼ`, component line from `OLS(βⱼ·xⱼ ~ xⱼ)`); Plotly small multiples (≤3 columns per row, cap `max_features`); artefact id **`REE.P.PARTIAL_RESID`**; `numbers.by_feature` holds β, component line params, and partial-residual coordinates for FACTS/oracle checks.
- Implementation body landed early on `main` in `d65b454` (bundled with oneshot-c85); this commit adds the oracle unit test and phase report for the c84 lane.

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_ree_partial_resid.py tests/unit/test_ree_resid_feature.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_import_allowlist.py .                                    [ 33%]
tests\unit\test_ree_partial_resid.py .                                   [ 66%]
tests\unit\test_ree_resid_feature.py .                                   [100%]

============================= 3 passed in 22.15s ==============================
```

## Notes
- On-demand linear diagnostic (not wired into default `run_regression_eval` suite; same pattern as `REE.P.RESID_FEATURE`).
- Seed 42 synthetic linear data; oracle replays statsmodels OLS + component-line fit per feature.
- Distinct from c83 **`REE.P.RESID_FEATURE`** (residual vs feature LOWESS on ML residuals, not CCPR).
- Next gap: remaining §42 influence / interval plots or further CLE.P compare IDs per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; oracle matches `plot_ccpr` arithmetic on OLS fit.
- [x] Thin wrapper; Plotly layout on statsmodels OLS numbers only.
- [x] Imports within pinned stack (statsmodels, plotly, numpy); import allowlist green.