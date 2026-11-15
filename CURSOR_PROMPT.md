# Cursor build prompt — "ARW ML Lab"

> **How to use:** open the project folder (`Machine Learning Lab`) in Cursor. The folder already contains `AGENTS.md`, `.cursor/rules/*.mdc`, `docs/ARCHITECTURE.md`, `docs/FLOWCHART.md`, `docs/diagrams/`, `data/samples/`, `render.yaml`, `frontend/vercel.json`, `supabase/`, `.github/workflows/` and `.env.example`. The quickest start is the short message in `CURSOR_KICKOFF.md`; it points the agent at this file. You can also paste this whole file (or type `@CURSOR_PROMPT.md build Phase 0`).
> This prompt is self-contained, but `docs/ARCHITECTURE.md` holds the full catalogues — algorithm IDs R*, C*, S*, T*, Q*, D*, K*, A*, F*, encoder IDs E*, dataset IDs DS*, check IDs FS*, decision IDs VD*, evaluation artefact IDs CLE.* (classification, §41) and REE.* (regression, §42), section numbers §n — which you must implement exactly. **§44 is the Library Matrix: every algorithm, encoder, metric, test and plot computation comes from a library listed there (rule `.cursor/rules/70-use-established-libraries.mdc`).**
> **Phase order (18 phases):** 0 → 1 → **8.1** (hosted skeleton) → 1A → 2 → **2A** → 3 → **3A** (Prediction Studio) → 4 → **4A** → **5B** → 5 → 5A → 6 → **6A** → **6B** → 7 → **8.2** (production hardening). The execution protocol (§000) defines done, the no-stub rules, the self-check and how to resume.
> Work **phase by phase**. Do not start a phase until the previous phase's acceptance criteria pass in CI. After each phase write `docs/PHASE_<n>_REPORT.md` (what was built, test results, deviations, TODOs), update `docs/PROGRESS.md`, commit, then stop and wait for the user to say "continue".

---

## 00. Cursor operating instructions (read before anything else)

**Models and modes**
* **Plan first with the strongest reasoning model available.** For every phase, switch to **Plan mode** and pick the most capable deep-reasoning model in the model picker (the top "thinking"/reasoning model, at its **highest reasoning effort**; turn off "Auto" for planning). Produce a written plan (`docs/plans/PHASE_<n>_PLAN.md`) listing files, contracts, tests and risks, and get it approved by the user before building.
* **Build in Agent mode.** Use the same top reasoning model for complex work (CV/purging, labelling, metrics, RLS, the VLM validator, deployment). A faster coding model is acceptable only for mechanical edits (renames, boilerplate, styling), and its output must still pass the same tests.
* **Long context:** if the workspace is on a legacy request-based plan, enable **Max Mode** for planning and for any task that reads `docs/ARCHITECTURE.md` in full (~340 KB). On current plans, choose a model with a long context window and reference sections with `@docs/ARCHITECTURE.md` plus the section number instead of pasting the file.
* Model names change often; do not hard-code one. If unsure which is strongest, pick the model the picker marks as best for reasoning/agentic coding at maximum effort.

**Project rules and context**
* Follow `AGENTS.md` and every rule in `.cursor/rules/` (they are always applied or scoped by glob). If a rule conflicts with this prompt, the rule wins; record the conflict in the phase report.
* Reference documents with `@` (e.g. `@docs/ARCHITECTURE.md §35.7`, `@docs/diagrams/16_vlm_decision_loop.png`). Read the diagrams; they are part of the spec.
* Keep a running `docs/DECISIONS.md` (architecture decision records) and `docs/TODO.md`.
* Use the terminal for real verification: run tests, linters and builds yourself; paste the key output into the phase report. **Never invent test results, metrics, benchmark numbers or plot values** — every number in a report must come from a run you executed.
* Default seed **42** everywhere.

**Hosted AI (ARCHITECTURE §40)**
* Do not self-host any model. Use `labcore/ai` with the NVIDIA API catalog (`https://integrate.api.nvidia.com/v1`). The user creates the NVIDIA Developer account and API key at build.nvidia.com and puts `NVIDIA_API_KEY` into Render and local `.env` themselves; never ask them to paste it into chat.
* The free key is a **trial** for development and testing. Remind the user that production use needs an NVIDIA AI Enterprise licence, a paid partner endpoint or another paid provider. Rate limits are per model and not published (~40 RPM observed), so design for 429s.
* Use mocked providers in CI; run live AI tests only as a manual/nightly job with the user's key.

**Accounts, repos and deployment (Phase 8)**
* The target is a **GitHub monorepo** deployed to **Vercel** (frontend), **Render** (FastAPI web service + Celery background workers + Key Value via `render.yaml`) and **Supabase** (Postgres + Auth + Storage + RLS, migrations via the Supabase CLI) — see `docs/ARCHITECTURE.md §39`.
* Before any action that creates or changes something outside this folder — creating the GitHub repository (and choosing private visibility), pushing, connecting Vercel/Render/Supabase, buying or upgrading a plan, setting production secrets, running `supabase db push` against a hosted project — **ask the user to confirm** in chat and use their own logged-in CLIs (`gh`, `vercel`, `supabase`, Render dashboard / Blueprint). Never paste secrets into code, commits or chat; put them in platform settings and `.env` (git-ignored).
* The reference repositories are private. Clone them with the user's GitHub credentials (`gh repo clone …`) into `refs/` (git-ignored) or read them through GitHub; never commit their code into this repo except the pinned TradingLab submodule under `vendor/`.

## 000. Execution protocol (binding — read with §00)

**Phase order (18 phases, do not reorder):**

| # | Phase | Spec (ARCHITECTURE) | Needs | Test layers that must be green before "done" |
|---|---|---|---|---|
| 1 | 0 Foundations | §3–§8, §39.5, §44 | — | unit, `supabase test db`, lint/type, build |
| 2 | 1 Data + EDA + Education | §9, §10, §24, §27 | 0 | unit, golden (EDA numbers), e2e smoke |
| 3 | 8.1 Hosted skeleton | §39 | 1 | deploy smoke on the hosted stack |
| 4 | 1A AI Dataset Intake | §33 | 1 | unit, golden intake |
| 5 | 2 Preprocess + Supervised + CV + Tuning | §11–§16, §41, §42 | 1A | unit, leakage tests, golden metrics, snapshot plots |
| 6 | 2A Deep Learning | §34 | 2 | DL smoke, unit |
| 7 | 3 Explain + Predict + Uncertainty + Registry | §17, §21, §22, §25 | 2 | unit, coverage tests, ONNX parity |
| 8 | **3A Prediction Studio** | **§45**, §46 | 3 | `tests/unit/test_predict_samples.py`, validator tests PV01–PV16, parity, pgTAP `prediction_rls_test.sql`, Playwright |
| 9 | 4 Time Series | §19, §20 | 3A | unit, horizon tests, golden forecasts |
| 10 | 4A Time Series full | §35 | 4 | unit, catalogue tests |
| 11 | 5B Financial suitability | §37 | 4A | unit FS1–FS20 |
| 12 | 5 Financial / sequential | §13 (purged K-fold, CPCV), §15, TradingLab (§1.3) | 5B | contract_tradinglab, purging tests |
| 13 | 5A Walk-forward | §32 | 5 | unit, golden WFO |
| 14 | 6 Unsupervised + AI Insights | §18, §23, §40 | 5A | unit, insights validator, mocked provider |
| 15 | 6A VLM decision agent | §38 | 6 | guard tests, eval harness |
| 16 | 6B Per-family catalogue | §36 | 6A | catalogue tests |
| 17 | 7 Reports, Monitoring, Enterprise | §25, §26, §46.4 | 6B | e2e, load (Locust), ZAP |
| 18 | 8.2 Production hardening | §39, **§46** | 7 | §39.13 AC, `docs/STRESS_TEST.md` items closed |

**Definition of done for every phase** — a phase is done only when all of these hold:
1. Every AC checkbox of the phase passes, run by you in the terminal; the command and its real output are pasted into `docs/PHASE_<n>_REPORT.md`.
2. All earlier phases' tests still pass (`make test`), lint and type checks are clean, the frontend builds.
3. New code has tests in the layers listed above; new registry keys have ExplainCards; new libraries are in §44 and `backend/requirements/` (rule 70).
4. Migrations apply on an empty database (`supabase db reset`) and pgTAP tests pass; RLS covers every new table and bucket.
5. `docs/PROGRESS.md` is updated (see "Resume") and the work is committed with message `phase <n>: <summary>`.
6. You stop and report: what was built, test results, deviations, open TODOs, and what the next phase will do. Wait for "continue".

**Do not skip, stub or fake:**
* No `pass`, `TODO`, `NotImplementedError`, mock data or hard-coded numbers in shipped code paths. Mocks are allowed only in tests (AI provider, network) and must be named `fake_*`/`mock_*`.
* Do not mark an AC as passed without running it. Do not delete, skip (`@pytest.mark.skip`, `xfail`, `.only`) or weaken a failing test to go green — fix the cause or record the blocker in the report and stop.
* Do not replace a specified library with your own implementation (rule 70) and do not silently change a specified behaviour; record any deviation with a reason in `docs/DECISIONS.md`.
* If something in the spec is contradictory or impossible, stop and ask; do not guess silently. `docs/ARCHITECTURE.md §46` wins over older sections; rules in `.cursor/rules/` win over this prompt.
* Never invent metrics, plot values or benchmark numbers (rule 20).

**Self-verification checklist (run at the end of every phase and paste the result into the report):**
- [ ] `make lint` and `make test` green (paste the summary lines).
- [ ] `supabase db reset && supabase test db` green (or `python tests/db_harness/run_db_tests.py` when Docker is unavailable — say which).
- [ ] `rg -n "TODO|FIXME|NotImplementedError|pass  # stub" labcore backend frontend/src` shows no new hits in shipped code.
- [ ] Every endpoint added this phase is in `docs/ARCHITECTURE.md §6.2`/§45.7 with the same path and method; every new table in §7/§45.10 and in a migration with RLS.
- [ ] No secret in the diff (`git diff --cached | rg -i "nvapi-|service_role|secret"` is empty); `NVIDIA_API_KEY` only in backend settings.
- [ ] Seed 42 used in every new random path; library versions recorded on runs.
- [ ] Screens added this phase have empty, loading and error states, keyboard access, and pass axe-core in Playwright.

**Resume after an interruption (new chat, crash, context limit):** keep `docs/PROGRESS.md` current with: current phase, last completed step, last green commit hash, open failures, next action. On restart: read `AGENTS.md`, this file's §00/§000, `docs/PROGRESS.md` and the last `docs/PHASE_<n>_REPORT.md`; run `git status` and `make test`; continue from "next action". Never restart a finished phase or rewrite finished work unless a test proves it broken.

---

## 0. Your role and ground rules

You are a senior full-stack ML engineer building a **production-grade, general-purpose Machine Learning Lab web app** for Anand Rathi Wealth (owner: Shibayan Biswas).

* **Data scope:** any **tabular** dataset (numeric + categorical + datetime). No NLP/text modelling.
* **Families:** users choose **Supervised** (auto-detected regression vs classification; **Sequential** e.g. financial, or **Non-sequential**), **Unsupervised** (dimensionality reduction, clustering, anomaly detection) or **Time Series** (analysis + forecasting).
* **Stages:** the lab runs EDA → preprocessing → modelling with every hyperparameter customisable → cross-validation and tuning → leaderboard and best-model selection → explainability → prediction with uncertainty → reports, export and registry.
* **Education:** every algorithm, metric, plot and test carries its LaTeX math and theory.
* **AI Insights:** a **hosted** vision-language model (NVIDIA API catalog, OpenAI-compatible, §40) reads every plot and table and writes grounded insights; a numbers-only mode works offline.

Non-negotiable engineering rules:
1. **Leakage-safe by construction.** Every fitted transform (imputer, encoder, scaler, selector, resampler, FFD d*) lives inside a pipeline that is fit **per CV fold on train rows only**. Resampling (SMOTE etc.) only uses `imblearn.pipeline.Pipeline`. Sequential data never shuffles.
2. **Registry-driven.** Algorithms, params, metrics, plots, CV schemes, encoders, tests and explanations are declared once in Python registries and exposed via `GET /catalog`. The frontend renders forms, tables and info cards generically from that catalogue. **Never** hand-code a form per algorithm.
3. **Plots are data.** Every plot is an `Artefact` holding a Plotly JSON spec, a PNG rendered with kaleido, and a `numbers` JSON of the exact values behind it. The UI, reports and the VLM all consume the same object.
4. **Every computation is a job.** Jobs are idempotent Celery tasks, cached by content hash `sha256(dataset_version, recipe, algo, params, cv, seed, lib_versions)`. Progress streams over SSE.
5. **Reproducible.** Global default seed **42** goes to numpy, random, torch, `random_state` and Optuna samplers. Library versions and the data hash are stored on every run.
6. **Typed end-to-end.** Use Pydantic v2 on the backend, zod on the frontend (generated from backend JSON Schema), mypy + ruff, and eslint + `tsc --noEmit`.
7. **Tests first for math.** Splitters, labelers, metrics, horizon rules and the insights validator get unit tests before the UI.
8. **Hosted AI, no self-hosting.** VLM/LLM calls go through `labcore/ai` (ARCHITECTURE §40) to the **NVIDIA API catalog** (`https://integrate.api.nvidia.com/v1`) with `NVIDIA_API_KEY` held **only by the Render backend**. Other providers (Gemini, OpenRouter, Groq) are optional fallbacks, **disabled by default**. No paid provider without an admin-set spend cap. Numbers-only mode is always available.
9. **Secrets.** Use `.env` files only (git-ignored), keep `.env.example` current with the per-platform matrix (ARCHITECTURE §39.10), and never commit secrets.
10. **No heavy compute on Vercel.** Vercel functions only do auth, signed URLs and light proxying; all data/ML work runs in Render workers (§39.4).
11. **Never fabricate.** Metrics, plots, tables and AI insights must be computed from real runs; placeholders are labelled as such and fail CI if they reach a report.
12. **Human approval for AI decisions.** The VLM decision agent (§38) proposes; deterministic guards and the user decide.
13. **Use established libraries only.** Every algorithm, encoder, transformer, metric, statistical test and plot computation must call a popular, maintained library from the Library Matrix (ARCHITECTURE §44) at the pinned version in `backend/requirements/*.txt`. Lab code may only be a thin wrapper (argument mapping, arranging outputs, arithmetic on library outputs such as NPV from a confusion matrix, Plotly rendering). Do not re-implement a formula that a listed library already provides. Need something new? Propose the library (licence, release date, maintainer activity) in the phase report and update §44 and the requirements files first. Items marked optional/off by default in §43 stay off unless the user enables them.
14. **Evaluation is complete, not sampled.** Every classification run produces the full §41 suite and every regression run the full §42 suite (on CV out-of-fold, per fold, CV-aggregated and test splits), with the split shown on every artefact.

