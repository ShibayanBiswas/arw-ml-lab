# Phase 2A report — Deep Learning thin smoke + deploy sync

**Date:** 2026-11-15 (IST)  
**Status:** green for locked thin scope (ADR-0009)

## Built

### `labcore/deep/`
- `engine.py` — seed 42, AdamW defaults, Lightning Trainer + EarlyStopping + ModelCheckpoint, LR finder (`Tuner.lr_find`)
- `tabular.py` — pytorch-tabular wrappers for **T1 MLP**, **T3 TabNet**, **T4 FT-Transformer**
- `sequential.py` — window builder + purge/embargo check; **Q2 LSTM** (`torch.nn`) + **Q7 TCN** (`pytorch-tcn`)
- `guards.py` — `TABPFN_ENABLED`, `LAB_GPU_WORKER`, `assert_gpu_allowed`
- `registry.py` — AlgorithmSpecs wired into `thin_algorithm_specs()` / catalog
- `artefacts.py` — minimal `DL.T.METRICS`, `DL.P.LOSS_CURVE`, `DL.P.LR_FINDER` number payloads

### API / catalog
- `GET /catalog` hides TabPFN unless `TABPFN_ENABLED=true`
- `POST /experiments/train|tune` → **422** for GPU-only (`seq.xlstm`) without GPU worker, or TabPFN while disabled

### Pins
- `dl-cpu.txt`: `pytorch-tabnet==4.1.0`, `requests==2.34.2`; `worker-train.lock.txt` recompiled

## AC (real runs)

| AC | Result |
|---|---|
| T1/T3/T4 defaults in registry | **PASS** |
| MLP / TabNet / FT smoke on DS3 (clf) Quick CPU | **PASS** (3 epochs, subset) |
| MLP smoke on DS12 (reg) | **PASS** |
| LSTM + TCN on windowed DS30 with purge/embargo | **PASS** |
| Window overlap test (positive + negative) | **PASS** |
| LR finder suggested LR + curve numbers; early-stop trainer | **PASS** |
| TabPFN hidden when disabled | **PASS** |
| GPU-only train → HTTP 422 | **PASS** |
| Import allow-list / prior catalog instantiate tests | **PASS** |

### Commands

```
uv run pytest tests/unit/test_phase2a_deep.py -q
............                                                             [100%]
EXIT:0

uv run pytest tests/unit/test_phase2_train.py \
  tests/unit/test_phase2_cont2_tune_cv.py::test_catalog_at_least_45_and_cv_schemes \
  tests/unit/test_phase2_cont_eval.py::test_catalog_at_least_30 \
  tests/unit/test_import_allowlist.py \
  tests/unit/test_api_phase0.py::test_catalog_populated -q
..............                                                           [100%]
EXIT:0
```

## Deviations / deferred (2A-cont)

- Full T2–T16 / Q1–Q13 matrix and full DL.P.* Plotly catalogue
- MC-dropout, deep ensembles, conformal DL heads
- Production leakage-safe scalers inside purged folds (thin smoke z-scores full series for stability only)
- GPU worker image / AMP bf16 path

## Self-check (§000)

- [x] ACs run with real output (no stubs)
- [x] seed 42; no fabricated metrics
- [x] libraries from §44 / `dl-cpu.txt` only (thin wrappers)
- [x] TabPFN off by default; GPU 422 without worker
- [x] report + DECISIONS + PROGRESS
- [x] commit + push + Vercel READY (below)

### Deploy closeout

- GitHub `main`: `1fc9929` (`phase 2a: dl thin smoke`)
- Vercel production **READY**: `https://arw-ml-6cjrcce90-shibayan-biswas-projects.vercel.app` (alias `https://arw-ml-lab.vercel.app`)

## Next

Stop and wait for user **continue** → Phase 2A-cont (full §34) or Phase 3.
