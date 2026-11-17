# Phase oneshot-c70 — REE.P.PVALUE_HEATMAP

## Built
- `plot_regression_pvalue_heatmap` — pairwise Nemenyi p-values from fold score matrices (`scikit_posthocs.posthoc_nemenyi_friedman`) with Holm–Bonferroni adjustment (`statsmodels.stats.multitest.multipletests`); Plotly heatmap with `sign_array` significance markers (default `higher_is_better=False` for RMSE/MAE).
- `_holm_adjust_symmetric` — thin Holm wrapper for symmetric post-hoc matrices.
- `cd_diagram.friedman_nemenyi` — fix `np.asarray(...)` when wrapping posthoc output (scikit-posthocs 0.18 returns a DataFrame).

## Tests
```
uv run pytest tests/unit/test_ree_pvalue_heatmap.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_pvalue_heatmap.py .                                  [100%]

============================== 1 passed in 9.67s ==============================
```

## Notes
- Seed 42 synthetic fold RMSE fixtures (ridge &lt; rf ≈ gbrt); test oracles Holm p-values against statsmodels on the same Nemenyi matrix.
- Compare-group slice after c69 `REE.P.CD`; next gap: `REE.P.LEARNING` / `REE.P.VALIDATION` (ARCHITECTURE §42).

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42 in fixtures; library-only posthoc + Holm.
- [x] Thin wrapper; no from-scratch statistical test.
- [x] Imports limited to pinned stack (`scikit-posthocs`, `statsmodels`, plotly).