---

## 1. Reference repositories (read them first)

The repos are private. Clone them with the user's GitHub credentials into `refs/` (git-ignored; the project kit deliberately ships **without** copies of their code), or read them through GitHub.

### 1.1 `ShibayanBiswas/sp-workstation` — **visual design language (must match)**

The UI must look like the SP Workstation modules.

* **Copy the design tokens and component classes** from `src/app/globals.css`:
  * Tokens: `--gold #c9a227`, `--gold-soft #e4d5a0`, `--gold-deep #9a7b1a`. Light `--bg #f7f9fc`, `--bg-elevated #fff`, `--fg #152033`. Dark `--bg #050506`, `--bg-elevated #0e0e10`, `--fg #f4f2ec`, `--border rgba(229,207,148,.10)`.
  * Fonts: Cormorant Garamond for display, DM Sans for body, IBM Plex Mono for numbers.
  * Classes: `panel-luxe`, `glass-panel`, `section-kicker`, `gold-gradient`, `status-pill`, `live-sync-pill`, `module-tile`, `tape-chip`, `terminal-header-luxe`, `fin-num`, `animate-rise`.
* **Reuse the shell pattern** from `src/components/DashboardShell.tsx` and `src/components/Sidebar.tsx`:
  * Sidebar is 280 px wide and collapses to 76 px; the collapsed state persists in `localStorage`.
  * Brand at the top, then a "Home Terminal" link, then a small-caps "MODULES" kicker.
  * Each module row has an icon badge, a label and a chevron. It expands to a gold-ruled nested `NavItem` tree.
  * User card with an initials avatar on a gold gradient; Light/Dark toggle; Sign out.
  * On mobile: a drawer plus a top bar.
* **Reuse the module registry pattern** from `src/data/modules.ts`, i.e. the `ModuleGroup`/`NavItem` types. Every module follows the same sub-page rhythm: **Home · Analytics · Workbench · domain pages · Intel (Logic Atlas) · Upload**.
* **Auth pattern (look only):** reuse the SP login screen design, but implement auth with **Supabase Auth** (email OTP / magic link with a company-domain allow-list; `@supabase/ssr` cookies) — ARCHITECTURE §39.5.
* Modules are **in-app routes**, not iframes. Keep `modules.ts` compatible so the lab can later be embedded in SP Workstation as one more `ModuleGroup`.

### 1.2 `ShibayanBiswas/blackcarbon-saas` — **ML UX, stack split and code structure**

* **Architecture split:** web → gateway → Python FastAPI ML service, with an ML package structured as `backend/ml/{data, preprocess, eda, pipeline, train, explain, predict, registry}` plus `config.py` and `plot_style.py`.
* **`frontend/components/ExplainCard.jsx`** and **`frontend/content/explanations.js`**: an expandable card with intuitive text, detail, KaTeX display and inline math, and a literature reference. Port it to TypeScript as `ExplainCard.tsx` and generalise the content registry.
* **`backend/ml/pipeline/param_grids.py`**: per-model search grids with presets fast/balanced/thorough. Rename them **Quick/Balanced/Thorough/Exhaustive** and turn them into the "Use defaults" side of the param-spec system.
* **`frontend/pages/Modeling.jsx`**:
  * the model × scaler grid becomes a **model × recipe** grid;
  * the metrics table (mean ± std on validation, then test) and the diagnostic plots (pred vs actual, residuals, residual distribution, Q-Q) are kept and made interactive.
* **`backend/ml/eda/run.py`**: EDA plots (hist, box, violin, strip, beeswarm, letter-value, raincloud, KDE, Q-Q, ECDF, pairplot, heatmap, PCA scree/2D/3D, scaler comparison). Port all of them to Plotly.
* **`infra/schema.sql`**: a starting point only; extend it to the multi-tenant schema in §7.

### 1.3 `ShibayanBiswas/ml-for-trading` (package `tradinglab`) — **financial and sequential toolkit (mirror exactly)**

Vendor it as a git submodule at `vendor/tradinglab`, pinned to a commit, and install it with `pip install -e vendor/tradinglab`. **Do not re-implement what it provides.** Wrap it in `labcore/finance/` adapters that make it work with sklearn Pipelines, Optuna and the CV visualiser. Files and functions to use:

| Purpose | TradingLab file → function/class |
|---|---|
| Purged K-fold + embargo | `tradinglab/cross_validation/time_series_cv.py` → `PurgedKFold(n_splits, samples_info_sets, pct_embargo)`, `PurgedSplit`, `ml_get_train_times(samples_info_sets, test_times)`, `ml_cross_val_score(classifier, X, y, cv_gen, sample_weight_train, sample_weight_score, scoring)` |
| CPCV | `tradinglab/cross_validation/combinatorial.py` → `CombinatorialPurgedKFold(n_splits, n_test_splits, samples_info_sets, pct_embargo)`, its backtest-path assembly, `_get_number_of_backtest_paths` (returns N−1, which is valid only for k=2; the adapter must compute φ(N,k) = (k/N)·C(N,k) and assert equality when k=2) |
| Triple barrier / meta-labelling | `tradinglab/labeling/triple_barrier_labeling.py` → `add_vertical_barrier`, `get_events(close, t_events, pt_sl, target, min_ret, num_threads, vertical_barrier_times, side_prediction)`, `get_bins(triple_barrier_events, close)` (meta-labels when `side` is given), `drop_labels` |
| Other labelers | `tradinglab/labeling/{fixed_time_horizon.py, trend_scanning.py, excess_over_mean.py, excess_over_median.py, raw_return.py, return_vs_benchmark.py, tail_sets.py, matrix_flags.py}` |
| Event sampling | `tradinglab/filters/event_filters.py` → `cusum_filter`, `z_score_filter` |
| Volatility | `tradinglab/util/volatility.py` → `get_daily_vol`, `get_parksinson_vol`, `get_garman_class_vol`, `get_yang_zhang_vol` |
| Uniqueness / concurrency | `tradinglab/sampling/concurrent.py` → `num_concurrent_events`, `get_av_uniqueness_from_triple_barrier` |
| Sequential bootstrap | `tradinglab/sampling/bootstrapping.py` → `get_ind_matrix`, `get_ind_mat_average_uniqueness`, `seq_bootstrap` |
| Sample weights | `tradinglab/sample_weights/attribution.py` → `get_weights_by_return`, `get_weights_by_time_decay` |
| Fractional differentiation | `tradinglab/features/fractional_differentiation.py` → `get_weights_ffd`, `frac_diff_ffd(series, diff_amt, thresh)`, `plot_min_ffd` (choose the minimum d passing ADF; **fit d* on train rows only**) |
| Bars | `tradinglab/data_structures/{standard_data_structures.py, imbalance_data_structures.py, run_data_structures.py, time_data_structures.py}` → `get_tick_bars`, `get_volume_bars`, `get_dollar_bars`, `get_time_bars`, `get_ema_*_imbalance_bars`, `get_const_*_imbalance_bars`, `get_*_run_bars` |
| Microstructure | `tradinglab/microstructural_features/` → `get_roll_measure`, `get_corwin_schultz_estimator`, `get_bar_based_kyle_lambda`, `get_bar_based_amihud_lambda`, `get_bar_based_hasbrouck_lambda`, `get_vpin`, entropies, `MicrostructuralFeaturesGenerator` |
| Structural breaks | `tradinglab/structural_breaks/{chow.py, cusum.py, sadf.py}` → `get_chow_type_stat`, `get_chu_stinchcombe_white_statistics`, `get_sadf` |
| Feature importance | `tradinglab/feature_importance/importance.py` → `mean_decrease_impurity`, `mean_decrease_accuracy`, `single_feature_importance`, `plot_feature_importance`; `orthogonal.py` → `get_orthogonal_features`, `feature_pca_analysis`; `fingerprint.py` → `RegressionModelFingerprint`, `ClassificationModelFingerprint` |
| Feature clustering | `tradinglab/clustering/onc.py` → `get_onc_clusters`; `feature_clusters.py` → `get_feature_clusters` |
| Codependence | `tradinglab/codependence/` → `distance_correlation`, `get_mutual_info`, `variation_of_information_score`, `angular_distance`, `get_dependence_matrix`, `get_distance_matrix`, GNPR |
| Ensemble | `tradinglab/ensemble/sb_bagging.py` → `SequentiallyBootstrappedBaggingClassifier/Regressor` |
| Bet sizing | `tradinglab/bet_sizing/bet_sizing_core.py` → `bet_size_probability`, `bet_size_dynamic`, `bet_size_budget`, `bet_size_reserve`; `ef3m.py` → `M2N` |
| Backtest statistics | `tradinglab/backtest_statistics/strategy_metrics.py` → `sharpe_ratio`, `information_ratio`, `probabilistic_sharpe_ratio`, `deflated_sharpe_ratio`, `minimum_track_record_length`, `drawdown_and_time_under_water`, `bets_concentration`, `all_bets_concentration`, `average_holding_period`, `timing_of_flattening_and_flips`; `campbell.py` → `CampbellBacktesting` (haircut Sharpe, profit hurdle) |
| Multi-product | `tradinglab/multi_product/etf_trick.py` → `ETFTrick`, `get_futures_roll_series` |
| Portfolio (Phase 7) | `tradinglab/portfolio_optimization/{hrp.py, herc.py, nco.py, cla.py, mean_variance.py, risk_estimators.py, returns_estimators.py, tic.py}`, `tradinglab/online_portfolio_selection/*` |
| Samples / synthetic | `tradinglab/datasets/sample_loaders.py`; `tradinglab/util/generate_dataset.py` → `get_classification_data` |

The function names above come from the repo's docs and tree. **Open each file and confirm the exact signatures before wrapping.** Where a name differs, follow the repo and record the difference in the phase report.

**PBO is NOT in TradingLab.** Implement it in `labcore/finance/pbo.py` following Bailey, Borwein, López de Prado & Zhu (2017), "The Probability of Backtest Overfitting" (CSCV):
1. Build the T×M matrix of OOS performance per period for M configurations: tuning trials, models, or CPCV paths.
2. Split the T rows into S even blocks (default S = 16).
3. For every one of the C(S, S/2) combinations, find the in-sample best configuration. Then compute its OOS relative rank ω̄ and the logit λ = ln(ω̄/(1−ω̄)).
4. **PBO = P(λ ≤ 0).**
5. Also output: the logit histogram, the IS-vs-OOS scatter with the degradation slope, the probability of loss, and stochastic dominance.

**Porting notes:**
* Replace pandas `iteritems` → `items`.
* Avoid mutable `RandomState` default arguments.
* Force `num_threads=1` inside Celery workers (no nested multiprocessing).
* Suppress or annotate deprecation warnings.
* **Re-run TradingLab's own tests as contract tests:**
  * `tradinglab/tests/cross_validation/test_cross_validation.py`
  * `tradinglab/tests/cross_validation/test_combinatorial_cross_validation.py`
  * `tradinglab/tests/labeling/test_labels.py` and the other `tests/labeling/test_*.py`
  * `tradinglab/tests/backtest_sampling/{test_sampling.py, test_sample_weights.py, test_backtest_statistics.py, test_backtests.py, test_bet_sizing.py, test_ef3m.py}`
  * `tradinglab/tests/features/{test_fractional_differentiation.py, test_filters.py, test_volatility_features.py, test_microstructural_features.py}`

---

## 2. Tech stack (use these unless a phase report justifies a change)

* **Frontend:**
  * Framework and styling: Next.js 16 (App Router) + React 19 + TypeScript 5 + Tailwind CSS 4 + the SP tokens; `lucide-react`; Radix UI primitives; `cmdk`.
  * Data and forms: TanStack Query v5, TanStack Table + Virtual, `zustand`, `react-hook-form` + `zod`.
  * Charts: **Plotly.js** (`react-plotly.js`, lazy) for scientific plots, **lightweight-charts** for OHLC, equity curves and price forecast fans, and `recharts` for sparklines.
  * Math and export: `katex`; `exceljs` and `jspdf` for client exports.
  * The Next.js server (on **Vercel**) acts as a thin **BFF**: Supabase Auth session (`@supabase/ssr`), RBAC, Supabase Storage signed upload URLs, light proxying, rate limits. SSE goes browser → `lab-api` directly.
* **Backend — "lab-core":**
  * Service: Python 3.12, FastAPI + Pydantic v2.
  * Jobs: Celery 5 + Redis 7. Queues: `q.ingest`, `q.eda`, `q.train.cpu`, `q.train.gpu`, `q.tune`, `q.explain`, `q.forecast`, `q.insights`, `q.report`, `q.predict.batch`.
  * Storage: **Supabase Postgres 17** (SQLAlchemy 2 for access; schema owned by **Supabase CLI migrations** in `supabase/migrations/`, not Alembic), **Supabase Storage** (S3-compatible; replaces MinIO), MLflow 3.x optional (backend on Supabase Postgres, artefacts on Supabase Storage) or the lab's own registry tables.
  * Broker: **Render Key Value** (Redis-compatible, `noeviction`) in hosted mode; Redis 7 container locally.
  * Data handling: Polars/pandas 2 + PyArrow + DuckDB.
