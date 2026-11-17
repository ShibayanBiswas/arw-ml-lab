# Phase oneshot-c80 — REE.P.ERR_FEATURE_BIN

## Built
- `plot_err_feature_bin` in `labcore/eval/regression/plots.py` — MAE by feature quantile/category bin via fairlearn `MetricFrame` (`sklearn.metrics.mean_absolute_error`); helper `_feature_bin_labels` for numeric quantiles or categorical groups (cap `max_categories`); Plotly bar chart with overall MAE reference line; artefact id `REE.P.ERR_FEATURE_BIN`.

## Tests
```
uv run pytest tests/unit/test_ree_err_feature_bin.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_err_feature_bin.py .                                 [100%]

============================= 1 passed in 10.84s ==============================
```

## Notes
- On-demand plot (not wired into default `run_regression_eval` suite; mirrors `plot_err_heatmap`).
- Seed 42; oracle checks per-bin MAE against direct `MetricFrame` on the same quantile digitization.
- Next gap: `CLE.P.ERROR_OVERLAP` (UpSet/compare) or `REE.P.RESID_FEATURE` per ARCHITECTURE §41–§42.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; library-only MetricFrame + sklearn MAE.
- [x] Thin wrapper; no from-scratch metrics.
- [x] Imports within pinned stack (`fairlearn`, `sklearn`, `plotly`).