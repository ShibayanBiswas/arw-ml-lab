# Phase oneshot-c86 — REE.P.REG_PATH

## Built
- `plot_reg_path` in `labcore/eval/regression/plots.py` — coefficient paths vs log10(α) via sklearn `lasso_path` (Lasso), `enet_path` (ElasticNet), and `enet_path` with `l1_ratio=0` plus explicit α grid (Ridge); Plotly one line per feature; artefact id **`REE.P.REG_PATH`**; on-demand regularised-linear diagnostic (not wired into default `run_regression_eval` suite).

## Tests
```
uv run pytest tests/unit/test_ree_reg_path.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 2 items

tests\unit\test_ree_reg_path.py ..                                       [100%]

============================= 2 passed in 5.93s ==============================
```

## Notes
- Seed 42 fixtures (`make_regression`); oracle compares `numbers.coefs` / `alphas` to direct `lasso_path` / `enet_path` calls.
- Ridge path uses log-spaced α when `alphas` is an int (sklearn does not auto-grid `l1_ratio=0`).
- Distinct from c85 **`REE.P.COEF_FOREST`** (single-fit CIs) and planned **`REE.P.ALPHA_CV`** (CV score vs α).
- Next gap: `REE.P.PRED_ACTUAL_FOLDS`, `REE.P.ALPHA_CV`, or remaining §42 per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; oracle aligns with sklearn path coefficients.
- [x] Thin wrapper; Plotly layout on library path output only.
- [x] Imports within pinned stack (sklearn, plotly, numpy).