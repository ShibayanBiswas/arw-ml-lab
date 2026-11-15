# Phase 2-cont — Eval Core + deploy sync

Approved scope: library-backed §41/§42 **core** (not full plot catalogues / full R*/C* matrix / Optuna loop). Keep GitHub + Vercel current after green.

## Locked decisions

1. Eval Core this green stop; full CLE.P/REE.P, remaining CV schemes, Optuna/Halving/NSGA-II, leftover algorithms → next 2-cont slice.
2. After every phase green: **commit → push `origin/main` → confirm Vercel READY**.
3. Rule 70: CLE/REE metrics via sklearn / imblearn / scipy / statsmodels / netcal / mlxtend / MLstatkit only.

## Workstreams

- A: `labcore/eval/classification` — CM suite, REPORT, CLE.M (B/M), CV_METRICS, threshold spy, McNemar/5×2/DeLong
- B: `labcore/eval/regression` — RESIDUALS, RESID_TESTS, INFLUENCE, REE.M core, residual plots
- C: Wire train/API/FE; expand registry ≥30 R*/C*
- D: Push + Vercel SSO/env/deploy; DEPLOY/HOSTED checklist standing rule

## AC (this stop)

DS4 CM+report; DS10 multiclass CM+report; DS12 residuals+tests+influence; oracle equality samples; threshold spy; compare smokes; ≥30 algos instantiate; unit green; git push + Vercel READY.
