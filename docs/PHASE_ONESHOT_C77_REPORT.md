# Phase oneshot-c77 — REE.P.COOKS

## Built
- `plot_cooks_distance` in `labcore/eval/regression/plots.py` — stem-style bar chart of Cook's D vs row index with horizontal **4/n** reference (`add_hline`); artefact id `REE.P.COOKS`; `numbers` carries `threshold_4_over_n`, per-index values for FACTS/oracle checks.
- Distinct from oneshot-c76 (`plot_residual_hist` / `REE.P.RESID_HIST`); stem plot body landed in `1f3410c` alongside the histogram slice — this commit adds the oracle test + phase report.

## Tests
```
uv run pytest tests/unit/test_ree_cooks.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_cooks.py .                                           [100%]

============================= 1 passed in 10.83s ==============================
```

## Notes
- Seed 42 on synthetic Cook's D fixture; oracle checks `4/n` threshold and array payloads (1e-12 atol).
- Cook's D values still sourced from `statsmodels` via `labcore/eval/regression/diagnostics.py` at suite time; this slice only hardens the plot artefact.
- Next gap: `REE.P.LEVERAGE` (influence contours) or `REE.P.ERR_FEATURE_BIN` (fairlearn) per ARCHITECTURE §42.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; 4/n rule as documented influence heuristic (thin arithmetic).
- [x] Thin wrapper; Plotly layout on library-provided Cook's D.
- [x] Imports within pinned stack (plotly, numpy).