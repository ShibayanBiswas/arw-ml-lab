# Phase oneshot-c78 — REE.P.LEVERAGE

## Built
- `plot_leverage_studentised` in `labcore/eval/regression/plots.py` — scatter of studentised residual vs leverage (`OLSInfluence` inputs) with dotted Cook's D contours at **0.5** and **1.0**; artefact id `REE.P.LEVERAGE`; `numbers` carries leverage/studentised arrays and contour grids for FACTS/oracle checks.
- `influence_table` now exposes per-row `leverage` and `n_params` for contour geometry.
- `run_regression_eval` suite emits the leverage plot in the influence group (after Cook's stem plot).

## Tests
```
uv run pytest tests/unit/test_ree_leverage.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_leverage.py .                                        [100%]

============================= 1 passed in 20.33s ==============================
```

## Notes
- Seed 42 synthetic OOF surrogate; oracle aligns `statsmodels` `OLSInfluence` hat values and internal studentised residuals; contour levels use Cook's D relation \(D = r^2 h / (p(1-h))\).
- Next gap: `REE.P.ERR_FEATURE_BIN` (fairlearn) or remaining §42 influence/residual IDs per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; contour rule matches statsmodels Cook's D on OLS surrogate.
- [x] Thin wrapper; Plotly layout on library-provided influence diagnostics.
- [x] Imports within pinned stack (plotly, numpy, statsmodels).