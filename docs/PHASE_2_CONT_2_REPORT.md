# Phase 2-cont-2 report — Tune / CV / plots + deploy sync

**Date:** 2026-11-15 (IST)  
**Status:** green for locked scope (ADR-0007)

## Built

### CV catalogue — `labcore/cv/`
- Schemes: holdout, KFold, StratifiedKFold, Repeated*, GroupKFold, ShuffleSplit*, TimeSeriesSplit, LOO, nested
- MI-03: `nested_default(n_train < 2000)` wired into `TrainConfig` / `run_supervised_cv`
- CV.P.FOLDS Plotly visualiser on every train result
- `GET /catalog` exposes full CV list + `target` encoder

### Optuna — `labcore/train/tune.py`
- TPE study, seed 42; Quick=20 / Balanced=60 presets
- Celery `lab.tune.run` on `q.tune`; `POST /api/v1/experiments/tune`
- Fixed user params asserted on best artefact; MLflow only if `MLFLOW_TRACKING_URI` set
- FE: Quick/Balanced preset + train/tune mode on TrainWorkbench

### Plots + integrity
- CLE.P: gains/lift, KS, threshold-vs-metric, DET, prob dens, per-class P/R/F1
- REE.P: Cook’s D, studentised residual index, Bland–Altman, residual ACF
- MI-02: TargetEncoder in recipe (`categorical_encoder=target`)
- MI-06: seed-42 reproduce
- CD (Friedman–Nemenyi via scikit-posthocs) + Nadeau–Bengio corrected-t
- Registry **47** AlgorithmSpecs (≥45)

## AC (real runs)

| AC | Result |
|---|---|
| Optuna Quick LightGBM + fixed params on DS3 | **PASS** |
| nested CV default n&lt;2000 | **PASS** |
| CV visualiser artefact | **PASS** |
| MI-02 noise TargetEncoder ~chance AUC | **PASS** |
| MI-06 reproduce | **PASS** |
| CD + corrected-t synthetic | **PASS** |
| Expanded CLE/REE plots | **PASS** |
| ≥45 algorithms instantiate | **PASS** (47) |
| Prior phase2 / eval unit | **PASS** |

### Commands

```
uv run pytest tests/unit/test_phase2_cont2_tune_cv.py tests/unit/test_phase2_cont_eval.py tests/unit/test_phase2_train.py -q
..............................   [100%] EXIT:0
```

## Deferred (2-cont-3 / later)

Full CLE.P.45 / REE.P.36; complete R*/C* + DL tabular; Halving/NSGA-II/Hyperband; purged/CPCV; full MLflow nested UX.

## Self-check (§000)

- [x] unit green for 2-cont-2 + prior phase2
- [x] seed 42 on Optuna / CV
- [x] no secrets in commit
- [x] push + Vercel READY (recorded below)

### Deploy closeout

- GitHub `main` commit: `046cfe7` (`phase 2-cont-2: tune cv plots`)
- Vercel production **READY**: `https://arw-ml-cpkn0e0tu-shibayan-biswas-projects.vercel.app` (alias `https://arw-ml-lab.vercel.app`)

## Next

**Phase 2-cont-3** or **Phase 2A** on user **continue**.
