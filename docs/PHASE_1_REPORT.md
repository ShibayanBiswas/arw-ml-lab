# Phase 1 report — Data + EDA + Education + rule insights

**Date:** 2026-11-15 (IST)  
**Status:** green (AC verified; soft-skip on 1M profile wall time)

## Built

### Ingest / type / task / samples (`labcore/data/`)
- Readers: CSV/TSV (charset-normalizer), XLSX (python-calamine), Parquet/Feather/JSONL → Parquet + content hash
- Semantic type inference §9 (id, datetime, boolean, discrete, categorical, high-card, text, continuous, constant)
- Task auto-detect + frequency + OHLCV heuristic
- Sample loader: `datasets_manifest.json` + presets → immutable parquet under `.cache/samples`

### EDA (`labcore/eda/`, `labcore/plots/`)
- All **19** `EDA.T.*` artefacts (gated sections emit `not_applicable` when T/S not active)
- §10.2 plot groups as Plotly artefacts + numbers (PNG via kaleido when available; off in unit tests)
- TradingLab-only cells → `not_computed` / `tradinglab_phase_5` (ADR-0002)
- Outliers: sklearn IsolationForest + LOF (not pyod on light worker)
- `arch` + `ruptures` pinned in `backend/requirements/eda.txt`

### Insights
- `labcore/insights/rules.py`: missingness 5/30%, skew/kurtosis, high card, near-zero variance, |r|>0.9, VIF>10, imbalance, leakage |corr|>0.98, duplicates, non-stationarity

### API + workers
- `StoragePort`: local `.cache/uploads/` (tests/dev); Supabase signed upload when service role + non-local URL
- Routers: `/api/v1/datasets/*`, `/api/v1/eda/*`
- Celery: `lab.ingest.parse`, `lab.ingest.sample` (`q.ingest`), `lab.eda.run` (`q.eda`)
- In-memory `DATASET_STORE` + existing `JOB_STORE` / SSE

### Frontend education + UI
- `ExplainCard` (KaTeX) + `content/explanations` registry for EDA tables/plots/tests
- Learn Logic Atlas searchable page
- Data Upload / Samples / Explorer / Schema workbenches
- EDA Overview workbench + Rule insights side panel
- Deps: katex, plotly.js, react-plotly.js, zustand, @tanstack/react-query

## Acceptance criteria (real runs)

| AC | Result |
|---|---|
| DS3: Survived binary-ish, Age continuous+missing, Name text excluded, Cabin high-card | **PASS** `tests/unit/test_type_inference.py` |
| DS22 monthly; DS30 daily_business/daily + OHLCV | **PASS** `tests/unit/test_task_detect.py` |
| 19 tables + §10.2 plot groups for DS3/22/30; edu_key on artefacts | **PASS** `tests/golden/test_eda_ds3.py` |
| 1M×50 profile &lt; 60s | **SOFT-SKIP** wall **145.39s** on this host (`test_eda_benchmark.py`); plan allows record + skip-strict |
| Rule engine Age ~19.9%, Cabin ~77% | **PASS** `tests/unit/test_eda_rules.py` + API insights |
| Phase 0 tests still green | **PASS** |

### Commands / output

```
uv run pytest tests/unit tests/golden --tb=no
59 passed, 1 skipped, 195 warnings in 143.70s

uv run ruff check labcore backend tests
All checks passed!

uv run mypy labcore
Success: no issues found in 19 source files

cd frontend && pnpm test --run
Test Files  3 passed (3) / Tests  6 passed (6)

cd frontend && pnpm exec tsc --noEmit
(exit 0)

uv run python tests/db_harness/run_db_tests.py
migrations ok; prediction_rls_test + rls_test ok
```

Golden missingness (DS3): Age ≈19.87%, Cabin ≈77% (asserted 19–21 / 75–80).

## Deviations / TODOs

- **TradingLab deferred** (ADR-0002): Chow/CUSUM/SADF, TL volatility estimators, ONC feature clustering → `not_computed`.
- **1M profile** exceeded 60s on this workstation (145.39s); CI should re-measure on 8 vCPU.
- Dataset/EDA persistence is in-memory + local files until hosted Supabase is wired in Phase 8.1.
- PNG export requires kaleido binary; unit/API paths keep `render_png=False` by default.
- Frontend lab-api calls use `AUTH_TEST_BYPASS` headers in local UI (`lab-session.ts`); production uses real Bearer JWTs.

## Self-verification checklist (§000)

- [x] lint (`ruff`) + mypy + unit/golden tests green (summary above); frontend vitest + tsc green
- [x] db_harness pgTAP green (Supabase CLI not required)
- [x] no new `TODO|FIXME|NotImplementedError|pass  # stub` in `labcore` / `backend` / `frontend/src`
- [x] endpoints added under `/api/v1/datasets` and `/api/v1/eda` (Phase 1 ingest/EDA; DB tables already from Phase 0 migrations)
- [x] no secrets in diff
- [x] seed 42 on EDA / sample / IF / MI / Optuna-adjacent paths
- [ ] Playwright axe-core: not in Phase 1 scope (shell + workbenches have empty/loading/error text states)

## Next phase

**Phase 8.1 — Hosted skeleton** (deploy early with sample data only). Ask before touching Vercel/Render/Supabase accounts or production secrets.
