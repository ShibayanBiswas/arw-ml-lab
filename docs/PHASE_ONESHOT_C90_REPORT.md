# Phase oneshot-c90 — CLE.P.ROC_MULTI

## Built
- `plot_roc_multi` in `labcore/eval/classification/plots.py` — per-class OvR ROC from `sklearn.metrics.roc_curve` + `label_binarize`; micro-average on flattened binarized labels/scores; macro display curve via sklearn OvR interpolation recipe (mean TPR on shared FPR grid); macro headline AUC = unweighted mean of per-class AUCs (matches `roc_auc_score(..., average="macro")`); artefact id **`CLE.P.ROC_MULTI`**; on-demand multiclass diagnostic (not wired into default single-model suite).

## Tests
```
uv run pytest tests/unit/test_import_allowlist.py tests/unit/test_cle_roc_multi.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 2 items

tests\unit\test_import_allowlist.py .                                    [ 50%]
tests\unit\test_cle_roc_multi.py .                                       [100%]

============================= 2 passed in 23.31s ==============================
```

## Notes
- Seed 42 `make_classification` + `LogisticRegression`; oracles: per-class / micro / macro AUC from `roc_auc_score` with `multi_class="ovr"`.
- Distinct from oneshot-c88–c89 REE lane (`ALPHA_CV`, planned `PI_BAND` / `BLAND_ALTMAN` tests); extends binary `CLE.P.ROC`.
- Next gap: `CLE.P.PR_MULTI`, `CLE.P.ROC_CV`, MAPIE `REE.P.PI_BAND`, or `FS.P.LABEL_BALANCE` per ARCHITECTURE.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; sklearn ROC/OvR only.
- [x] Thin wrapper; Plotly layout on library-computed curves/AUCs.
- [x] Imports within pinned stack (sklearn, plotly, numpy); import allowlist green.