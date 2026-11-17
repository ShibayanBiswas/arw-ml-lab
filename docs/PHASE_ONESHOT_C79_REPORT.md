# Phase oneshot-c79 — CLE.P.PVALUE_HEATMAP

## Built
- `plot_pvalue_heatmap` in `labcore/eval/classification/plots.py` — pairwise Nemenyi p-values from fold score matrices (`scikit_posthocs.posthoc_nemenyi_friedman`) with Holm–Bonferroni adjustment via shared `_holm_adjust_symmetric` (`statsmodels.stats.multitest.multipletests`); Plotly heatmap with `sign_array` significance markers; artefact id `CLE.P.PVALUE_HEATMAP`; default `higher_is_better=True` for accuracy-style metrics.
- Distinct from expected oneshot-c78 slice (`REE.P.LEVERAGE` per c77 next gap); classification compare group mirrors regression `REE.P.PVALUE_HEATMAP` (c70) with flipped ranking default.

## Tests
```
uv run pytest tests/unit/test_cle_pvalue_heatmap.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_cle_pvalue_heatmap.py .                                  [100%]

============================= 1 passed in 14.59s ==============================
```

## Notes
- Seed 42 synthetic fold accuracy fixtures (logreg ≥ rf ≈ gbrt); oracle checks Holm p-values against statsmodels on the same Nemenyi matrix(symmetric off-diagonal pairs).
- Next gap: `REE.P.LEVERAGE` (c78 lane) or `CLE.P.ERROR_OVERLAP` / `CLE.P.CD` plot wrapper per ARCHITECTURE §41 compare group.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42 in fixtures; library-only posthoc + Holm.
- [x] Thin wrapper; reuses regression Holm helper; no from-scratch statistical test.
- [x] Imports within pinned stack (`scikit-posthocs`, `statsmodels`, plotly).