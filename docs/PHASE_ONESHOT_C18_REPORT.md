# Phase oneshot-c18 — EBM (interpret)

**Date:** 16 Nov 2026

## Built
- `labcore/explain/ebm.py` — ExplainableBoostingClassifier/Regressor thin wrapper (`EXPLAIN.T.EBM`).

## Tests
```
pytest tests/unit/test_explain_ebm.py -q
# . passed (test ROC-AUC > 0.9 on breast cancer)
```
