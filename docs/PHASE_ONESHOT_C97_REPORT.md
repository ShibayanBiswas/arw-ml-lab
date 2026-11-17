# Phase oneshot-c97 — REE.P.PIT

## Built
- `_pit_from_quantile_grid` and `plot_pit` in `labcore/eval/regression/plots.py` — PIT ordinates via inverse piecewise-linear quantile function (`scipy.interpolate.interp1d`); histogram density with uniform reference; calibration check via `scipy.stats.kstest` vs `Uniform(0,1)`; artefact id **`REE.P.PIT`**; on-demand quantile-calibration diagnostic (not wired into default `run_regression_eval` suite).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_ree_pit.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_import_allowlist.py .                                    [ 33%]
tests\unit\test_ree_pit.py ..                                            [100%]

============================= 3 passed in 13.01s ==============================
```

## Notes
- Seed 42 median-at-0.5 oracle plus row-wise interp1d cross-check; histogram and KS numbers match `scipy` / `numpy` on the same PIT vector.
- Distinct from c96 **`REE.P.WIDTH_FITTED`** (MAPIE width vs ŷ) and c91 **`REE.P.COVERAGE_BIN`** (decile PICP).
- Next gap: `FS.P.LABEL_BALANCE`, F60 `pmdarima_auto_arima` (train image / `ts.txt`), or F10 generic SARIMA per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; scipy PIT + KS only (no hand-rolled calibration stats).
- [x] Thin wrapper; Plotly layout on library-computed PIT/histogram.
- [x] Imports within pinned stack; import allowlist green.