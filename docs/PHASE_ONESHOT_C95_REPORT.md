# Phase oneshot-c95 — CLE.P.ROC_CV

## Built
- `plot_roc_cv` in `labcore/eval/classification/plots.py` — per-fold binary ROC from `sklearn.metrics.roc_curve`; fold traces on a common FPR grid via `numpy.interp`; mean TPR ± 1 std band across folds; per-fold and mean AUC from `roc_auc_score`; artefact id **`CLE.P.ROC_CV`**; on-demand CV diagnostic (not wired into default single-model suite).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_cle_roc_cv.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 2 items

tests\unit\test_import_allowlist.py .                                    [ 50%]
tests\unit\test_cle_roc_cv.py .                                          [100%]

============================= 2 passed in 13.82s ==============================
```

## Notes
- Seed 42 `make_classification` + `StratifiedKFold(4)` + `LogisticRegression`; oracle recomputes fold `roc_curve` interpolation on the same FPR grid.
- Mirrors oneshot-c94 **`CLE.P.PR_CV`** (recall/precision lane); complements c90 **`CLE.P.ROC_MULTI`** (multiclass OvR, pooled data).
- Next gap: `REE.P.WIDTH_FITTED`, `REE.P.PIT`, or `FS.P.LABEL_BALANCE` per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; sklearn ROC/AUC only.
- [x] Thin wrapper; Plotly layout on library-computed curves/AUC.
- [x] Imports within pinned stack (sklearn, plotly, numpy); import allowlist green.