# ARW ML Lab — Build Plan

Live Page: https://cursor.com/canvas/store-e0b12a15-de4c-4810-858b-72090d8f0713/4ced1d9e-3efe-4a36-afca-1981b050bd2a

Source: ARCHITECTURE.md §30 (phased roadmap), v2.3. Build instructions: ../../CURSOR_PROMPT.md (§000). Progress: ../PROGRESS.md. Wind-up: ../FINAL_REPORT.md.

v2.3 (16 Nov 2026): backend hosting is a **Contabo Cloud VPS** (`docs/DEPLOY_CONTABO.md`); Vercel and Supabase unchanged; Render is the alternative / legacy path.

v2.2 additions: Phase **3A Prediction Studio** (§45 — batch upload + custom input form, prediction samples for all 33 datasets) and the stress-test hardening (§46, `docs/STRESS_TEST.md`) closed in Phase 8.2.

## 30. Phased roadmap

> Build order (18 phases, CURSOR_PROMPT §000): 0 → 1 → 8.1 → 1A → 2 → 2A → 3 → 3A → 4 → 4A → 5B → 5 → 5A → 6 → 6A → 6B → 7 → 8.2. Rows below are grouped by family, not by order.

| Phase | Scope | Exit criteria |
|---|---|---|
| **0 · Foundations** (1–2 wk) | GitHub monorepo, docker-compose for local dev (web, lab-core, worker, redis, supabase local stack via `supabase start`; AI via the hosted NVIDIA API with a dev key or a mocked provider), Supabase migrations + RLS skeleton, SP shell & theme, Supabase Auth (email OTP), module registry, CI | login → Home Terminal; sidebar with 13 modules; light/dark; CI green |
| **1 · Data + EDA** (2–3 wk) | upload/versioning, type inference, task-family wizard, all EDA tables/plots, education cards, rule-engine insights | all §10 artefacts on DS1/DS3/DS22/DS30; 1 M-row profiling < 60 s |
| **1A · AI Dataset Intake** (1–2 wk; LLM adjudicator wired in Phase 6) | §33: detectors D1–D8, Intake Review UI, versioning (append/replace/upsert), schema diff + drift, impact list | golden intake results on DS3/12/18/22/24/27/28/30 + synthetic leak |
| **2 · Preprocess + Supervised core** (3–4 wk) | recipes, all encoders/imputers/scalers, classical ML registry R*/C*, CV (non-financial), tuning presets, leaderboard, Classification and Regression Evaluation Suites (§41, §42), library-pinned requirements (§44) | DS3/DS12 end-to-end; every param editable; leakage tests pass; confusion matrix in counts + 3 normalisations and the full classification report on DS4/DS10; every metric as CV mean ± std |
| **3 · Explain + Predict + Uncertainty** (2–3 wk) | SHAP/LIME/PDP/ICE/ALE/permutation, calibration, conformal, single/batch/what-if prediction, registry + export | SHAP additivity; 90 % interval coverage 88–92 % on DS12; ONNX parity |
| **3A · Prediction Studio** (1–2 wk; after Phase 3) | §45: feature contracts, batch upload + validation report + downloads, auto-generated custom form, what-if, AI explanation, prediction tables/RLS, samples for DS1–DS33 | §45.13 tests; template round-trip; single/batch parity |
| **4 · Time Series** (3–4 wk) | analysis, tests, F* models (stat + ML + DL), backtesting, intervals, horizon guard | DS22–DS28 forecasts; horizon tests pass |
| **5 · Financial / sequential** (3–4 wk) | TradingLab vendoring + adapters: labeling, weights, purged K-fold, CPCV, FFD, feature packs, MDI/MDA/SFI, PBO, DSR/PSR, bet sizing, sequential DL (S*) | TradingLab contract tests pass; CPCV/PBO on DS30 |
| **5A · Walk-Forward Optimisation** (2–3 wk) | §32: window planner, purge/embargo, per-window re-tuning (inner purged CV, warm start, plateau selection), retrain policies, stitching, costs, WFE, parameter stability, MC/bootstrap/permutation, DSR with honest trial count, PBO from shared candidates, CPCV cross-check, UI + AI insights | planner property tests, purge parity with `ml_get_train_times`, synthetic edge/no-edge tests pass |
| **6 · Unsupervised + AI Insights** (3 wk) | D*/K*/A* registries; VLM adapters, prompts, validator, side panel, caching, streaming | insights schema-valid with 100 % citation validity on golden set |
| **7 · Enterprise & Portfolio Lab** (3–4 wk) | reports, monitoring/drift, SSO, quotas, observability, optional K8s/KEDA scale-out of workers (§39.12), Portfolio Lab (TradingLab `portfolio_optimization/` HRP/HERC/NCO/CLA/MVO, `online_portfolio_selection/`) | load & security tests pass; production deploy |
| **2A · Deep Learning full** (3 wk; after Phase 2) | §34: shared training engine, tabular T1–T16, sequential Q1–Q13, LR finder, all DL.T/DL.P artefacts, MC dropout / deep ensembles / conformal, CPU/GPU routing | DL smoke tests on DS3/DS12 CPU in < 10 min; GPU-only models refuse cleanly without a GPU worker |
| **4A · Time Series full** (3 wk; after Phase 4) | §35: TS EDA tables/plots, stationarity verdict matrix, breaks, Granger/CCF, all F* hyperparameters, multi-step strategies, exog, hierarchical reconciliation, metrics, residual diagnostics, leaderboards | DS22–DS28 full reports; metric unit tests vs reference values |
| **6B · Per-family catalogue completion** (2 wk; after Phase 6A) | §36: every REG/CLF/DR/CLU/ANO table and plot, KMO/Bartlett, trustworthiness/continuity, Shepard, gap statistic, bootstrap stability, external indices | catalogue tests: each artefact renders on its golden dataset |
| **5B · Financial labelling suitability** (1 wk; before Phase 5 labels) | §37: FS1–FS20 checks, grid preview, report, fallback | DS30 Suitable; airline Not suitable → fallback; synthetic FAIL cases |
| **6A · VLM decision agent** (2 wk; after Phase 6) | §38: VD1–VD12, baselines, guards, decision cards, audit, eval harness | 0 guard violations; agreement ≥ baseline on golden decisions; numbers-only fallback |
| **8 · Deployment** (8.1 after Phase 1; 8.2 after Phase 7) | §39 + `docs/DEPLOY_CONTABO.md`: Contabo VPS (hardening, `docker-compose.prod.yml`, Caddy HTTPS, GHCR + SSH deploy with rollback; `render.yaml` kept as legacy alternative), vercel.json, supabase migrations/RLS/storage, GitHub Actions CI/CD, env matrix, smoke tests; 8.2 closes §46 and `docs/STRESS_TEST.md` | §39.13 acceptance criteria; STRESS_TEST items closed |

---
