# Phase oneshot-c75 — REE.P.SCALE_LOCATION

## Built
- `plot_scale_location` in `labcore/eval/regression/plots.py` — √|standardised residual| vs fitted scatter plus `statsmodels.nonparametric.smoothers_lowess.lowess` trend (default `frac=2/3`); artefact id `REE.P.SCALE_LOCATION`; `numbers` carries `residual_sd` and LOWESS coordinates for FACTS/oracle checks.
- Distinct from oneshot-c73 (`plot_resid_fitted` / `REE.P.RESID_FITTED`).

## Tests
```
uv run pytest tests/unit/test_ree_scale_location.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_scale_location.py .                                  [100%]

============================== 1 passed in 13.30s ==============================
```

## Notes
- Seed 42 on synthetic `y_pred` / residual fixture; oracle compares `numbers.lowess_*` to a direct `lowess` call on `√|stud|` at `frac=0.5` (1e-12 atol).
- Next gap: `REE.P.QQ` (ProbPlot envelope), `REE.P.COOKS` (stem + 4/n), `REE.P.RESID_HIST` (KDE + normal) per ARCHITECTURE §42.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; statsmodels LOWESS only (no hand-rolled smoother).
- [x] Thin wrapper; Plotly layout on library coordinates.
- [x] Imports within pinned stack (statsmodels, plotly, numpy).