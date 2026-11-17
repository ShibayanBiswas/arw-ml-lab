# Phase oneshot-c81 — REE.P.STUDENTISED_INDEX

## Built
- `plot_studentised_residuals` in `labcore/eval/regression/plots.py` — scatter of externally studentised residual vs row index with reference lines at **0**, **±3**; artefact id **`REE.P.STUDENTISED_INDEX`** (replaces legacy `REE.P.STUD_RESID`); `numbers` carries index, studentised array and band levels for FACTS/oracle checks.
- `run_regression_eval` already emitted this plot via influence table; integration test id updated in `test_phase2_cont2_tune_cv.py`.

## Tests
```
uv run pytest tests/unit/test_ree_studentised_index.py tests/unit/test_phase2_cont2_tune_cv.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 12 items

tests\unit\test_ree_studentised_index.py .                               [  8%]
tests\unit\test_phase2_cont2_tune_cv.py ...........                      [100%]

================= 12 passed, 19 warnings in 60.05s (0:01:00) ==================
```

## Notes
- Seed 42 synthetic OOF surrogate; studentised values from `influence_table` (statsmodels `OLSInfluence`).
- Distinct from oneshot-c80 lane **`REE.P.ERR_FEATURE_BIN`** (fairlearn MAE-by-bin).
- Next gap: `REE.P.ERR_FEATURE_BIN`, `CLE.P.ERROR_OVERLAP`, or MAPIE interval plots per ARCHITECTURE §41–§42.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; oracle aligns plot `numbers` with `influence_table` studentised residuals.
- [x] Thin wrapper; Plotly layout on statsmodels-derived diagnostics.
- [x] Imports within pinned stack (plotly, numpy, statsmodels via diagnostics).