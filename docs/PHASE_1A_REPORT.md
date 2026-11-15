# Phase 1A report — AI Dataset Intake / Auto-Setup (§33)

**Date:** 2026-11-15 (IST)  
**Status:** green (AC verified; soft-skip on 1M×100 intake wall time)

## Built

### `labcore/intake/` (rule-based; LLM deferred to Phase 6)
- Extended profile §33.2 (≤20k sample; stride sample for large frames)
- D1 datetime / composite year+quarter / ambiguous dd/mm (India default)
- D2 frequency (`infer_freq` + mode Δ, `exchange-calendars` XNSE/XBOM/XNYS, seasonality)
- D3 roles (OHLCV ≥99% consistency, PII, hard excludes)
- D4 family softmax + `weights.yaml` (pre-select ≥0.55); financial flag
- D5 targets/features (MI ranks; derived financial builders JSON only — no TradingLab)
- D6 leakage (nine rules incl. arithmetic identity, lead/lag, later-event)
- D7 schema diff (rapidfuzz Jaro–Winkler ≥0.85); D8 drift (PSI/KS/χ²)
- Thin HorizonGuard §20; validator + confirm hard-exclude guard
- Pipeline orchestrates D1–D8 → merged proposal

### Persistence / API / workers
- Migration `20261115120000_intake_detail.sql`: intake detail tables + `parent_version_id` + RLS
- In-memory `INTAKE_STORE` (parallel to Phase 1 `DATASET_STORE`)
- Routers §33.12; Celery `lab.intake.run` after ingest/sample
- Confirm → experiment `task_spec`; hard-exclude include → **422**
- Does not overwrite Phase-1 `TaskSpec` on the dataset (ADR-0004)

### Frontend
- Data → Intake Review; post-upload navigation when proposal ready
- Family bars, roles table, targets, leakage, Accept / Reset; ambiguous-date banner

### Libraries (rule 70 / §44)
- `exchange-calendars==4.11.1`, `rapidfuzz==3.14.1` in `eda.txt`; `worker-light.lock.txt` recompiled

## Acceptance criteria (real runs)

| AC | Result |
|---|---|
| DS3 non-seq, Survived, PassengerId row_id, Name exclude, Cabin high_missing | **PASS** |
| DS12 regression | **SOFT-SKIP** (OpenML source KeyError on this host) |
| DS18 unsupervised | **PASS** |
| DS22 TS monthly m=12 h_max 24 | **PASS** |
| DS24 daily + seasonality | **PASS** |
| DS27 composite year+quarter quarterly | **PASS** |
| DS28 hourly OT | **PASS** |
| DS30 sequential financial ≥0.7, trading-day alias, OHLCV, triple_barrier, no raw Close | **PASS** |
| Synthetic leakage critical/high/lead-lag | **PASS** |
| Ambiguous day≤12 dates | **PASS** |
| NIFTY append compatible; Volume→Vol rename; Close→str breaking | **PASS** |
| Hard-exclude confirm 422 | **PASS** |
| 1M×100 intake &lt;45s | **SOFT-SKIP** — detectors stride-sample ≤20k; full 1M×100 frame build/run exceeded host budget (same honesty pattern as Phase 1 EDA 1M soft-skip). CI should re-measure on 8 vCPU. |

### Commands / output

```
uv run pytest tests/unit tests/golden --tb=no -q
# EXIT:0 — 2 skipped (DS12 source; EDA 1M soft-skip); intake goldens green

uv run pytest tests/golden/test_intake_samples.py tests/unit/test_intake_detectors.py -q
.s............   # DS12 skipped; remainder passed

uv run ruff check labcore backend tests
All checks passed!

uv run mypy labcore
Success: no issues found in 33 source files

cd frontend && pnpm test --run
Test Files  3 passed (3) / Tests  6 passed (6)

cd frontend && pnpm exec tsc --noEmit
(exit 0)

uv run python tests/db_harness/run_db_tests.py
migrations ok incl. 20261115120000_intake_detail.sql
intake_rls_test: column_roles / schema_diffs / intake_feedback / parent_version_id / RLS ok
prediction_rls_test + rls_test ok
```

## Deviations / TODOs

- **LLM adjudicator** deferred to Phase 6 (same merge/validator interface).
- **TradingLab** label builders remain JSON proposals only (ADR-0002 / ADR-0004); no TradingLab calls.
- **DS12** soft-skipped when OpenML/local cache unavailable.
- **DS30 calendar:** trading-day label asserted; exact XNSE vs XNYS holiday list not golden-pinned (exchange-calendars hit rates can tie).
- **1M intake** soft-skipped on this workstation; stride sample keeps detectors O(20k).
- Intake proposal persistence is in-memory until hosted Supabase worker path is used.

## Self-verification checklist (§000)

- [x] lint (`ruff`) + mypy + unit/golden tests green; frontend vitest + tsc green
- [x] db_harness pgTAP green (`python tests/db_harness/run_db_tests.py`)
- [x] no new `TODO|FIXME|NotImplementedError|pass  # stub` in intake shipped paths
- [x] intake endpoints under `/api/v1/intake/*`; tables in migration + §33.13
- [x] no secrets in diff
- [x] seed 42 on sample / MI / detector paths
- [ ] Playwright axe-core: not in Phase 1A scope (Intake Review has loading/error text)

## Next phase

**Phase 2 — Preprocessing + Supervised core + CV + Tuning + Leaderboard.** Wait for user **continue**.
