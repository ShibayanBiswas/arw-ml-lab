# Phase oneshot-c91 — REE.P.COVERAGE_BIN

## Built
- `plot_coverage_bin` in `labcore/eval/regression/plots.py` — ŷ-decile bars (quantile digitize, same recipe as `REE.P.ERR_SEGMENT`); per-bin coverage and mean width via MAPIE `regression_coverage_score` / `regression_mean_width_score`; nominal horizontal line when `confidence_level` set; `conditional_coverage_gap` (REE.M.37) = max decile |coverage − nominal|; artefact id **`REE.P.COVERAGE_BIN`**; on-demand uncertainty diagnostic (not wired into default `run_regression_eval` suite).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_ree_coverage_bin.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 3 items

tests\unit\test_import_allowlist.py .                                    [ 33%]
tests\unit\test_ree_coverage_bin.py ..                                   [100%]

============================== 3 passed in 7.70s ==============================
```

## Notes
- Seed 42 synthetic (narrow vs wide intervals by ŷ sign) oracle for decile coverage + gap; `make_regression` + MAPIE `SplitConformalRegressor` integration test.
- Companion to c89 **`REE.P.PI_BAND`**; next gap: `REE.P.WIDTH_FITTED`, `REE.P.PIT`, `CLE.P.PR_MULTI`, or `FS.P.LABEL_BALANCE` per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; MAPIE metrics only (no hand-rolled PICP/MPIW).
- [x] Thin wrapper; Plotly layout on library-computed numbers.
- [x] Imports within pinned stack (mapie, plotly, numpy); import allowlist green.