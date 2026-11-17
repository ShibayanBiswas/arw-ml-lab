# Phase oneshot-c83 — REE.P.RESID_FEATURE

## Built
- `plot_resid_feature` in `labcore/eval/regression/plots.py` — residual vs each column of `X` as Plotly small multiples (≤3 columns per row, cap `max_features`); per-panel scatter, zero reference line, and `statsmodels.nonparametric.smoothers_lowess.lowess` trend (default `frac=2/3`); artefact id **`REE.P.RESID_FEATURE`**; `numbers.by_feature` holds LOWESS coordinates per feature name for FACTS/oracle checks.

## Tests
```
uv run pytest tests/unit/test_ree_resid_feature.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_resid_feature.py .                                   [100%]

============================= 1 passed in 10.82s ==============================
```

## Notes
- On-demand plot (not wired into default `run_regression_eval` suite; same pattern as `REE.P.ERR_FEATURE_BIN`).
- Seed 42 synthetic features; oracle compares each panel LOWESS to direct `statsmodels` `lowess` on the same column.
- Distinct from oneshot-c80 **`REE.P.ERR_FEATURE_BIN`** (fairlearn MAE-by-bin) and c81 **`REE.P.STUDENTISED_INDEX`**.
- Next gap: `CLE.P.ERROR_OVERLAP` (UpSet/compare) or `REE.P.PARTIAL_RESID` per ARCHITECTURE §41–§42.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; oracle aligns per-feature `numbers` with statsmodels LOWESS.
- [x] Thin wrapper; Plotly layout on statsmodels LOWESS only.
- [x] Imports within pinned stack (plotly, numpy, statsmodels).