# Phase oneshot-c82 — CLE.P.ERROR_OVERLAP

## Built
- `plot_error_overlap` in `labcore/eval/classification/plots.py` — per-model misclassified row sets via `upsetplot.from_contents`, intersection sizes from grouped membership index, Plotly UpSet-style layout (marginal error bars + intersection counts + set matrix); artefact id **`CLE.P.ERROR_OVERLAP`**; on-demand compare plot (not in default single-model suite).

## Tests
```
uv run pytest tests/unit/test_cle_error_overlap.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_cle_error_overlap.py .                                   [100%]

============================== warnings summary ===============================
tests/unit/test_cle_error_overlap.py::test_error_overlap_oracle_matches_upsetplot
tests/unit/test_cle_error_overlap.py::test_error_overlap_oracle_matches_upsetplot
  C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab\.venv\Lib\site-packages\upsetplot\data.py:385: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
    df.fillna(False, inplace=True)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 1 passed, 2 warnings in 9.40s ========================
```

## Notes
- Seed 42 synthetic overlap fixture; oracle re-runs `from_contents` + `groupby` on the same misclassification sets.
- Distinct from c83 **`REE.P.RESID_FEATURE`** (regression residual vs feature LOWESS); c82 fills the skipped classification compare gap flagged since c79.
- Next gap: `REE.P.PARTIAL_RESID` or remaining §42 influence IDs per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; oracle matches upsetplot intersection counts.
- [x] Thin wrapper; Plotly layout on upsetplot membership data only.
- [x] Imports within pinned stack (`upsetplot`, plotly, numpy).