* **ML libraries (exact pins in `backend/requirements/*.txt`; full list with licences in ARCHITECTURE §44):**
  * Python **3.12**; numpy 2.4.x, scipy 1.17.x, pandas 2.3.x (pandas 3 blocked by pytorch-tabular), scikit-learn 1.9.1. Resolve with `uv pip compile` and commit the `*.lock.txt` files; do not bump a pin without re-resolving the whole worker image.
  * Classical and boosting: scikit-learn 1.9.x, imbalanced-learn, category_encoders, feature-engine, skrub, XGBoost, LightGBM, CatBoost, NGBoost, quantile-forest, glum, imodels.
  * Evaluation and statistics (§41, §42): sklearn.metrics, imbalanced-learn metrics, netcal, model-diagnostics, MLstatkit (DeLong), mlxtend (5×2cv), statsmodels, scipy.stats, scikit-posthocs, fairlearn (slices), cleanlab (label issues), scikit-plots (gain/lift), MAPIE, crepes, venn-abers, scoringrules.
  * Deep learning: PyTorch 2 (CPU wheels on Render) + Lightning, pytorch-tabular (MLP, TabNet, FT-Transformer, TabTransformer, NODE, GANDALF, AutoInt, DANet, GATE, MDN, SSL), pytorch-forecasting, pytorch-tcn, captum; sequential Q-models from built-in `torch.nn` layers (§43.3). ResNet-MLP, SAINT and DCN-v2 are optional/off (no compatible maintained library, §43.4); TabPFN off (licence).
  * Time series: statsmodels, statsforecast, neuralforecast, mlforecast, hierarchicalforecast, utilsforecast, `arch`, pmdarima, Prophet, sktime, skforecast, darts, aeon (sequence classifiers), tslearn, tsfresh, tsfel, stumpy, ruptures.
  * Unsupervised: umap-learn, hdbscan, openTSNE, pacmap, trimap, pyod + pythresh, tslearn, minisom, prince, kmodes (optional), scikit-fuzzy (optional). K-Medoids, PHATE, Anchors (alibi), DEC and autoencoder DR are optional/off (§43.5, §43.11).
  * Tuning: Optuna 5 + optuna-integration (all samplers/pruners and `optuna.visualization` plots, §43.11).
  * Explainability: shap, lime, PyALE, dice-ml, interpret, captum, dtreeviz, shapiq (optional). **Not alibi** (BSL-1.1; licence review only).
  * Uncertainty: MAPIE, NGBoost, `scoringrules`.
  * Export: skl2onnx, onnxmltools.
  * Plotting: plotly + kaleido.
  * Reports: WeasyPrint/Quarto, python-pptx, openpyxl.
* **AI (hosted, §40):** OpenAI Python SDK pointed at the **NVIDIA API catalog** (`https://integrate.api.nvidia.com/v1`, `NVIDIA_API_KEY`).
  * Primary VLM: **`nvidia/nemotron-3.5-super-vl-120b-a12b`**; fallbacks `google/gemma-4-31b-it` → `meta/llama-3.2-90b-vision-instruct`; fast tier `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`.
  * Text reasoning LLM: **`nvidia/nemotron-3-super-120b-a12b`**; fallbacks `deepseek-ai/deepseek-v4.1-flash` → `openai/gpt-oss-20b`; Deep mode `nvidia/nemotron-3-ultra-550b-a55b`.
  * Model IDs live in `labcore/ai/providers.yaml` and are probed at startup (`GET /v1/models` + a tiny probe); verify them on build.nvidia.com before Phase 6 because the catalog changes.
  * Optional fallback providers: Gemini API, OpenRouter, Groq, or any OpenAI-compatible endpoint — disabled by default.
  * Offline fallback: numbers-only mode (rule engine).
* **Infra and quality:**
  * Infra: **GitHub monorepo → Vercel (frontend) + Render Blueprint `render.yaml` (lab-api web service, lab-worker-light and lab-worker-train background workers, lab-kv Key Value) + Supabase (Postgres, Auth, Storage, RLS)**; Docker Compose + `supabase start` for local dev; Kubernetes + KEDA only as an optional later worker scale-out (§39.12).
  * Observability: OTel, Prometheus, Grafana, Loki, Sentry, Flower.
  * Testing: pytest + hypothesis, Vitest, Playwright, Locust.
  * Tooling and CI: ruff, mypy, eslint, pre-commit, GitHub Actions.

---

## 3. Repository layout (create exactly; the kit already has the top level)

```
Machine Learning Lab/                 (git repo root → GitHub monorepo "arw-ml-lab")
├─ AGENTS.md  CURSOR_PROMPT.md  CURSOR_KICKOFF.md  README.md  .env.example  .gitignore  render.yaml
├─ .cursor/rules/*.mdc                project rules (do not delete; extend when you learn something)
├─ .github/workflows/{ci.yml, deploy.yml}
├─ frontend/                          Next.js 16 app → Vercel (Root Directory = frontend)
│   ├─ vercel.json
│   └─ src/app/{(auth)/login, (lab)/layout.tsx, (lab)/page.tsx (Home Terminal),
│              (lab)/{data,eda,preprocess,supervised,unsupervised,timeseries,explain,predict,experiments,reports,learn,admin},
│              api/…}  src/components/{shell,panels,plots,forms,tables,insights,decisions,education}
│              src/lib/{modules.ts, api.ts, sse.ts, supabase/, theme.ts, schemas/}  src/content/explanations/
├─ backend/                           FastAPI lab-api + Celery app → Render (Dockerfile)
│   ├─ app/{main.py, routers, schemas, services, deps, security}
│   └─ worker/{celery_app.py, tasks/}
├─ labcore/                           pure-Python ML library used by the workers
│   └─ {data,intake,eda,preprocess,supervised,deep,unsupervised,timeseries,cv,tuning,finance,suitability,
│       explain,uncertainty,predict,insights,decisions,plots,registry,reports,ai,eval}
│      # finance/: wfo.py, costs.py, montecarlo.py, pbo.py; suitability/: checks FS1–FS20; decisions/: VD1–VD12
├─ vendor/tradinglab/                 git submodule (pinned)
├─ supabase/{config.toml, migrations/*.sql, seed.sql, tests/*.sql (pgTAP RLS tests)}
├─ data/samples/{*.csv, urls.txt, datasets_manifest.json, presets/*.yaml, predict/ (prediction samples + contracts/)}
├─ scripts/make_predict_samples.py      regenerates data/samples/predict (seed 42)
├─ tests/{unit,contract_tradinglab,golden,e2e,load,db_harness}
├─ infra/{docker-compose.yml, k8s/ (optional)}
└─ docs/{ARCHITECTURE.md, FLOWCHART.md, STRESS_TEST.md, GAP_AUDIT.md, contracts/, diagrams/, plans/, PHASE_<n>_REPORT.md, PROGRESS.md, DECISIONS.md}
```

---

## 4. Core contracts (implement in Phase 0–1 and keep stable)

### 4.1 AlgorithmSpec (Python, `labcore/registry/spec.py`)

```python
class ParamSpec(BaseModel):
    name: str; type: Literal["int","float","categorical","bool","str","int_or_none","float_or_none","tuple"]
    default: Any; low: float|None=None; high: float|None=None; log: bool=False; step: float|None=None
    choices: list[Any]|None=None; condition: str|None=None   # e.g. "penalty == 'elasticnet'"
    help_key: str                                           # education registry key
    presets: dict[Literal["quick","balanced","thorough","exhaustive"], list[Any]|dict]  # search space per preset
class AlgorithmSpec(BaseModel):
    id: str            # e.g. "R17", "C9", "K5", "F23"
    key: str           # e.g. "reg.lightgbm"
    family: Literal["regression","classification","sequential","dr","clustering","anomaly","forecast"]
    name: str; library: str; estimator: str   # import path
    params: list[ParamSpec]; supports: set[str]   # {"sample_weight","predict_proba","multioutput","gpu","categorical_native","early_stopping","partial_fit"}
    min_rows: int=0; max_rows_hint: int|None=None; needs_scaling: bool; handles_missing: bool
    edu_key: str; tags: list[str]
```

The UI shows a **"Use defaults / Customise"** toggle per algorithm:
* **Defaults** = the library defaults plus the chosen preset's search space. The **Balanced** preset is the default; it searches a rich grid, e.g. LightGBM `num_leaves [15,31,63,127]`, `learning_rate log[0.01,0.3]`, `n_estimators [200..2000]` with early stopping, `min_child_samples [5..100]`, `subsample [0.6..1]`, `colsample_bytree [0.5..1]`, `reg_alpha/lambda log[1e-8,10]`.
* **Customise** exposes every ParamSpec with validation, conditional visibility, "fix value" vs "search range", and reset.

### 4.2 Artefact envelope

```json
{"id":"EDA.P.HIST.Age","kind":"plot|table|metric","stage":"eda","title":"Histogram — Age",
 "plotly":{...}, "png_uri":"s3://…/EDA.P.HIST.Age.png", "numbers":{"n":891,"mean":29.7,"skew":0.39,"bins":[...]},
 "edu_key":"plot.histogram","run_id":null,"dataset_version_id":"…","created_at":"…"}
```

### 4.3 Job / SSE

* Endpoints: each resource's create call (e.g. `POST /experiments/{id}/runs`, `POST /predict/batch`) returns `202 {job_id}` and accepts an `Idempotency-Key` header; generic `GET /jobs/{id}`, `GET /jobs/{id}/events` (SSE, served by `lab-api` directly — never through a Vercel function) and `POST /jobs/{id}/cancel` (calls the `request_job_cancel()` RPC). See ARCHITECTURE §6.2.
* Events: `progress {pct, step, eta}`, `log`, `partial_result` (leaderboard rows as folds finish), `artefact`, `done`, `error`.

### 4.4 CV spec

```json
{"scheme":"purged_kfold","n_splits":5,"pct_embargo":0.01,"samples_info_sets":"t1","shuffle":false,"repeats":1,"groups":null,"nested":{"outer":5,"inner":3}}
```

---

## 5. Phases

Each phase lists its scope and then **Acceptance criteria (AC)**. All AC must be automated where possible.

### Phase 0 — Foundations

**Scope:**
* Initialise git in this folder (keep the kit files). Docker Compose for local dev (frontend, lab-api, worker, redis; AI via the hosted NVIDIA API with a developer key, or a mocked provider in tests) plus `supabase start` for local Postgres/Auth/Storage; `.env.example`; Makefile (`make dev`, `make test`, `make lint`).
* **SP Workstation shell:** port `globals.css` tokens, `DashboardShell`, `Sidebar` and the `modules.ts` registry with the 13 modules (Home Terminal, Data, EDA, Preprocess, Supervised, Unsupervised, Time Series, Explain, Predict, Experiments, Reports, Learn (Logic Atlas), Admin), each with its sub-pages per ARCHITECTURE §5.
* Light/Dark theme and the collapsible sidebar.
* Auth: **Supabase Auth** email OTP / magic link (local: Inbucket/Mailpit from `supabase start`), `@supabase/ssr` in Next.js, FastAPI verifies JWTs via the project JWKS; RBAC roles (owner/admin/scientist/analyst/viewer) stored in `workspace_members`.
* Postgres schema via **Supabase CLI migrations** (`supabase migration new …`; start from the kit's `supabase/migrations/`) per ARCHITECTURE §7 + §32/§33/§37/§38 tables, with **RLS enabled on every table** and storage buckets/policies per §39.5 (start from the kit's six migrations — core schema, RLS, storage, helpers, Prediction Studio, hardening — which already define 30 tables: tenancy (`organisations`, `workspaces`, `workspace_members`; users are Supabase `auth.users`), datasets/versions/columns, experiments, recipes, jobs, runs, models, metrics, CV folds, tuning trials, artefacts, insights (+ feedback), decisions (+ feedback), `intake_proposals`, `suitability_reports`, AI usage/health, registry, predictions, reports, audit log and the Prediction Studio tables. Add the remaining tables in the phase that owns them with a new migration: intake detail tables `column_roles`, `schema_diffs`, `intake_feedback` (Phase 1A, §33.13) and the WFO tables `wfo_*` (Phase 5A, §32.13)). Users never write computed tables; workers use the service role (§46.3 SEC-01).
* Celery app with all queues; SSE plumbing; `GET /catalog` stub; OTel tracing; CI (lint, type, unit, build).
* **Python dependencies:** use the kit's `backend/requirements/` files (`api.txt`, `worker-light.txt`, `worker-train.txt`, `dev.txt` + optional images). Re-run `uv pip compile` for Python 3.12 and commit the lock files; build the Render images from the lock files. Add a CI job that fails if `labcore` imports a package that is not in `backend/requirements/*.txt` (and therefore not in ARCHITECTURE §44).

**AC:**
- [ ] `supabase start` + `docker compose up` bring all services healthy. `make test` passes.
- [ ] `supabase db reset` applies all migrations; pgTAP RLS tests pass (a member of workspace A cannot read workspace B rows or storage objects).
- [ ] Login with email OTP (Supabase Auth) works. The sidebar shows 13 modules with nested sub-pages. Collapse persists. Light/dark matches SP Workstation tokens; a visual snapshot test passes.
- [ ] A dummy Celery job streams progress over SSE to a `JobProgress` component.
- [ ] Migrations create all tables. RBAC middleware denies a viewer on POST routes (tested).
- [ ] `uv pip compile` resolves `worker-train.txt` + `dev.txt` for Python 3.12 with no conflicts, and the import-allow-list CI check passes.

