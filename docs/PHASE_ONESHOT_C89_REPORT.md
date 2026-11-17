# Phase oneshot-c89 — REE.P.PI_BAND

## Built
- `plot_pi_band` in `labcore/eval/regression/plots.py` — samples sorted by ŷ; Plotly shaded band (`y_lower`–`y_upper`), predicted line, actual markers; PICP and mean interval width via MAPIE `regression_coverage_score` / `regression_mean_width_score` on `(n, 2, 1)` interval layout; artefact id **`REE.P.PI_BAND`**; on-demand uncertainty diagnostic (not wired into default `run_regression_eval` suite).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_ree_pi_band.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_import_allowlist.py .                                    [ 33%]
tests\unit\test_ree_pi_band.py ..                                        [100%]

============================== 3 passed in 11.46s ==============================
```

## Notes
- Seed 42 `make_regression` + MAPIE `SplitConformalRegressor` (absolute score) oracle for integration test; synthetic fixed intervals for metric oracle.
- Distinct from c88 **`REE.P.ALPHA_CV`** (regularisation CV curve) and planned **`REE.P.COVERAGE_BIN`** (decile coverage vs nominal).
- Next gap: `REE.P.COVERAGE_BIN`, `REE.P.WIDTH_FITTED`, `REE.P.BLAND_ALTMAN` (wrapper exists), or remaining §42 per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; MAPIE metrics only (no hand-rolled PICP/MPIW).
- [x] Thin wrapper; Plotly layout on library-computed numbers.
- [x] Imports within pinned stack (mapie, plotly, numpy); import allowlist green.