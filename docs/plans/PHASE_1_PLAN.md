# Phase 1 — Data + EDA + Education plan

Approved plan source: `phase_1_data_eda_2e872e53`.

## Locked decisions

- TradingLab deferred to Phase 5; TL-only EDA cells → `not computed` / `tradinglab_phase_5`.
- Outliers: sklearn IsolationForest + LocalOutlierFactor (not pyod on light worker).
- Add `ruptures` + `arch` to `backend/requirements/eda.txt` for sequential EDA on light worker.
- StoragePort: Supabase signed URL when configured; local `.cache/uploads/` for tests/dev.
- Seed 42; every artefact has real `numbers` JSON.

## Workstreams

A. `labcore/data` — readers, type inference §9, task detect, sample loader  
B. API + Celery `q.ingest` / `q.eda` + StoragePort  
C. `labcore/eda` + `labcore/plots` — 19 EDA.T.* + §10.2 plots  
D. ExplainCard, explanations registry, Learn atlas, rule insights, Data/EDA UI  
E. AC verification → PHASE_1_REPORT → commit → STOP

## AC

1. DS3 type inference (Survived binary, Age numeric+missing, Name text, Cabin high-card)  
2. DS22 monthly; DS30 daily business OHLCV  
3. All 19 tables + §10.2 plots for DS3/22/30 with ExplainCard + PNG  
4. 1M×50 profile < 60s (benchmark; record wall time)  
5. Rule engine flags Titanic Age ~19.9% and Cabin ~77%