### Phase 1 — Data ingestion + EDA + Education + rule-based insights

**Scope — ingestion and task setup:**
* Upload CSV/TSV/XLSX (sheet picker)/Parquet/Feather/JSONL up to the configured limit. Upload directly from the browser to **Supabase Storage** with a signed upload URL (TUS resumable for files > 6 MB; never through a Vercel function — 4.5 MB body limit), then a worker converts to Parquet. Create an immutable dataset version.
* **Type inference** (§9): numeric continuous/discrete, categorical nominal/ordinal, boolean, datetime, ID-like, constant, text-like (flag and exclude), high cardinality.
* **Task setup wizard:** choose the family; pick target(s) and inputs; **auto-detect** regression / binary / multiclass / multilabel / multioutput (rules in §9) with an override; choose Sequential vs Non-sequential (time index, group/entity column); for TS choose the frequency (auto-inferred) and exog roles (past-only vs known-future).
* **Sample loader** for DS1–DS33 (§27) with preset YAMLs (`samples/*.yaml`: family, target, inputs, CV, seed 42). The data files already validated are in `data/samples/` with `datasets_manifest.json` (id, file, task, target, seed, source URL, licence).

**Scope — EDA:**
* All **EDA tables** EDA.T.* (19, §10.1) and all **EDA plots** (§10.2) as Plotly artefacts with PNG and numbers.
* Overview, univariate, categorical, missingness, outliers, bivariate, multivariate (correlations: Pearson/Spearman/Kendall/φK/Cramér's V/η/MI, plus TradingLab `codependence` distance correlation and variation of information), target analysis, sequential/temporal (ADF/KPSS, ACF/PACF, STL, TradingLab `structural_breaks`), financial stats (TradingLab `util/volatility.py` estimators), data-quality score.
* Big data: DuckDB profiling and plot sampling over 100k rows, with a "sampled" badge.

**Scope — education and insights:**
* **Education:** `ExplainCard.tsx` (KaTeX) and the `content/explanations` registry. Every EDA plot and table and every statistical test gets an entry with: intuitive, detail, math, assumptions, when_to_use, pitfalls, references. **Learn (Logic Atlas)** is a searchable page.
* **Rule engine** (`labcore/insights/rules.py`) for EDA: skew, kurtosis, missingness > 5/30%, high cardinality, near-zero variance, |r| > 0.9, VIF > 10, class imbalance ratio, potential leakage (|corr with target| > 0.98 or a perfect predictor), duplicates, non-stationarity. Render it in the **AI Insights side panel** as "Rule insights" until Phase 6.

**AC:**
- [ ] Uploading DS3 (Titanic) infers Survived as binary, Age as numeric with missing values, Name as text-like (excluded) and Cabin as high-cardinality.
- [ ] DS22 is inferred as monthly. DS30 is inferred as daily business with OHLCV.
- [ ] All 19 EDA tables and every §10.2 plot render for DS3, DS22 and DS30. Each panel has ⓘ ExplainCard math and a PNG export.
- [ ] 1M rows × 50 cols profile in < 60 s on 8 vCPU (Locust/pytest-benchmark).
- [ ] The rule engine flags Titanic's Age missingness (~19.9%) and Cabin missingness (~77%).

### Phase 1A — AI Dataset Intake / Auto-Setup (ARCHITECTURE §33)

Build the deterministic detectors now. The LLM adjudicator is wired in Phase 6 behind the same interface, so Phase 1A ships with rule-based proposals only.

**Scope — detection:**
* **Extended column profile** (§33.2) is computed in `q.ingest`. It covers parse rates, epoch and Excel-serial ranges, monotonic fraction, regex hits (email, phone, PAN, Aadhaar-like, ISIN, UUID, ticker), name tokens and pairwise association.
* **D1 index/datetime detection** (§33.3):
  * multi-format parsing with dd/mm vs mm/dd disambiguation (default locale India → dd/mm), composite indices (`year`+`quarter`, `date`+`time`, `yyyymm`), and time-zone handling (naive → Asia/Kolkata);
  * `time_score` formula with acceptance ≥ 0.6, an ambiguity rule (two candidates within 0.1 → ask the user), panel/entity detection, and the row_id rule.
* **D2 frequency inference** (§33.4): `pandas.infer_freq` → mode Δ fallback, the regularity score, a trading-calendar check with `exchange_calendars` (XNSE, XBOM, XNYS), intraday session detection, the irregular → resample suggestion, and seasonal-period candidates confirmed by ACF/periodogram.
* **D3 column roles** (§33.5): implement every role in the table, including the OHLCV consistency rule (high ≥ max(open, close), low ≤ min(open, close) in ≥ 99% of rows), PII, constant/near-constant, and duplicate_of. Hard-exclude roles can never become features.
* **D4 family inference** (§33.6): evidence features → logits, using the weights in `labcore/intake/weights.yaml` → softmax confidence. Pre-select only when confidence ≥ 0.55. Add the financial flag and the within-supervised task type with alternatives.
* **D5 target/feature recommendation** (§33.7):
  * Rank targets with `target_score`. For financial data, never propose a raw price; propose derived targets instead (triple barrier via TradingLab `labeling/triple_barrier_labeling.py`, forward return, direction, trend-scanning via `labeling/trend_scanning.py`, realised volatility).
  * Annotate features with MI rank, collinearity groups, and the suggested encoder/transform/imputer.
* **D6 leakage suspects** (§33.8): all nine rules, including the arithmetic-identity search over column pairs (R² ≥ 0.999), the lead/lag check for sequential data, later-event timestamps, and group leakage.

**Scope — review screen and updates:**
* **Intake Review screen** (Data → Intake Review, which opens automatically after upload; layout in §33.10):
  * family cards with confidence bars;
  * an editable roles table (role dropdown, include checkbox, encoder/transform overrides, "why" popovers);
  * target choice including derived financial targets;
  * a leakage panel, and CV/WFO presets;
  * buttons Accept all / Reset to rule-based / Compare with previous version.
  * Edits are stored as `user_overrides`.
* **Versioning and drift** (§33.11):
  * update modes append / replace / upsert, a parent pointer, and a content hash;
  * D7 schema diff (add/remove, rename detection by Jaro-Winkler ≥ 0.85 plus distribution similarity, type change, new levels, range, missingness, time overlap/gaps/frequency change);
  * D8 drift (PSI, KS, χ²);
  * the breaking vs compatible decision → carry the spec forward or require re-confirmation;
  * an impact list (experiments, registered models via schema contract, WFO runs, forecasts).
* **API** per §33.12 and **tables** per §33.13 (`intake_proposals`, `column_roles`, `schema_diffs`, `intake_feedback`, plus lineage columns on `dataset_versions`).

**AC:**
- [ ] The golden intake tests in §33.14 pass:
  - [ ] DS3: non-sequential, target `Survived`, `PassengerId` row_id, `Name` excluded, `Cabin` high_missing;
  - [ ] DS12: regression;
  - [ ] DS18: unsupervised top;
  - [ ] DS22: time series, `Month` monthly, m = 12, h_max 24;
  - [ ] DS24: daily;
  - [ ] DS27: composite `year`+`quarter` index → quarterly;
  - [ ] DS28: hourly, target `OT`;
  - [ ] DS30: sequential financial ≥ 0.7, XNSE trading days, OHLCV roles, `Close` not proposed as target, triple-barrier target proposed.
- [ ] Synthetic leakage file: `y_copy = 2·y + 1` is flagged critical, `ship_date` > `order_date` is flagged high, and a centred rolling mean feature is flagged by the lead/lag rule.
- [ ] A date column with every day ≤ 12 is marked ambiguous and the UI asks the user.
- [ ] Appending NIFTY rows produces a compatible diff, and the spec is carried forward. Renaming `Volume` → `Vol` is detected as a rename proposal. Changing `Close` to strings is a breaking change that forces re-confirmation.
- [ ] Intake on 1 M rows × 100 cols completes in < 45 s (detectors on samples where stated).
- [ ] No hard-excluded column can be confirmed as a feature (API returns 422).

### Phase 2 — Preprocessing + Supervised core + CV + Tuning + Leaderboard

**Scope — preprocessing:**
* **Recipe builder** (§11): imputation (mean/median/mode/constant/KNN/iterative/MissForest-style/indicator, time-aware ffill/bfill/interpolate for sequential).
* **22 encoders** (one-hot, dummy, ordinal, label, count/frequency, target (K-fold, smoothing), leave-one-out, James-Stein, M-estimate, WOE, CatBoost, GLMM, Helmert, sum, backward-difference, polynomial, binary, base-N, hashing, rare-grouping, quantile, embedding (DL)) with the auto-policy by cardinality.
* Scalers and transforms (standard, minmax, robust, maxabs, power Yeo-Johnson/Box-Cox, quantile, log1p, winsorise, spline, polynomial, binning).
* Outliers: IQR, z, MAD, IsolationForest, LOF — flag/cap/remove, train-only.
* Feature selection (filter/wrapper/embedded, Boruta).
* Imbalance: class weights, SMOTE/BorderlineSMOTE/SVMSMOTE/ADASYN/SMOTENC/SMOTEN/KMeansSMOTE/random under- and over-sampling/Tomek/ENN/NearMiss/SMOTETomek/SMOTEENN — fold-internal only.
* Recipes compile to `sklearn.compose.ColumnTransformer` inside `imblearn.Pipeline`. A recipe diff view and versioning are included.

**Scope — algorithms:**
* **Regression R1–R51** and **Classification C1–C35** exactly as in ARCHITECTURE §12, each with a full AlgorithmSpec and presets. Include stacking/voting/blending ensembles over tuned bases (blackcarbon pattern), calibrated classifiers, and DL tabular (pytorch-tabular) behind `q.train.gpu`.

**Scope — CV, tuning and comparison:**
* **CV catalogue** (§13.1, 20 schemes): holdout, KFold, StratifiedKFold, RepeatedKFold/RepeatedStratified, GroupKFold, StratifiedGroupKFold, LeaveOneOut/LeavePOut, LeaveOneGroupOut, ShuffleSplit/StratifiedShuffleSplit, bootstrap/.632+, Monte-Carlo, nested CV, TimeSeriesSplit (expanding), sliding window, blocked, walk-forward with gap. Purged/CPCV come in Phase 5.
* Default: StratifiedKFold(5, shuffle, seed 42) ×2 repeats for classification and KFold(5)×2 for regression, with a 20% hold-out test.
* A **CV visualiser** plot shows train/test/purged/embargo indices per fold.
* **Tuning:** Grid, Random, HalvingGrid/HalvingRandom, Optuna (TPE, CMA-ES, Random, QMC, NSGA-II for multi-objective), Hyperband/ASHA pruning, early stopping. Budget by trials and/or time. Presets Quick/Balanced/Thorough/Exhaustive; default **Balanced** = 60 Optuna TPE trials (Quick 20, Thorough 200) × 5-fold.
* **Metrics** (§15) with formulas; bootstrap 95% CIs on the test set.
* **Plots** (§16): regression, classification, common, leaderboard.
* **Classification Evaluation Suite (ARCHITECTURE §41)** — implement in `labcore/eval/classification/` on top of sklearn/imbalanced-learn/netcal/statsmodels/mlxtend/MLstatkit (no re-implemented formulas):
  * store OOF predictions per fold/repeat (Parquet in Supabase Storage);
  * confusion matrices: raw counts, row-normalised (true), column-normalised (pred), all-normalised, per fold, CV-aggregated (pooled + mean ± std), cost-weighted, sample-weighted, multilabel per-label 2×2, default vs tuned threshold, model-delta; the TP/FP/TN/FN derived table (CLE.T.CM_DERIVED);
  * full classification report (CLE.T.REPORT) with per-class precision, recall, F1, F-β, support, specificity, NPV, FPR, FNR, OvR AUC/AP/Brier, plus macro / micro / weighted / samples rows, accuracy and balanced accuracy; CV mean ± std and per-fold variants; imbalanced report;
  * all 55 CLE.M.* metrics with averaging modes (MCC, Cohen's/linear/quadratic κ, Youden J, informedness/markedness, G-mean, IBA, log loss, Brier + Murphy/CORP decomposition, ROC-AUC OvR/OvO macro/weighted/micro, partial AUC, PR-AUC/AP, KS, Gini, top-k, Hamming, Jaccard, subset accuracy, ranking metrics, ECE/MCE/classwise ECE, calibration slope, HL test, expected cost, lift/gain, precision@k, EER);
  * all 45 CLE.P.* plots (normalisation toggle Counts/Row/Column/All, per-class and micro/macro ROC, PR with iso-F1, reliability + histogram, gains, lift, KS, threshold-vs-metric, discrimination threshold, cost curves, DET, probability distributions, per-class P/R/F1 bars, error analysis);
  * threshold optimisation (13 methods, §41.6) tuned on training OOF only via `TunedThresholdClassifierCV`; imbalance-specific reporting (§41.7); CLE.T.CV_METRICS for every metric; comparison tables and statistical tests (McNemar, Cochran Q, DeLong, 5×2cv t and F, corrected t, Wilcoxon, Friedman–Nemenyi, bootstrap, Holm);
  * Evaluation tab with sub-tabs Overview · Confusion · Report · Curves · Calibration · Threshold · Errors · Imbalance · Compare.
* **Regression Evaluation Suite (ARCHITECTURE §42)** — `labcore/eval/regression/`: all 40 REE.M.* metrics, the 17 REE.T.* tables (row-level residuals, residual tests with verdicts, influence, calibration bins, CV metrics, intervals, baselines, comparison), all 36 REE.P.* plots (incl. Cook's distance, studentised index, CCPR, Bland–Altman, REC curve, calibration-in-bins), CV aggregation and comparison tests.
* **Leaderboard:** multi-metric, rank, mean ± std, fold heatmap, Pareto score vs time. **Statistical comparison** (§13.3): corrected resampled t-test (Nadeau-Bengio), Wilcoxon, Friedman + Nemenyi critical-difference diagram, McNemar, DeLong for AUC. Best-model rule: primary metric, then the CD-group tie-break by simplicity and latency.
* Every run is logged to MLflow with nested fold and trial runs.
* **Leaderboard export** (CSV/XLSX, formula-injection-safe) and a read-only **pipeline graph view** of each run (recipe → estimator → calibrator) (§46.5).
* ML integrity guarantees MI-01…MI-18 (§46.1) are implemented here or in the phase that owns the feature.

**AC:**
- [ ] For each of DS3, DS11, DS12 and DS14, the whole flow runs end to end: recipe → 10+ algorithms → leaderboard → plots.
- [ ] Every AlgorithmSpec instantiates with defaults and with a random draw from every preset (parametrised test over all R*/C*).
- [ ] **Leakage tests pass:**
  - [ ] the shuffled-target score falls to chance;
  - [ ] a scaler/encoder fit-count spy proves per-fold fitting;
  - [ ] SMOTE is never applied to validation folds.
- [ ] Customise mode can change every parameter of LightGBM, and the run uses exactly those values (asserted from the MLflow params).
- [ ] The CD diagram and the corrected t-test match reference values on a fixed synthetic example.
- [ ] Golden metric bands (seed 42) hold for DS3 and DS12.
- [ ] §46.1 tests: target-encoder noise column stays at chance (MI-02); nested CV is on by default for n < 2 000 (MI-03); constant/all-NaN columns are dropped with a warning (MI-11); an ambiguous date column triggers the format prompt (MI-12); rerunning a Quick run reproduces metrics exactly (MI-06).
- [ ] **Classification evaluation (§41):** a DS4 (binary) run, a DS10 (multiclass) run and a multilabel fixture each render the confusion matrix in **raw counts and all three normalisations (row/true, column/pred, all)**, per fold and CV-aggregated (pooled + mean ± std), and the **full classification report table** (per-class precision, recall, F1, F-β, support, specificity, NPV, FPR, FNR + macro/micro/weighted rows, plus samples avg for multilabel, accuracy and balanced accuracy).
- [ ] Every CLE.M.* metric equals its library reference (`classification_report(output_dict=True)`, `roc_auc_score`, `matthews_corrcoef`, `cohen_kappa_score(weights='quadratic')`, …) to 1e-9; Σ per-fold matrices == pooled OOF matrix; normalised rows/columns/all sum to 1; single-label micro-F1 == accuracy.
- [ ] CLE.T.CV_METRICS lists mean ± std, SEM, min, max, 95% CI, pooled OOF, train gap and test CI for **every** applicable metric; zero-division cells show "—", never 0.
- [ ] Threshold optimisation: every §41.6 method returns t* with per-fold mean ± std; a spy proves the test split is never read by threshold tuning or calibration.
- [ ] McNemar matches statsmodels, 5×2cv matches mlxtend, DeLong agrees with a paired bootstrap on a fixed example.
- [ ] All 45 CLE.P.* plots render for DS4 and the applicable ones for DS10 and the multilabel fixture (visual snapshot tests).
- [ ] **Regression evaluation (§42):** a DS12 run renders REE.T.RESIDUALS, REE.T.RESID_TESTS (Shapiro, JB, Anderson–Darling, Breusch–Pagan, White, Goldfeld–Quandt, Durbin–Watson, Ljung–Box, RESET, Harvey–Collier, runs test with verdicts), REE.T.INFLUENCE and all 36 REE.P.* plots; every REE.M.* equals its library reference; studentised residuals and Cook's D equal statsmodels `OLSInfluence`.

### Phase 2A — Deep Learning, full (ARCHITECTURE §34)

**Scope:**
* `labcore/deep/`: one training engine (Lightning) shared by all DL models — AdamW default (lr 1e-3, weight decay 1e-5), schedulers (OneCycle, cosine with warm-up, ReduceLROnPlateau), **LR finder**, gradient clipping (1.0), early stopping (patience 10 on validation loss), best-epoch checkpointing to Supabase Storage, AMP bf16 on GPU, deterministic flags and seed 42.
* **Tabular registry T1–T16** (§34.3) via pytorch-tabular configs and lab modules: MLP, ResNet-MLP, TabNet, FT-Transformer, TabTransformer, SAINT, NODE, AutoInt, DCN-v2, GANDALF, GATE, DANet, TabPFN (**disabled unless `TABPFN_ENABLED=true` and a licence is confirmed**), MDN, Stacked, SSL pre-training. Every hyperparameter in §34.5 exposed through `ParamSpec` with default and search space.
* **Sequential registry Q1–Q13** (§34.4): window builder (lookback L, horizon, stride; purge/embargo for financial), RNN/LSTM/GRU, BiLSTM/BiGRU (guarded: only when the window is fully in the past), attention-LSTM, CNN-1D, TCN, CNN-LSTM, Transformer encoder, patch encoder, TFT, xLSTM/Mamba (optional), sequential-bootstrap bagging.
* **Artefacts:** all DL.T.* tables (9) and DL.P.* plots (17): loss/metric curves per fold, LR finder, LR trace, gradient norms, weight and activation histograms, attention maps (feature and time), TabNet masks, embeddings (UMAP of entity embeddings), latent space, trials, fold curves, uncertainty, saliency, architecture graph.
* **Uncertainty (§34.8):** MC dropout (T = 50), deep ensembles (M = 5, seeds 42–46), quantile and Gaussian-NLL heads, conformal wrappers, temperature scaling.
* **Resources (§34.9):** `q.train.gpu` only when a GPU worker is registered; GPU-only models refuse on CPU with a clear message and a smaller-preset suggestion; CPU threads = vCPU; memory estimator before start.

**AC:**
- [ ] Every T*/Q* spec instantiates with defaults and with one random draw from its search space (parametrised test).
- [ ] MLP, FT-Transformer and TabNet train on DS3 and DS12 on CPU (Quick) in < 10 min each, and their CV metrics appear in the shared leaderboard.
- [ ] LSTM and TCN on windowed DS30 use purged CV with embargo; a test proves no window overlaps a validation label horizon.
- [ ] LR finder returns a suggested LR and plot; early stopping restores the best epoch (asserted from logs).
- [ ] MC-dropout and deep-ensemble intervals reach 85–95% empirical coverage for nominal 90% on DS12.
- [ ] Requesting a GPU-only model with no GPU worker returns HTTP 422 with the reason; TabPFN is hidden when disabled.

### Phase 3 — Explainability + Prediction + Uncertainty + Registry/Export

**Scope:**
* **Explain** (§17): SHAP (all explainers, all plots), LIME (fidelity, stability), PDP 1D/2D, ICE/c-ICE, ALE, permutation and drop-column, Friedman H, global surrogate, Anchors, counterfactuals (DiCE), EBM, coefficient/odds forest. By default, compute SHAP for the top-3 models on ≤ 2,000 rows.
* **Uncertainty** (§21):
  * Calibration: Platt, isotonic, temperature, Venn-Abers; reliability diagram, ECE/MCE, Brier.
  * Conformal: MAPIE split/CV+/jackknife+ for regression; LAC/APS/RAPS sets for classification; Mondrian/conditional.
  * Other methods: quantile regression (GBM, linear, QRF), NGBoost, bootstrap ensembles, MC dropout, deep ensembles, Bayesian (BayesianRidge, GP, ARD).
  * **Confidence score per prediction:** 0–100, combining calibrated max-probability or normalised interval width, OOD distance (Mahalanobis or kNN in recipe space) and ensemble disagreement. Show the formula in ExplainCard.
* **Predict module** (§22):
  * Modes: single form auto-generated from the schema, batch scoring, what-if sliders with a sensitivity tornado.
  * Each output shows: point, probabilities, conformal set or interval, quantiles, confidence, OOD flag, local SHAP and LIME, and a counterfactual.
* **Registry** (§25): MLflow registry with `@champion/@challenger` aliases, an approval flow and an auto model card.
* **Export:** joblib/skops pipeline, ONNX (with a parity test), MLflow pyfunc, a generated reproducible Python script **and Jupyter notebook**, a reproduction bundle (data hash, config, code, lock), a Docker serving bundle, and `POST /serve/{name}@{alias}/predict` with an API key.
* **Feature contract** (§45.2) written by every training job from the training split and stored in `model_signatures` + Storage + MLflow; **refit on full training data** before registration (toggle, default on).
* The detailed Single/Batch UI is built in Phase 3A; this phase delivers the prediction engine (`labcore/predict`) that 3A calls.

**AC:**
- [ ] TreeSHAP additivity |Σφ + E[f] − f(x)| < 1e-6.
- [ ] The PDP equals the mean of ICE curves.
- [ ] Split-conformal 90% intervals reach **88–92% empirical coverage** on DS12. APS sets reach ≥ 89% on DS10.
- [ ] Calibration reduces ECE on DS4 (calibrated vs uncalibrated LightGBM), shown in CLE.P.CALIB_COMPARE and CLE.T.COMPARE_CALIBRATION (§41).
- [ ] ONNX vs native prediction max-abs diff < 1e-4 for 5 model types.
- [ ] A batch file of 100k rows is scored asynchronously with SHAP top-3 reasons per row.
- [ ] Every trained model has a feature contract that validates against `docs/contracts/feature_contract.schema.json`; identifier-like columns store no values.
- [ ] The exported notebook re-runs end to end and reproduces the CV score of the run to 1e-9.

### Phase 3A — Prediction Studio: batch upload + custom input form (ARCHITECTURE §45, §46)

**Scope:**
* **Mode chooser** in Predict: (A) Batch upload and (B) Custom input, for any finished or registered model the user can read.
* **(A) Batch upload:** template download (`GET /models/{id}/template?format=csv|xlsx`), upload via signed URL to bucket `predictions`, `POST /predict/batch`, validation PV01–PV16 with a report (`needs_review` → confirm), chunked scoring on `q.predict.batch` / `q.predict.heavy`, progress over SSE, cancel, results grid, CSV/XLSX download (formula-injection-safe), summary plots, AI explanation. Output columns per task exactly as §45.4 (regression intervals at chosen levels; classification class + calibrated probabilities + confidence + margin + entropy + threshold + conformal set; TS forecast + intervals ≤ h_max; clustering/DR cluster, distance/membership, coordinates; flags and SHAP top-k for all).
* **(B) Custom input form:** generated from the feature contract (`GET /models/{id}/schema`) with the widget mapping of §45.6 (sliders + number boxes bounded by training ranges with median defaults, dropdowns of seen categories with mode defaults, toggles, date pickers, lookback window editor / pick-a-date-from-history for sequential models, derived features computed automatically); live `POST /predict/single` with 300 ms debounce; result card with interval/probabilities, gauge, confidence badges, OOD flags, local SHAP waterfall, what-if sliders (ICE + tornado), "Fill from a random training row", "Reset to defaults", "Add to batch"; AI explanation (`prompts/prediction.md`).
* **Humility rules** (§46.5): per model, configurable actions when a row is OOD, out of range or has a wide interval — warn (default), abstain (no prediction, reason shown) or route to review.
* **Data:** tables `model_signatures`, `prediction_jobs`, `prediction_results` and bucket `predictions` already exist in the kit migrations (`20261115000000_prediction_studio.sql`, `20261115000100_hardening.sql`); keep them and extend only with a new migration. Retention cleanup runs in the `lab-beat` cron job.
* **Samples:** `data/samples/predict/` holds 35 prediction files for DS1–DS33 (target removed, seed 42) and their contracts; regenerate with `python scripts/make_predict_samples.py` (cached downloads; `--offline` uses the cache only). Every preset references its file. The "Load sample" flow offers the matching prediction file next to the training data.
* Components and endpoints exactly as §45.7 and §45.11.

**AC:**
- [ ] `pytest tests/unit/test_predict_samples.py` passes (all 33 datasets covered; columns match the contracts; targets absent; TS row counts respect HorizonGuard).
- [ ] For DS3 (classification), DS12 (regression), DS22 (forecast), DS18 (clustering) and DS33: train a Quick model, download the template, upload the matching `data/samples/predict/*_predict.csv`, and get a validation report with **zero blocking issues** and an output file with every §45.4 column for that task; the XLSX opens in Excel/LibreOffice.
- [ ] Validator tests: one crafted file per PV code (missing column, extra target column, bad dtype > 5 %, unseen category, out-of-range, NaN, unsorted/duplicate timestamps, horizon > h_max → HTTP 422, formula cells, XLSX bomb, duplicate headers, wrong type) each produce exactly the expected code and severity.
- [ ] Parity: `POST /predict/single` and the batch path return identical outputs (1e-9) for the same 30 rows; both equal the saved pipeline's `predict`/`predict_proba`.
- [ ] Coverage: on the DS12 hold-out, 90 % conformal intervals have empirical coverage within 88–92 % (same band as Phase 3); DS10 APS sets reach ≥ 89 % (computed by the test and reported, not assumed).
- [ ] Custom form for DS3: every contract feature has the right widget and default; "Reset to defaults" restores medians/modes; "Fill from a random training row" fills all fields; moving the Age slider re-predicts in < 1 s (p95, local) and the SHAP waterfall sums to the prediction (additivity 1e-6 for tree models).
- [ ] Sequential model (DS30): the lookback editor is pre-filled from the end of training; picking a historical date shows the actual value alongside the prediction.
- [ ] A 1 M-row CSV (synthetic, 20 columns) is scored in chunks without exceeding the light worker's memory; cancel during scoring stops within one chunk; re-posting with the same Idempotency-Key returns the same job.
- [ ] pgTAP `supabase/tests/prediction_rls_test.sql` passes: members read their workspace's jobs/results/contracts; users cannot write `prediction_results` or change job status; malformed storage paths are denied; other workspaces see nothing.
- [ ] Playwright: upload `titanic_predict.csv` → report → download XLSX; custom form → change a slider → card updates; keyboard-only flow works; axe-core shows no serious violations.
- [ ] AI explanation for one row and one batch cites only FACTS values; with the provider off, the numbers-only explanation appears.

### Phase 4 — Time Series

**Scope — analysis and models:**
* **Analysis** (§19.1): decomposition (classical, STL, MSTL, X-13 if available), ACF/PACF, periodogram, seasonal/subseries.
* **Tests:** ADF, KPSS, PP, Zivot-Andrews, ARCH-LM, Ljung-Box, Jarque-Bera, Granger, Johansen, Chow/CUSUM/SADF via TradingLab.
* **Forecasters F1–F54** (§19.2):
  * baselines;
  * ETS/ARIMA/SARIMA(X)/AutoARIMA/Theta/TBATS/MSTL/CES/MFLES/Croston family/VAR/VECM/UCM/GARCH family (arch) and Prophet;
  * ML via mlforecast/skforecast (LightGBM/XGB/RF/Ridge with lags, rolling and calendar features);
  * DL via neuralforecast: RNN, LSTM, GRU, TCN, DeepAR, N-BEATS(x), N-HiTS, TFT, Informer, Autoformer, FEDformer, PatchTST, iTransformer, TimesNet, TiDE, TSMixer(x), TimeMixer, NLinear/DLinear, KAN, xLSTM;
  * optional foundation models (Chronos/TimesFM/Moirai) behind a flag.
* Exog handling (§19.3).

**Scope — horizon, backtesting and plots:**
* **HorizonGuard** (`labcore/timeseries/horizon_guard.py`) — implement ARCHITECTURE §20 exactly:
  * Step 1 frequency caps (recommended / hard): monthly 12/36, quarterly 8/16, daily 14/90, business-daily financial 5/21 (volatility models 66), hourly 24/168, weekly 13/52, yearly 3/10.
  * Step 2 data feasibility: `h ≤ floor((n − n_min_train)/(W+1))` with defaults W = 4 backtest windows and n_min_train = max(2m, 24); `h ≤ floor(n/3)` (for n < 50: `h ≤ max(1, floor(n/4))`); seasonal ETS needs `n ≥ 2m + h`; SARIMA needs `n ≥ p+q+P+Q+d+mD+1 + h`; DL window rules and GARCH (n ≥ 250 hard, 500 recommended) per §20.
  * Step 3 empirical truncation after backtest: h* = largest step with MASE_j < 1 vs seasonal naive and 95% PI relative width < 2; beyond h* the forecast is drawn dashed.
  * Step 4: `h_max = min(all caps)`; requests above h_max return HTTP 422 with reasons; the UI slider is hard-limited and shows a "why" tooltip.
* **Backtesting** (§19.4): rolling origin with expanding/sliding windows, step, refit every k, horizon-wise metrics.
* **Intervals:** model-based, bootstrap, conformal (MAPIE/statsforecast conformal), quantile loss.
* **Metrics** (§19.6): MAE, RMSE, MAPE, sMAPE, MASE, RMSSE, WAPE, CRPS, pinball, coverage, Winkler, plus Diebold-Mariano.
* **Residual diagnostics:** Ljung-Box, ACF, normality, ARCH.
* **Plots** (§19.8) and the forecast fan chart.

**AC:**
- [ ] DS22 (n=144, m=12, default W=4, n_min_train=24): h_max = 24 (= (144 − 24)/5); SARIMA(0,1,1)(0,1,1)12 beats seasonal naive on MASE across the W = 4 backtest origins; Ljung-Box p > 0.05 on residuals.
- [ ] DS23 (n=36): h_max ≤ 9 (n < 50 rule) and seasonal models are disabled with the reason shown (n < 2m + h).
- [ ] A table-driven HorizonGuard test with ≥ 20 cases passes.
- [ ] DS28 trains N-HiTS and PatchTST on the GPU queue, with a CPU fallback in under 10 min.
- [ ] 80/95% interval empirical coverage is within ±5 pp on DS24 backtests.

### Phase 4A — Time Series, full (ARCHITECTURE §35)

**Scope:**
* **TS EDA tables** TS.T.SUMMARY, STATIONARITY, STATIONARITY_VERDICT, SEASONALITY, BREAKS, HETERO, NORMALITY, AUTOCORR, GRANGER, CCF, COINT, OUTLIERS, FEATURES and **plots** TS.P.* (§35.1): classical/STL/MSTL/X-13 decompositions, ACF/PACF, lag, seasonal, subseries, seasonal box plots, periodogram/Welch, spectrogram, calendar heatmap, differencing, Box-Cox profile, breaks, volatility clustering, CCF, Granger heatmap, rolling correlation.
* **All F1–F54 hyperparameters with defaults and search spaces** exactly as §35.2 (Customise mode for every field).
* **Multi-step strategies** (§35.3): recursive, direct, DirRec, MIMO, DIRMO, rectify — a parameter of every ML forecaster, shown as a leaderboard column.
* **Exogenous handling** (§35.4): static / historic-only / known-future / generated; leakage guard and future-coverage check.
* **Multivariate and hierarchical** (§35.5): VAR family with IRF/FEVD; global models over `unique_id`; reconciliation (BottomUp, TopDown, MiddleOut, MinTrace variants, ERM) with coherent intervals.
* **Backtesting set-ups** (§35.6) and the **complete metrics table** (§35.7): ME, MAE, RMSE, MAPE, sMAPE, WAPE, MASE, RMSSE, MSIS, Winkler, coverage, MPIW, pinball, CRPS, Theil U1/U2, directional accuracy, out-of-sample R² vs naive, relative MAE, QLIKE, Kupiec/Christoffersen VaR tests.
* **Residual diagnostics** TS.T.RESID_TESTS / RESID_ACF / PARAMS (§35.8), **forecast plots** (§35.9) and **leaderboards** TS.T.LEADERBOARD / BY_HORIZON / BY_WINDOW / BY_SERIES / DM / ENSEMBLE (§35.10) with the default selection rule.

**AC:**
- [ ] Every metric in §35.7 has a unit test against hand-computed values (including MASE with m = 12 and CRPS for a Gaussian forecast vs the closed form).
- [ ] The stationarity verdict matrix gives "unit root, d = 1" for DS22 (log) and "stationary" for a simulated AR(1) φ = 0.5.
- [ ] Recursive vs direct LightGBM on DS22 both run; the leaderboard shows the strategy column and the by-horizon table.
- [ ] A 3-level synthetic hierarchy reconciles with MinTrace(shrink); coherence error after reconciliation < 1e-8.
- [ ] Residual table flags autocorrelation for a deliberately mis-specified ARIMA(0,0,0) on DS22 (Ljung-Box p < 0.05).
- [ ] Known-future exog missing for part of the horizon blocks the forecast with a clear message.

### Phase 5B — Financial labelling suitability check (ARCHITECTURE §37) — runs before Phase 5 labels

**Scope:**
* `labcore/suitability/`: detection of index, price/returns, OHLCV, frequency, asset id (§37.2); checks **FS1–FS20** with PASS/WARN/FAIL thresholds (§37.3, editable, versioned); per-method verdicts (§37.4); deterministic recommendations (§37.5); 36-cell parameter grid preview (§37.6); report JSON (§37.7) stored in `suitability_reports` (RLS); FS.P.* plots (§37.8).
* API and UI per §37.9: "Financial → Label suitability" card before the Labels step; financial labels disabled while Not suitable (admin override is logged); one-click fallback to standard targets.

**AC:**
- [ ] DS30 (NIFTY 50 daily) → Suitable or Suitable with cautions for triple barrier; the report lists every FS check with its value.
- [ ] DS22 airline passengers → Not suitable (no price semantics / too short) → forecasting fallback pre-selected.
- [ ] Synthetic stale-price series → FS8 FAIL; 300-bar series → FS6 FAIL; inconsistent OHLC → FS4 FAIL.
- [ ] Meta-labelling is Not suitable until a primary model or rule with ≥ 100 signals exists (FS18).
- [ ] The grid default cell maximises effective sample size subject to minority share ≥ 15% (unit test).

### Phase 5 — Financial / Sequential supervised (mirror TradingLab)

**Scope — labels, weights and features:**
* **Financial target builder** (enabled only when the Phase 5B suitability report allows the method; otherwise offer the fallback target): triple barrier with `get_events`/`get_bins` (pt/sl multipliers on `get_daily_vol`, vertical barrier via `add_vertical_barrier`, CUSUM events via `cusum_filter`), **meta-labelling** (primary side model → secondary 0/1 classifier), fixed horizon, trend scanning, excess over mean/median, vs benchmark, tail sets, matrix flags.
* **Sample uniqueness and weights:** `get_av_uniqueness_from_triple_barrier`, `get_weights_by_return`, `get_weights_by_time_decay`. Weights are computed once on the timeline, then sliced per fold into `sample_weight_train` and `sample_weight_score` (the `ml_cross_val_score` contract).
* **Feature packs** (§11.7): rolling stats, returns/lags, technicals, volatility estimators, **FFD** with d* chosen on train only (`plot_min_ffd` logic), microstructure, bars, CUSUM events.

**Scope — validation and backtesting:**
* **CV:** Purged K-fold + embargo (`PurgedKFold`, default k=5 and `pct_embargo=0.01`), PurgedSplit, **CPCV** (`CombinatorialPurgedKFold`, default N=6, k=2 → 15 splits and 5 paths), walk-forward with purge. These are the defaults whenever Sequential + financial is chosen.
* **CPCV backtest paths → strategy returns:** sign or bet-size × forward return, minus a costs-in-bps parameter. Then per-path Sharpe distribution, **PBO** (`labcore/finance/pbo.py`, CSCV S=16), **PSR/DSR** (`probabilistic_sharpe_ratio`, `deflated_sharpe_ratio` with the number of trials = Optuna trials), Campbell haircut, MinTRL, drawdowns, HHI concentration.
* **Sequential models S1–S11** (§12): lagged-feature GBMs, RNN/LSTM/GRU/TCN/Transformer/TFT classifiers/regressors on windows, `SequentiallyBootstrappedBagging*`.
* **Financial feature importance:** MDI/MDA/SFI (clustered via ONC), orthogonal features, fingerprints.
* **Bet sizing:** probability → size, EF3M.
* **Plots:** equity curve, underwater, CPCV path fan, PBO logit histogram, IS vs OOS scatter, rolling Sharpe, signal overlay with lightweight-charts.
* **Model selection rule** for financial runs: champion only if PBO < 0.2 (configurable) and DSR > 0.95. Otherwise mark the model "overfit risk".

**AC:**
- [ ] All listed **TradingLab contract tests pass** inside the lab's CI against the vendored commit.
- [ ] Adapter outputs (fold indices, labels, weights, FFD series) are identical to direct TradingLab calls on `tradinglab/datasets` samples and DS30.
- [ ] Purged train sets never overlap any test label span [t0, t1] (property test with hypothesis); the embargo removes ⌈pct·T⌉ observations after each test block.
- [ ] φ(6,2)=5 equals TradingLab N−1. The general φ(N,k) is correct for (8,3)=21 and (10,4)=84.
- [ ] PBO on 100 pure-noise strategies ≈ 0.5 (±0.1). With one injected true signal and few configurations, PBO drops toward 0.
- [ ] End to end on DS30: CUSUM events → triple barrier → meta-labels → LightGBM with purged CV → CPCV → PBO/DSR report rendered.

### Phase 5A — Walk-Forward Optimisation (ARCHITECTURE §32)

TradingLab has **no** walk-forward driver. Implement `labcore/finance/wfo.py` (planner, driver, stitching), `labcore/finance/costs.py` and `labcore/finance/montecarlo.py`. **Reuse TradingLab for every building block**, as mapped in §32.15.

**Scope — window planning:**
* **Window planner** (§32.1–32.2):
  * modes: rolling, anchored, anchored with decay (`sample_weights/attribution.py → get_weights_by_time_decay`), calendar-aligned (offset aliases), and event-based (CUSUM events from `filters/event_filters.py → cusum_filter`);
  * L_IS, L_OOS, step, gap (`auto` = max(label horizon, feature look-ahead)), purge, and `pct_embargo`;
  * the closed form for K, the frequency defaults table, and guards (K ≥ 4, OOS ≥ 30 samples, IS:OOS outside 3:1–12:1 → hint);
  * a compute estimate before launch.
* **Purging** at each window boundary with `cross_validation/time_series_cv.py → ml_get_train_times(samples_info_sets, test_times)`; the embargo mirrors `PurgedKFold` semantics.

**Scope — per-window loop** (§32.3), run as a Celery chord (sequential when warm-starting):
* Fit the recipe on IS_k only, and re-estimate FFD d* per window (`features/fractional_differentiation.py → frac_diff_ffd`, using the `plot_min_ffd` logic on IS_k).
* Compute weights with `sampling/concurrent.py → get_av_uniqueness_from_triple_barrier` × `sample_weights/attribution.py → get_weights_by_return`.
* **Re-tune** with Optuna using inner `PurgedKFold` scored by `ml_cross_val_score(..., sample_weight_train, sample_weight_score)`:
  * warm start via `study.enqueue_trial`;
  * robust objective mean − λ·std;
  * selection `best` or `plateau` (k-NN neighbourhood average in normalised parameter space);
  * **persist every trial** in `wfo_trials`.
* **Retrain** according to policy.
* Predict OOS_k. Calibrate on the last inner fold only.

**Scope — strategy, costs and policies:**
* **Strategy and costs** (§32.3 steps 8–9):
  * positions from a threshold or `bet_sizing/bet_sizing_core.py → bet_size_probability` / `bet_size_dynamic` / `bet_size_budget` / `bet_size_reserve` (EF3M `bet_sizing/ef3m.py → M2N`);
  * net returns with commission, slippage, half-spread, STT, sqrt impact and borrow;
  * a cost-sensitivity sweep and the break-even cost multiple;
  * **re-pricing costs from stored positions without retraining**.
* **Re-tune/retrain policies** (§32.4): `fixed`, `every_window`, `every_k`, `calendar`, `performance_trigger`, `drift_trigger`, `frozen`. Run the `frozen` and `fixed` baselines automatically for comparison. Warm-start models where supported (LightGBM/XGBoost/CatBoost `init_model`, PyTorch fine-tune).

**Scope — results and verdict:**
* **Stitching** (§32.5) of predictions, positions, gross/net returns and equity, with benchmarks (buy-and-hold, frozen, random equal-turnover, majority class).
* **Metrics** (§32.6):
  * walk-forward efficiency (return and Sharpe), IS→OOS degradation slope, % profitable windows with a binomial test, consistency;
  * parameter stability (CV, mode share, normalised distance d_k, Kendall τ), surface flatness;
  * predictive metrics;
  * financial metrics via `backtest_statistics/strategy_metrics.py` (`sharpe_ratio`, `information_ratio`, `probabilistic_sharpe_ratio`, `deflated_sharpe_ratio`, `minimum_track_record_length`, `drawdown_and_time_under_water`, `bets_concentration`, `average_holding_period`, `timing_of_flattening_and_flips`), plus CAGR, Sortino, Calmar, VaR/CVaR, profit factor, turnover, cost drag and capacity;
  * Campbell haircut via `backtest_statistics/campbell.py → CampbellBacktesting`.
  * **DSR uses N = total trials across all windows.**
* **PBO and CPCV link** (§32.7):
  * shared candidate set (top-n per window, n = 10, C ≤ 50) re-scored on every OOS window → `labcore/finance/pbo.py` CSCV (S = 16);
  * CPCV cross-check with `cross_validation/combinatorial.py → CombinatorialPurgedKFold`, reporting the WF Sharpe percentile among the CPCV paths.
* **Monte Carlo** (§32.8): stationary block bootstrap (`arch.bootstrap.StationaryBootstrap`, `optimal_block_length`), signal-permutation test within windows, trade resampling/shuffle for the drawdown distribution, random-entry benchmark, optional Hansen SPA (`arch.bootstrap.SPA`), parameter perturbation, probability of hitting a drawdown limit.
* **Verdict rule:** DSR > 0.95, PBO < 0.2, WFE ≥ 0.5, ≥ 60% profitable windows, MC p < 0.05 → "Champion-eligible"; otherwise "Research only" with the failing rules listed.

**Scope — plots, UI, insights, API, data:**
* **Plots:** all 24 WFO.P.* artefacts (§32.9), including the timeline Gantt, stitched equity (lightweight-charts), IS-vs-OOS bars with the WFE line, the **parameter stability heatmap**, **parameter drift lines**, surface small multiples, MC fan/histograms, cost decomposition and sensitivity, feature-importance drift, regime overlay (`structural_breaks/sadf.py → get_sadf` or volatility terciles), policy comparison, and CPCV vs WF.
* **Tables:** WFO.T.WINDOWS and WFO.T.SUMMARY (§32.10).
* **UI** (§32.14): Supervised → Walk-Forward with sub-pages Home · Designer (live timeline preview from `POST /wfo/plan`) · Runs (live, partial stitched curve over SSE) · Results · Parameters · Robustness · Costs · Compare · Intel. Time Series → Backtesting reuses the engine for rolling-origin forecasts.
* **AI Insights:** stage `wfo` with prompt `prompts/wfo.md`, extra schema fields `wfo_verdict`, `unstable_params` and `weak_windows`, and `apply_patch` recommendations (§32.11). Until Phase 6, show the rule-engine version.
* **API** per §32.12 and **tables** per §32.13 (`wfo_runs`, `wfo_windows`, `wfo_trials`, `wfo_series`, `wfo_mc_results`). `POST /wfo/runs/{id}/promote` registers a model trained on the latest IS window, with the WFO report attached to the model card.

**AC:**
- [ ] Planner property tests (hypothesis) pass:
  - [ ] no OOS overlap when step = L_OOS;
  - [ ] every IS index < every OOS index;
  - [ ] after purging, no IS label span intersects its OOS window;
  - [ ] embargo size = ⌈pct·T⌉;
  - [ ] K equals the closed form.
- [ ] **Purge parity:** the lab's purged IS sets equal `ml_get_train_times` output exactly on the TradingLab samples and DS30.
- [ ] Synthetic AR(1)-signal series: pooled WFE is between 0.7 and 1.3, DSR > 0.95 and permutation p < 0.05. Pure-noise features: permutation p > 0.1, PBO ≥ 0.4 and verdict "Research only".
- [ ] Re-pricing costs from stored positions equals a full re-run (max abs diff < 1e-12). The break-even multiple gives net Sharpe = 0 ± 1e-3.
- [ ] The DSR trial count equals `SELECT count(*) FROM wfo_trials` for the run.
- [ ] End to end on DS30 (rolling 504/63/63, gap = 10, LightGBM on triple-barrier meta-labels, 40 trials per window):
  - [ ] all 24 plots and both tables render;
  - [ ] the policy comparison includes `frozen` and `fixed`;
  - [ ] the CPCV cross-check percentile is reported;
  - [ ] AI insight JSON validates with 100% citation validity (Phase 6 model) or the rule-based fallback.
- [ ] The WFO run of 15 windows × 40 trials × 4 inner folds finishes in < 15 min on 16 vCPU.

### Phase 6 — Unsupervised + AI Insights (VLM)

**Scope — unsupervised:**
* **Unsupervised** (§18):
  * DR D1–D22 (PCA, IncrementalPCA, KernelPCA, SparsePCA, TruncatedSVD, FA, ICA, NMF, LDA, MCA/FAMD (prince), Isomap, LLE/MLLE/HLLE, Spectral embedding, MDS, t-SNE (openTSNE), UMAP, PaCMAP/TriMap, autoencoder/VAE, random projection).
  * Clustering K1–K19 (K-Means/++/MiniBatch, K-Medoids, K-Modes, K-Prototypes, GMM/Bayesian GMM, Agglomerative (ward/complete/average/single), BIRCH, DBSCAN, HDBSCAN, OPTICS, Mean-shift, Spectral, Affinity propagation, SOM).
  * Anomaly A1–A14 (IsolationForest, LOF, OCSVM, EllipticEnvelope, ECOD, COPOD, HBOS, kNN, ABOD, CBLOF, LODA, autoencoder, SUOD/ensemble).
* All plots and metrics (§18): silhouette, CH, DB, gap, BIC, ARI/NMI vs labels, stability via bootstrap; trustworthiness/continuity; precision@k.
* Best-config selection by consensus of indices plus stability. Cluster profiles. Write labels back as a new dataset version.

**Scope — AI Insights (§23):**
* **AI provider layer** (`labcore/ai/`, ARCHITECTURE §40): `OpenAICompatClient` (OpenAI SDK with per-provider `base_url`), `providers.yaml` registry and **chains** (`vision_standard`, `vision_fast`, `text_reasoning`, `text_deep`), router with health probes, token-bucket rate limiting shared via Key Value (NVIDIA `rpm_limit` 35), retries with exponential back-off + jitter (max 4, honour `Retry-After`; no retry on 400/401/403/404/422; 404/403 → next model; 413 → shrink image), circuit breakers (3 failures → 5 min), per-call timeouts (90 s / 180 s Deep).
* **Requests:** OpenAI chat format with `image_url` data URIs (PNG/JPEG) placed before the text; `response_format: {type: "json_schema"}` when the provider supports it (NVIDIA NIM does; fall back to `nvext.guided_json`, then to prompt-only JSON + local validation); temperature 0.2, top_p 0.9; reasoning off by default, on for Deep mode and decisions VD3/VD10.
* **Images (§40.4):** kaleido 1024 × 640; palette PNG, then JPEG q85, then smaller widths until the **base64 string is ≤ 170,000 bytes** (NVIDIA inline limit 180 KB); tile big grids; NVCF asset upload implemented but off by default.
* **Cost controls (§40.7):** cache by content hash before any call; lazy generation; map-reduce with the fast tier; per-workspace/per-user daily budgets with an `ai_usage` table and a banner + numbers-only at the cap.
* **Data protection (§40.8):** aggregate plots and FACTS only, no raw rows; PII redaction; workspace classification `public` / `internal` (NVIDIA only, default) / `restricted` (numbers-only); `NVIDIA_API_KEY` only in Render and local `.env`, never in Vercel or any `NEXT_PUBLIC_*`.
* **Admin → AI providers** page: health, chains, usage vs budget, probe button.
* **Context builder:** collect PNGs (≤ 6 per call; map-reduce beyond that), the artefact `numbers`, top-N table rows, the task spec, recipe, params, CV spec and seed. Build a **FACTS** JSON in which every number has a `fact_id`. Include rule-engine findings.
* **Prompt templates**, versioned in `labcore/insights/prompts/`:
  * `system.md`;
  * `eda_artefact.md`, `eda_summary.md` (including recommended preprocessing as `apply_patch` and suitable models + CV);
  * `model.md` (per-model: CV mean/std, fold CV%, train–CV gap, learning/validation curves, overfitting diagnosis, residual or confusion analysis, next steps);
  * `eval_classification_{cm,report,curves,calibration,threshold,errors,imbalance,compare}.md` (§41.14) and `eval_regression_{fit,residuals,influence,segments,intervals,compare}.md` (§42.8), with the rule-engine triggers listed there;
  * `leaderboard.md` (champion/challenger rationale with CD groups);
  * `explain.md` (SHAP/LIME/PDP/ICE/ALE/permutation narrative + plain-language math + method disagreements);
  * `prediction.md` (probabilities, calibration, intervals/conformal guarantee in words, confidence score, OOD, counterfactual);
  * `timeseries.md`; `unsupervised.md`; `finance.md` (PBO/DSR/CPCV-path narrative);
  * `wfo.md` (walk-forward verdict, WFE, parameter stability, costs, retraining value; extra fields per §32.11);
  * `intake.md` (dataset intake adjudicator; output schema §33.9, not the insight schema).
* **Intake LLM adjudicator** (§33.9): plug into the Phase 1A detector pipeline. Send the profile JSON with no raw rows (≤ 5 sanitised example values per non-PII column) and column names only as data. Use JSON-schema decoding. The validator enforces that columns exist, hard rules win, family changes stay within 0.15 of the detector confidence and cite evidence, and h_max ≤ HorizonGuard. Fall back to the rule-based proposal on failure.
* **Output JSON schema** exactly as ARCHITECTURE §23.4: `stage`, `scope`, `headline`, `findings[{title, detail, severity, category, evidence[{ref, value}], plain_language}]`, `recommendations[{action, why, target_module, apply_patch, priority}]`, `model_commentary[]`, `ranking_rationale`, `caveats[]`, `glossary[]`, `confidence`.
* **Validator:**
  * The output must pass the JSON schema.
  * Every numeric token in the text must match a FACTS value (rounding-aware, rel tol 1e-3) or sit in a `derived` list with its formula.
  * Every finding must cite ≥ 1 existing fact or artefact ID.
  * Banned content: investment advice and certainty claims.
  * On failure, run 1 repair round, then fall back to the rule engine output.
* **Caching:** `insights` table keyed by `sha256(inputs) + model + prompt_version`. Invalidate when the artefacts change.
* **Async + streaming:** `q.insights` with priority and per-user quota. Stream tokens over SSE; the final validated JSON replaces the stream.
* **UI — AI Insights side panel** on every module:
  * Tabs: This page / This panel / Chat (grounded Q&A over the same FACTS).
  * Content: severity pills, citation chips that scroll to the cited panel, **Apply** buttons (creating a new recipe or run version, with confirmation), glossary, feedback 👍/👎, regenerate (brief/standard/deep), and a footer with model, prompt version and timestamp (IST).
  * Each `LabPanel` gets a ✦ button for a single-artefact insight.
* **Guardrails:**
  * Local-only by default; PII column redaction.
  * Cell values never appear in the instruction section; column names are sanitised against prompt injection.
  * Rate limits; audit log of prompt hash and output.
  * Human-in-the-loop for Apply.
  * Disclaimer on financial stages.

**AC:**
- [ ] DS18 (Mall Customers): K-Means picks k=5 by silhouette/gap consensus and profiles render; HDBSCAN and GMM run.
- [ ] DS19: anomaly scores render. On DS21 (fraud, labels hidden), IsolationForest PR-AUC is reported against the hidden labels.
- [ ] With the NVIDIA primary chain (live key, manual/nightly job), insights are produced for every stage on DS3, DS12, DS22 and DS30:
  - [ ] 100% schema-valid;
  - [ ] **100% citation validity**;
  - [ ] **0 unmatched numbers** after validation;
  - [ ] p95 latency under 30 s per artefact (record the measured value; do not invent it).
- [ ] The cache hit returns in under 200 ms.
- [ ] With the provider unreachable or `NVIDIA_API_KEY` unset, the panel shows rule-based and numbers-only insights without errors.
- [ ] Mocked-provider tests pass: 429 → back-off → success; 404 → next model in chain; 413 → image shrunk and retried; circuit breaker opens after 3 failures; budget exhausted → numbers-only.
- [ ] Every golden artefact image encodes to ≤ 170,000 base64 bytes.
- [ ] A grep test proves `NVIDIA_API_KEY` never appears in logs, API responses or the frontend bundle.
- [ ] A prompt-injection test (a column named `"ignore previous instructions…"`) does not alter the output schema or behaviour.
- [ ] A hosted adapter cannot be called while disabled (test).
- [ ] Intake with the LLM keeps every Phase 1A golden result. A prompt-injection column name cannot change roles of other columns. An LLM proposal that uses a hard-excluded column is rejected and falls back to rules.
- [ ] The WFO insight for DS30 lists `wfo_verdict.failed_rules` consistent with the computed verdict, and every `weak_windows[].window` exists.
- [ ] Evaluation insights: on DS4 the `cm` and `threshold` templates cite CLE.T.CM / CLE.T.THRESHOLD_CHOICE fact IDs, name the most-confused class pair that CLE.T.TOP_CONFUSIONS reports, and every number matches FACTS; on DS12 the `residuals` template's verdicts match REE.T.RESID_TESTS.

### Phase 6A — VLM decision agent (ARCHITECTURE §38)

**Scope:**
* `labcore/decisions/`: decision points **VD1–VD12** (§38.2), each with: plot set to render, FACTS builder, enumerated action space, **rule baseline**, **hard guards**, per-decision `choice` sub-schema (§38.5).
* Agent loop (§38.3): observe → baseline → propose (VLM, JSON-schema constrained, temperature 0.2, seed 42) → verify (schema, numbers vs FACTS, option in action space; 1 repair round) → guard → review (decision card) → apply (new versioned config) → log → optional reflection (≤ 2 iterations).
* Modes per decision point: Manual / Propose (default) / Auto-apply (admin-enabled; only when guards pass, confidence high and the proposal equals or is within tolerance of the baseline).
* Tables `decisions`, `decision_feedback` (RLS); API per §38.6; UI decision cards inline in the stepper and an **Agent timeline** drawer; workspace settings page listing VD1–VD12 with mode toggles.
* Evaluation harness with golden expected decisions (e.g. DS22 m = 12, DS18 k = 5, iris DR k = 2, DS30 triple barrier suitable).

**AC:**
- [ ] 0 guard violations reach APPLY across the golden set (property test with adversarial VLM outputs, e.g. h > h_max, shuffled CV on sequential data, financial label on a Not-suitable dataset).
- [ ] With the NVIDIA `vision_standard` chain, agreement with expected decisions ≥ the rule baseline's agreement on the golden set; results stored per model/prompt version.
- [ ] With the VLM unreachable, every decision point shows the baseline labelled "numbers-only" within 10 s.
- [ ] Every applied decision creates a new config version and an audit row with inputs hash, prompt version and user action.
- [ ] A prompt-injection column name cannot change the action space or bypass guards.

### Phase 6B — Per-family catalogue completion (ARCHITECTURE §36)

**Scope:** implement every metric, table and plot listed in §36 that is not yet built: REG.T.* / CLF.T.* (incl. threshold, gains, WOE/IV), DR (KMO/MSA, Bartlett, eigen table with Kaiser / broken-stick / parallel analysis, loadings, communalities, contributions, cos², trustworthiness/continuity, Shepard, stress, reconstruction error, method comparison; scree, cumulative variance, biplot, correlation circle, loadings heatmap, 2D/3D embeddings, perplexity/UMAP grids), clustering (k-scan table with inertia, silhouette, CH, DB, Dunn, gap, BIC/AIC, bootstrap ARI/Jaccard; sizes, centroids, profiles, distinguishing features, surrogate rules; external ARI/AMI/NMI/homogeneity/completeness/V-measure/FMI/purity; elbow, silhouette knife plot, dendrogram + cophenetic, k-distance, reachability, HDBSCAN tree, cluster-on-PCA/UMAP, profile heatmap, parallel coordinates, radar, Sankey, co-association), anomaly (ANO.T.*, score histogram, ranked scores, contribution bars, agreement heatmap).

**Also in scope (round-3 library audit, ARCHITECTURE §43):** register the added algorithms R52–R62, C36–C45, Q14–Q18, D23–D28, K20–K23, A15–A23, F55–F67 and encoders E23–E32, the added CV keys (§43.9), EDA additions (§43.10: EDA.T.ALERTS, PHIK, ASSOC, SPLIT_COMPARE, DIST_CORR, HURST, CONTRACT and plots) and the XAI/UQ/tuning additions (§43.11). Items flagged optional/off by default stay off. KMO/Bartlett are computed with thin numpy/scipy formulas and tested against `factor_analyzer` (dev-only, GPL) as an oracle.

**AC:**
- [ ] A catalogue test renders every artefact ID in §36, §41 (CLE.*) and §42 (REE.*) on its golden dataset (DS3/DS12 regression, DS4/DS10 classification, iris/wine DR, DS18 clustering, DS19/DS21 anomaly) and fails on any missing ID.
- [ ] KMO and Bartlett match `factor_analyzer` on the wine dataset to 1e-6; trustworthiness matches sklearn.
- [ ] Gap statistic and bootstrap stability are reproducible with seed 42.
- [ ] Every new artefact has an ExplainCard with LaTeX math.
- [ ] Every §43 addition is in `GET /catalog` with its Library value, fits on its golden dataset, and no registry entry lacks a library from §44 (CI test).

### Phase 7 — Reports, Monitoring, Enterprise, Portfolio Lab

**Scope:**
* **Reports:** a builder where panels and insights are dragged in. Templates: EDA, Model, Forecast, Financial validation, Executive. Formats: PDF (SP gold theme), HTML (interactive), DOCX, PPTX, XLSX. Scheduled re-runs.
* **Monitoring:** PSI/KS/JS drift per feature, prediction drift, performance when labels arrive, calibration drift, alerts.
* **Enterprise:** OIDC SSO, quotas (jobs, CPU/GPU-hours, storage, VLM tokens), admin dashboards, audit export, data retention, backups (Supabase daily backups / PITR). Optional: Kubernetes + KEDA scale-out of workers and a GPU node pool (§39.12) — only if the user asks.
* **Scheduled batch scoring** (optional): run a saved Prediction Studio job on a schedule against a new file in Storage, with drift checks and an in-app notice; scheduled drift checks for `@champion` models.
* **Portfolio Lab** (new module) wrapping TradingLab `portfolio_optimization` (HRP, HERC, NCO, CLA, MVO, risk estimators) and `online_portfolio_selection`. Inputs: a returns matrix (e.g. NIFTY constituents via the Yahoo chart API, DS31).

**AC:**
- [ ] A PDF report for DS3 includes EDA, the leaderboard, SHAP and insights, with correct fonts and gold theme.
- [ ] The PPTX opens in PowerPoint/LibreOffice.
- [ ] Drift alerts fire on a synthetic shift (PSI > 0.2).
- [ ] Locust: 50 users and 20 concurrent jobs keep API p95 under 300 ms.
- [ ] OWASP ZAP baseline shows no high findings.
- [ ] HRP weights match TradingLab's own tests.

---

### Phase 8 — Deployment: GitHub monorepo + Vercel + Render + Supabase (ARCHITECTURE §39)

Run **8.1** right after Phase 1 (deploy early, with sample data only) and **8.2** after Phase 7. Ask the user before every step that touches an external account (see §00).

**8.1 Hosted skeleton — scope:**
* **GitHub:** with the user's confirmation, create a **private** repo `arw-ml-lab` (`gh repo create … --private --source . --push`); branch protection on `main` (CI required); add the TradingLab submodule.
* **Supabase:** user creates (or confirms) a Pro project in a region close to India (Mumbai `ap-south-1` or Singapore); `supabase link`; `supabase db push --remote --yes` for the kit migrations; buckets `datasets`, `artefacts`, `models`, `reports`, `plots`, `predictions` (private) with storage policies and the size/type limits of the migrations; raise the project's **global file size limit to 2 GB** (Pro; Free caps uploads at 50 MB); Auth email OTP with the company-domain allow-list; redirect URLs for the Vercel domains.
* **Render:** connect the repo and create services from `render.yaml` (Blueprint): `lab-api` (web, `1c-2g`), `lab-worker-light` (worker, `2c-4g`), `lab-worker-train` (worker, `4c-16g`), `lab-beat` (cron job `0.5c-512mb`, hourly maintenance), `lab-kv` (Key Value `1g`, `noeviction`, internal only); services use `autoDeployTrigger: "off"` so only `deploy.yml` deploys them, after migrations; fill `sync: false` secrets in the dashboard; region Singapore.
* **Vercel:** import the repo with Root Directory `frontend`; set env vars per the matrix; Pro plan for company use.
* **CI/CD:** `.github/workflows/ci.yml` (frontend lint/typecheck/vitest/build; backend ruff/mypy/pytest; `supabase start` + `supabase db reset` + `supabase test db`) and `deploy.yml` (migrations → Render deploy hooks → smoke tests; Vercel via its Git integration). Migrations follow expand → migrate → contract so a running app keeps working (§46.2 OPS-11). Secrets only in GitHub/Vercel/Render settings.

**8.2 Production hardening — scope:** job soft/hard time limits per queue (§39.3), memory estimator and refusal messages, worker recycling, `maxShutdownDelaySeconds: 300`, Optuna study resumability, Supabase pooler settings (transaction mode for API, session/direct for workers), CORS allow-list, rate limits, Sentry, backups/PITR, the hosted AI provider settings (`NVIDIA_API_KEY` as a Render secret on lab-api and both workers only, chains, `AI_RPM_LIMIT`, daily caps, health check + circuit breaker → numbers-only), optional external GPU worker for `q.train.gpu` (heavy DL only), a deploy/admin guide in `docs/DEPLOY.md`. Implement and close every open item of `docs/STRESS_TEST.md` and §46.2–§46.4 (heartbeats + reaper, idempotency keys, cancellation, egress allow-list, Sentry PII scrubbing, OpenTelemetry, backups incl. Storage copies, restore drill).

**AC (from §39.13):**
- [ ] Render Blueprint sync creates lab-api, two workers, the lab-beat cron job and lab-kv from `render.yaml` with no manual service creation.
- [ ] `supabase db push` applies all migrations to an empty project; `supabase test db` RLS tests pass in CI.
- [ ] The Vercel production build succeeds from `frontend/`; no server bundle imports Python or data libraries; no BFF route exceeds 10 s in tests.
- [ ] A 200 MB CSV uploads browser → Supabase Storage (resumable) without touching a Vercel function.
- [ ] On the hosted stack, DS1 runs EDA → Quick train → leaderboard → explain → predict; artefacts appear in Storage; progress streams over SSE.
- [ ] Killing `lab-worker-train` mid-tuning and restarting resumes the Optuna study.
- [ ] With the AI provider unreachable (or the key unset), insights and decisions fall back to numbers-only within 10 s; `NVIDIA_API_KEY` is not set in Vercel and is absent from every client bundle.
- [ ] CI blocks merges on lint/type/test/RLS failures; `deploy.yml` runs migrations before services and the smoke tests pass.
- [ ] `docs/DEPLOY.md` lists every service, plan, env var and the rollback procedure.
- [ ] Every row of `docs/STRESS_TEST.md` with status "build" is implemented and has a passing test or a documented manual check.
- [ ] Restore drill: a PITR restore to a scratch project and a Storage restore of one model succeed (documented).

---

## 6. UX details to get right

* **Module sub-pages:** every module follows the SP rhythm, e.g. Supervised → Home · Setup · Model Lab · Runs · Leaderboard · Diagnostics · Intel (Logic Atlas) · Upload.
* **Shared components:**
  * `LabPanel`: SP `panel-luxe` card with title, section-kicker, ⓘ ExplainCard, ✦ insight, ⤢ expand overlay, download PNG/CSV/JSON.
  * `DataGrid`: virtualised. `MetricTile`. `StatusPill`.
  * `ParamForm`: generated from ParamSpec, with Defaults/Customise toggle and a search-range editor.
  * `CVVisualizer`, `JobProgress` (live-sync-pill), `LeaderboardTable`, `PlotlyChart` (theme-aware: gold accents, teal `#00d4aa` as data-viz accent from blackcarbon), `FinanceChart` (lightweight-charts), `InsightsPanel`, `ExplainCard`.
* **Home Terminal:** KPI tiles (datasets, running jobs, champions, insights), recent experiments, live job tape (SP `tape-chip` style), quick start with sample datasets.
* **Interaction:** every plot is interactive (zoom, hover with exact values, legend toggle, lasso where useful), switches with the dark/light theme, and exports PNG/SVG.
* **Accessibility:** keyboard navigation and WCAG AA contrast in both themes.
* **Time zone:** all timestamps display in **Asia/Kolkata (IST)** by default; this is a user setting.

---

## 7. Definition of done (whole project)

* All phase AC are green in CI, plus Playwright E2E for these journeys:
  * Titanic (classification);
  * California Housing (regression);
  * Airline (forecast);
  * NIFTY 50 (financial CPCV/PBO and walk-forward optimisation with verdict);
  * upload → AI Intake Review → confirm → EDA on a new file, then append an update and verify the schema-diff/carry-forward flow;
  * Mall Customers (clustering);
  * Prediction Studio: batch upload of a `data/samples/predict` file and the custom form for Titanic, California Housing and Airline.
* Every algorithm, metric, plot, test, encoder and CV scheme has an ExplainCard with LaTeX math. A CI test fails if any registry key lacks an education entry.
* Every classification run shows the complete §41 suite (confusion matrix in counts + 3 normalisations, per fold and CV-aggregated; full classification report; all applicable metrics with CV mean ± std; curves; calibration; threshold; errors) and every regression run the complete §42 suite.
* Every registry entry names its library, and every library is in ARCHITECTURE §44 and `backend/requirements/*.txt` (import allow-list check green).
* The AI Insights side panel works on every module, with grounded and validated output.
* `docs/` contains updated ARCHITECTURE.md, FLOWCHART.md (Mermaid), STRESS_TEST.md (all items closed or accepted with a reason), PROGRESS.md, the phase reports, a user guide and an admin/deploy guide.
* The app is live on Vercel + Render + Supabase with CI/CD from GitHub, Phase 8 AC green, and the financial suitability check and VLM decision agent active on every relevant flow.
