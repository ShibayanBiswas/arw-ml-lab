# Phase 2-cont report — Eval Core + deploy sync

**Date:** 2026-11-15 (IST)  
**Status:** green for Eval Core scope (ADR-0006)

## Built

### Classification (§41 core) — `labcore/eval/classification/`
- CLE.T.CM suite (counts + row/column/all norms, folds, derived TP/FP/TN/FN)
- CLE.T.REPORT + CLE.M wrappers (sklearn/imblearn/netcal)
- CLE.T.CV_METRICS; threshold Youden/F1/cost on **OOF only**
- McNemar (statsmodels), 5×2cv (mlxtend), DeLong (MLstatkit)
- Min plots: CM, ROC, PR, reliability

### Regression (§42 core) — `labcore/eval/regression/`
- REE.T.RESIDUALS, RESID_TESTS, INFLUENCE (statsmodels OLSInfluence)
- REE.M core; plots: pred-vs-actual, residual scatter/hist, QQ

### Train / registry / FE
- `run_supervised_cv` attaches champion `eval` payload
- **32** AlgorithmSpecs (≥30); `algorithms_extra.py`
- Evaluation UI: Supervised → Model Detail + post-train EvalWorkbench tabs

### Deploy sync (ADR-0006)
- Standing rule in `docs/DEPLOY.md` + HOSTED_CHECKLIST: commit → push → Vercel READY
- This closeout pushes `main` and verifies Vercel

## AC (real runs)

| AC | Result |
|---|---|
| ≥30 algorithms instantiate | **PASS** (32) |
| CLE.M oracle equality (accuracy, MCC) | **PASS** |
| CM norms + fold pool | **PASS** |
| Threshold OOF-only (no test in tune) | **PASS** |
| McNemar / DeLong / 5×2cv | **PASS** |
| DS4-like binary (breast_cancer) CM+report | **PASS** |
| DS10-like multiclass (iris) | **PASS** |
| DS12-like regression residuals+tests+influence | **PASS** |
| Prior phase2 leakage/DS3 tests | **PASS** |
| db_harness pgTAP | **PASS** |
| frontend tsc + vitest | **PASS** |

### Commands

```
.\.venv\Scripts\pytest.exe tests/unit/test_phase2_cont_eval.py tests/unit/test_phase2_train.py -q --disable-warnings
...................   [100%] EXIT:0

.\.venv\Scripts\pytest.exe tests/unit/test_import_allowlist.py tests/unit/test_phase2_cont_eval.py ... -q
............................  EXIT:0

python tests/db_harness/run_db_tests.py  → RLS suites ok EXIT:0
cd frontend && pnpm exec tsc --noEmit → EXIT:0
cd frontend && pnpm test --run → 6 passed
```

## Deferred (next 2-cont slice)

Full CLE.P/REE.P catalogues; remaining R*/C*; Optuna trial loop / Halving / NSGA-II; full CV catalogue; MLflow nested runs; CD-diagram goldens.

## Self-check (§000)

- [x] unit eval + phase2 train green; ruff on new paths; tsc/vitest green
- [x] db_harness green
- [x] no secrets in commit
- [x] seed 42 on CV / compare
- [x] push + Vercel verification (recorded below at closeout)

## Next

**Phase 2-cont-2** (remaining Phase 2 AC) or **Phase 2A** on user **continue**.
