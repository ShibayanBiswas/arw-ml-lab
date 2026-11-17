# Phase oneshot-c94 — CLE.P.PR_CV

## Built
- `plot_pr_cv` in `labcore/eval/classification/plots.py` — per-fold binary PR from `sklearn.metrics.precision_recall_curve`; fold traces on a common recall grid via `numpy.interp` (increasing recall); mean precision ± 1 std band across folds; per-fold and mean AP from `average_precision_score`; artefact id **`CLE.P.PR_CV`**; on-demand CV diagnostic (not wired into default single-model suite).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_cle_pr_cv.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 2 items

tests\unit\test_import_allowlist.py .                                    [ 50%]
tests\unit\test_cle_pr_cv.py .                                           [100%]

============================= 2 passed in 19.90s ==============================
```

## Notes
- Seed 42 `make_classification` + `StratifiedKFold(4)` + `LogisticRegression`; oracle recomputes fold `precision_recall_curve` interpolation on the same grid.
- Distinct from planned oneshot-c93 **`CLE.P.ROC_CV`** (FPR/TPR lane); complements c92 **`CLE.P.PR_MULTI`** (multiclass OvR, pooled data).
- Next gap: `CLE.P.ROC_CV`, `REE.P.WIDTH_FITTED`, `REE.P.PIT`, or `FS.P.LABEL_BALANCE` per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; sklearn PR/AP only.
- [x] Thin wrapper; Plotly layout on library-computed curves/AP.
- [x] Imports within pinned stack (sklearn, plotly, numpy); import allowlist green.