# Phase oneshot-c92 — CLE.P.PR_MULTI

## Built
- `plot_pr_multi` in `labcore/eval/classification/plots.py` — per-class OvR PR from `sklearn.metrics.precision_recall_curve` + `label_binarize`; micro-average on flattened binarized labels/scores; per-class and micro AP from `average_precision_score`; artefact id **`CLE.P.PR_MULTI`**; on-demand multiclass diagnostic (not wired into default single-model suite).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_cle_pr_multi.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 2 items

tests\unit\test_import_allowlist.py .                                    [ 50%]
tests\unit\test_cle_pr_multi.py .                                        [100%]

============================= 2 passed in 15.52s ==============================
```

## Notes
- Seed 42 `make_classification` + `LogisticRegression`; oracles: per-class and micro AP from `average_precision_score`.
- Mirrors oneshot-c90 **`CLE.P.ROC_MULTI`** (OvR + micro); distinct from c89 REE **`REE.P.PI_BAND`** lane.
- Next gap: `CLE.P.ROC_CV`, `CLE.P.PR_CV`, `REE.P.COVERAGE_BIN`, or `FS.P.LABEL_BALANCE` per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; sklearn PR/AP only.
- [x] Thin wrapper; Plotly layout on library-computed curves/AP.
- [x] Imports within pinned stack (sklearn, plotly, numpy); import allowlist green.