# ARW ML Lab — End-to-End Architecture (v2.2, design only)

> A world-class, general-purpose **Machine Learning Lab** web app for any tabular dataset (numeric + categorical; not NLP/text).
> Users upload data, pick inputs and output(s), choose the family (**Supervised**, **Unsupervised**, **Time Series**),
> and the lab runs EDA → preprocessing → modelling → cross-validation/tuning → model selection → explainability →
> prediction, with an **AI Insights** layer (hosted vision-language model via the NVIDIA API catalog, swappable providers, numbers-only offline fallback — §40) that reads every plot and table.
>
> Owner: Shibayan Biswas (Anand Rathi Wealth). Prepared 14 Nov 2026 (IST). Status: architecture + build plan; nothing built yet. v2.0 (round 2) adds §34 Deep Learning, §35 Time Series, §36 per-family metrics/tables/plots, §37 financial labelling suitability, §38 VLM decision agent and §39 hosted deployment (GitHub + Vercel + Render + Supabase, now the primary path). v2.2 (round 4, 15 Nov 2026) adds §45 **Prediction Studio** (batch upload with validation, intervals/probabilities/flags and downloads; auto-generated custom input form; feature contracts; prediction samples for all 33 datasets) and §46 **Hardening** (stress-test results: ML integrity, scale/ops, security, UX, feature parity with AutoML tools; findings in `docs/STRESS_TEST.md`). The build prompt is `CURSOR_PROMPT.md`.

---

## Table of contents

1. Reference study: what we take from each repo
2. Product scope, personas and the end-to-end journey
3. System architecture
4. Tech stack (with justification)
5. Frontend: workstation shell, design language and full module map
6. Backend services and API
7. Data model / database schema
8. Job orchestration, progress streaming and scaling
9. Ingestion, schema inference and problem-type detection
10. EDA module catalogue (tables + plots)
11. Preprocessing and feature-engineering catalogue (incl. all encodings)
12. Supervised learning catalogue (regression, classification, DL, sequential)
13. Cross-validation catalogue
14. Hyperparameter tuning and the parameter-spec system ("defaults vs customise")
15. Metrics catalogue with formulas
16. Supervised plot catalogue
17. Explainability (SHAP, LIME, PDP, ICE, ALE, permutation, more)
18. Unsupervised learning catalogue (dimensionality reduction, clustering, anomaly detection)
19. Time-series analysis and forecasting catalogue
20. Smart forecast-horizon rules
21. Probabilistic prediction and uncertainty
22. Prediction / Inference module
23. AI Insights layer (open-weights VLM)
24. Education layer (math + theory for every algorithm, metric and plot)
25. Experiment tracking, model registry, export and reports
26. Security, multi-tenancy, governance
27. Sample dataset catalogue (verified URLs, defaults, seeds)
28. Testing strategy
29. Repository / folder structure
30. Phased roadmap
31. Open questions and what could not be verified
32. Walk-Forward Optimisation (WFO) module — anchored/rolling windows, purging, per-window re-tuning, stitched OOS, WFE, parameter stability, Monte Carlo, DSR/PBO, costs
33. AI Dataset Intake / Auto-Setup — index & frequency detection, family/task inference with confidence, column roles, target/feature recommendation, leakage suspects, schema drift & versioning
34. Deep Learning — full specification: tabular T1–T16 and sequential Q1–Q13 architectures with math, hyperparameters, defaults/search spaces, training plots, DL tables, uncertainty, CPU/GPU
35. Time Series — full specification: TS EDA and test tables, every family's hyperparameters, multi-step strategies, exogenous, hierarchical/multivariate, backtesting, metrics, residual diagnostics, leaderboards
36. Per-family catalogue — metrics (formula + interpretation), tables (exact columns) and plots (shows/axes/when) for regression, classification, DL, TS, dimensionality reduction, clustering, anomaly detection
37. Financial labelling suitability check — FS1–FS20 pass/warn/fail rules before triple-barrier / meta-labelling / fixed-horizon / trend-scanning, report schema, fallback
38. VLM decision agent — 12 decision points, rule baselines, hard guards, human approval, prompts, JSON schemas, agent loop, audit
39. Deployment — GitHub monorepo, Vercel (frontend), Render (API + workers + Key Value via render.yaml), Supabase (Postgres, Auth, Storage, RLS, CLI migrations), sizing/limits, VLM hosting, CI/CD, env matrix, optional K8s
40. AI provider layer — hosted VLM/LLM via NVIDIA API catalog (primary), provider abstraction (Gemini / OpenRouter / Groq fallbacks), image sizing, retries, rate limits, caching, budgets, data protection
41. Classification Evaluation Suite — confusion matrices (counts, row/column/all-normalised, per-fold, CV-aggregated, cost-weighted, multilabel), full classification report, 55 metrics with formulas, 45 plots, threshold optimisation, imbalance reporting, CV mean ± std, model comparison, statistical tests, AI prompts
42. Regression Evaluation Suite — audit and completion: 40 metrics, residual/influence/test tables, 36 plots, CV aggregation, comparison tests, AI prompts
43. Library gap audit — additions (algorithms, encoders, preprocessing, CV, EDA, XAI) and replacements so every item is backed by a maintained library
44. Appendix — Library Matrix (library, version pin, licence, purpose, requirements file, PyPI link)
45. Prediction Studio — batch upload (validation, outputs per task, downloads) and custom input form (auto-generated from the feature contract), API, DB, components, samples
46. Hardening — ML integrity, scale/ops, security, UX guarantees and feature parity (stress test v2.2)

---

## 1. Reference study

### 1.1 `ShibayanBiswas/blackcarbon-saas` (main UX/stack/code-structure reference)

Read via the GitHub connector (repo is private): README, `docs/WEB_APP_PLAN.md`, `frontend/orchestrator.jsx`, `frontend/index.css`,
`frontend/pages/Modeling.jsx`, `frontend/components/ExplainCard.jsx`, `backend/ml/{orchestrator.py, pipeline/models.py, pipeline/param_grids.py, train/run.py, eda/run.py, preprocess/scale.py}`, `infra/schema.sql`.

| Aspect | What blackcarbon-saas does | What the ML Lab keeps / upgrades |
|---|---|---|
| Topology | 3 tiers: React (Vite) SPA → Node/Express gateway (`backend/api/orchestrator.js`, port 4080: auth, data, models, predict, explain, admin) → Python FastAPI ML service (`ml.orchestrator:app`, port 5080: `/eda`, `/train`, `/train/{job}/status`, `/models/{ds}/{t}/summary`, `/plot`, `/deploy`, `/predict`, `/explain/shap`) | Keep the **gateway + Python ML service** split. Gateway becomes Next.js route handlers (aligned with SP Workstation); ML service stays FastAPI, plus Celery workers. |
| Pages | Sidebar: Home, Data & EDA, Modeling, Explainability, Prediction, Admin, Account | Same skeleton, expanded into workstation **modules with nested sub-pages** (see §5). |
| ML layout | `backend/ml/{data, preprocess, eda, pipeline, train, explain, predict, registry}` + `config.py`, `plot_style.py`, `log_config.py` | Same package split, generalised from 2 fixed datasets to any dataset; add `unsupervised/`, `timeseries/`, `cv/`, `uncertainty/`, `insights/`. |
| Models | 22 sklearn regressors + XGB/LGBM/CatBoost, then Stacking/Voting on tuned bases | Carried over and extended to classification, DL, sequential, unsupervised and TS. |
| Tuning | `param_grids.py`: per-model grids with **presets fast / balanced / thorough**, `RandomizedSearchCV`, KFold / RepeatedKFold (`cv`, `cv_repeats`) | Presets kept (renamed **Quick / Balanced / Thorough / Exhaustive**) and become the "defaults" side of the defaults-vs-customise toggle. Optuna added. |
| Scalers | standard, minmax, robust, maxabs, power (Yeo-Johnson), quantile (normal); IQR + z-score outliers; median imputation; every model trained × every scaler (`Model__scaler`) | Kept, plus full imputation/encoding/transform catalogue; the "model × scaler" grid becomes a "model × preprocessing recipe" grid. |
| Metrics table | R², RMSE, MAE, MSE, MedAE, MaxErr, MAPE, explained variance, Pearson r for val (mean ± std) and test | Same table component, generalised per task. |
| Diagnostic plots | pred_vs_actual, residuals, residual_dist, residual_qq; EDA: histograms, heatmap, PCA scree/2D/3D, box, violin, strip, beeswarm, letter-value, raincloud, KDE, Q-Q, ECDF, pairplot, scaler comparison | All kept; switched from static PNG (matplotlib/base64) to **interactive Plotly JSON** with server-side PNG export (needed for reports and the VLM). |
| Explainability | SHAP bar, beeswarm, waterfall; PDP; feature importance | Extended (LIME, ICE, ALE, permutation, interactions, counterfactuals). |
| Education | `ExplainCard` (expandable card: intuitive text, detail, KaTeX display math, inline `\( \)` math, literature ref); content in `frontend/content/explanations.js` (82 KB) and `pageIntros.js` | Kept as the **Education layer**: every algorithm, metric, plot and test gets an ExplainCard entry from a typed content registry. |
| Registry/deploy | joblib in `backend/ml/models/<ds>/<target>/<model>/<scaler>/`, deploy = best by R² val | Replaced by MLflow 3 tracking + registry with aliases (`@champion`). |
| Theme | Dark "tech dashboard": `--bg-deep #0a0b0f`, glass cards, accent teal `#00d4aa`, gold `#e8c547`, fonts DM Sans / Outfit / JetBrains Mono, sci-fi glows | Superseded by SP Workstation tokens (below) for brand consistency; teal kept as a **data-viz accent**. |
| DB | Postgres: users, datasets, training_jobs, models, predictions | Extended to a multi-tenant schema (§7). |

### 1.2 "SP Workstation modules" = `ShibayanBiswas/sp-workstation`

The user asked that the whole app look like the **SP workstation modules**. That phrase matches a sibling repo,
`ShibayanBiswas/sp-workstation` ("Anand Rathi Wealth — Structured Products Team Workstation"), found via the GitHub connector. Its design language:

* **Stack:** Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 4 + global CSS design tokens, `lucide-react` icons, `zod`, `jose` JWT + `bcryptjs`, local OTP sign-in, MongoDB/Mongoose, `lightweight-charts` (TradingView) for candlesticks. Desk modules (Primary SP, Secondary SP, Dynamic Probability Calculator, Unwinding Calculator, Active Management, Swap Product Creation, Hedging Sheet, Gift City AIF Backtester/Forwardtester, Options Lab) are separate Next.js apps (recharts, framer-motion, exceljs, jspdf, @tanstack/react-virtual) embedded via iframes.
* **Shell (`DashboardShell.tsx` + `Sidebar.tsx`):** left sidebar 280 px (collapsed 76 px, persisted in `localStorage`), mobile drawer + top bar; brand logo on top; **"Home Terminal"** link; a small-caps **MODULES** kicker; each module is a row with an icon badge + label + chevron, expanding to a gold-ruled nested tree of sub-pages (`NavItem` tree with arbitrary depth); user card with initials avatar on a gold gradient; Light/Dark toggle and Sign out at the bottom.
* **Module registry (`src/data/modules.ts`):** a typed `ModuleGroup { id, label, description, icon, href, routeSlug, embedBase, frameTitle, nav: NavItem[], submodules }`. Every desk module follows the same sub-page rhythm: **Home · Analytics · Desk/Workbench · (domain pages) · Intel/Intelligence (Logic Atlas) · Upload**.
* **Tokens (`globals.css`):** light `--bg #f7f9fc`, `--bg-elevated #fff`, `--fg #152033`; dark `--bg #050506`, `--bg-elevated #0e0e10`, `--fg #f4f2ec`, `--border rgba(229,207,148,.10)`; **gold** `--gold #c9a227` / `--gold-soft #e4d5a0` / `--gold-deep #9a7b1a`; fonts **Cormorant Garamond** (display), **DM Sans** (body), **IBM Plex Mono** (numbers); classes `panel-luxe`, `glass-panel`, `section-kicker`, `gold-gradient`, `gold-text-shimmer`, `status-pill`, `live-sync-pill`, `module-tile`, `tape-chip`, `terminal-header-luxe`, `fin-num`/`tv-num` tabular numerals, `animate-rise` entrance motion.
* **Home Terminal:** live tape, snapshot cards, 70/30 chart + quote panel with Expand overlay, live-sync indicator.

**Decision:** the ML Lab is built as a workstation of the same kind: the same shell, sidebar tree, tokens, typography, panel styles and
"Home / Analytics / Workbench / Intel / Upload" rhythm, with ML modules instead of desk modules. Unlike SP Workstation (iframes to
separate apps) the ML Lab modules are **in-app routes** of one Next.js app, because they share one dataset/experiment context;
the `modules.ts` registry pattern is reused as-is so the lab can later be **embedded as a module inside SP Workstation** (one more `ModuleGroup` with `embedBase` = the lab URL).

### 1.3 `ShibayanBiswas/ml-for-trading` (TradingLab — financial/sequential reference)

A Python research toolkit (`tradinglab/`) following López de Prado's *Advances in Financial ML*. Packages read: README, `cross_validation/README.md` (+ `time_series_cv.py`, `combinatorial.py`), `backtest_statistics/strategy_metrics.py`, `docs/source/DEPTH_REFERENCE.md`, tree of all 320 files.

| TradingLab package | Used in the ML Lab for |
|---|---|
| `data_structures/` (time, tick, volume, dollar, imbalance and run bars) | Sequential ingestion option "resample to bars" for tick/intraday uploads. |
| `features/fractional_differentiation.py` (FFD) | Stationarity-preserving-memory transform in Preprocessing (sequential) and TS. |
| `labeling/` (triple-barrier, meta-labeling, fixed horizon, trend-scanning, excess over mean/median, vs benchmark, tail sets, matrix flags) | **Target builder** for financial sequential supervised tasks. |
| `sampling/` + `sample_weights/` (concurrency, uniqueness, sequential bootstrap, return attribution, time decay) | Sample weights passed to estimators; sequential bootstrap bagging. |
| `cross_validation/` (`PurgedKFold`, `PurgedSplit`, `CombinatorialPurgedKFold`, `ml_cross_val_score`; purge + embargo using label spans `samples_info_sets`) | **Purged/embargoed K-fold and CPCV** in the CV catalogue; required default for financial sequential data. |
| `feature_importance/` (MDI, MDA, SFI, clustered FI, orthogonal/PCA FI, model fingerprints) | Extra explainability for sequential/financial models. |
| `clustering/onc.py`, `feature_clusters.py`; `codependence/` (distance correlation, mutual info, variation of information, GNPR) | Feature clustering and dependence matrices in EDA/Unsupervised. |
| `structural_breaks/` (Chow, CUSUM, SADF) | Structural break tests in TS analysis. |
| `filters/event_filters.py` (CUSUM filter) | Event sampling for financial targets. |
| `microstructural_features/` (Roll, Corwin-Schultz, Kyle/Amihud lambda, VPIN, entropy) | Optional feature packs for intraday data. |
| `backtest_statistics/` (Sharpe, Information ratio, **Probabilistic and Deflated Sharpe**, MinTRL, drawdown & time under water, bets concentration (HHI), holding period, flips) | Financial metrics for sequential models (strategy-from-predictions backtest). |
| `ensemble/sb_bagging.py` | Sequentially-bootstrapped bagging classifier/regressor. |
| `portfolio_optimization/` (MVO, CLA, HRP, HERC, NCO, TIC), `online_portfolio_selection/` | Out of scope for v1 (could become a later "Portfolio" module). |
| Docs style: Mermaid flows, one deep-reference README per package, explicit seeds, artifact runs `figures/ tables/ logs/` | Same conventions for the lab's docs and test artefacts. |

---

## 2. Product scope, personas and journey

**Personas:** (1) Analyst/RM with no ML background (uses defaults, reads AI Insights + ExplainCards); (2) Quant/data scientist (customises every parameter, uses purged CV, exports code); (3) Admin (users, quotas, model approvals); (4) Consumer of a deployed model (Prediction module / REST API).

**In scope:** tabular CSV, TSV, Excel (xlsx/xls, sheet picker), Parquet, Feather, JSON lines; numeric, categorical, boolean, datetime, ID columns; up to ~10 M rows × 2 000 cols per dataset (sampling for heavy plots). **Out of scope:** free-text NLP, images, audio (text columns are detected and either dropped, hashed or length-encoded — never modelled as language).

**The journey (one "Experiment" = dataset version + task spec + runs):**

1. **Upload** → schema inference → data-quality report → dataset version stored as Parquet.
2. **Task setup wizard:** pick **family** (Supervised / Unsupervised / Time Series) — required, user's choice.
   * Supervised: pick target(s) + inputs → lab **auto-detects** regression vs binary vs multiclass vs multi-label vs multi-output (rules in §9) with an override; pick **data ordering: Sequential (time-ordered, e.g. financial) or Non-sequential (i.i.d.)**; if sequential, pick the time index and optional group/entity column.
   * Unsupervised: pick inputs; sub-task **Dimensionality reduction**, **Clustering**, **Anomaly detection**, or all.
   * Time Series: pick time index, target series (one or many), frequency (auto-inferred), exogenous regressors (past-only vs known-future), optional series-ID column for panels; forecast horizon (smart-limited, §20).
3. **EDA** (auto-runs on upload; task-aware sections appear once a target is set).
4. **Preprocessing recipe** (auto-suggested, editable; leakage-safe pipelines).
5. **Model lab**: choose algorithms (all ticked by default per family, grouped), per-algorithm "Use defaults / Customise" toggle, CV strategy, tuning strategy, budget.
6. **Run** → async jobs with live progress, logs, partial leaderboard.
7. **Leaderboard & model selection** (multi-metric, statistical comparison, Pareto of score vs latency).
8. **Diagnostics + Explainability** per model.
9. **Prediction** (single row form, batch file, what-if; probabilistic outputs).
10. **AI Insights** side panel at every step; **Report** export; **Register/Deploy**.

---

## 3. System architecture

See `FLOWCHART.md` §3 and `diagrams/03_system_architecture.png`.

> **Hosted deployment (primary, §39):** the logical architecture below maps to Vercel (Next.js BFF), Render (FastAPI `lab-api` web service, Celery background workers, Render Key Value as Redis), and Supabase (Postgres 17, Auth, Storage replacing MinIO). AI calls go from the workers to the hosted NVIDIA API catalog (§40); only optional heavy DL training may use an external GPU worker. The single-box Docker Compose layout remains for local development.

```
Browser (Next.js 16 / React 19 workstation UI)
   │  HTTPS (cookies: JWT session); SSE job progress + AI streaming go directly to lab-api (§39.4, §46.6)
   ▼
Next.js server (BFF / gateway): auth, RBAC, routing, upload signing, rate limits (short requests only, < 10 s)
   │  internal HTTP (mTLS / service token)
   ▼
FastAPI "lab-core" (Python 3.12): datasets, EDA, experiments, runs, models, predict, explain, insights, reports, catalog
   │                     │                      │
   ▼                     ▼                      ▼
PostgreSQL 17     Redis 7 (broker,         Object storage (S3 / MinIO): raw uploads, Parquet versions,
(metadata, JSONB)  cache, pub/sub)          plot JSON/PNG, artefacts, reports, MLflow artefacts
                         │
                         ▼
      Celery workers (queues): q.ingest · q.eda · q.train.cpu · q.train.gpu · q.tune · q.explain · q.forecast · q.insights · q.report · q.predict.batch
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
   MLflow 3 tracking + registry   Hosted AI API (§40): NVIDIA API catalog, OpenAI-compatible
                                   Nemotron 3.5 Super VL primary · Gemma 4 31B / Llama 3.2 90B Vision fallback · numbers-only offline
Observability: OpenTelemetry → Prometheus + Grafana + Loki; Sentry for errors; Flower for Celery.
```

Design principles: (1) **every computation is a job** (idempotent, cached by content hash); (2) **plots are data** (Plotly JSON spec + PNG render + the numbers behind it, so the UI, the report and the VLM read the same object); (3) **leakage-safe by construction** (all fitted transforms live inside the CV pipeline); (4) **registry-driven UI** (algorithms, parameters, metrics, plots, tests, encodings and explanations are declared once in Python registries and exposed via `/catalog`, so the frontend renders forms and info panels generically); (5) **reproducible** (global seed + per-dataset default seed + library versions + data hash stored on every run).

---

## 4. Tech stack

| Layer | Choice | Why (alignment with refs) |
|---|---|---|
| Frontend framework | **Next.js 16 (App Router) + React 19 + TypeScript 5** | Same as SP Workstation; server layout session checks; route handlers act as BFF. |
| Styling | **Tailwind CSS 4** + SP Workstation `globals.css` tokens (gold/ink, light+dark), `lucide-react` icons | Identical look to SP Workstation. |
| UI primitives | Radix UI primitives (dialog, tabs, popover, slider, select) styled in-house; `cmdk` command palette; `@tanstack/react-table` + `@tanstack/react-virtual` (virtualised data grid, as in secondary-sp-dashboard) | Accessible, headless, matches the custom look. |
| Forms | `react-hook-form` + `zod` (zod already used in SP Workstation) — forms generated from backend JSON-Schema param specs | One schema drives validation on both ends. |
| Server state | TanStack Query v5; client state `zustand` (experiment context, panel layout) | Caching, polling fallback, optimistic updates. |
| Charts (scientific) | **Plotly.js** (`react-plotly.js`, `plotly.js-dist-min`, lazy-loaded) | 2D/3D scatter, surface, contour, heatmap, dendrogram, parallel coordinates, violin, box, Sankey, subplot grids; JSON spec produced by Python `plotly` so server and client agree; `kaleido` renders PNGs for reports/VLM. |
| Charts (financial) | **lightweight-charts** (TradingView) | Already used in SP Workstation for candlesticks; used for OHLC, equity curves, forecast fans on price. |
| Charts (KPI micro) | recharts (sparklines, tiny bars) | Already used in blackcarbon & SP desks. |
| Math | **KaTeX** (`katex` + ExplainCard pattern from blackcarbon) | Proven component. |
| Tables export | exceljs, jspdf + jspdf-autotable (as in SP desks) client-side; server-side reports via WeasyPrint/Quarto | Matches existing desk exports. |
| Gateway / auth | Next.js route handlers (BFF on Vercel) + **Supabase Auth** (email OTP / magic link, domain allow-list, optional Google/Microsoft SSO) via `@supabase/ssr`; FastAPI verifies Supabase JWTs with JWKS. (Original SP Workstation `jose` + OTP flow kept only as a fallback pattern.) | Managed auth with RLS integration; keeps the SP look. |
| ML service | **FastAPI** + Pydantic v2 + Uvicorn/Gunicorn, Python **3.12** | Same as blackcarbon ML service. |
| Jobs | **Celery 5** + Redis 7 broker/result backend; Flower | Mature, routing to CPU/GPU/LLM queues, retries, rate limits, chords for parallel CV folds. |
| Data | pandas 2 / **Polars** + **PyArrow** Parquet + **DuckDB** (profiling SQL over large Parquet) | Fast profiling of millions of rows. |
| Classical ML | **scikit-learn 1.9.x** (1.9.1 released Sep 2026), imbalanced-learn, category_encoders, feature-engine, scipy, statsmodels | Core estimators, pipelines, CV, metrics. |
| GBMs | XGBoost, LightGBM, CatBoost | As in blackcarbon `_optional_imports`. |
| Tabular DL | PyTorch 2 + Lightning; **pytorch-tabular** (TabNet, FT-Transformer, TabTransformer, NODE, GANDALF, AutoInt, DANet, GATE, CategoryEmbedding MLP); **TabPFN** (foundation model, ≤10k rows v2; off by default — weights licence) | Breadth with one trainer API. |
| Time series | **statsmodels** (ARIMA/SARIMAX/ETS/UCM/VAR/VECM/STL/tests), **Nixtla statsforecast** (AutoARIMA/ETS/CES/Theta/MFLES/TBATS/MSTL, Croston family, GARCH/ARCH; fast), **neuralforecast** (36 deep models: RNN/LSTM/GRU/TCN/DeepAR/N-BEATS(x)/N-HiTS/TFT/Informer/Autoformer/FEDformer/PatchTST/iTransformer/TimesNet/TiDE/TSMixer/TimeMixer/xLSTM/KAN…), **mlforecast** (LightGBM/XGB with lags), `arch` (GARCH family), `pmdarima` (auto-ARIMA alternative), Prophet, sktime (extra transformers/tests), `ruptures` (change points) | Nixtla covers stats+ML+DL with a single dataframe format (`unique_id, ds, y`) and built-in cross-validation. |
| Unsupervised | scikit-learn, `umap-learn`, `hdbscan` (sklearn has HDBSCAN too), `pyod` (anomaly zoo) + `pythresh`, `tslearn` (time-series clustering), optional K-Medoids (see §43.5), `openTSNE` (fast t-SNE), `prince` (MCA/FAMD for mixed data), `kmodes` (KModes/KPrototypes) | Full coverage incl. categorical clustering. |
| Tuning | **Optuna 5** + optuna-integration (TPE, CMA-ES, GP, NSGA-II/III, QMC, pruners), sklearn Grid/Randomized/Halving search | Bayesian + successive halving. |
| Explainability | **shap**, **lime**, sklearn `inspection` (PDP/ICE/permutation), `PyALE` (ALE), `dice-ml` (counterfactuals), `interpret` (EBM), `captum` (DL), `shapiq` (optional); alibi is BSL-1.1 → licence review only (§43.11) | Full XAI catalogue. |
| Uncertainty | **MAPIE** (conformal regression/classification/time series), NGBoost, quantile GBMs, sklearn calibration, `properscoring`/`scoringrules` (CRPS) | Probabilistic predictions. |
| Tracking/registry | **MLflow 3.x** (3.18.0 released 2 Nov 2026) tracking server on Postgres + S3; model aliases `@champion/@challenger` | Industry standard; lineage. |
| Export | joblib/cloudpickle, **ONNX** (skl2onnx, onnxmltools for XGB/LGBM, torch.onnx), MLflow pyfunc, generated Python training script, FastAPI serving bundle, Docker image | Portable models. |
| VLM / LLM | **Hosted NVIDIA API catalog** (`https://integrate.api.nvidia.com/v1`, OpenAI-compatible): `nvidia/nemotron-3.5-super-vl-120b-a12b` primary VLM, `google/gemma-4-31b-it` and `meta/llama-3.2-90b-vision-instruct` fallbacks, `nvidia/nemotron-3-super-120b-a12b` text reasoning; Gemini / OpenRouter / Groq as optional fallback providers; numbers-only offline (§40) | No GPU to run; swappable by config. Superseded: self-hosted Ollama/vLLM. |
| (superseded) VLM self-hosting | Ollama/vLLM with Qwen3-VL — kept only as an optional `local_openai_compat` provider | Free, self-hosted, no paid API. |
| Infra (primary, §39) | **GitHub monorepo → Vercel** (frontend) + **Render Blueprint `render.yaml`** (FastAPI web service, Celery background workers, Render Key Value) + **Supabase** (Postgres 17, Auth, Storage, RLS, CLI migrations); GitHub Actions CI/CD; Docker Compose for local dev | Managed, low-ops; scale workers independently by plan. |
| Infra (optional scale-out) | Kubernetes + Helm with KEDA on queue length and a GPU node pool for workers only (§39.12) | When Render workers are outgrown. |
| Object storage | **Supabase Storage** (S3-compatible; buckets datasets/artefacts/models/reports/plots) — replaces MinIO | Signed/resumable uploads bypass Vercel's 4.5 MB body limit. |
| Observability | OpenTelemetry, Prometheus, Grafana, Loki, Sentry; structured JSON logs with `run_id` (blackcarbon LOGGING.md style step logs) | Traceability. |
| Quality | pytest + hypothesis, Playwright (as in secondary-sp-dashboard), Vitest + Testing Library, ruff, mypy, eslint, pre-commit, GitHub Actions CI (blackcarbon `ci.yml`) | |

Note on persistence: SP Workstation uses MongoDB; blackcarbon uses Postgres. The lab needs relational integrity (experiments → runs → folds → metrics → artefacts) and MLflow's backend store, so **Postgres** is chosen. Auth users can still be federated with the SP Workstation Mongo roster through SSO/OIDC or a sync job.

---

## 5. Frontend: workstation shell, design language, module map

### 5.1 Shell (mirrors SP Workstation `DashboardShell` + `Sidebar`)

```
┌──────────────┬───────────────────────────────────────────────────────────────┬──────────────────┐
│ SIDEBAR 280px│ TERMINAL HEADER: breadcrumb · dataset chip · task chip ·       │ AI INSIGHTS      │
│ (76 collapsed)│ seed chip · job-status pill (live-sync style) · ⌘K           │ SIDE PANEL       │
│ [ARW ML LAB] ├───────────────────────────────────────────────────────────────┤ (collapsible,    │
│ Home Terminal│ CONTEXT BAR: Experiment ▾  Dataset v3 ▾  Target ▾  Family pill │  360–480px,      │
│ MODULES      │                                                               │  resizable)      │
│ ▸ Data       │  MAIN CANVAS: panel grid (panel-luxe cards), tabs per page,   │ • stage insights │
│ ▸ EDA        │  each panel = [title · ⓘ ExplainCard · ⤢ expand · ⤓ export ·  │ • per-plot notes │
│ ▸ Preprocess │  ✦ Ask AI]                                                    │ • chat w/ context│
│ ▸ Supervised │                                                               │ • citations to   │
│ ▸ Unsupervised│                                                              │   plot/table IDs │
│ ▸ Time Series│                                                               │                  │
│ ▸ Explain    │                                                               │                  │
│ ▸ Predict    │                                                               │                  │
│ ▸ Experiments│                                                               │                  │
│ ▸ Reports    │                                                               │                  │
│ ▸ Learn      │                                                               │                  │
│ ▸ Admin      │                                                               │                  │
│ [user card]  │                                                               │                  │
│ ☾ Dark ⎋ Out │                                                               │                  │
└──────────────┴───────────────────────────────────────────────────────────────┴──────────────────┘
```

* Tokens copied from SP Workstation `globals.css` (light + dark, gold accents, Cormorant Garamond / DM Sans / IBM Plex Mono, `panel-luxe`, `section-kicker`, `status-pill`, `live-sync-pill`, `module-tile`, `animate-rise`). Add data-viz tokens: categorical palette (gold `#c9a227`, teal `#00d4aa` from blackcarbon, ink-blue `#3b6fd8`, coral `#e4572e`, violet `#8a5cf6`, green `#0f7a3c`, grey), diverging (RdBu-like gold↔blue) and sequential (ink→gold) ramps; Plotly template `arw-light` / `arw-dark` generated from tokens so every chart matches the theme.
* `src/data/modules.ts` uses the SP `ModuleGroup`/`NavItem` types (without `embedBase`, plus `requires: TaskFamily[]` so modules that do not apply to the chosen family are dimmed).
* Every module follows the SP rhythm: **Home** (KPI tiles + status) · **Workbench** (do the work) · **Analytics** (plots/tables) · **Intel** (Logic Atlas: math/theory + AI Insights history) · **Upload/Export**.
* Panel primitive `<LabPanel id title kicker explainKey plotId insightScope actions>`: every plot/table is one panel with a stable **artefact ID** (e.g. `EDA.CORR.SPEARMAN`, `SUP.RUN42.LGBM.ROC`), used by AI Insights citations, reports and deep links.
* Global: command palette (⌘K: jump to any plot/model/param), keyboard shortcuts, per-user layout persistence, light/dark, responsive (drawer < 1024 px), WCAG 2.2 AA, i18n-ready, IST timestamps by default (configurable).

### 5.2 Module map (every screen and panel)

| # | Module (sidebar) | Sub-pages (nested tree) | Key panels |
|---|---|---|---|
| 0 | **Home Terminal** | — | Recent experiments tiles; job queue tape (`tape-chip` style: running/queued/done); leaderboard snapshot of champion models; storage/quota; sample-dataset launcher; AI "what next" card. |
| 1 | **Data** | Home · Upload · Sample Datasets · Explorer · Schema & Types · Versions · Joins/Merge | Drag-drop uploader (CSV/XLSX sheet picker/Parquet/Feather/JSONL; delimiter/encoding/decimal sniffing; header row; date parsing; NA tokens); sample gallery cards (§27); virtualised data grid (sort/filter/search, column stats in header); schema editor (role: feature/target/ID/time/group/weight/ignore; type: numeric/categorical-nominal/ordinal(with order editor)/boolean/datetime/text/ID; unit); version diff; data-quality score. |
| 2 | **EDA** | Home · Overview · Univariate · Bivariate · Multivariate · Missingness · Outliers · Target Analysis · Correlation & Dependence · Sequential/Temporal · Data Quality · Report | All tables/plots in §10, each a panel; column picker; sampling control; AI Insights per panel and per page. |
| 3 | **Preprocess** | Home · Recipe Builder · Imputation · Encoding · Scaling & Transforms · Outliers · Feature Engineering · Feature Selection · Imbalance · Financial Features · Leakage Check · Preview | Drag-ordered recipe (sklearn `Pipeline`/`ColumnTransformer` view); per-step params with defaults/customise toggle; before/after distribution plots; leakage audit; recipe diff; "auto-recipe" button. |
| 4 | **Supervised** | Home · Task Setup · Model Lab · CV & Tuning · Runs (live) · Leaderboard · Model Detail · Compare · Ensembles · Financial Backtest | Algorithm picker (grouped tiles with checkboxes + "Use defaults / Customise" per algo); parameter forms; CV designer with fold visualiser; tuning budget; live run monitor (fold progress, partial scores, Optuna history); leaderboard table + metric bar/box plots; model detail tabs: Metrics · Plots · CV folds · Learning curves · Hyperparams · Explain · Predict · Export. |
| 5 | **Unsupervised** | Home · Setup · Dimensionality Reduction · Clustering · Anomaly Detection · Model Selection · Profiles · Compare | DR runner + embedding viewer (2D/3D, colour by any column); clustering runner + k-selection dashboards; anomaly score viewer; cluster profiling tables; assign/export labels back to dataset as a new column. |
| 6 | **Time Series** | Home · Setup · Analysis (Decomposition, ACF/PACF, Stationarity, Seasonality, Breaks, Volatility) · Model Lab · Backtesting · Leaderboard · Forecast · Residual Diagnostics · Multivariate (VAR/VECM, Granger) | Series viewer (lightweight-charts for financial, Plotly otherwise); test result tables; model lab with horizon guard; rolling-origin backtest visualiser; forecast fan chart with intervals; residual 4-pack. |
| 7 | **Explain** | Home · Global (SHAP/permutation/PDP/ALE) · Local (SHAP waterfall/force, LIME, counterfactuals) · Interactions · Financial FI (MDI/MDA/SFI/clustered) · Compare across models | §17. |
| 8 | **Predict** | Home · Single (form) · Batch (file) · What-if / Scenario · Forecast (TS) · Monitoring · API | §22. |
| 9 | **Experiments** | Home · Runs table · Compare runs · Registry · Lineage · Artifacts | MLflow-backed; promote alias; diff params. |
| 10 | **Reports** | Home · Builder · Templates · History | Drag panels into a report; export PDF/HTML/DOCX/XLSX/PPTX; scheduled. |
| 11 | **Learn (Logic Atlas)** | Algorithms · Metrics · Plots · Tests · Encodings · CV · Glossary | Every ExplainCard browsable/searchable; formula sheet. |
| 12 | **Admin** | Users & Roles · Workspaces · Quotas · Workers & Queues · VLM settings · Audit log · System health | Flower/Grafana embeds; model approval queue. |

### 5.3 Frontend component inventory

`LabPanel`, `ExplainCard` (port of blackcarbon, KaTeX), `PlotlyFigure` (lazy, theme-aware, PNG/SVG/CSV export, sync with artefact ID), `FinancialChart` (lightweight-charts wrapper with forecast fan + markers), `DataGrid` (TanStack virtualised), `MetricTable` (blackcarbon `metrics-table` with best-per-column highlight, ± std, sort), `ParamForm` (JSON-Schema → react-hook-form; sliders/log sliders/enums/booleans/arrays/conditional fields; "search space" editor per param: fixed | list | range(lin/log, step) | distribution), `CVVisualiser` (fold × time bar chart showing train/test/purge/embargo), `AlgoPicker`, `RecipeBuilder` (dnd-kit), `JobMonitor` (SSE), `Leaderboard`, `InsightPanel` (streaming markdown + citation chips that scroll to the panel), `HorizonGuard` (slider with hard/soft caps and reasons), `SeedChip`, `DatasetChip`, `StatusPill`, `ModuleTile`.

---

## 6. Backend services and API

### 6.1 Services

| Service | Tech | Responsibility |
|---|---|---|
| `web` | Next.js 16 | UI, session (Supabase Auth via `@supabase/ssr`), RBAC checks, BFF proxy for short calls, upload pre-signing. SSE streams connect to `lab-api` directly (§39.4). |
| `lab-core` | FastAPI | REST API, validation, catalog, enqueue jobs, read results. Stateless; horizontally scalable. |
| `worker-cpu` | Celery | ingest, EDA, sklearn/GBM training, CV folds, explain, unsupervised, stats TS. |
| `worker-gpu` | Celery (CUDA image) | PyTorch tabular DL, neuralforecast, large UMAP (cuML optional). |
| `worker-llm` | Celery | AI Insights: build grounded context, call VLM, validate JSON, store. |
| `worker-report` | Celery | PNG renders (kaleido), PDF/DOCX/PPTX/XLSX reports. |
| `ai` (external) | NVIDIA API catalog (+ optional fallback providers) | OpenAI-compatible `/v1/chat/completions` with images, called only from Render workers/API (§40). |
| `mlflow` | MLflow 3 server | tracking + registry. |
| `postgres`, `redis`, `minio` | infra | state, queue/cache, objects. |

### 6.2 REST API (prefix `/api/v1`; all JSON; long ops return `202 {job_id}`)

| Area | Method & path | Purpose |
|---|---|---|
| Auth | `POST /auth/login`, `/auth/otp/verify`, `/auth/logout`, `GET /auth/me` | SP Workstation pattern. |
| Catalog | `GET /catalog/{algorithms,encoders,imputers,scalers,transforms,cv,metrics,plots,tests,explainers,datasets}` ; `GET /catalog/algorithms/{key}` | Registry incl. JSON-Schema param specs, default search spaces, ExplainCard content keys. |
| Datasets | `POST /datasets/upload-url` (presigned) → `POST /datasets` (register) ; `GET /datasets` ; `GET /datasets/{id}` ; `GET /datasets/{id}/versions` ; `GET /datasets/{id}/preview?offset&limit&sort&filter` ; `PATCH /datasets/{id}/schema` ; `POST /datasets/{id}/derive` (filter/join/new column) ; `POST /datasets/samples/{key}/load` ; `DELETE /datasets/{id}` | |
| EDA | `POST /eda/{dataset_version_id}/run {sections, sample_rows, target?, time_col?}` ; `GET /eda/{run_id}` ; `GET /eda/{run_id}/artefacts/{artefact_id}` | |
| Experiments | `POST /experiments {dataset_version_id, family, task_spec}` ; `GET/PATCH /experiments/{id}` ; `POST /experiments/{id}/detect-task` | Task detection preview. |
| Recipes | `POST /experiments/{id}/recipes` ; `POST /recipes/{id}/suggest` ; `POST /recipes/{id}/preview` ; `POST /recipes/{id}/leakage-audit` | |
| Runs | `POST /experiments/{id}/runs {algorithms:[{key, mode: defaults\|custom, params, search_space}], cv, tuning, budget, seed}` ; `GET /runs/{id}` ; `GET /runs/{id}/events` (SSE) ; `POST /runs/{id}/cancel` ; `GET /runs/{id}/leaderboard` ; `GET /runs/{id}/models/{model_id}` ; `GET /models/{model_id}/artefacts/{artefact_id}` ; `GET /models/{model_id}/cv-folds` ; `POST /runs/{id}/ensemble {type: stacking\|voting\|blending\|greedy}` | |
| Compare | `POST /compare {model_ids, test: corrected_t\|wilcoxon\|friedman_nemenyi\|mcnemar\|diebold_mariano}` | |
| Unsupervised | `POST /experiments/{id}/dr-runs` ; `POST /experiments/{id}/cluster-runs` ; `POST /experiments/{id}/anomaly-runs` ; `POST /cluster-runs/{id}/assign-labels` | |
| Time series | `POST /ts/{exp}/analyze` ; `POST /ts/{exp}/horizon-check {h}` ; `POST /ts/{exp}/runs` ; `GET /ts/runs/{id}/backtest` ; `POST /ts/models/{id}/forecast {h, level:[80,95], exog_future}` | |
| Explain | `POST /explain/{model_id} {methods, rows?, features?, background_size}` ; `GET /explain/jobs/{id}` | |
| Predict (§45.7) | `GET /models/{id}/schema` ; `GET /models/{id}/template?format=csv\|xlsx` ; `GET /models/{id}/sample-row` ; `POST /predict/single` ; `POST /predict/batch` ; `GET /predict/jobs/{id}` (+ `/events` SSE, `/results`, `/download`) ; `POST /predict/jobs/{id}/confirm` ; `POST /predict/jobs/{id}/cancel` ; `POST /predict/explain` ; `POST /predict/{model_id}/what-if` | Prediction Studio. Old `POST /predict/{model_id}` and `/batch` stay as aliases for one release. |
| Insights | `POST /insights {scope: stage\|artefact\|model\|leaderboard, ids, depth}` → job ; `GET /insights/{id}` ; `GET /insights/{id}/stream` (SSE tokens) ; `POST /insights/{id}/feedback` ; `POST /insights/chat {context_ids, question}` | |
| Registry | `POST /models/{id}/register` ; `POST /registry/{name}/aliases {alias, version}` ; `GET /registry` | |
| Export | `GET /models/{id}/export?format=joblib\|onnx\|mlflow\|python_script\|docker` | |
| Reports | `POST /reports {template, artefact_ids, format}` ; `GET /reports/{id}` | |
| Jobs | `GET /jobs?status` ; `GET /jobs/{id}` ; `GET /jobs/{id}/events` (SSE) ; `POST /jobs/{id}/cancel` (calls `request_job_cancel()`) | All create endpoints accept an `Idempotency-Key` header (§46.2 OPS-04). |
| Walk-forward | `POST /wfo/plan` ; `POST /wfo/runs` ; `GET /wfo/runs/{id}` (+ `/windows`, `/stitched`, `/params`, `/montecarlo`, `/costs`, `/pbo`, `/cpcv-compare`, `/events`) ; `POST /wfo/compare` ; `POST /wfo/runs/{id}/promote` | Full list in §32.12. |
| Intake | `POST /datasets/{id}/versions` ; `POST /intake/{version_id}/run` ; `GET /intake/{version_id}` ; `PATCH /intake/{proposal_id}` ; `POST /intake/{proposal_id}/confirm` ; `GET /datasets/{id}/versions/{v}/diff` ; `GET /datasets/{id}/lineage` ; `GET /datasets/{id}/impact` | Full list in §33.12. |
| Admin | `GET/POST /admin/users`, `/admin/quotas`, `/admin/workers`, `/admin/audit`, `/admin/vlm` | |

**Artefact envelope** (every plot/table returned by the API):

```json
{
  "artefact_id": "SUP.R42.LGBM.CALIBRATION",
  "kind": "plot|table|metric_set|test_result",
  "title": "Reliability diagram (calibration)",
  "explain_key": "plot.calibration_curve",
  "plotly": { "data": [...], "layout": {...} },
  "png_uri": "s3://lab/artefacts/.../calibration.png",
  "table": { "columns": [...], "rows": [...] },
  "numbers": { "ece": 0.031, "brier": 0.118, "bins": 10 },
  "provenance": { "run_id": "...", "model_id": "...", "fold": "oof", "seed": 42, "data_hash": "sha256:..." }
}
```

---

## 7. Data model (PostgreSQL 17)

> v2.2 naming note: the kit migrations (`supabase/migrations/`) are authoritative for names. `orgs` below is `public.organisations`; with Supabase Auth (primary, §39.5) `users` is `auth.users` plus `workspace_members` (role per workspace), so the `users.password_hash` column below applies only to the fallback BFF auth. The WFO tables (§32.13) and the intake detail tables (§33.13) are created by the phases that own them (5A, 1A).

> Additional tables: `model_signatures`, `prediction_jobs`, `prediction_results` (§45.10, migration `20261115000000_prediction_studio.sql`; worker-only writes per `20261115000100_hardening.sql`), `wfo_runs`, `wfo_windows`, `wfo_trials`, `wfo_series`, `wfo_mc_results` (§32.13) and `intake_proposals`, `column_roles`, `schema_diffs`, `intake_feedback` + `dataset_versions` lineage columns (§33.13).

```sql
-- tenancy & auth
CREATE TABLE orgs (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), name text NOT NULL, created_at timestamptz DEFAULT now());
CREATE TABLE users (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), org_id uuid REFERENCES orgs, email citext UNIQUE NOT NULL,
  name text, password_hash text, role text CHECK (role IN ('owner','admin','scientist','analyst','viewer')) DEFAULT 'analyst',
  created_at timestamptz DEFAULT now(), last_login_at timestamptz);
CREATE TABLE workspaces (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), org_id uuid REFERENCES orgs, name text, created_by uuid REFERENCES users);
CREATE TABLE workspace_members (workspace_id uuid REFERENCES workspaces, user_id uuid REFERENCES users, role text, PRIMARY KEY (workspace_id, user_id));

-- data
CREATE TABLE datasets (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), workspace_id uuid REFERENCES workspaces, name text, description text,
  source text CHECK (source IN ('upload','sample','derived','connector')), sample_key text, created_by uuid REFERENCES users, created_at timestamptz DEFAULT now());
CREATE TABLE dataset_versions (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), dataset_id uuid REFERENCES datasets, version int,
  storage_uri text, format text DEFAULT 'parquet', n_rows bigint, n_cols int, bytes bigint, content_hash text, parent_version_id uuid,
  transform_spec jsonb, created_at timestamptz DEFAULT now(), UNIQUE (dataset_id, version));
CREATE TABLE dataset_columns (dataset_version_id uuid REFERENCES dataset_versions, name text, ordinal int, physical_type text,
  semantic_type text, role text, ordinal_order jsonb, unit text, stats jsonb, PRIMARY KEY (dataset_version_id, name));

-- experiments
CREATE TABLE experiments (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), workspace_id uuid REFERENCES workspaces, dataset_version_id uuid REFERENCES dataset_versions,
  name text, family text CHECK (family IN ('supervised','unsupervised','timeseries')),
  task_spec jsonb,      -- {task: regression|binary|multiclass|multilabel|multioutput|clustering|dr|anomaly|forecast, targets, features, sequential, time_col, group_col, horizon, freq, season_lengths, exog}
  seed int DEFAULT 42, mlflow_experiment_id text, created_by uuid REFERENCES users, created_at timestamptz DEFAULT now(), archived bool DEFAULT false);
CREATE TABLE recipes (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), experiment_id uuid REFERENCES experiments, name text, steps jsonb, version int, created_at timestamptz DEFAULT now());

-- jobs & runs
CREATE TABLE jobs (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), workspace_id uuid, kind text, queue text, status text
  CHECK (status IN ('queued','running','succeeded','failed','cancelled')), progress real DEFAULT 0, params jsonb, cache_key text,
  error text, celery_task_id text, created_by uuid, created_at timestamptz DEFAULT now(), started_at timestamptz, finished_at timestamptz);
CREATE INDEX ON jobs (status, queue); CREATE INDEX ON jobs (cache_key);
CREATE TABLE runs (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), experiment_id uuid REFERENCES experiments, recipe_id uuid REFERENCES recipes,
  job_id uuid REFERENCES jobs, kind text, cv_spec jsonb, tuning_spec jsonb, budget jsonb, seed int, env jsonb, mlflow_run_id text, status text, created_at timestamptz DEFAULT now());
CREATE TABLE models (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), run_id uuid REFERENCES runs, algorithm_key text, library text,
  params jsonb, best_params jsonb, search_space jsonb, mode text CHECK (mode IN ('defaults','custom')), fit_seconds real, predict_ms_per_1k real,
  artefact_uri text, onnx_uri text, size_bytes bigint, status text, rank int, is_ensemble bool DEFAULT false, members uuid[], created_at timestamptz DEFAULT now());
CREATE TABLE model_metrics (model_id uuid REFERENCES models, split text CHECK (split IN ('train','cv_mean','cv_std','oof','test','backtest')),
  metric text, value double precision, PRIMARY KEY (model_id, split, metric));
CREATE TABLE cv_folds (model_id uuid REFERENCES models, fold int, repeat int DEFAULT 0, path int, train_idx_uri text, test_idx_uri text,
  n_train int, n_test int, n_purged int, n_embargoed int, metrics jsonb, PRIMARY KEY (model_id, repeat, fold, path));
CREATE TABLE tuning_trials (model_id uuid REFERENCES models, trial int, params jsonb, score double precision, state text, duration_s real, PRIMARY KEY (model_id, trial));

-- artefacts (plots/tables) and insights
CREATE TABLE artefacts (id text PRIMARY KEY, experiment_id uuid REFERENCES experiments, run_id uuid, model_id uuid, kind text,
  explain_key text, plotly_uri text, png_uri text, table_uri text, numbers jsonb, content_hash text, created_at timestamptz DEFAULT now());
CREATE TABLE insights (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), scope text, scope_ids text[], stage text, model_name text, prompt_version text,
  input_hash text, output jsonb, status text, tokens_in int, tokens_out int, latency_ms int, validator_report jsonb, created_by uuid, created_at timestamptz DEFAULT now());
CREATE UNIQUE INDEX ON insights (input_hash, model_name, prompt_version);
CREATE TABLE insight_feedback (insight_id uuid REFERENCES insights, user_id uuid, rating smallint, comment text, created_at timestamptz DEFAULT now());

-- registry mirror, predictions, reports, audit
CREATE TABLE registered_models (name text, version int, model_id uuid REFERENCES models, aliases text[], stage_note text, approved_by uuid, created_at timestamptz DEFAULT now(), PRIMARY KEY (name, version));
CREATE TABLE predictions (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), model_id uuid REFERENCES models, user_id uuid, mode text, input_uri text, output_uri text, n_rows int, created_at timestamptz DEFAULT now());
CREATE TABLE reports (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), experiment_id uuid, template text, artefact_ids text[], format text, uri text, created_by uuid, created_at timestamptz DEFAULT now());
CREATE TABLE audit_log (id bigserial PRIMARY KEY, ts timestamptz DEFAULT now(), user_id uuid, action text, target text, detail jsonb, ip inet);
```

Object storage layout: `s3://lab/{org}/{workspace}/datasets/{dataset}/{version}/data.parquet` · `.../experiments/{exp}/runs/{run}/models/{model}/{model.joblib|model.onnx}` · `.../artefacts/{artefact_id}.{json,png,parquet}` · `.../reports/{id}.pdf`.

---

## 8. Job orchestration, progress, caching, scaling

* **Celery queues:** `q.ingest`, `q.eda`, `q.train.cpu`, `q.train.gpu`, `q.tune`, `q.explain`, `q.forecast`, `q.insights`, `q.report`, `q.predict.batch` (light worker), `q.predict.heavy` (train worker: TS, unsupervised and DL predictions, §45). Routing by algorithm registry flag `resources: {gpu: bool, mem_gb, threads}`.
* **Run DAG:** `prepare_split` → `group(fit_fold(algo, fold) for algo for fold)` → `chord(aggregate_cv)` → `refit_best` → `group(make_plots, compute_explain_light)` → `rank` → `insights(stage=modelling)`. Tuning: one Optuna study per algorithm (RDB storage in Postgres) with parallel workers; MedianPruner/Hyperband on fold-wise intermediate scores.
* **Progress:** workers publish `{"run_id","step","algo","fold","pct","partial_score","eta_s","log"}` on Redis pub/sub channel `run:{id}`; `lab-api` streams it to the browser via **SSE** (direct connection, CORS allow-list; not through Vercel functions); UI `live-sync-pill` shows status.
* **Caching:** `cache_key = sha256(data_hash, recipe_hash, algo_key, params, cv_spec, seed, lib_versions)`; finished results are reused. EDA artefacts cached per dataset version + sample size.
* **Budgets & limits:** per-run wall-clock budget, max trials, max models; per-user concurrency quota; soft time limit → graceful stop with best-so-far; hard memory limit per worker (cgroups).
* **Large data:** profiling via DuckDB/Polars on full data; heavy plots on stratified samples (default 50 000 rows, configurable; sample size shown on panel); t-SNE/UMAP/GP/SVM/KNN/LOO auto-guarded (warn above thresholds, e.g. SVR > 50k rows, GP > 5k, t-SNE > 100k → openTSNE/FIt-SNE or sample).
* **Scaling (primary, §39):** Render workers split into `lab-worker-light` and `lab-worker-train`, sized by plan (2c-4g / 4c-16g–8c-32g), Celery time limits per queue, GPU queue served by an external GPU worker. **Optional later scale-out:** Kubernetes; HPA on `lab-core`; KEDA ScaledObjects on Redis list length per queue; GPU node pool for `worker-gpu`; spot nodes for `q.tune`. Single-box mode: Docker Compose with one CPU worker (concurrency = cores-1), optional GPU worker; AI stays on the hosted provider (§40).
* **Reliability:** idempotent tasks, `acks_late`, retries with backoff for transient errors, dead-letter queue, cancellation via `request_job_cancel()` + revoke + cooperative checks between folds; heartbeats, time limits and memory limits per queue are specified in §46.2 (OPS-02…OPS-05).

---

## 9. Ingestion, schema inference and task detection

> The AI-assisted **Dataset Intake / Auto-Setup** that builds on these rules (index/frequency detection, family inference with confidence, column roles, leakage suspects, editable confirmation, schema drift on updates) is specified in full in **§33**.

**Ingestion:** CSV/TSV via Polars with sniffing (delimiter, quote, encoding via charset-normalizer, decimal comma, thousands sep); Excel via `openpyxl`/`calamine` (sheet + header row picker, merged-cell warning); Parquet/Feather/JSONL native. Normalise column names (keep original as label), dedupe names, parse datetimes (multiple formats, timezone → configurable, default Asia/Kolkata for Indian market data), convert to Parquet, compute content hash.

**Semantic type inference (per column):**

| Rule | Type |
|---|---|
| all unique, monotone integer or UUID/hash pattern, name like `id`, `_id`, `code` | ID (ignored by default) |
| parses as datetime ≥ 95% | datetime (expands to year/month/dow/hour/is_month_end... features on request; candidate time index) |
| bool-like ({0,1}, {yes,no}, {true,false}, {Y,N}) | boolean |
| numeric with n_unique ≤ min(20, 5% n) and integer-valued | numeric-discrete (flag "could be categorical") |
| object with n_unique ≤ 50 or ≤ 5% of n | categorical (nominal); ordinal if user supplies order or values match known ordinal vocab (low/med/high, S/M/L, grades) |
| object with high cardinality, short tokens | high-cardinality categorical (suggest target/CatBoost/hashing/frequency encoding) |
| object with mean length > 30 chars and many spaces | text (excluded; optional length/word-count features) |
| numeric otherwise | continuous |

**Supervised task auto-detection (target y):**

| Condition | Task |
|---|---|
| y non-numeric (string/category/bool) with 2 classes | binary classification |
| y non-numeric with 3 … 200 classes | multiclass (warn if any class < 10 rows, offer merge "rare classes → other") |
| y numeric, integer-valued, n_unique == 2 | binary |
| y numeric, integer-valued, 3 ≤ n_unique ≤ min(20, 0.05 n) | multiclass **suggested**, with banner "could be ordinal/count regression" (offer Poisson/Tweedie regression or ordinal) |
| y numeric float or many unique values | regression (check: non-negative counts → suggest Poisson; heavy right skew → log/Box-Cox target transform; bounded [0,1] → Beta/logit transform) |
| multiple targets all numeric | multi-output regression |
| multiple binary targets | multi-label classification |
| y is datetime / text | rejected with explanation |

Imbalance flag: minority share < 20% (warning) / < 5% (strong; default metric switches to PR-AUC / balanced accuracy; resampling suggested).

**Sequential vs non-sequential:** user selects (required). The lab helps: if a datetime column exists and is monotone, or ADF/Ljung-Box on y shows strong autocorrelation (Ljung-Box p < 0.01 at lag 10), it suggests "Sequential". Sequential mode enforces: no shuffling, time-aware CV (§13), fitted transforms inside folds, lag/rolling features computed with strict `shift(≥1)`, target-encoding only with time-ordered out-of-fold scheme, and an embargo equal to the label horizon.

---

## 10. EDA module catalogue

Every item is an artefact (Plotly + PNG + numbers) with an ExplainCard and an AI-insight hook. "S" = shown when sequential/time index present; "T" = shown when a target is set.

### 10.1 Tables

| ID | Table | Contents | Library |
|---|---|---|---|
| EDA.T.OVERVIEW | Dataset overview | rows, cols, memory, duplicates (rows / keys), constant & quasi-constant cols, type counts, missing %, data-quality score (0–100) | pandas / polars |
| EDA.T.SCHEMA | Column dictionary | name, physical type, semantic type, role, n_unique, % unique, % missing, example values, warnings | pandas / polars (dtype inference) |
| EDA.T.NUMSUMMARY | Numeric summary | count, mean, std, min, p1, p5, Q1, median, Q3, p95, p99, max, IQR, range, CV = σ/μ, MAD, skewness, excess kurtosis, zeros %, negatives %, infinities | pandas describe / scipy.stats |
| EDA.T.CATSUMMARY | Categorical summary | n_unique, mode, mode freq %, entropy H = −Σp log p, normalised entropy, rare-level count (< 1%), top-10 levels | pandas / scipy.stats.entropy |
| EDA.T.NORMALITY | Normality tests | Shapiro-Wilk (n ≤ 5000), D'Agostino-Pearson K², Jarque-Bera, Anderson-Darling, Kolmogorov-Smirnov (vs fitted normal), Lilliefors; statistic, p-value, verdict | scipy.stats |
| EDA.T.DISTFIT | Best-fit distribution | fit normal, lognormal, gamma, Weibull, exponential, beta, Student-t, Pareto, Laplace; AIC/BIC/KS ranking | scipy.stats (fit, AIC) |
| EDA.T.MISSING | Missingness | per-column count/%, pattern counts, Little's MCAR test, missing-vs-target association | pandas / missingno |
| EDA.T.OUTLIERS | Outliers | per column: IQR (1.5/3.0), z-score (\|z\|>3), modified z (MAD, >3.5), Isolation-Forest share, LOF share; multivariate Mahalanobis (χ² p<0.001) | scipy.stats / sklearn.ensemble.IsolationForest / pyod |
| EDA.T.CORR.* | Correlation matrices | Pearson r, Spearman ρ, Kendall τ-b, distance correlation, maximal information-ish via MI; numeric×categorical: correlation ratio η, point-biserial; categorical×categorical: Cramér's V (bias-corrected), Theil's U (asymmetric), χ² p-values; phik (φK) for mixed | pandas / scipy.stats / phik / dcor |
| EDA.T.MI | Mutual information with target | `mutual_info_regression/classif` (k=3 neighbours), normalised; TradingLab `codependence.get_mutual_info`, `variation_of_information_score` | sklearn.feature_selection |
| EDA.T.VIF | Multicollinearity | VIF_j = 1/(1−R²_j), tolerance, condition number κ of standardised X, eigenvalues; flags VIF > 5 / > 10 | statsmodels.stats.outliers_influence |
| EDA.T.TARGET | Target summary (T) | regression: summary + normality + skew transform suggestion; classification: class counts, %, imbalance ratio, majority baseline accuracy | pandas / scipy.stats |
| EDA.T.FEAT_TARGET | Feature–target association (T) | numeric→reg: Pearson/Spearman/MI/F-stat; numeric→clf: ANOVA F, Kruskal-Wallis, point-biserial, AUC of single feature, KS; cat→reg: η², ANOVA; cat→clf: χ², Cramér's V, WoE/IV (binary) | scipy.stats / sklearn.feature_selection |
| EDA.T.WOE_IV | Weight of Evidence / Information Value (T, binary) | per-bin WoE = ln(%good/%bad), IV = Σ(%good−%bad)·WoE; IV bands <0.02 useless, 0.02–0.1 weak, 0.1–0.3 medium, 0.3–0.5 strong, >0.5 suspicious | optbinning |
| EDA.T.STATIONARITY | Stationarity (S) | ADF, KPSS (level & trend), Phillips-Perron, Zivot-Andrews (break), DF-GLS; statistic, lags, p, verdict; suggested d | statsmodels / arch.unitroot |
| EDA.T.AUTOCORR | Autocorrelation (S) | Ljung-Box Q at lags 5/10/20, Box-Pierce, Durbin-Watson, Hurst exponent, ARCH-LM (Engle) | statsmodels / nolds |
| EDA.T.BREAKS | Structural breaks (S) | TradingLab `structural_breaks.get_chow_type_stat`, `get_chu_stinchcombe_white_statistics` (CUSUM), `get_sadf` (SADF bubbles); ruptures PELT change points | TradingLab structural_breaks / ruptures |
| EDA.T.FINSTATS | Financial return stats (S, price-like) | annualised return, vol, Sharpe, Sortino, max DD, skew, kurtosis, VaR/CVaR 95/99 (hist & Cornish-Fisher), TradingLab `util.volatility` (daily vol, Parkinson, Garman-Klass, Yang-Zhang) | TradingLab / scipy.stats |
| EDA.T.DUPES | Duplicates / leakage hints | duplicate rows, near-duplicate rows, features ≈ target (\|r\| > 0.98), ID-like features predictive of target, future-dated columns | pandas / sklearn.neighbors (near-duplicates) |

### 10.2 Plots

| Group | Plots | Library |
|---|---|---|
| Univariate numeric | histogram (Freedman-Diaconis / Sturges / Scott bins, selectable), KDE (Scott/Silverman bandwidth), histogram+KDE+rug, box, violin, strip/jitter, beeswarm, letter-value (boxen), raincloud, ECDF, Q-Q (normal + best-fit dist), P-P, log-scale histogram, transformation preview grid (raw / log1p / sqrt / Box-Cox / Yeo-Johnson / quantile-normal), scaler comparison (raw vs standard/minmax/robust/maxabs/power/quantile — blackcarbon) | numpy.histogram_bin_edges / scipy.stats.gaussian_kde |
| Univariate categorical | bar (counts, %), Pareto chart (cumulative %), treemap, donut (≤ 8 levels), rare-level chart | pandas value_counts |
| Missingness | missing matrix (missingno-style), bar, heatmap of nullity correlation, dendrogram of nullity, missing-by-time (S), UpSet plot of patterns | missingno / pandas |
| Outliers | box with flagged points, scatter of robust z, Mahalanobis distance vs χ² quantile plot, Isolation-Forest score histogram | scipy.stats / sklearn.covariance.MinCovDet |
| Bivariate | scatter (+OLS/LOWESS trend, marginal hist), hexbin/2D-KDE density for large n, joint plot, grouped box/violin by category, mosaic plot, stacked/100% bars, crosstab heatmap, ridgeline by group | statsmodels lowess / scipy.stats |
| Multivariate | correlation heatmaps (clustered, masked upper triangle, each method), correlation network graph (\|r\| > threshold), pairplot/scatter-matrix (≤ 8 vars, hue = target), parallel coordinates, Andrews curves, radar of group means, PCA scree + biplot + 2D/3D projection (blackcarbon), quick UMAP/t-SNE preview, feature-clustering dendrogram (TradingLab `clustering.get_feature_clusters`, ONC), VIF bar chart, 3D scatter | pandas / scipy.cluster.hierarchy / sklearn.decomposition |
| Target analysis (T) | target distribution (+ transform preview), class balance bar, feature-vs-target: per feature scatter/box/violin, binned mean target plot (with CI), WoE bars, MI bar chart, univariate ROC per feature (binary), conditional density by class | pandas / scipy.stats / sklearn.feature_selection |
| Sequential / temporal (S) | line plot with range slider, candlestick + volume (OHLC), rolling mean/std (window selector), seasonal plot (by month/dow/hour), seasonal subseries, lag plot (lags 1…12), ACF, PACF, STL decomposition, periodogram/spectral density, calendar heatmap, return distribution vs normal, volatility clustering (\|r\| and r²), drawdown curve, rolling correlation between two series, missing timestamps / gap chart | pandas / statsmodels → Plotly / lightweight-charts |
| Data quality | quality-score gauge per column, duplicates chart, type-consistency chart | pandas / pandera |

---

## 11. Preprocessing and feature-engineering catalogue

All steps are sklearn-compatible transformers composed in a `Pipeline` + `ColumnTransformer` and **fitted inside each CV training fold only** (leakage-safe). Every step has a param spec and an ExplainCard.

### 11.1 Imputation

| Key | Method | Params (default) | Library |
|---|---|---|---|
| imp.drop_rows / imp.drop_cols | drop rows/cols above missing threshold | `threshold=0.5` | pandas / feature_engine.imputation.DropMissingData |
| imp.mean / median / most_frequent / constant | `SimpleImputer` | `fill_value`, `add_indicator=True` | sklearn.impute.SimpleImputer |
| imp.knn | `KNNImputer` | `n_neighbors=5`, `weights=uniform\|distance` | sklearn.impute.KNNImputer |
| imp.iterative | `IterativeImputer` (MICE) | `estimator=BayesianRidge\|ExtraTrees\|KNN`, `max_iter=10`, `sample_posterior=False`, `random_state=seed` | sklearn.impute.IterativeImputer |
| imp.missforest | IterativeImputer + RandomForest | `n_estimators=100` | sklearn IterativeImputer(estimator=ExtraTreesRegressor) |
| imp.ffill / bfill / interpolate (S) | time-aware | `method=linear\|time\|spline(order)`, `limit` (bfill disabled in sequential mode to prevent look-ahead) | pandas ffill / bfill / interpolate |
| imp.seasonal (S) | STL-based seasonal interpolation | `period` | statsmodels STL + pandas interpolate (thin) |
| imp.indicator | `MissingIndicator` | `features=missing-only` | sklearn.impute.MissingIndicator |

### 11.2 Encodings (categorical)

| Key | Encoder | Library | Notes / params |
|---|---|---|---|
| enc.onehot | One-hot | sklearn `OneHotEncoder` | `drop=None\|first\|if_binary`, `min_frequency=0.01`, `max_categories=30`, `handle_unknown=infrequent_if_exist` |
| enc.dummy | Dummy (k−1) | sklearn (`drop='first'`) | for linear models without regularisation |
| enc.ordinal | Ordinal | sklearn `OrdinalEncoder` | user order, `unknown_value=-1` |
| enc.label | Label (target only) | sklearn `LabelEncoder` | targets only |
| enc.binary | Binary | category_encoders `BinaryEncoder` | log2(k) columns |
| enc.basen | Base-N | `BaseNEncoder` | `base=3` |
| enc.hashing | Feature hashing | `HashingEncoder` / sklearn `FeatureHasher` | `n_components=32` |
| enc.frequency | Count/frequency | `CountEncoder` | `normalize=True` |
| enc.target | Target (mean) encoding w/ smoothing | sklearn `TargetEncoder` (internal cross-fitting) | `smooth='auto'`, `cv=5`, `target_type` |
| enc.mestimate | M-estimate | `MEstimateEncoder` | `m=1.0` |
| enc.loo | Leave-one-out | `LeaveOneOutEncoder` | `sigma=0.05` noise |
| enc.catboost | CatBoost ordered target stats | `CatBoostEncoder` | `a=1` prior; time-ordered in sequential mode |
| enc.james_stein | James-Stein | `JamesSteinEncoder` | `model=independent\|pooled\|beta\|binary` |
| enc.glmm | GLMM | `GLMMEncoder` | |
| enc.woe | Weight of Evidence | `WOEEncoder` | binary target; `regularization=1.0` |
| enc.quantile | Quantile encoder | `QuantileEncoder` | `quantile=0.5`, `m=1` |
| enc.summary | Summary (multi-quantile) | `SummaryEncoder` | `quantiles=[0.25,0.5,0.75]` |
| enc.helmert / sum / backward_diff / polynomial | Contrast codings | category_encoders | for statistical models |
| enc.gray | Gray code | `GrayEncoder` | |
| enc.rankhot | Rank-hot (ordinal thermometer) | `RankHotEncoder` | ordinal data |
| enc.entity_embedding | Learned embeddings | PyTorch (DL models) | `dim=min(50, (k+1)//2)` |
| enc.native | Native categorical handling | LightGBM / CatBoost / XGBoost (`enable_categorical`) / HistGB (`categorical_features`) | no explicit encoding |

Auto-policy (editable): cardinality ≤ 2 → binary 0/1; 3–15 → one-hot (linear/NN/SVM/KNN) or native (GBMs); 16–100 → target encoding (cross-fitted) or CatBoost encoder; > 100 → hashing or frequency + target; ordinal flagged → ordinal; binary target + credit-style data → offer WoE.

### 11.3 Scaling and transforms

Scalers: `StandardScaler`, `MinMaxScaler(feature_range)`, `RobustScaler(quantile_range=(25,75))`, `MaxAbsScaler`, `Normalizer(norm=l1|l2|max)`, `QuantileTransformer(output_distribution=uniform|normal, n_quantiles=1000)`, `PowerTransformer(method=yeo-johnson|box-cox, standardize=True)`, none. Transforms: log, log1p, sqrt, reciprocal, Box-Cox (λ by MLE; positive data only), Yeo-Johnson, arcsinh, logit (proportions), rank/Gaussian-rank, binning (`KBinsDiscretizer`: uniform/quantile/kmeans; optimal binning via `optbinning` for WoE), splines (`SplineTransformer`), polynomial & interaction features (`PolynomialFeatures(degree=2, interaction_only)`), ratio/difference features, cyclical encodings sin/cos for hour/dow/month, date-part extraction. **Target transforms** for regression: `TransformedTargetRegressor` with log1p / Box-Cox / Yeo-Johnson / quantile (predictions back-transformed; smearing correction for log).

### 11.4 Outlier handling

detect: IQR (k=1.5), z (3), modified-z (3.5), percentile caps (1/99), Isolation Forest (contamination=auto), LOF, Elliptic Envelope, DBSCAN noise; act: flag column, winsorise/clip, remove (train folds only), robust scaling, leave. Blackcarbon `apply_outlier_logic` is the reference behaviour.

### 11.5 Feature selection

Filter: variance threshold, correlation filter (|r| > 0.95 drop one), VIF elimination (> 10), univariate `SelectKBest`/`SelectPercentile` (f_regression, f_classif, chi2, mutual_info), mRMR (`feature_engine.selection.MRMR`). Full feature-engine/mlxtend/probatus selector list in §43.8. Wrapper: RFE / `RFECV`, `SequentialFeatureSelector` (forward/backward), Boruta (BorutaPy), Boruta-SHAP. Embedded: L1 (Lasso/LogReg-L1) `SelectFromModel`, tree importance, permutation importance threshold, SHAP-based. Financial: TradingLab clustered MDA/SFI (`feature_importance.mean_decrease_accuracy(..., clustered_subsets=...)`, `single_feature_importance`) with ONC clusters (`clustering.get_feature_clusters`), orthogonal PCA features (`feature_importance.get_orthogonal_features`, `feature_pca_analysis`, `get_pca_rank_weighted_kendall_tau`).

### 11.6 Class imbalance (classification)

`class_weight='balanced'` / custom; resampling (imbalanced-learn, **inside folds via `imblearn.pipeline.Pipeline`**): RandomOverSampler, SMOTE, BorderlineSMOTE (1/2), SVMSMOTE, KMeansSMOTE, ADASYN, SMOTENC (mixed types), SMOTEN (categorical), RandomUnderSampler, NearMiss (1/2/3), TomekLinks, EditedNearestNeighbours, RepeatedENN, AllKNN, CondensedNN, OneSidedSelection, NeighbourhoodCleaningRule, InstanceHardnessThreshold, ClusterCentroids, SMOTETomek, SMOTEENN; ensembles: BalancedRandomForest, BalancedBagging, EasyEnsemble, RUSBoost; threshold moving (optimise F1/Youden J/cost on OOF predictions); focal loss for NN/GBM.

### 11.7 Feature engineering for sequential/financial data (mirrors TradingLab)

| Feature pack | Implementation (TradingLab file → function) | Leakage rule |
|---|---|---|
| Lags & differences | pandas / `feature_engine.timeseries.forecasting.LagFeatures` (`shift(k)`, k ∈ user list, default [1,2,3,5,10,20]) | strictly past |
| Rolling stats | mean, std, min, max, skew, kurt, z-score, quantile over windows [5,10,20,60]; EWMA via `tradinglab/util/fast_ewma.py → ewma` | window ends at t−1 |
| Returns | simple, log, multi-horizon cumulative, excess vs benchmark | label horizon h ⇒ embargo ≥ h |
| Volatility estimators | `tradinglab/util/volatility.py → get_daily_vol, get_parksinson_vol, get_garman_class_vol, get_yang_zhang_vol` | past window |
| Technical indicators | RSI, MACD, Bollinger %b, ATR, Stochastic, ADX, OBV, MFI, CCI, Williams %R, momentum/ROC (implemented with `pandas`/`ta`-style formulas; no future bars) | |
| Fractional differentiation | `tradinglab/features/fractional_differentiation.py → frac_diff_ffd(series, diff_amt, thresh=1e-5)`, `get_weights_ffd`, `plot_min_ffd` (find minimum d that passes ADF while maximising correlation with original) | weights use past only |
| Microstructure (intraday/tick uploads) | `tradinglab/microstructural_features/` → `get_roll_measure`, `get_roll_impact`, `get_corwin_schultz_estimator`, `get_bekker_parkinson_vol`, `get_bar_based_kyle_lambda`, `get_bar_based_amihud_lambda`, `get_bar_based_hasbrouck_lambda`, trade-based lambdas, `get_vpin`, entropy (`get_shannon_entropy`, `get_lempel_ziv_entropy`, `get_plug_in_entropy`, `get_konto_entropy`), `MicrostructuralFeaturesGenerator`, `vwap` | |
| Bars (tick uploads) | `tradinglab/data_structures/` → `get_time_bars`, `get_tick_bars`, `get_volume_bars`, `get_dollar_bars`, `get_ema_*_imbalance_bars`, `get_const_*_imbalance_bars`, `get_ema_*_run_bars`, `get_const_*_run_bars` | |
| Event sampling | `tradinglab/filters/event_filters.py → cusum_filter(raw_time_series, threshold)`, `z_score_filter` | |
| Buy volume classification | `tradinglab/util/volume_classifier.py → get_bvc_buy_volume` | |
| Calendar | day-of-week, month, quarter, month-end, expiry week (NSE monthly/weekly expiry), holiday flags (NSE calendar) | known in advance |
| Cross-asset | returns of related series (e.g. India VIX, Bank Nifty, USD/INR) as exogenous lags | past only |

---

## 12. Supervised learning catalogue

> Evaluation of every supervised model follows **§41 (classification)** and **§42 (regression)**. Algorithms added in the round-3 library audit (R52–R62, C36–C45, Q14–Q18) are in **§43.2–§43.4**; every algorithm's library is in the Library column and in **§44**.

Conventions: **Default** = value used when "Use defaults" is on and tuning is off. **Search space (Balanced)** = default tuning space (Optuna/Random); Quick uses a ⅓-size subset, Thorough widens ranges ×2 and adds params, Exhaustive = full grid where finite. `log(a,b)` = log-uniform; `int(a,b)` = integer uniform; `{…}` = categorical. Every parameter of the underlying estimator is exposed in the "Customise" form (auto-generated from the estimator signature + curated spec); only the key ones are listed here. All stochastic estimators receive `random_state=seed`.

### 12.1 Regression (non-sequential & sequential tabular)

| # | Algorithm (key) | Library | Key hyperparameters: default → Balanced search space |
|---|---|---|---|
| R1 | Linear Regression (OLS) `reg.ols` | sklearn | fit_intercept=True → {T,F}; positive=False |
| R2 | Ridge `reg.ridge` | sklearn | alpha=1 → log(1e-4,1e3); solver auto → {auto,svd,cholesky,lsqr,sag,saga} |
| R3 | Lasso `reg.lasso` | sklearn | alpha=1e-3 → log(1e-5,10); selection {cyclic,random}; max_iter=10000 |
| R4 | ElasticNet `reg.enet` | sklearn | alpha=1e-3 → log(1e-5,10); l1_ratio=0.5 → [0.05,0.95] |
| R5 | Lars / LassoLars `reg.lars` | sklearn | n_nonzero_coefs=500; alpha (LassoLars)=1e-3 → log(1e-5,1) |
| R6 | Orthogonal Matching Pursuit `reg.omp` | sklearn | n_nonzero_coefs=None → int(1,p) |
| R7 | Bayesian Ridge `reg.bayes_ridge` | sklearn | alpha_1,alpha_2,lambda_1,lambda_2=1e-6 → log(1e-8,1e-3) each |
| R8 | ARD Regression `reg.ard` | sklearn | threshold_lambda=1e4 → log(1e2,1e6) |
| R9 | Huber `reg.huber` | sklearn | epsilon=1.35 → [1.1,3]; alpha=1e-4 → log(1e-6,1) |
| R10 | RANSAC `reg.ransac` | sklearn | min_samples=None → [0.1,0.9]; residual_threshold auto; max_trials=100 |
| R11 | Theil-Sen `reg.theilsen` | sklearn | max_subpopulation=1e4 |
| R12 | Quantile Regression `reg.quantile` | sklearn | quantile=0.5 → user list; alpha=0 → log(1e-6,1); solver highs |
| R13 | Poisson / Gamma / Tweedie GLM `reg.glm_*` | sklearn | alpha=1 → log(1e-4,10); power (Tweedie)=1.5 → [1,2]; link auto |
| R14 | SGD Regressor `reg.sgd` | sklearn | loss {squared_error,huber,epsilon_insensitive}; penalty {l2,l1,elasticnet}; alpha log(1e-6,1e-1) |
| R15 | Passive-Aggressive `reg.pa` | sklearn | C=1 → log(1e-3,10) |
| R16 | Polynomial + Ridge `reg.poly_ridge` | sklearn | degree=2 → {2,3}; alpha log(1e-3,1e3) |
| R17 | Spline GAM `reg.gam` | pygam / sklearn SplineTransformer+Ridge | n_splines=10 → int(5,25); lam log(1e-3,1e3) |
| R18 | KNN Regressor `reg.knn` | sklearn | n_neighbors=5 → int(2,50); weights {uniform,distance}; p {1,2}; algorithm {auto,ball_tree,kd_tree,brute}; leaf_size int(10,60) (blackcarbon grid) |
| R19 | Radius Neighbors `reg.radius_nn` | sklearn | radius=1 → log(0.1,10) |
| R20 | SVR `reg.svr` | sklearn | C=1 → log(1e-3,1e3); epsilon=0.1 → log(1e-3,1); kernel {rbf,poly,sigmoid,linear}; gamma {scale,auto}∪log(1e-4,1); degree int(2,5) |
| R21 | Linear SVR `reg.linear_svr` | sklearn | C log(1e-3,1e2); loss {epsilon_insensitive, squared_epsilon_insensitive} |
| R22 | Nu-SVR `reg.nusvr` | sklearn | nu=0.5 → [0.1,0.9]; C log(1e-3,1e3) |
| R23 | Kernel Ridge `reg.kernel_ridge` | sklearn | alpha=1 → log(1e-4,10); kernel {rbf,laplacian,poly,linear}; gamma log(1e-4,1) |
| R24 | Gaussian Process `reg.gp` | sklearn | kernel {RBF, Matern(ν=0.5,1.5,2.5), RationalQuadratic, RBF+White, ExpSineSquared}; alpha=1e-10 → log(1e-10,1e-1); n_restarts_optimizer=3 (guard n ≤ 5 000) |
| R25 | Decision Tree `reg.dt` | sklearn | max_depth=None → int(2,30)∪None; min_samples_split int(2,40); min_samples_leaf int(1,30); criterion {squared_error,friedman_mse,absolute_error,poisson}; ccp_alpha log(1e-6,1e-1) |
| R26 | Extra Tree (single) `reg.extra_tree` | sklearn | as R25 |
| R27 | Random Forest `reg.rf` | sklearn | n_estimators=300 → int(100,1000); max_depth None∪int(3,40); max_features {1.0,sqrt,log2,0.3–0.9}; min_samples_leaf int(1,20); bootstrap {T,F}; max_samples [0.5,1] |
| R28 | Extra Trees `reg.et` | sklearn | as R27 |
| R29 | Bagging `reg.bagging` | sklearn | n_estimators=50 → int(10,300); max_samples [0.3,1]; max_features [0.3,1]; base estimator {DT, KNN, Ridge} |
| R30 | AdaBoost `reg.ada` | sklearn | n_estimators=100 → int(50,800); learning_rate log(1e-3,1); loss {linear,square,exponential} |
| R31 | Gradient Boosting `reg.gbr` | sklearn | n_estimators=300 → int(100,1500); learning_rate log(5e-3,0.3); max_depth int(2,8); subsample [0.5,1]; loss {squared_error,absolute_error,huber,quantile}; min_samples_leaf int(1,50) |
| R32 | Hist Gradient Boosting `reg.hgb` | sklearn | max_iter=300 → int(100,2000); learning_rate log(0.01,0.3); max_leaf_nodes int(15,255); l2_regularization log(1e-6,10); early_stopping=True |
| R33 | XGBoost `reg.xgb` | xgboost | n_estimators=500 → int(200,3000) + early stopping; eta log(5e-3,0.3); max_depth int(2,12); min_child_weight log(1,20); subsample [0.5,1]; colsample_bytree [0.4,1]; gamma log(1e-8,5); reg_alpha log(1e-8,10); reg_lambda log(1e-3,10); tree_method hist; device cpu/cuda |
| R34 | LightGBM `reg.lgbm` | lightgbm | n_estimators=500 → int(200,5000) + early stopping; learning_rate log(5e-3,0.3); num_leaves int(15,511); max_depth −1∪int(3,16); min_child_samples int(5,200); subsample [0.5,1] (+subsample_freq=1); colsample_bytree [0.4,1]; reg_alpha log(1e-8,10); reg_lambda log(1e-8,10); boosting {gbdt,dart,goss} |
| R35 | CatBoost `reg.catboost` | catboost | iterations=1000 → int(300,5000) + od; learning_rate log(5e-3,0.3); depth int(4,10); l2_leaf_reg log(1,30); bagging_temperature [0,10]; random_strength log(1e-3,10); border_count {32,64,128,254}; cat_features native |
| R36 | NGBoost `reg.ngboost` | ngboost | n_estimators=500; learning_rate log(1e-3,0.1); Dist {Normal, LogNormal, Laplace, T} — native predictive distribution |
| R37 | Explainable Boosting Machine `reg.ebm` | interpret | max_bins=256; interactions=10 → int(0,30); learning_rate log(1e-3,0.1) |
| R38 | RuleFit `reg.rulefit` | imodels | max_rules=30; tree_size=4 |
| R39 | Stacking `reg.stack` | sklearn | base = top-k (k=5) tuned models; final_estimator {RidgeCV, LGBM, ElasticNetCV}; passthrough {F,T}; cv = same CV |
| R40 | Voting `reg.vote` | sklearn | estimators = top-k; weights ∝ CV score or uniform |
| R41 | Blending / Greedy ensemble selection (Caruana) `reg.greedy_ens` | sklearn `StackingRegressor` / `VotingRegressor`; greedy Caruana selection = optional thin wrapper over OOF predictions (AutoGluon-style weighted ensemble available in the optional AutoML image) | n_iter=50, with replacement |
| R42 | Sequentially bootstrapped bagging (S) `reg.sb_bagging` | **TradingLab** `ensemble/sb_bagging.py → SequentiallyBootstrappedBaggingRegressor` | n_estimators=100; base DT; uses `samples_info_sets` + `price_bars` |
| R43 | MLP (sklearn) `reg.mlp_sk` | sklearn | hidden_layer_sizes=(128,64) → {(64,),(128,),(128,64),(256,128),(256,128,64)}; activation {relu,tanh}; alpha log(1e-6,1e-1); learning_rate_init log(1e-4,1e-2); early_stopping=True |
| R44 | MLP (PyTorch) `reg.mlp_torch` | PyTorch Lightning | layers int(1,5); width {64,128,256,512}; dropout [0,0.5]; batchnorm {T,F}; activation {ReLU,GELU,SiLU}; lr log(1e-4,3e-3); weight_decay log(1e-6,1e-2); batch {64,128,256,512}; epochs=200 + early stopping(patience 20); optimizer {AdamW, Adam, SGD+momentum}; scheduler {cosine, onecycle, plateau} |
| R45 | ResNet-MLP (tabular) `reg.resnet` | **optional, off by default** — no maintained library (rtdl last released 2022; pytorch-widedeep needs numpy < 2) (§43.4) | blocks int(1,8); d int(64,512); dropout [0,0.5] |
| R46 | TabNet `reg.tabnet` | pytorch-tabular `TabNetModelConfig` (replaces pytorch-tabnet, last released 2023) | n_d=n_a=16 → {8,16,32,64}; n_steps=3 → int(3,10); gamma=1.3 → [1,2]; lambda_sparse log(1e-6,1e-2); mask {sparsemax, entmax} |
| R47 | FT-Transformer `reg.ftt` | pytorch-tabular | d_token=192 → {64,128,192,256}; n_blocks=3 → int(1,6); attention_dropout [0,0.5]; ffn_dropout [0,0.5]; lr log(1e-5,1e-3) |
| R48 | TabTransformer `reg.tabtransformer` | pytorch-tabular | as R47 for categorical tokens |
| R49 | NODE `reg.node` | pytorch-tabular | num_layers=1–4; num_trees {256,512,1024}; depth int(4,8) |
| R50 | GANDALF / GATE / AutoInt / DANet | pytorch-tabular | curated per model |
| R51 | TabPFN (foundation, ≤10k rows, ≤500 features) `reg.tabpfn` | tabpfn | n_estimators=8 → {4,8,16}; no training; GPU recommended (licence check before commercial use) |

### 12.2 Classification (binary / multiclass / multilabel)

| # | Algorithm (key) | Library | Key hyperparameters: default → Balanced search space |
|---|---|---|---|
| C1 | Logistic Regression `clf.logreg` | sklearn | C=1 → log(1e-4,1e3); penalty {l2,l1,elasticnet,None}; solver {lbfgs,saga,liblinear}; l1_ratio [0,1]; class_weight {None,balanced}; multi: multinomial |
| C2 | Ridge Classifier `clf.ridge` | sklearn | alpha log(1e-4,1e3) |
| C3 | SGD Classifier `clf.sgd` | sklearn | loss {hinge,log_loss,modified_huber}; penalty; alpha log(1e-6,1e-1) |
| C4 | Perceptron / Passive-Aggressive `clf.pa` | sklearn | C log(1e-3,10) |
| C5 | LDA `clf.lda` | sklearn | solver {svd,lsqr,eigen}; shrinkage {None,auto}∪[0,1] |
| C6 | QDA `clf.qda` | sklearn | reg_param=0 → [0,1] |
| C7 | Gaussian NB `clf.gnb` | sklearn | var_smoothing=1e-9 → log(1e-12,1e-2) |
| C8 | Multinomial / Complement / Bernoulli / Categorical NB `clf.*nb` | sklearn | alpha=1 → log(1e-3,10); binarize (Bernoulli) |
| C9 | KNN `clf.knn` | sklearn | as R18 |
| C10 | Nearest Centroid / Radius NN | sklearn | shrink_threshold [0,2] |
| C11 | SVC `clf.svc` | sklearn | C log(1e-3,1e3); kernel {rbf,poly,sigmoid,linear}; gamma; degree; probability=True (Platt) or CalibratedClassifierCV; class_weight |
| C12 | Linear SVC / Nu-SVC | sklearn | C; loss {hinge,squared_hinge}; nu [0.05,0.9] |
| C13 | Gaussian Process Classifier `clf.gp` | sklearn | kernel as R24; guard n ≤ 3 000 |
| C14 | Decision Tree `clf.dt` | sklearn | criterion {gini,entropy,log_loss}; others as R25 |
| C15 | Random Forest `clf.rf` | sklearn | as R27 + criterion; class_weight {None,balanced,balanced_subsample} |
| C16 | Extra Trees `clf.et` | sklearn | as C15 |
| C17 | Bagging `clf.bagging` | sklearn | as R29 |
| C18 | AdaBoost `clf.ada` | sklearn | n_estimators int(50,800); learning_rate log(1e-3,1) (SAMME) |
| C19 | Gradient Boosting `clf.gbc` | sklearn | as R31 (loss log_loss/exponential) |
| C20 | Hist Gradient Boosting `clf.hgb` | sklearn | as R32 + class_weight |
| C21 | XGBoost `clf.xgb` | xgboost | as R33 + scale_pos_weight {1, n_neg/n_pos}; objective binary:logistic / multi:softprob |
| C22 | LightGBM `clf.lgbm` | lightgbm | as R34 + is_unbalance / class_weight |
| C23 | CatBoost `clf.catboost` | catboost | as R35 + auto_class_weights {None,Balanced,SqrtBalanced} |
| C24 | NGBoost Classifier `clf.ngboost` | ngboost | Dist {Bernoulli, k_categorical} |
| C25 | EBM `clf.ebm` | interpret | as R37 |
| C26 | Balanced RF / EasyEnsemble / RUSBoost / BalancedBagging | imbalanced-learn | n_estimators; sampling_strategy {auto, 0.5–1.0} |
| C27 | Stacking `clf.stack` | sklearn | final_estimator {LogisticRegression, LGBM}; stack_method {predict_proba,decision_function}; passthrough |
| C28 | Voting `clf.vote` | sklearn | voting {soft,hard}; weights |
| C29 | Greedy ensemble selection `clf.greedy_ens` | sklearn `StackingClassifier` / `VotingClassifier`; greedy selection = optional thin wrapper over OOF probabilities | optimise log-loss on OOF |
| C30 | One-vs-Rest / One-vs-One / Output-Code wrappers | sklearn | wraps any binary estimator for multiclass; `ClassifierChain` / `MultiOutputClassifier` for multilabel |
| C31 | Sequentially bootstrapped bagging (S) `clf.sb_bagging` | **TradingLab** `SequentiallyBootstrappedBaggingClassifier` | n_estimators=100; max_samples=1.0; base DT(criterion=entropy, class_weight=balanced) |
| C32 | Calibrated wrapper `clf.calibrated` | sklearn `CalibratedClassifierCV` | method {sigmoid, isotonic, temperature (sklearn ≥1.8)}; cv=5 |
| C33 | MLP (sklearn / PyTorch) | sklearn / Lightning | as R43/R44 with BCE / CE / focal loss (γ=2) and label smoothing [0,0.2] |
| C34 | ResNet, TabNet, FT-Transformer, TabTransformer, NODE, GANDALF, AutoInt, DANet | pytorch-tabular (ResNet optional, see §43.4) | as R45–R50 |
| C35 | TabPFN Classifier | tabpfn | as R51 (≤10 classes for v2) |

### 12.3 Sequential supervised models (time-ordered tabular, mostly financial)

Input: windows of length L (lookback) over features (lags, indicators) → target at t+h (regression of return/price, or class: up/down/flat, triple-barrier label, meta-label).

| # | Model | Library | Key hyperparameters: default → search space |
|---|---|---|---|
| S1 | Any §12.1/§12.2 model on engineered lag/rolling features | sklearn/GBMs | as above; CV forced to time-aware (§13) |
| S2 | Vanilla RNN (Elman) | built-in `torch.nn` layers + `lightning` (§43.3) | lookback L=30 → {10,20,30,60,120}; hidden {32,64,128,256}; layers int(1,3); dropout [0,0.5]; bidirectional=False (no future leak); lr log(1e-4,3e-3); batch {32,64,128}; grad_clip 1.0 |
| S3 | LSTM | built-in `torch.nn` layers + `lightning` (§43.3) | as S2 (+ stateful {F,T}, layer-norm) |
| S4 | GRU | built-in `torch.nn` layers + `lightning` (§43.3) | as S2 |
| S5 | Stacked/Attention LSTM (Bahdanau/additive attention) | built-in `torch.nn` layers + `lightning` (§43.3) | heads; attention dim {32,64} |
| S6 | 1D-CNN | built-in `torch.nn` layers + `lightning` (§43.3) | filters {32,64,128}; kernel {3,5,7}; layers int(1,4); pooling {max,avg} |
| S7 | TCN (dilated causal conv) | `pytorch-tcn` + `lightning` | levels int(2,8); kernel {2,3,5}; channels {32,64,128}; dropout [0,0.3] |
| S8 | CNN-LSTM hybrid | built-in `torch.nn` layers + `lightning` (§43.3) | conv + LSTM params |
| S9 | Transformer encoder (causal mask, positional enc.) | built-in `torch.nn` layers + `lightning` (§43.3) | d_model {32,64,128}; heads {2,4,8}; layers int(1,4); ff {64,256}; dropout |
| S10 | xLSTM / Mamba-style SSM (optional) | `xlstm` / `mamba-ssm` (optional GPU image) | d_model, blocks |
| S11 | Sequentially bootstrapped bagging | TradingLab (C31/R42) | |

Financial **target builder** (sequential classification/regression), mirroring TradingLab `labeling/`:

| Labeler | TradingLab file → function | Output |
|---|---|---|
| Raw / log return over h | `labeling/raw_return.py → raw_return` | regression or sign |
| Fixed time horizon with threshold τ | `labeling/fixed_time_horizon.py → fixed_time_horizon` | {−1,0,1} |
| **Triple-barrier** | `labeling/triple_barrier_labeling.py → add_vertical_barrier(t_events, close, num_days…)`, `get_events(close, t_events, pt_sl, target, min_ret, num_threads, vertical_barrier_times, side_prediction)`, `get_bins(triple_barrier_events, close)`, `barrier_touched`, `drop_labels(events, min_pct=0.05)` | {−1,0,1} + `t1` (label end time = `samples_info_sets`) |
| **Meta-labeling** | same `get_events(..., side_prediction=primary_side)` → `get_bins` returns {0,1} ("take the bet or not"); secondary model's P(1) sizes the bet via `bet_sizing.bet_size_probability` | {0,1} |
| Trend-scanning | `labeling/trend_scanning.py → trend_scanning_labels` (max \|t-value\| of linear trend over look-forward windows) | sign + t-value (weight) |
| Excess over mean / median | `excess_over_mean`, `excess_over_median` | regression / sign |
| Return vs benchmark | `labeling/return_vs_benchmark.py → return_over_benchmark` | regression / sign |
| Tail sets | `labeling/tail_sets.py → TailSetLabels` | {−1,0,1} by cross-sectional tails |
| Matrix flags | `labeling/matrix_flags.py → MatrixFlagLabels` | template-match labels |
| Event sampling for t_events | `filters/event_filters.py → cusum_filter`, `z_score_filter`; volatility target `util/volatility.get_daily_vol` | |

**Sample weights** (passed as `sample_weight` to fit and scorer): uniqueness from `sampling/concurrent.py → num_concurrent_events, get_av_uniqueness_from_triple_barrier`; indicator-matrix uniqueness `sampling/bootstrapping.py → get_ind_matrix, get_ind_mat_average_uniqueness, get_ind_mat_label_uniqueness`; sequential bootstrap `seq_bootstrap(ind_mat, sample_length, warmup_samples, random_state=RandomState(seed))`; return attribution `sample_weights/attribution.py → get_weights_by_return(triple_barrier_events, close_series)`; time decay `get_weights_by_time_decay(triple_barrier_events, close_series, decay=1)`; class weights. **Bet sizing** from predicted probabilities: `bet_sizing/bet_sizing_core.py → bet_size_probability, bet_size_dynamic, bet_size_budget, bet_size_reserve` (EF3M mixture fit via `bet_sizing/ef3m.py → M2N`).

---

## 13. Cross-validation catalogue

### 13.1 Strategies

| Key | Strategy | Implementation | Default params | When (auto-policy) |
|---|---|---|---|---|
| cv.holdout | Train/validation/test split | sklearn `train_test_split` | 70/15/15, stratify for clf, seed | always reserves a final **untouched test set** (non-seq: random/stratified; seq: last 15–20% in time) |
| cv.kfold | K-Fold | `KFold(shuffle=True)` | k=5 | regression, i.i.d. |
| cv.stratified | Stratified K-Fold | `StratifiedKFold` | k=5 | classification (default) |
| cv.repeated | Repeated (Stratified) K-Fold | `RepeatedKFold` / `RepeatedStratifiedKFold` | k=5, repeats=3 (blackcarbon `cv_repeats`) | small data (< 2 000 rows) default |
| cv.group | Group K-Fold / Stratified Group K-Fold | sklearn | k=5, `groups` col | entities repeated (customers, tickers) |
| cv.lpgo | Leave-P-Groups-Out / Leave-One-Group-Out | sklearn | p=1 | few groups |
| cv.shuffle | ShuffleSplit / StratifiedShuffleSplit / GroupShuffleSplit | sklearn | n_splits=10, test_size=0.2 | large data, quick |
| cv.loo | Leave-One-Out / Leave-P-Out | sklearn | p=1 | n ≤ 200 only (guard) |
| cv.mccv | Monte-Carlo CV | ShuffleSplit with many splits | 50 splits | variance estimation |
| cv.bootstrap | Bootstrap .632 / .632+ | `mlxtend.evaluate.bootstrap_point632_score` | B=200 | tiny data |
| cv.ts_expanding | TimeSeriesSplit (expanding window) | `TimeSeriesSplit` | n_splits=5, `gap`=h, `test_size` | sequential default (non-financial) |
| cv.ts_sliding | Sliding (rolling) window | `TimeSeriesSplit(max_train_size=W)` | W = 3×test | regime drift |
| cv.walk_forward | Walk-forward with refit every r steps | `sktime.split.ExpandingWindowSplitter` / `SlidingWindowSplitter` (thin WFO driver) | initial=50%, step=h, refit every fold | TS & financial backtests — full WFO module in **§32** |
| cv.blocked | Blocked K-Fold (contiguous blocks, no shuffle) with margin | sklearn `KFold(shuffle=False)` + thin gap wrapper | k=5, margin=h | autocorrelated, stationary |
| cv.hv_block | hv-block CV (Racine 2000) | optional thin wrapper over `KFold(shuffle=False)` (no maintained library) | h = v = ACF decay lag | dependent data |
| cv.purged | **Purged K-Fold + embargo** | **TradingLab** `cross_validation/time_series_cv.py → PurgedKFold(n_splits, samples_info_sets, pct_embargo)` + `ml_get_train_times` | k=5, pct_embargo=0.01 | **financial sequential default** |
| cv.purged_split | Purged single train/test split | TradingLab `PurgedSplit` | test_size=0.25 | quick financial holdout |
| cv.cpcv | **Combinatorial Purged CV (CPCV)** with backtest paths | **TradingLab** `cross_validation/combinatorial.py → CombinatorialPurgedKFold(n_splits=N, n_test_splits=k, samples_info_sets, pct_embargo)`; `backtest_paths` | N=6, k=2 → 15 splits, 5 paths | financial model selection, PBO |
| cv.nested | Nested CV (outer for estimate, inner for tuning) | sklearn `cross_validate` over `GridSearchCV`/Optuna search (thin) | outer = chosen strategy (k=5), inner = 3-fold same family | unbiased estimate when tuning |
| cv.ts_nixtla | Rolling-origin backtest | statsforecast/neuralforecast `cross_validation(h, n_windows, step_size)` | n_windows=5, step=h | Time-Series family |

The **CV visualiser** renders a folds × index chart (train = ink, test = gold, purged = hatched red, embargo = amber, gap = grey) for every strategy before a run starts, and reports `n_train, n_test, n_purged, n_embargoed` per fold (stored in `cv_folds`).

### 13.2 Financial validation — mirrored from `ml-for-trading` (TradingLab)

The lab vendors TradingLab as a pinned dependency (`tradinglab` package from `ShibayanBiswas/ml-for-trading`, installed with `pip install -e` or as a git submodule under `vendor/`) and wraps it in `labcore/finance/` adapters so it plugs into sklearn pipelines, Optuna and the CV visualiser. Behaviour must match TradingLab's own tests (`tradinglab/tests/cross_validation/test_cross_validation.py`, `test_combinatorial_cross_validation.py`, `tests/labeling/*`, `tests/backtest_sampling/*`, `tests/features/test_fractional_differentiation.py`), which the lab re-runs as **contract tests**.

1. **Label spans (`samples_info_sets`).** Every sequential sample i carries an information interval [t0_i, t1_i]: index = time the features were observed, value = time the label is resolved. Built from the target builder: triple-barrier `t1` from `get_events` (first barrier touched or vertical barrier from `add_vertical_barrier`), fixed-horizon `t0 + h`, trend-scanning window end. For plain sequential tabular data without a labeler, t1 = t0 + h (h = prediction horizon in rows).
2. **Purging** (`time_series_cv.py → ml_get_train_times(samples_info_sets, test_times)`, AFML snippet 7.1): drop any training sample whose interval (a) starts inside the test window, (b) ends inside it, or (c) envelops it.
3. **Embargo** (`PurgedKFold.split`, AFML 7.2/7.3): after each test fold, also drop training samples in the next `h_e = ceil(pct_embargo · T)` bars (default 1%; UI shows it in bars and calendar days). Embargo extends the test *times*, not the test indices.
4. **Purged K-fold** (`PurgedKFold(n_splits, samples_info_sets, pct_embargo)`): contiguous test folds via `np.array_split`, no shuffling; scoring through `ml_cross_val_score(classifier, X, y, cv_gen, sample_weight_train, sample_weight_score, scoring=log_loss)` (AFML 7.4) — weights split consistently per fold.
5. **CPCV** (`combinatorial.py → CombinatorialPurgedKFold`, AFML ch. 12): split T into N contiguous groups; every combination of k test groups (C(N,k) splits, `_generate_combinatorial_test_ranges`) is a test set; train on the rest after purging + embargo; `_fill_backtest_paths` stitches the out-of-sample predictions into φ backtest paths, so each model gets a *distribution* of path Sharpe ratios / scores instead of one number.
   * Number of paths: φ(N,k) = (k/N)·C(N,k). TradingLab's `_get_number_of_backtest_paths` returns `N − 1`, which equals φ only for k = 2 (its documented convention). **The lab's adapter computes the general formula and asserts equality with TradingLab when k = 2.**
   * Defaults: N=6, k=2 → 15 train/test splits, 5 paths; Thorough: N=10, k=2 → 45 splits, 9 paths. UI guard: C(N,k) ≤ 200.
6. **Probability of Backtest Overfitting (PBO)** — not present in the TradingLab tree (no PBO/CSCV module found), so the lab **adds** it in `labcore/finance/pbo.py` following Bailey, Borwein, López de Prado & Zhu (2017) CSCV: build the T × M matrix of per-period OOS performance for M configurations (all tuning trials / models), split rows into S even blocks (default 16), for each of the C(S, S/2) combinations pick the in-sample best config and compute its OOS relative rank ω̄, logit λ = ln(ω̄/(1−ω̄)); PBO = share of λ ≤ 0. Outputs: PBO, logit histogram, IS-vs-OOS performance scatter (performance degradation slope), probability of loss, stochastic dominance plot. CPCV path scores feed the same module.
7. **Deflated / Probabilistic Sharpe and multiple testing**: `backtest_statistics/strategy_metrics.py → sharpe_ratio, probabilistic_sharpe_ratio, deflated_sharpe_ratio(observed_sr, sr_estimates, number_of_returns, skewness, kurtosis)`, `minimum_track_record_length`, `information_ratio`; haircut Sharpe and profit hurdles via `backtest_statistics/campbell.py → CampbellBacktesting(simulations=2000).haircut_sharpe_ratios(...)` and `.profit_hurdle(num_mult_test, num_obs, alpha_sig, vol_anu, rho)` (Bonferroni / Holm / BHY). The number of trials N fed into DSR = number of Optuna trials × models actually tried (tracked automatically).
8. **Sample uniqueness & weights** inside CV: weights computed **on the full timeline once** (they depend only on label spans, not on y) then sliced per fold; training weights only from train rows (`sample_weight_train`), scoring weights from test rows (`sample_weight_score`) — exactly the TradingLab `ml_cross_val_score` contract.
9. **Fractional differentiation** inside folds: `frac_diff_ffd` is a fixed-width causal filter, so it can be applied before splitting; the d* search (`plot_min_ffd` logic: smallest d with ADF p < 0.05) runs on the **training span only** to avoid look-ahead in d selection.
10. **Strategy backtest from predictions** (Financial Backtest page): positions = sign(pred) or bet size from probabilities (`bet_size_probability`); P&L with costs (bps) and slippage; stats: `drawdown_and_time_under_water`, `average_holding_period`, `timing_of_flattening_and_flips`, `bets_concentration`/`all_bets_concentration` (HHI), Sharpe/PSR/DSR, hit ratio, turnover. Plots: equity curve (lightweight-charts), drawdown/underwater, rolling Sharpe, CPCV path fan (one line per path), PBO logit histogram, IS-vs-OOS scatter, returns distribution.
11. **Feature importance for financial models**: `feature_importance/importance.py → mean_decrease_impurity(model, feature_names, clustered_subsets)`, `mean_decrease_accuracy(model, X, y, cv_gen=PurgedKFold(...), clustered_subsets, sample_weight_train, sample_weight_score, scoring=log_loss, random_state=seed)`, `single_feature_importance`; clustered FI with `clustering/feature_clusters.py → get_feature_clusters` and `clustering/onc.py → get_onc_clusters`; orthogonal features & PCA-rank Kendall τ (`feature_importance/orthogonal.py`); model fingerprints (`fingerprint.py → RegressionModelFingerprint, ClassificationModelFingerprint`: linear / non-linear / pairwise interaction effects).
12. **Dependence matrices** for financial EDA/clustering: `codependence/codependence_matrix.py → get_dependence_matrix(df, dependence_method)`, `get_distance_matrix(X, distance_metric='angular')`; measures `distance_correlation`, `angular_distance`, `absolute_angular_distance`, `squared_angular_distance`, `get_mutual_info`, `variation_of_information_score`, `get_optimal_number_of_bins`, `spearmans_rho`, `gpr_distance`, `gnpr_distance`.
13. **Porting notes found while reading the code** (to fix in the adapter, not by editing TradingLab): `ml_get_train_times` uses `Series.iteritems()` (removed in pandas 2.0 → use `.items()`); `seq_bootstrap(..., random_state=np.random.RandomState())` has a mutable default (always pass `RandomState(seed)`); the CPCV path-count convention above. Several functions take `num_threads` and use `util/multiprocess.py → mp_pandas_obj` — inside Celery workers set `num_threads=1` and parallelise at fold level instead.
14. Also exposed from TradingLab in the lab: `multi_product/etf_trick.py` (ETF trick / futures roll for continuous series), `structural_breaks` tests in TS analysis, microstructure feature packs, event filters, bars. Portfolio optimisation (`portfolio_optimization/`: MVO, CLA, HRP, HERC, NCO, TIC) and online portfolio selection are listed for a later **Portfolio Lab** module (Phase 7).

### 13.3 Statistical comparison of models

Corrected resampled t-test (Nadeau & Bengio), paired Wilcoxon signed-rank on fold scores, 5×2cv F-test, McNemar (classification on test), Friedman + Nemenyi post-hoc with critical-difference diagram (many models), Diebold-Mariano (forecasts), bootstrap CI of the metric difference.

---

## 14. Hyperparameter tuning and the parameter-spec system

### 14.1 Tuning strategies

| Key | Method | Library | Defaults |
|---|---|---|---|
| tune.none | Use defaults | — | — |
| tune.grid | Grid search | `GridSearchCV` | finite grid from spec; guard ≤ 2 000 combos |
| tune.random | Random search | `RandomizedSearchCV` (blackcarbon) | n_iter: Quick 15 / Balanced 40 / Thorough 100 |
| tune.halving | Successive halving | `HalvingGridSearchCV`, `HalvingRandomSearchCV` | factor=3, resource=n_samples or n_estimators |
| tune.bayes_tpe | Bayesian (TPE) | Optuna `TPESampler(multivariate=True, seed)` | **default**; n_trials: Quick 20 / Balanced 60 / Thorough 200; timeout per algo |
| tune.cmaes | CMA-ES | Optuna `CmaEsSampler` | continuous spaces |
| tune.gp | GP-BO | Optuna `GPSampler` | small budgets |
| tune.hyperband | Hyperband / ASHA pruning | Optuna `HyperbandPruner` / `SuccessiveHalvingPruner` | for GBMs/NN (iterations as resource) |
| tune.nsga2 | Multi-objective (score vs latency/size) | Optuna `NSGAIISampler` | Pareto front plot |
| tune.auto_nixtla | Auto models (AutoARIMA, AutoNHITS…) | statsforecast/neuralforecast Auto* (Ray/Optuna) | TS family |

Early stopping for boosting/NN uses an inner validation slice of the training fold only. Objective = selected primary metric on CV mean (optionally mean − λ·std for robustness, λ=0.5 configurable).

### 14.2 Parameter-spec system ("Use defaults" vs "Customise")

Each algorithm is registered once (`labcore/registry/algorithms/*.py`):

```python
AlgorithmSpec(
  key="clf.lgbm", family="supervised", tasks=["binary","multiclass"], library="lightgbm",
  estimator="lightgbm.LGBMClassifier", resources={"gpu": False, "threads": 4},
  supports={"sample_weight": True, "native_categorical": True, "early_stopping": True, "predict_proba": True, "sequential_ok": True},
  params=[
    Param("n_estimators", "int", default=500, low=50, high=10000, log=True, group="Boosting",
          space={"quick": Int(200, 1000), "balanced": Int(200, 5000, log=True), "thorough": Int(100, 10000, log=True)}),
    Param("learning_rate", "float", default=0.05, low=1e-4, high=1.0, log=True, space={"balanced": Float(5e-3, 0.3, log=True)}),
    Param("num_leaves", "int", default=31, low=2, high=4096, space={"balanced": Int(15, 511, log=True)}),
    Param("boosting_type", "enum", default="gbdt", choices=["gbdt","dart","goss","rf"]),
    Param("drop_rate", "float", default=0.1, visible_if={"boosting_type": "dart"}),
    ...  # every constructor argument, auto-introspected; curated ones get groups, help text and spaces
  ],
  explain_key="algo.lightgbm",
)
```

* The registry introspects the estimator signature (`inspect.signature` / `get_params()`) so **every parameter** is customisable even if not curated (shown under "Advanced"), with type inferred from the default.
* `GET /catalog/algorithms/{key}` returns JSON-Schema + UI hints; the frontend `ParamForm` renders it; zod mirrors validation.
* Per algorithm the UI offers: **Use defaults** (default values, preset search space if tuning on) | **Customise** (edit fixed values *and* the search space per param: fixed / choices / range lin-log / distribution) | **Import JSON** | **Reset**. Conditional params (`visible_if`), constraints (e.g. `l1_ratio` only if `penalty=elasticnet`; `box-cox` only for positive data) and warnings (e.g. SVR with n>50k) are declared in the spec.
* Presets mirror blackcarbon `param_grids.py` (`fast/balanced/thorough`) → **Quick / Balanced / Thorough / Exhaustive**; Balanced is default, giving "a good amount of parameters in the CV by default".

---

## 15. Metrics catalogue (with formulas)

> Summary only. The complete, authoritative lists are **§41.4** (classification: 55 metrics with averaging modes and library functions) and **§42.3** (regression: 40 metrics).

Notation: yᵢ true, ŷᵢ prediction, ȳ mean, n samples, p features, p̂ predicted probability, TP/FP/TN/FN counts.

### 15.1 Regression

| Metric | Formula | Library |
|---|---|---|
| MAE | (1/n) Σ \|yᵢ − ŷᵢ\| | sklearn.metrics (exact function per metric in §42.3) |
| MSE | (1/n) Σ (yᵢ − ŷᵢ)² | sklearn.metrics (exact function per metric in §42.3) |
| RMSE | √MSE | sklearn.metrics (exact function per metric in §42.3) |
| RMSLE | √[(1/n) Σ (ln(1+yᵢ) − ln(1+ŷᵢ))²] | sklearn.metrics (exact function per metric in §42.3) |
| MedAE | median \|yᵢ − ŷᵢ\| | sklearn.metrics (exact function per metric in §42.3) |
| Max error | max \|yᵢ − ŷᵢ\| | sklearn.metrics (exact function per metric in §42.3) |
| MAPE | (100/n) Σ \|(yᵢ − ŷᵢ)/yᵢ\| (undefined at yᵢ = 0; masked) | sklearn.metrics (exact function per metric in §42.3) |
| sMAPE | (100/n) Σ 2\|yᵢ − ŷᵢ\| / (\|yᵢ\| + \|ŷᵢ\|) | sklearn.metrics (exact function per metric in §42.3) |
| WAPE | Σ\|yᵢ − ŷᵢ\| / Σ\|yᵢ\| | sklearn.metrics (exact function per metric in §42.3) |
| R² | 1 − Σ(yᵢ − ŷᵢ)² / Σ(yᵢ − ȳ)² | sklearn.metrics (exact function per metric in §42.3) |
| Adjusted R² | 1 − (1 − R²)(n − 1)/(n − p − 1) | sklearn.metrics (exact function per metric in §42.3) |
| Explained variance | 1 − Var(y − ŷ)/Var(y) | sklearn.metrics (exact function per metric in §42.3) |
| Pearson r / Spearman ρ | cov(y,ŷ)/(σ_y σ_ŷ); rank version | sklearn.metrics (exact function per metric in §42.3) |
| Poisson / Gamma / Tweedie deviance | D = 2Σ[y ln(y/ŷ) − (y − ŷ)] (Poisson) etc. | sklearn.metrics (exact function per metric in §42.3) |
| D² (pinball / abs error) | 1 − dev(model)/dev(null) | sklearn.metrics (exact function per metric in §42.3) |
| Pinball loss (quantile τ) | (1/n) Σ max(τ(y−q̂), (τ−1)(y−q̂)) | sklearn.metrics (exact function per metric in §42.3) |
| AIC / BIC (linear/GLM) | 2k − 2 ln L ; k ln n − 2 ln L | sklearn.metrics (exact function per metric in §42.3) |
| Prediction-interval coverage (PICP), mean width (MPIW), Winkler/interval score | PICP = (1/n)Σ 1[y ∈ [l,u]]; IS_α = (u−l) + (2/α)(l−y)1[y<l] + (2/α)(y−u)1[y>u] | sklearn.metrics (exact function per metric in §42.3) |
| CRPS | ∫ (F(z) − 1[z ≥ y])² dz | sklearn.metrics (exact function per metric in §42.3) |

### 15.2 Classification

| Metric | Formula | Library |
|---|---|---|
| Accuracy | (TP + TN)/n | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| Balanced accuracy | ½(TPR + TNR) (macro recall for multiclass) | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| Precision / Recall (TPR) / Specificity (TNR) / NPV / FPR / FNR | TP/(TP+FP); TP/(TP+FN); TN/(TN+FP); TN/(TN+FN); FP/(FP+TN); FN/(FN+TP) | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| F1 / Fβ | (1+β²)·P·R / (β²P + R) | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| Macro / micro / weighted averages | per-class average / pooled counts / support-weighted | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| MCC | (TP·TN − FP·FN)/√((TP+FP)(TP+FN)(TN+FP)(TN+FN)) | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| Cohen's κ | (p_o − p_e)/(1 − p_e) | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| ROC-AUC (OvR/OvO macro for multiclass) | ∫ TPR d(FPR) = P(score⁺ > score⁻) | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| PR-AUC / Average precision | Σ (R_k − R_{k−1}) P_k | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| Log-loss | −(1/n) Σ Σ_c y_{ic} ln p̂_{ic} | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| Brier score | (1/n) Σ (p̂ᵢ − yᵢ)² (multiclass: Σ over classes) | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| ECE / MCE | Σ_b (n_b/n) \|acc(b) − conf(b)\| ; max_b \|acc(b) − conf(b)\| | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| Gini | 2·AUC − 1 | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| KS statistic | max_t \|F₁(t) − F₀(t)\| | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| Lift@k / Gain@k | precision in top k% / base rate; cumulative share of positives captured | scikit-plots |
| Hamming loss, Jaccard, subset accuracy (multilabel) | | sklearn.metrics |
| Top-k accuracy | 1[y ∈ top-k p̂] | sklearn.metrics / imbalanced-learn / netcal (exact function in §41.4) |
| Cost-sensitive expected cost | Σ C_{ij} N_{ij} (user cost matrix) | sklearn.metrics.confusion_matrix + numpy (thin) |
| Youden J / optimal threshold | max_t (TPR − FPR) | sklearn.metrics.roc_curve |

### 15.3 Financial (sequential supervised; TradingLab `strategy_metrics.py`)

Directional accuracy / hit ratio; information coefficient IC = Spearman(ŷ, y_{t+h}), ICIR = mean(IC)/std(IC); Sharpe SR = μ/σ·√A; Sortino; Calmar = CAGR/|MaxDD|; max drawdown & time under water; PSR(SR*) = Φ[(SR̂ − SR*)√(n−1) / √(1 − γ₃SR̂ + (γ₄−1)/4·SR̂²)]; DSR = PSR with SR* = √V[SR_n]·((1−γ)Φ⁻¹(1−1/N) + γΦ⁻¹(1−1/(Ne))); MinTRL; profit factor; turnover; HHI bets concentration; PBO.

### 15.4 Unsupervised and time series

See §18.4 and §19.6.

---

## 16. Supervised plot catalogue

> Summary only. Full plot catalogues with axes and compute libraries: **§41.5** (classification, 45 plots) and **§42.5** (regression, 36 plots).

| Task | Plots (per model; all interactive, exportable, AI-readable) | Library |
|---|---|---|
| Regression | predicted vs actual (y=x line, R² annotation, density for big n), residuals vs fitted, residuals vs each feature, residual histogram + KDE, residual Q-Q, scale-location (√\|std resid\|), Cook's distance / leverage (linear models), residuals over time (S), ACF of residuals (S), error distribution by segment/bin, prediction-interval band plot sorted by ŷ, coverage-by-bin, quantile-calibration (PIT histogram), cumulative absolute error, coefficient plot with CIs (linear), regularisation path (Lasso/ENet α path), alpha vs CV score | see §42.5 |
| Classification | confusion matrix (counts & normalised by true/pred), classification report heatmap, ROC curves (per class OvR + micro/macro, with AUC & CI by bootstrap), PR curves (with iso-F1 lines), threshold sweep (precision/recall/F1/MCC vs threshold), reliability/calibration diagram + histogram of p̂, cumulative gains, lift chart, KS chart, DET curve, probability distribution by class, decision-boundary plot (2D PCA projection), cost curve, multiclass ROC grid, misclassified examples table | see §41.5 |
| Common | learning curve (train vs CV score vs n, with ±σ bands), validation curve (score vs one hyperparameter), CV fold-score box/strip plot per model, fold-score heatmap (model × fold), Optuna optimisation history, param importance (fANOVA), parallel-coordinate of trials, contour/slice plots of the search space, feature importance (native: gain/split/cover; coef magnitude), permutation importance with error bars, training time vs score (Pareto), model size vs latency, epoch loss curves (train/val) for NN/GBM, early-stopping curve | sklearn.model_selection / sklearn.inspection / optuna.visualization |
| Leaderboard | multi-metric table (mean ± std, rank per metric, best highlighted), metric bar chart with error bars (blackcarbon R² bar), critical-difference diagram (Friedman-Nemenyi), radar chart of top-5 across metrics, score-vs-time scatter, ensemble weight bar | scikit-posthocs / numpy |
| Financial (S) | equity curve, underwater/drawdown, rolling Sharpe/IC, CPCV path fan, PBO logit histogram, IS vs OOS scatter, return distribution of strategy, monthly returns heatmap, position/bet-size timeline, signal vs price overlay (lightweight-charts markers) | TradingLab / numpy → Plotly |

---

## 17. Explainability

| Method | Scope | Implementation | Plots / outputs |
|---|---|---|---|
| SHAP (Tree, Linear, Kernel, Permutation, Deep/Gradient, Partition) | global + local | `shap` (TreeExplainer for trees/GBMs, LinearExplainer, PermutationExplainer default for black boxes with background = k-means(50) or 100 sampled rows) | summary bar, beeswarm, dependence/scatter (with auto interaction colour), interaction-value heatmap (trees), waterfall, force (single + stacked), decision plot, heatmap plot, cohort bar (by segment), mean \|SHAP\| table |
| LIME | local | `lime.lime_tabular.LimeTabularExplainer` (discretize_continuous=True, num_features=10, num_samples=5000, kernel_width=0.75√p) | feature-weight bar, local fidelity R², stability across 10 reruns |
| PDP | global | sklearn `PartialDependenceDisplay` | 1D PDP (numeric & categorical), 2D PDP contour/surface for pairs |
| ICE / c-ICE | local-global | sklearn (`kind='both'`, centered) | ICE lines + PDP overlay, derivative ICE |
| ALE | global (robust to correlation) | `PyALE` (alibi is BSL-1.1, not used) | 1D ALE with CI, 2D ALE |
| Permutation importance | global | sklearn `permutation_importance(n_repeats=10, scoring=primary)` on held-out | bar with error bars; drop-column importance (Thorough) |
| Friedman H-statistic | interactions | default replaced by `shap` interaction values; H optional thin wrapper over sklearn PDP | pairwise H heatmap |
| Global surrogate | global | depth-3 decision tree on model predictions | tree diagram + fidelity R² |
| Anchors | local rules | alibi `AnchorTabular` — **optional, off until licensed (BSL-1.1)** | rule + precision/coverage |
| Counterfactuals | local | dice-ml (random / genetic / KD-tree) | table of minimal changes flipping the prediction; diversity |
| EBM shape functions | glass-box | interpret | per-feature shape plots + pairwise interactions |
| Coefficients / odds ratios | linear | statsmodels summary (SE, t, p, CI), odds ratio = e^β | coefficient forest plot |
| Financial FI (sequential) | global | TradingLab MDI / MDA / SFI / clustered FI / orthogonal PCA / fingerprints (see §13.2 item 11) | bars with std across purged folds; linear/non-linear/interaction fingerprint bars |
| Unsupervised explainability | clusters | surrogate classifier (LightGBM) predicting cluster label + SHAP; centroid/medoid tables; PCA loadings | per-cluster SHAP bars |
| TS explainability | forecasts | TFT variable-selection & attention weights; N-BEATS interpretable stack (trend/seasonality); SHAP on mlforecast lag models | attention heatmap, component decomposition |

Defaults: compute SHAP for the top-3 leaderboard models on ≤ 2 000 sampled rows (background 100); LIME/counterfactuals on demand per row. Each explanation carries an ExplainCard with its math (e.g. Shapley value φᵢ = Σ_{S⊆F∖{i}} |S|!(|F|−|S|−1)!/|F|! · [f(S∪{i}) − f(S)]; PDP f̂_S(x_S) = (1/n) Σ f̂(x_S, x_C⁽ⁱ⁾); ALE uses conditional differences integrated over x_S; permutation importance I_j = s − (1/K)Σ s_{k,j}).

---

## 18. Unsupervised learning catalogue

Pre-step (auto, editable): impute → encode (one-hot for ≤ 15 levels else frequency; or Gower distance / FAMD for mixed data) → scale (Standard default; Robust if outliers) → optional PCA to 95% variance before t-SNE/UMAP/clustering on wide data.

### 18.1 Dimensionality reduction

| # | Algorithm | Library | Key hyperparameters: default → search space |
|---|---|---|---|
| D1 | PCA | sklearn | n_components=0.95 (variance) or int(2,50); whiten {F,T}; svd_solver {auto,full,randomized,arpack,covariance_eigh} |
| D2 | Incremental PCA | sklearn | n_components; batch_size=None → {256,1024,4096} |
| D3 | Kernel PCA | sklearn | kernel {rbf,poly,sigmoid,cosine,linear}; gamma log(1e-4,10); degree int(2,5); fit_inverse_transform=True (for reconstruction error) |
| D4 | Sparse PCA / MiniBatch Sparse PCA | sklearn | alpha=1 → log(1e-2,10); ridge_alpha=0.01 |
| D5 | Truncated SVD (LSA) | sklearn | n_components; algorithm {randomized,arpack}; n_iter=5 |
| D6 | Factor Analysis | sklearn | n_components; rotation {None,varimax,quartimax} |
| D7 | FastICA | sklearn | n_components; algorithm {parallel,deflation}; fun {logcosh,exp,cube}; whiten unit-variance |
| D8 | NMF | sklearn | n_components; init {nndsvda,nndsvd,random}; beta_loss {frobenius,kullback-leibler}; alpha_W/H log(1e-4,1); l1_ratio [0,1] (non-negative data only) |
| D9 | Dictionary Learning / MiniBatch DL | sklearn | n_components; alpha=1 |
| D10 | Linear Discriminant Analysis (supervised DR) | sklearn | n_components ≤ classes−1; solver; shrinkage |
| D11 | Gaussian / Sparse Random Projection | sklearn | n_components auto (Johnson-Lindenstrauss eps=0.1) |
| D12 | t-SNE | sklearn / openTSNE | perplexity=30 → [5,100]; learning_rate auto; early_exaggeration=12; max_iter=1000; metric {euclidean,cosine,…}; init pca; n_components {2,3} |
| D13 | UMAP | umap-learn | n_neighbors=15 → int(5,200); min_dist=0.1 → [0,0.99]; metric {euclidean,manhattan,cosine,correlation,hamming(cat)}; n_components {2,3}; densmap {F,T}; supervised (target) option |
| D14 | Isomap | sklearn | n_neighbors=5 → int(5,50); n_components |
| D15 | LLE (standard, modified, Hessian, LTSA) | sklearn | n_neighbors=10; method {standard,modified,hessian,ltsa}; reg=1e-3 |
| D16 | Spectral Embedding (Laplacian eigenmaps) | sklearn | affinity {nearest_neighbors,rbf}; n_neighbors |
| D17 | Metric / non-metric MDS; Classical MDS (PCoA, sklearn ≥1.8) | sklearn | n_init=4; metric {T,F}; dissimilarity {euclidean,precomputed} |
| D18 | PHATE / TriMap / PaCMAP (optional) | trimap / pacmap; phate (GPL-2.0) licence review | n_neighbors; MN/FP ratios |
| D19 | MCA / FAMD (categorical / mixed) | prince | n_components; n_iter |
| D20 | Autoencoder (dense) | **optional, off by default**: built-in `torch.nn` layers + `lightning` (no maintained tabular AE library, §43.5) | bottleneck {2,3,8,16}; layers [256,128]; activation; dropout; lr; epochs + early stop |
| D21 | Variational Autoencoder | **optional, off by default**: built-in `torch.nn` layers + `lightning` (no maintained tabular AE library, §43.5) | latent {2,8,16}; β (β-VAE) [0.5,4]; KL warm-up |
| D22 | Denoising / Sparse Autoencoder | **optional, off by default**: built-in `torch.nn` layers + `lightning` (no maintained tabular AE library, §43.5) | noise σ [0,0.3]; L1 activity reg |

**DR plots:** scree plot (eigenvalues, Kaiser line λ=1), explained variance + cumulative variance with 80/90/95% markers, broken-stick and parallel-analysis (Horn) overlays, biplot (scores + loading arrows), loadings heatmap & bar per component, correlation circle, contribution (cos²) plots, 2D/3D embeddings coloured by any column/target/cluster, Shepard diagram (original vs embedded distances), trustworthiness & continuity curves vs k, reconstruction-error curve vs n_components (PCA/KPCA/AE), AE training loss, latent-space traversal grid (VAE), t-SNE perplexity grid, UMAP n_neighbors × min_dist grid, ICA source signals, NMF component heatmap, LDA projection by class.
**DR metrics:** explained variance ratio, reconstruction MSE, trustworthiness T(k) = 1 − 2/(nk(2n−3k−1)) Σᵢ Σ_{j∈U_k(i)} (r(i,j) − k), continuity, Kruskal stress-1 = √(Σ(dᵢⱼ − d̂ᵢⱼ)²/Σdᵢⱼ²), KMO and Bartlett's sphericity (suitability for PCA/FA), neighbourhood preservation (kNN recall).
**DR model selection:** n_components by cumulative variance threshold, Kaiser, parallel analysis, elbow of reconstruction error, or maximum trustworthiness; method comparison table.

### 18.2 Clustering

| # | Algorithm | Library | Key hyperparameters: default → search space |
|---|---|---|---|
| K1 | K-Means | sklearn | n_clusters=auto(2–15 sweep); init {k-means++, random}; n_init=10; algorithm {lloyd,elkan}; max_iter=300 |
| K2 | Mini-Batch K-Means | sklearn | batch_size=1024 → {256,1024,4096}; n_clusters sweep |
| K3 | Bisecting K-Means | sklearn | bisecting_strategy {biggest_inertia, largest_cluster} |
| K4 | K-Medoids (PAM / alternate / CLARA) | **optional**: `kmedoids` (GPL-3.0) or `scikit-learn-extra` (last release 2023) — licence/maintenance review (§43.5) | metric {euclidean,manhattan,cosine,precomputed(Gower)}; method {pam,alternate} |
| K5 | K-Modes / K-Prototypes (categorical / mixed) | kmodes | init {Huang,Cao}; gamma (prototype weight) auto |
| K6 | Fuzzy C-Means | scikit-fuzzy | m=2 → [1.5,3]; error=1e-5 |
| K7 | Agglomerative (hierarchical) | sklearn + scipy | linkage {ward,complete,average,single}; metric; n_clusters or distance_threshold; connectivity (kNN graph) |
| K8 | BIRCH | sklearn | threshold=0.5 → [0.1,2]; branching_factor=50 |
| K9 | DBSCAN | sklearn | eps auto (k-distance knee) → [0.05,5]; min_samples=2·dim → int(3,50); metric |
| K10 | HDBSCAN | sklearn / hdbscan | min_cluster_size=max(5, n/100) → int(5,200); min_samples None∪int; cluster_selection_method {eom,leaf}; cluster_selection_epsilon [0,1] |
| K11 | OPTICS | sklearn | min_samples=5; xi=0.05 → [0.01,0.2]; cluster_method {xi,dbscan} |
| K12 | Mean Shift | sklearn | bandwidth auto (`estimate_bandwidth` quantile=0.3 → [0.1,0.5]); bin_seeding=True |
| K13 | Affinity Propagation | sklearn | damping=0.5 → [0.5,0.99]; preference median → quantiles |
| K14 | Spectral Clustering | sklearn | affinity {rbf,nearest_neighbors}; n_neighbors=10; gamma; assign_labels {kmeans,discretize,cluster_qr} |
| K15 | Gaussian Mixture | sklearn | n_components sweep 1–15 (BIC); covariance_type {full,tied,diag,spherical}; reg_covar=1e-6; n_init=3 |
| K16 | Bayesian GMM (Dirichlet process) | sklearn | weight_concentration_prior_type {dirichlet_process,dirichlet_distribution}; n_components upper=15 |
| K17 | ONC (Optimal Number of Clusters, López de Prado) | **TradingLab** `clustering/onc.py → get_onc_clusters(corr_mat, repeat=10)` | for correlation matrices of assets/features |
| K18 | Self-Organising Map | MiniSom | grid 10×10; sigma=1; learning_rate=0.5 |
| K19 | Deep Embedded Clustering (DEC) (Thorough) | **optional, off by default**: `torch.nn` AE + sklearn KMeans init (no maintained DEC library, §43.5) | AE + KL clustering; n_clusters |

**Clustering plots:** elbow (inertia/WCSS vs k) with knee detection (Kneedle), silhouette-score vs k, **silhouette plot** per cluster (knife plot), Calinski-Harabasz vs k, Davies-Bouldin vs k, gap statistic vs k (with 1-SE rule), BIC/AIC vs k (GMM), dendrogram (truncated, colour threshold, cophenetic correlation shown), clustered heatmap (clustermap), k-distance plot (DBSCAN eps knee), OPTICS reachability plot, HDBSCAN condensed tree + single-linkage tree, cluster scatter in 2D/3D (PCA/UMAP projection) with centroids, convex hulls and GMM ellipses, cluster size bar, cluster profile heatmap (z-scored means), parallel coordinates by cluster, radar/spider per cluster, box/violin of features by cluster, categorical composition stacked bars by cluster, Sankey of cluster stability across k or across algorithms, co-association/consensus matrix (bootstrap stability), ARI/NMI comparison heatmap between algorithms, surrogate-tree rules, SHAP of surrogate model.
**Clustering metrics (internal):** silhouette s(i) = (b(i) − a(i))/max(a(i), b(i)); Calinski-Harabasz CH = [tr(B_k)/(k−1)] / [tr(W_k)/(n−k)]; Davies-Bouldin DB = (1/k) Σᵢ maxⱼ≠ᵢ (σᵢ + σⱼ)/d(cᵢ,cⱼ); Dunn index = min inter / max intra; inertia/WCSS = Σ ||x − μ_c||²; gap statistic Gap(k) = E*[log W_k] − log W_k; BIC/AIC (GMM); DBCV (density-based, for DBSCAN/HDBSCAN); cophenetic correlation; noise fraction. **External** (when a label column exists, e.g. sample datasets): ARI, AMI/NMI, homogeneity, completeness, V-measure, Fowlkes-Mallows, purity, contingency matrix. **Stability:** bootstrap Jaccard per cluster, consensus score.
**Model selection:** composite rank across silhouette (↑), CH (↑), DB (↓), DBCV (↑), stability (↑) with user weights; k chosen by knee/silhouette max/gap 1-SE/BIC min; leaderboard of (algorithm, params, k).

### 18.3 Anomaly / outlier detection

| # | Algorithm | Library | Key hyperparameters |
|---|---|---|---|
| A1 | Isolation Forest | sklearn | n_estimators=300; contamination auto → [0.001,0.2]; max_samples auto; max_features [0.5,1] |
| A2 | Extended Isolation Forest | `pyod.models.iforest` / `pyod.models.dif` (isotree not required) | ndim |
| A3 | Local Outlier Factor (novelty) | sklearn | n_neighbors=20 → int(5,100); contamination |
| A4 | One-Class SVM / SGD-OCSVM | sklearn | nu=0.05 → [0.01,0.3]; kernel; gamma |
| A5 | Elliptic Envelope (robust covariance, MCD) | sklearn | contamination; support_fraction |
| A6 | COPOD / ECOD (parameter-free) | pyod | contamination |
| A7 | HBOS | pyod | n_bins=10 → int(5,50) |
| A8 | KNN / Average-KNN detector | pyod | n_neighbors; method {largest, mean, median} |
| A9 | PCA reconstruction error | `pyod.models.pca.PCA` | n_components |
| A10 | Autoencoder / VAE detector | pyod / PyTorch | hidden sizes, epochs |
| A11 | Deep SVDD | pyod | |
| A12 | LODA, CBLOF, Feature Bagging, SUOD ensemble | pyod | |
| A13 | Mahalanobis / robust z | `sklearn.covariance.MinCovDet` / `pyod.models.mad.MAD` | threshold χ² p |
| A14 | TS anomalies: STL residual z, S-H-ESD (Twitter), rolling z, Prophet interval breach | `statsmodels` STL + `pyod` MAD; S-H-ESD optional thin wrapper (§43.5) | window, α |

Plots: score histogram with threshold, ranked scores (Pareto), 2D/3D projection with anomalies highlighted, feature contributions per anomaly (SHAP on surrogate / COPOD dimensional outlier graph), time-series overlay of anomalies, precision@k & ROC/PR when labels exist (e.g. credit-card fraud sample). Metrics: ROC-AUC, PR-AUC, precision@n, contamination found, score separation.

### 18.4 Outputs

Assign cluster/anomaly labels and DR coordinates back to the dataset as new columns (new dataset version), so they can feed Supervised models; export cluster profiles to Excel; register the fitted pipeline for scoring new rows (Predict module).

---

## 19. Time-series analysis and forecasting catalogue

Internal format: long dataframe `unique_id, ds, y, [exog...]` (Nixtla convention) so univariate, multi-series panels and hierarchical data share one path. Frequency inferred (`pd.infer_freq`; business-day and NSE trading-calendar aware for financial data), gaps reported and fillable.

### 19.1 Analysis page

| Analysis | Implementation | Output |
|---|---|---|
| Line / OHLC chart, rolling stats | Plotly / lightweight-charts | |
| Classical decomposition (additive / multiplicative) | `statsmodels.tsa.seasonal.seasonal_decompose` | trend, seasonal, resid panels |
| STL / MSTL (multiple seasonalities) | `statsmodels STL(period, robust=True)`, `MSTL(periods)` | components + strength of trend F_T = max(0, 1 − Var(R)/Var(T+R)), strength of seasonality F_S |
| X-13 / SEATS (optional, needs binary) | statsmodels x13 | |
| ACF / PACF (with Bartlett / 95% bands), cross-correlation (CCF) with exog | statsmodels | suggested p, q from cut-offs |
| Stationarity tests | ADF (`adfuller`, autolag AIC), KPSS (level/trend), Phillips-Perron & DF-GLS (`arch.unitroot`), Zivot-Andrews (break), seasonal unit root (OCSB/CH via pmdarima `nsdiffs`) | table + verdict + recommended d, D (`ndiffs`, `nsdiffs`) |
| Differencing / transform preview | pandas / `scipy.stats.boxcox` / `coreforecast` (Guerrero) / TradingLab | Δ, Δ_m, log, Box-Cox (Guerrero λ), FFD (TradingLab `frac_diff_ffd`) with ADF after each |
| Seasonality detection | periodogram/Welch spectrum peaks, ACF peaks, Fourier F-test, `seasonal_test` (statsforecast), candidate m list {7, 5 (trading week), 12, 4, 24, 168, 52, 365.25, 21 (trading month), 252 (trading year)} | detected season lengths |
| Autocorrelation tests | Ljung-Box, Box-Pierce, Durbin-Watson, BDS (non-linearity), runs test | |
| Heteroskedasticity / ARCH | Engle ARCH-LM, McLeod-Li; rolling volatility; \|r\|, r² ACF | GARCH suitability |
| Structural breaks / change points | TradingLab `get_chow_type_stat`, `get_chu_stinchcombe_white_statistics`, `get_sadf`; `ruptures` (PELT/BinSeg, cost rbf/l2); Bai-Perron (optional) | break dates overlaid |
| Granger causality, cointegration (multivariate) | statsmodels `grangercausalitytests`, Engle-Granger `coint`, Johansen `coint_johansen` | lag tables, rank r for VECM |
| Hurst exponent, variance ratio test (Lo-MacKinlay) | `nolds` (Hurst) / `arch.unitroot.VarianceRatio` | mean-reversion vs trend |
| Intermittency (ADI, CV²) classification | thin (pandas; Syntetos-Boylan rule) | smooth / erratic / intermittent / lumpy → suggests Croston family |
| Seasonal plots, subseries, lag plots, calendar heatmap, box by period | Plotly | |

### 19.2 Forecasting algorithms

| # | Model | Library | Key hyperparameters: default → search space |
|---|---|---|---|
| F1 | Naive (random walk) | statsforecast `Naive` | — |
| F2 | Seasonal Naive | `SeasonalNaive` | season_length=m |
| F3 | Random Walk with Drift | `RandomWalkWithDrift` | — |
| F4 | Historic Average / Window Average / Seasonal Window Average | statsforecast | window_size=int(3,52) |
| F5 | Simple Exponential Smoothing (fixed / optimised) | statsforecast / statsmodels | α ∈ (0,1) |
| F6 | Holt (linear trend, damped) | statsmodels `Holt` / statsforecast `Holt` | α, β, φ ∈ [0.8,0.98]; damped {T,F} |
| F7 | Holt-Winters (additive/multiplicative seasonality) | statsmodels `ExponentialSmoothing` / statsforecast `HoltWinters` | trend {add,mul,None}; seasonal {add,mul}; damped; use_boxcox; requires n ≥ 2m |
| F8 | ETS state-space / AutoETS | statsforecast `AutoETS(season_length, model='ZZZ', damped)`; statsmodels `ETSModel` | model code E,T,S ∈ {A,M,N,Z}; selection by AICc |
| F9 | ARIMA (p,d,q) | statsmodels `ARIMA` / statsforecast `ARIMA` | p int(0,5), d int(0,2), q int(0,5); trend {n,c,t,ct}; method |
| F10 | SARIMA (p,d,q)(P,D,Q)m | statsmodels `SARIMAX` | P,Q int(0,2), D int(0,1) |
| F11 | SARIMAX (with exogenous) | statsmodels `SARIMAX(exog)` | as F10 + exog columns (past-known / future-known) |
| F12 | Auto-ARIMA | statsforecast `AutoARIMA(max_p=5,max_q=5,max_P=2,max_Q=2,max_d=2,max_D=1, ic='aicc', stepwise=True, test='kpss', seasonal_test='seas', season_length)`; pmdarima alternative | all exposed |
| F13 | Dynamic regression / ARIMA with Fourier terms (long seasonality) | statsforecast + `utilsforecast.feature_engineering.fourier` | K harmonics int(1,10) per period (AICc) |
| F14 | Theta / Optimised / Dynamic / Dynamic-Optimised Theta; AutoTheta | statsforecast | decomposition_type {multiplicative,additive}; season_length |
| F15 | Complex Exponential Smoothing (AutoCES) | statsforecast | model {N,S,P,F,Z} |
| F16 | TBATS / BATS / AutoTBATS | statsforecast `TBATS` / `AutoTBATS` | use_box_cox, use_trend, use_damped_trend, use_arma_errors, seasonal_periods (multiple) |
| F17 | MSTL + trend forecaster | statsforecast `MSTL(season_length=[...], trend_forecaster=AutoETS)` | |
| F18 | MFLES / AutoMFLES | statsforecast | season_length, n_boosting_rounds |
| F19 | Unobserved Components (structural, UCM) | statsmodels `UnobservedComponents` | level {llevel, lltrend, rwdrift…}; freq_seasonal; cycle |
| F20 | Prophet | prophet | growth {linear,logistic,flat}; changepoint_prior_scale log(1e-3,0.5); seasonality_prior_scale log(0.01,10); seasonality_mode {additive,multiplicative}; holidays (NSE / India calendar); n_changepoints=25 |
| F21 | VAR | statsmodels `VAR` | maxlags by AIC/BIC/HQIC; trend {c,ct,n} |
| F22 | VARMAX | statsmodels `VARMAX` | order (p,q) |
| F23 | VECM | statsmodels `VECM` | k_ar_diff; coint_rank (Johansen); deterministic {n,co,ci,lo,li} |
| F24 | GARCH(p,q) / ARCH | `arch` (`arch_model`) / statsforecast `GARCH`,`ARCH` | mean {Constant, Zero, AR(k), HAR}; vol {GARCH, ARCH, EGARCH, GJR-GARCH (o=1), TARCH, FIGARCH, APARCH, HARCH}; p,q int(1,3); dist {normal, t, skewt, ged}; rescale=True — forecasts **variance/volatility**, also VaR/ES |
| F25 | Croston (Classic / Optimised / SBA), ADIDA, IMAPA, TSB | statsforecast | α (Croston classic/SBA), α_d, α_p (TSB) — intermittent demand |
| F26 | Kalman filter / local level (state space) | statsmodels state space / `darts` KalmanForecaster (pykalman dropped, §43.12) | |
| F27 | ML with lag features (direct / recursive / DirRec) | **mlforecast** (`MLForecast(models=[LGBM, XGB, CatBoost, RF, Ridge, ...], lags, lag_transforms (rolling/expanding/EWM), date_features, target_transforms (Differences, LocalStandardScaler)`) | lags default [1..m, 2m]; strategy {recursive, direct}; any §12.1 regressor |
| F28 | sktime reduction / skforecast (alternative) | sktime / skforecast | window_length |
| F29 | RNN | neuralforecast `RNN` | input_size = 3·h → {2h,3h,5h,7h}; encoder_hidden_size {64,128,256}; encoder_n_layers int(1,3); context_size; decoder_hidden_size; learning_rate log(1e-4,1e-2); max_steps=1000; loss {MAE, MSE, MQLoss, DistributionLoss(Normal/StudentT)} |
| F30 | LSTM | neuralforecast `LSTM` | as F29 |
| F31 | GRU | neuralforecast `GRU` | as F29 |
| F32 | Dilated RNN | neuralforecast `DilatedRNN` | dilations [[1,2],[4,8]]; cell {LSTM,GRU} |
| F33 | xLSTM | neuralforecast `xLSTM` | blocks, hidden |
| F34 | TCN | neuralforecast `TCN` | kernel_size=2; dilations [1,2,4,8,16]; encoder_hidden_size |
| F35 | BiTCN | neuralforecast `BiTCN` | hidden_size; dropout |
| F36 | DeepAR (probabilistic, autoregressive) | neuralforecast `DeepAR` | lstm_n_layers int(1,4); lstm_hidden_size {32,64,128}; loss DistributionLoss(StudentT/Normal/NegBin) |
| F37 | DeepNPTS | neuralforecast | |
| F38 | MLP (multi-horizon) / MLPMultivariate | neuralforecast | num_layers, hidden_size |
| F39 | N-BEATS (generic / interpretable) | neuralforecast `NBEATS` | stack_types [identity,trend,seasonality]; n_blocks [1,1,1]; mlp_units; n_harmonics=2; n_polynomials=2 |
| F40 | N-BEATSx (with exogenous) | neuralforecast `NBEATSx` | as F39 + exog |
| F41 | N-HiTS | neuralforecast `NHITS` | n_pool_kernel_size [2,2,1]; n_freq_downsample [4,2,1]; pooling {MaxPool1d,AvgPool1d}; interpolation {linear,nearest} |
| F42 | DLinear / NLinear / XLinear | neuralforecast | moving_avg_window=25 |
| F43 | TiDE | neuralforecast `TiDE` | hidden_size, decoder_output_dim, temporal_width |
| F44 | Temporal Fusion Transformer (TFT) | neuralforecast `TFT` | hidden_size {64,128,256}; n_head {4,8}; dropout; static/hist/future exog; quantile loss MQLoss([0.1,0.5,0.9]) |
| F45 | Vanilla Transformer | neuralforecast | |
| F46 | Informer | neuralforecast `Informer` | factor=3 (ProbSparse); n_head; encoder_layers int(1,3) |
| F47 | Autoformer / FEDformer | neuralforecast | moving_avg; modes (FED) |
| F48 | PatchTST | neuralforecast `PatchTST` | patch_len=16 → {8,16,24}; stride=8; encoder_layers int(2,4); revin=True |
| F49 | iTransformer (multivariate) | neuralforecast `iTransformer` | n_series; hidden_size; e_layers |
| F50 | TimesNet | neuralforecast `TimesNet` | top_k=5; num_kernels=6 |
| F51 | TSMixer / TSMixerx / TimeMixer / SOFTS / TimeXer / StemGNN / KAN / RMoK / HINT | neuralforecast | per-model curated specs (multivariate & hierarchical options) |
| F52 | Auto* versions of every neural model | neuralforecast `AutoNHITS`, `AutoLSTM`, … (Optuna/Ray backend) | default search spaces from Nixtla, overridable |
| F53 | Foundation zero-shot models (optional, self-hosted) | Chronos-Bolt / TimesFM / Moirai (open weights) | context length, quantiles — **opt-in**, licence check |
| F54 | Ensembles / combinations | `sktime` EnsembleForecaster / `darts` RegressionEnsembleModel | simple mean, median, inverse-MSE weights, stacking on backtest windows |

### 19.3 Exogenous variables

Past-only (historical) vs future-known (calendar, planned events, holidays): UI asks per regressor; models declare support (Nixtla `EXOGENOUS_FUTR/HIST/STAT`); for future-known regressors the Forecast page requires their future values (upload or scenario).

### 19.4 Backtesting

Rolling-origin evaluation (expanding default, sliding option): `n_windows` default 5 (≤ 10), `step_size` = h, refit each window (stats) or every k windows (DL), final holdout = last h observations untouched. Financial series also support purged/embargoed CV and CPCV (§13.2). Output: per-window metrics, per-horizon-step metrics (error growth curve), overall leaderboard.

### 19.5 Prediction intervals

Model-native (ARIMA/ETS analytic, DeepAR/TFT distribution or quantile outputs, GARCH vol), **conformal** (statsforecast `ConformalIntervals(h, n_windows)`, MAPIE `MapieTimeSeriesRegressor` EnbPI/ACI), bootstrap residuals (block bootstrap for dependence), quantile losses (MQLoss). Levels default [80, 95].

### 19.6 Metrics

MAE, RMSE, MAPE, sMAPE, WAPE, **MASE** = MAE / [(1/(n−m)) Σ_{t=m+1}^{n} |y_t − y_{t−m}|], RMSSE, MSIS (scaled interval score), coverage, CRPS / scaled CRPS, pinball per quantile, bias (ME), Theil's U2, directional accuracy, for volatility: QLIKE = σ²/σ̂² − ln(σ²/σ̂²) − 1 and MSE on realised variance; in-sample AIC/AICc/BIC.

### 19.7 Residual diagnostics

Residual time plot, histogram + normal overlay, Q-Q, ACF of residuals, **Ljung-Box** table (lags 10, 2m; df adjusted by p+q), Jarque-Bera, ARCH-LM on residuals, cumulative periodogram (Bartlett), standardised residuals of GARCH + their squared ACF, PIT histogram for probabilistic forecasts.

### 19.8 Time-series plots (catalogue)

series + forecast + PI fan (80/95) with backtest windows shaded, actual vs fitted, backtest windows small multiples, error-by-horizon curve, model comparison of forecasts overlay, decomposition panels, ACF/PACF, seasonal/subseries plots, periodogram, rolling metric plot, components (Prophet trend/seasonalities/holidays; N-BEATS interpretable stacks; TFT attention & variable importance), volatility forecast with realised vol, VaR breaches plot (Kupiec/Christoffersen tests), impulse-response functions & FEVD (VAR), Granger heatmap, cointegration residual plot, fan chart of quantiles, hierarchical reconciliation tree (optional).

---

## 20. Smart forecast-horizon rules

Inputs: n = effective length after cleaning; freq; m = dominant season length (and set of m's); model family; number of backtest windows W; requested h. The **HorizonGuard** computes a hard cap, a recommended value and reasons shown next to the slider. Background: Hyndman & Kostenko (2007) give minimum sample sizes per model (seasonal ARIMA needs at least p+q+P+Q+d+mD+1 observations, e.g. 16 for the airline model; seasonal ETS needs ≥ 2 full seasons for initial states), and FPP3 §13 notes that only "more observations than parameters" is a theoretical limit and out-of-sample testing must decide the rest — so the lab combines hard feasibility rules with empirical truncation.

**Step 1 — frequency caps (recommended / hard max):**

| Frequency | Recommended h | Hard max h | Typical m |
|---|---|---|---|
| minutely | 60 | 1 440 (1 day) | 60, 1440 |
| hourly | 24 | 168 (1 week) | 24, 168 |
| daily (calendar) | 14 | 90 | 7, 365.25 |
| business daily / trading days (financial prices) | 5 | 21 (≈1 trading month); volatility models 66 | 5, 21, 252 |
| weekly | 13 | 52 | 52.18 |
| monthly | 12 | 36 | 12 |
| quarterly | 8 | 16 | 4 |
| yearly | 3 | 10 | 1 |

**Step 2 — data feasibility (hard):**

* `h ≤ floor((n − n_min_train) / (W + 1))` so that W backtest windows of size h plus a final holdout of size h fit after the minimum training length (defaults W = 4, n_min_train = max(2m, 24); admin-configurable).
* `h ≤ floor(n / 3)` (never forecast further than a third of history); for n < 50, `h ≤ max(1, floor(n/4))`.
* Seasonal models: require `n ≥ 2m + h` (ETS/Holt-Winters) and `n ≥ p+q+P+Q+d+mD+1 + h`(SARIMA; checked with the chosen/auto orders); recommended `h ≤ 2m`.
* Long seasonality (m > 24 for ETS, m > ~200 for SARIMA): switch to Fourier/TBATS/MSTL/Prophet automatically (message explains why).
* Deep models: lookback L = input_size (default 3h; min 2h) ⇒ need `n_train ≥ L + h + val_size` and at least 1 000 training windows recommended; so `h ≤ floor((n − val − test) / (k + 1))` with k = L/h (default 3) → if fewer than 300 windows, DL models are greyed out with a reason.
* GARCH family: need n ≥ 500 returns recommended (≥ 250 hard); horizon in trading days ≤ 66 because multi-step variance forecasts converge to the unconditional variance (shown as a reason).
* VAR/VECM: `n ≥ k·p + h + 10` parameters per equation check (k series, p lags).
* Intermittent series (Croston family): flat forecasts — h unrestricted by structure but capped by Step 1.

**Step 3 — empirical truncation (soft, after backtest):** compute per-horizon-step MASE_j (j = 1..h) on backtest windows; the **useful horizon** h* = largest j such that MASE_j < 1 (beats seasonal naive) and the 95% PI relative width (u − l)/|ŷ| < 2 (configurable). If h > h*, the forecast beyond h* is greyed/dashed in the chart and AI Insights explains that skill is lost.

**Step 4 — final:** `h_max = min(freq hard max, data feasibility caps, model caps)`; `h_default = min(recommended(freq), h_max, 2m if seasonal)`. User may request up to h_max; beyond it the API returns 422 with reasons. All caps are configurable by admins.

---

## 21. Probabilistic prediction and uncertainty

> How these outputs appear per row in batch files and in the custom form (column names, levels, flags): §45.4.

| Need | Methods (library) | Output |
|---|---|---|
| Class probabilities | `predict_proba`; calibration via `CalibratedClassifierCV` (sigmoid/Platt, isotonic, temperature scaling) fitted on OOF / calibration split; Venn-Abers (optional) | calibrated p̂ per class, ECE before/after, reliability plot |
| Confidence score per prediction | max p̂, margin (p̂₁ − p̂₂), entropy H(p̂), conformal p-values / credibility; for regression: interval width relative to target scale, ensemble disagreement (std of members), kNN distance-to-train (applicability domain / OOD flag via Mahalanobis or Isolation Forest on the training feature space) | `confidence ∈ [0,1]` + band (High/Med/Low) with the rule shown |
| Conformal prediction — regression | MAPIE `SplitConformalRegressor`, `CrossConformalRegressor` (CV+/Jackknife+), `ConformalizedQuantileRegressor` (CQR) | [l, u] at 1−α with finite-sample marginal coverage guarantee |
| Conformal — classification | MAPIE `SplitConformalClassifier` (LAC, APS, RAPS, top-k) | prediction sets with coverage 1−α; set size distribution |
| Conformal — time series | EnbPI, ACI (adaptive), statsforecast `ConformalIntervals` | forecast bands |
| Quantile regression | LightGBM/XGBoost/CatBoost quantile objective, sklearn `GradientBoostingRegressor(loss='quantile')`, `QuantileRegressor`, quantile random forest (quantile-forest), MQLoss in neuralforecast | q̂_τ for τ ∈ {0.05,0.1,0.5,0.9,0.95} |
| Distributional models | NGBoost (Normal/LogNormal/Laplace/T), DeepAR/TFT distribution heads, GLMs, Bayesian Ridge/ARD (posterior predictive σ), Gaussian Process (posterior σ) | full predictive distribution; CRPS, NLL |
| Bootstrap | bootstrap refits (B=100) or residual bootstrap; block bootstrap for sequential | percentile intervals |
| MC dropout / deep ensembles | PyTorch models: dropout at inference T=50 passes; 5-seed ensembles | mean ± σ, epistemic vs aleatoric split (law of total variance) |
| Bayesian models | BayesianRidge, ARD, GP, (optional) PyMC/NumPyro Bayesian linear/logistic regression, Prophet MCMC | credible intervals |

Validation of uncertainty: coverage (PICP) vs nominal, interval score, CRPS, sharpness (mean width), calibration of quantiles (PIT histogram), conditional coverage by bin/segment. AI Insights reports coverage gaps explicitly.

---

## 22. Prediction / Inference module

> v2.2: the Single and Batch sub-pages are specified in full by **§45 Prediction Studio** (feature contract, validation codes PV01–PV16, output columns per task, API, tables, components, samples). The rows below remain the overview.

| Sub-page | Function |
|---|---|
| Single | Auto-generated form from the model's input schema (types, ranges, category dropdowns, defaults = training medians/modes, out-of-range warnings); output card: point prediction, class probabilities bar, calibrated probability, prediction set (conformal), interval [l,u] at chosen α, quantiles, confidence score + OOD flag, SHAP waterfall + LIME for this row, nearest training neighbours, counterfactual "what would change the decision". |
| Batch | Upload CSV/XLSX/Parquet → schema check (missing/extra columns, dtype coercion report) → async scoring job → downloadable file with predictions, probabilities, intervals, confidence, OOD flag, top-3 SHAP reasons per row; summary plots (distribution of predictions, confidence histogram, drift vs training). |
| What-if / Scenario | sliders per feature with live re-prediction, ICE line for the active feature, sensitivity tornado chart, scenario table save/compare. |
| Forecast (TS) | pick model + h (HorizonGuard) + levels + future exog → forecast table + fan chart + per-step skill; re-forecast with latest data; for GARCH: volatility & VaR forecast. |
| Monitoring | for registered models: prediction volume, input drift (PSI, KS, Jensen-Shannon per feature), prediction drift, performance when labels arrive, calibration drift; alerts thresholds (PSI > 0.2). |
| API | auto-generated REST endpoint per registered model (`POST /serve/{name}@{alias}/predict`), OpenAPI spec, API keys, code snippets (Python/JS/cURL/Excel Power Query). |

---

## 23. AI Insights layer (hosted vision-language model — provider details in §40)

### 23.1 Goals

Read **rendered plots (PNG)** plus the **exact tables/metrics JSON** behind them and produce detailed, grounded insights at every stage: EDA, Modelling (per model and leaderboard), Explainability, Prediction/Uncertainty, Time-Series forecasts. Uses a hosted OpenAI-compatible API — the NVIDIA API catalog by default, with swappable fallback providers and a numbers-only offline mode (§40). No GPU hosting required.

### 23.2 Model comparison (researched Nov 2026)

> **Superseded for deployment by §40.** The user chose a hosted API instead of self-hosting. The table below is kept as background on open-weights VLMs (several of them, e.g. Gemma and Llama Vision, are also served by NVIDIA's catalog). The current primary/fallback picks are in §40.1.

| Model | Sizes | Licence | Size on disk (Ollama Q4) / VRAM | Chart/table reading | Runtime | Verdict |
|---|---|---|---|---|---|---|
| **Qwen3-VL** (Alibaba) | 2B, 4B, 8B, 30B-A3B (MoE), 32B, 235B-A22B | **Apache-2.0** | 2B 1.9 GB · 4B 3.3 GB · 8B 6.2 GB · 30B 20 GB · 32B 21 GB (Ollama library); 8B usable on 8 GB, comfortable 12–16 GB | strongest open family on ChartQA-style tasks (Qwen3-VL variants top published ChartQA leaderboards; Qwen2.5-VL-7B 87.3, Qwen2.5-VL-72B 89.5) ; 256K context; tools + thinking modes | Ollama ≥ 0.12.7, vLLM, llama.cpp | **Primary: Qwen3-VL-8B-Instruct**; **High-quality tier: Qwen3-VL-32B or 30B-A3B on a 24–48 GB GPU via vLLM** |
| Gemma 3 (Google) | 4B, 12B, 27B (vision); 1B/270M text | Gemma Terms (commercial allowed, prohibited-use policy) | 4B 3.4 GB · 12B 8.2 GB · 27B 17 GB | good doc/chart/OCR (DocVQA 85.6 on 27B per Google); 128K ctx; 140+ languages | Ollama native | **Lightweight fallback (CPU-friendly): Gemma 3 4B** if licence acceptable; otherwise Qwen3-VL-4B/2B |
| InternVL3.5 (OpenGVLab) | 1B–241B | MIT code; weights inherit LLM backbone licence | 8B ≈ 8 GB | best open reasoning over diagrams (MMMU 73.4 @8B) | vLLM / LMDeploy (partial Ollama) | Optional "reasoning" alternative |
| MiniCPM-V 4.5 (OpenBMB) | 8B | MiniCPM licence (free commercial with registration) | ~6 GB | ChartQA 87.4 | Ollama / llama.cpp | Edge alternative |
| Llama 3.2 Vision (Meta) | 11B, 90B | Llama Community Licence | 11B ≈ 8 GB | a generation behind Qwen3-VL | Ollama | Not recommended |
| Pixtral 12B / Mistral Small 3.x (Mistral) | 12B, 24B | Apache-2.0 | 12B ≈ 8–10 GB; 24B ≈ 15 GB | solid chart/doc | vLLM / Ollama (`mistral-small3.2`) | Alternative primary if Qwen unavailable |
| GLM-4.6V / 4.6V-Flash (Z.ai) | 9B Flash, 106B | MIT | 9B ≈ 12 GB | frontier-level at 106B | vLLM / llama.cpp | Optional large-server tier |
| Phi-4-reasoning-vision (Microsoft) | 15B | MIT | ~10 GB | ChartQA 83.3 (VLMEvalKit) | vLLM | Optional |

Note: sources include a June 2026 self-hosting guide (aifoss.dev), the Ollama library pages (qwen3-vl, gemma3 tags) and a public ChartQA leaderboard; benchmark numbers come from vendor reports and were not re-run by us. Newer families mentioned in one 2026 cheat-sheet (e.g. Gemma 4, Qwen 3.5/3.8 with built-in vision) could not be cross-verified and are on a watch-list; the adapter makes swapping models a config change.

**Original self-hosting recommendation (superseded by §40.1)**

* **Primary (old):** `qwen3-vl:8b` (Ollama) / `Qwen/Qwen3-VL-8B-Instruct` (vLLM), temperature 0.2, top_p 0.9, JSON mode / guided decoding (vLLM `guided_json`, Ollama `format` = JSON schema), context 32K. Hardware: 1× 12–16 GB GPU (e.g. RTX 4070 Ti/4080, L4) → ~20–40 tokens/s.
* **High-quality tier (optional):** Qwen3-VL-32B-Instruct (AWQ/FP8) or 30B-A3B on 1× 48 GB (L40S/A6000) or 2× 24 GB via vLLM tensor parallel.
* **Lightweight fallback:** `qwen3-vl:4b` (GPU ≥ 6 GB or CPU) → `qwen3-vl:2b` (CPU-only laptops, ~4 GB RAM); Gemma 3 4B as alternative where its licence is acceptable.
* **Text-only degradation:** if no vision model is available, insights are generated from the numbers JSON only (any open text LLM, e.g. Qwen3-8B), and the UI labels them "numbers-only".
* **Opt-in hosted free tiers (disabled by default; admin toggle + per-workspace consent + data-classification check, never for client/PII data):** Google AI Studio (Gemini free tier), OpenRouter `:free` vision models, Groq / Hugging Face Inference free tiers — all via the same OpenAI-compatible adapter; quotas and terms change frequently, so treat as best-effort.

### 23.3 Pipeline

```
artefact(s) ready ─▶ InsightRequest(scope, ids, stage, depth) ─▶ q.insights
  1. Collect: PNG renders (kaleido, 1024×640, dark-on-light theme for legibility; encoded under the provider's 180 KB base64 inline limit and large grids split into tiles, §40.4),
     artefact.numbers JSON, table extracts (top-N rows), task_spec, dataset profile, model params, CV spec, seed.
  2. Ground: build a FACTS block = canonical JSON of all numbers the model may cite, each with a fact_id
     (e.g. F12 = {"artefact":"SUP.R42.LGBM.ROC","metric":"auc_macro","value":0.9132,"ci95":[0.902,0.924]}).
  3. Prompt: system + stage template + FACTS + images (≤ 6 per call; more → map-reduce: per-artefact calls, then a stage summary call over the per-artefact JSONs).
  4. Generate with JSON-schema-constrained decoding.
  5. Validate: JSON schema; every number in text must match a FACTS value (tolerance 1e-3 relative, rounding-aware) or be marked derived; every claim must cite ≥ 1 fact_id or artefact_id; banned phrases (guarantees, investment advice); hallucinated artefact IDs rejected. On failure: one repair round with the validator errors, else fall back to deterministic rule-based insights.
  6. Store: insights table (input_hash, model_name, prompt_version) → cache hit on identical inputs.
  7. Stream: tokens via SSE to the AI Insights side panel; final validated JSON replaces the stream; citation chips link to panels.
```

Deterministic **rule engine** runs first (always available, no LLM): e.g. "skew > 1 → suggest log/Yeo-Johnson", "VIF > 10", "train−CV R² gap > 0.1 → overfitting", "fold std > 2× median → unstable", "ECE > 0.05 → calibrate", "Ljung-Box p < 0.05 on residuals → autocorrelation left", "coverage 95% PI < 90% → intervals too narrow". Its findings are passed to the VLM as `rule_findings` so the model explains and prioritises them rather than inventing.

### 23.4 Output JSON schema (all stages)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["stage", "scope", "headline", "findings", "recommendations", "confidence"],
  "properties": {
    "stage": {"enum": ["eda", "preprocess", "modelling", "leaderboard", "explainability", "prediction", "timeseries", "unsupervised"]},
    "scope": {"type": "object", "properties": {"artefact_ids": {"type": "array", "items": {"type": "string"}}, "model_ids": {"type": "array", "items": {"type": "string"}}}},
    "headline": {"type": "string", "maxLength": 240},
    "findings": {"type": "array", "items": {"type": "object",
      "required": ["title", "detail", "severity", "evidence"],
      "properties": {
        "title": {"type": "string"},
        "detail": {"type": "string"},
        "severity": {"enum": ["info", "low", "medium", "high", "critical"]},
        "category": {"enum": ["data_quality", "distribution", "relationship", "leakage", "imbalance", "stationarity", "performance", "overfitting", "stability", "calibration", "uncertainty", "explainability", "drift", "other"]},
        "evidence": {"type": "array", "items": {"type": "object", "required": ["ref"], "properties": {"ref": {"type": "string", "description": "fact_id or artefact_id"}, "value": {}}}},
        "plain_language": {"type": "string", "description": "math terms explained simply"}
      }}},
    "recommendations": {"type": "array", "items": {"type": "object",
      "required": ["action", "why"],
      "properties": {"action": {"type": "string"}, "why": {"type": "string"}, "target_module": {"type": "string"},
                     "apply_patch": {"type": "object", "description": "optional machine-applicable change, e.g. {recipe_step:'yeo_johnson', columns:['Income']}"},
                     "priority": {"enum": ["now", "next", "later"]}}}},
    "model_commentary": {"type": "array", "items": {"type": "object", "properties": {"model_id": {"type": "string"}, "summary": {"type": "string"}, "strengths": {"type": "array", "items": {"type": "string"}}, "weaknesses": {"type": "array", "items": {"type": "string"}}, "overfit_gap": {"type": "number"}, "fold_cv": {"type": "number"}}}},
    "ranking_rationale": {"type": "string"},
    "caveats": {"type": "array", "items": {"type": "string"}},
    "glossary": {"type": "array", "items": {"type": "object", "properties": {"term": {"type": "string"}, "explanation": {"type": "string"}}}},
    "confidence": {"enum": ["low", "medium", "high"]}
  }
}
```

### 23.5 Stage prompt templates (abridged; full text lives in `labcore/insights/prompts/*.md`, versioned)

**System (all stages):** "You are the ARW ML Lab analyst. You see chart images and a FACTS JSON. Use only numbers that appear in FACTS; cite every claim with fact_id or artefact_id in `evidence`. If an image and FACTS disagree, trust FACTS and say so. Do not give investment advice. Explain technical terms in `plain_language` for a non-specialist. Output only JSON matching the schema."

| Stage | Template focus (inputs → required content) |
|---|---|
| EDA (per artefact) | image + numbers of one plot/table → what it shows, anomalies (skew, multimodality, outliers, heaping, zero-inflation, gaps), data issues (missingness pattern MCAR/MAR hints, duplicates, leakage suspects, constant columns), implications. |
| EDA (stage summary) | all per-artefact JSONs + rule_findings + task_spec → top issues ranked by severity, **recommended preprocessing** (imputer/encoder/transform/scaler/outlier/imbalance choices with columns) as `apply_patch`, **suitable model families** and CV strategy for this data (size, dimensionality, types, sequential flag), expected pitfalls. |
| Modelling (per model) | metrics table (train, CV mean±std, test), fold scores, learning curve + validation curve images, residual/confusion/ROC images, params → performance summary, **overfitting** (train–CV gap, learning-curve convergence), **fold variance** (coefficient of variation of fold scores), bias/variance diagnosis, error structure, hyperparameter commentary, what to try next. |
| Classification evaluation | see §41.14 — 8 templates (`cm`, `report`, `curves`, `calibration`, `threshold`, `errors`, `imbalance`, `compare`) |
| Regression evaluation | see §42.8 — 6 templates (`fit`, `residuals`, `influence`, `segments`, `intervals`, `compare`) |
| Leaderboard | leaderboard table, CD diagram, statistical test results, time/size → which models are best **and why** (statistically indistinguishable groups, trade-offs score vs latency vs interpretability), recommended champion and challenger, ensemble suggestion. |
| Explainability (per model) | SHAP bar/beeswarm/dependence, PDP/ICE/ALE, permutation, LIME images + numbers → global drivers, direction & shape of effects (monotone, threshold, saturation), interactions, disagreements between methods (e.g. SHAP vs permutation under correlated features), sanity checks (leakage-looking drivers), **plain-language explanation of Shapley values, PDP vs ALE, etc.** |
| Prediction | prediction output (point, proba, sets, intervals, quantiles, confidence, OOD flag), local SHAP/LIME, calibration stats, coverage stats → what the prediction means, how certain it is (calibrated probability, interval width, conformal guarantee in words, OOD risk), what would change it (counterfactual), caveats. |
| Time series | decomposition, ACF/PACF, tests, backtest metrics by horizon, forecast fan, residual diagnostics → structure (trend/seasonality/breaks), model fit adequacy (Ljung-Box), useful horizon h*, interval reliability, regime risks. |
| Unsupervised | k-selection plots, silhouette, profiles, embeddings → how many clusters and why, cluster personas from profile table, stability, DR quality (trustworthiness, variance explained). |

### 23.6 UI

**AI Insights side panel** on every module (collapsible right column): tabs *This page* · *This panel* · *Chat*. Shows headline, findings cards with severity pills, recommendation cards with **Apply** buttons (applying `apply_patch` creates a new recipe/run version — never silent), glossary, model used + prompt version + timestamp (IST), feedback 👍/👎, regenerate (depth: brief / standard / deep), "numbers-only" badge when no vision. Each `LabPanel` has a ✦ button for a single-artefact insight. Insights are included in Reports.

### 23.7 Guardrails

Hosted calls send only aggregate plots and FACTS, never raw rows; workspace data classification controls which providers may be used (`restricted` → numbers-only) (§40.8); PII columns (detected by name/pattern) redacted from prompts; images rendered without raw row-level data where possible; prompt-injection defence (dataset cell values never placed in the instruction section; column names sanitised); numeric verification (§23.3 step 5); no financial advice disclaimers; rate limits & per-user token quotas; full audit (prompt hash, model, output) for compliance; human-in-the-loop for any "Apply"; evaluation harness with golden datasets (§28) measuring factual accuracy, citation validity and usefulness.

---

## 24. Education layer

* One typed content registry `content/explanations/*.ts` (generated partly from Python registry docstrings) keyed by `algo.*`, `metric.*`, `plot.*`, `test.*`, `enc.*`, `cv.*`, `concept.*`. Each entry: `title`, `intuitive`, `detail`, `math` (KaTeX display), `assumptions`, `when_to_use`, `pitfalls`, `hyperparameters` (meaning of each param), `complexity` (time/memory big-O), `references` (papers/books, e.g. López de Prado AFML chapters for financial items, Hyndman FPP3 for TS), `related`.
* Rendered by blackcarbon's `ExplainCard` (KaTeX, inline `\( \)` math, literature ref) inside every panel (ⓘ), in parameter forms (hover help per param), and browsable in **Learn (Logic Atlas)** — same naming as SP desks' "Logic Atlas".
* Example entries required at minimum: every algorithm in §12/§18/§19, every metric in §15/§18/§19.6, every plot in §10/§16/§18/§19.8, every test (ADF, KPSS, PP, Ljung-Box, Shapiro, JB, ARCH-LM, Granger, Johansen, Chow, CUSUM, SADF), every encoder (§11.2), every CV scheme (§13) incl. purging/embargo/CPCV/PBO diagrams.

---

## 25. Experiment tracking, registry, export, reports

* **MLflow 3:** experiment per lab experiment; run per model (nested runs for folds/trials); logs params, metrics, fold metrics, artefacts (plots JSON/PNG, OOF predictions, CV indices), dataset input (hash + schema), signature, conda/pip env; models logged as `mlflow.sklearn` / `xgboost` / `lightgbm` / `catboost` / `pytorch` / `pyfunc` (for pipelines incl. preprocessing + calibration + conformal wrapper).
* **Registry:** register → version; aliases `@champion`, `@challenger`, `@staging`; approval workflow (scientist proposes, admin approves); model card auto-generated (intended use, data, metrics, fairness slices, limitations, AI insights summary).
* **Export:** joblib/cloudpickle pipeline; ONNX (skl2onnx/onnxmltools/torch.onnx) with parity test; MLflow model; generated **Python training script** reproducing the run (recipe + estimator + CV + seed); Docker serving bundle (FastAPI + model); Excel scoring template (inputs sheet + predictions via API).
* **Reports:** builder that drags panels/insights into sections; templates: EDA report, Model report, Forecast report, Executive summary; formats PDF (WeasyPrint/Quarto, SP gold theme), HTML (interactive Plotly), DOCX, PPTX (python-pptx), XLSX (tables). Scheduled re-runs optional.

---

## 26. Security, multi-tenancy, governance

* Auth (primary, §39.5): **Supabase Auth** (email OTP / magic link with company-domain allow-list; SSO later) and Postgres **RLS** per workspace; Supabase Storage policies per workspace folder. Previous design, kept as fallback: in the Next.js BFF, SP Workstation-style email + password + OTP; OIDC SSO (Azure AD / Google Workspace) for company rollout; sessions as signed JWT (jose) in httpOnly, Secure, SameSite=Lax cookies; refresh rotation.
* RBAC: org → workspace → roles (owner/admin/scientist/analyst/viewer); row-level filtering by workspace in every query; object storage prefixes per org; presigned URLs short-lived.
* Data: encryption at rest (S3 SSE/KMS, Postgres TDE/volume encryption), TLS everywhere, PII detection and masking in previews/prompts, retention policies, dataset deletion cascades to artefacts.
* Execution safety: no user code execution in v1 (only registry-declared estimators); pickles loaded only from the lab's own artefact store (signed hashes); upload limits (size, rows), file-type validation, zip-bomb guard; Celery workers run as non-root, read-only FS except scratch, network egress blocked except to storage/DB, the hosted AI provider and the sample-dataset hosts (§46.2 OPS-14). Detailed controls: §46.3.
* Audit log for logins, uploads, runs, exports, registry changes, insight generations; admin dashboards; compliance export.
* Quotas & cost control: per-user concurrent jobs, CPU/GPU-hours per month, storage, VLM tokens.
* Secrets in Vercel / Render / GitHub Actions environment settings (Vault / K8s secrets only on the optional K8s path); never committed (SP Workstation SECURITY.md conventions).

---

## 27. Sample dataset catalogue (one-click "Load sample")

Default global seed **42** (numpy, random, torch, sklearn `random_state`, Optuna `TPESampler(seed=42)`, CV shuffles). Each sample ships with a preset (`samples/*.yaml`): task family, target(s), default inputs, CV, seed. ✔ = URL resolved HTTP 200 on 14 Nov 2026 (IST); ⬇ = downloaded into `datasets/`.

| # | Dataset | Family / task | Source URL | Target | Default inputs / notes | Seed | Status |
|---|---|---|---|---|---|---|---|
| DS1 | Iris | Sup · multiclass (3) | https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data | class | 4 numeric | 42 | ✔⬇ |
| DS2 | Breast Cancer Wisconsin (WDBC) | Sup · binary | https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.data | diagnosis | 30 numeric | 42 | ✔⬇ |
| DS3 | Titanic | Sup · binary, mixed + missing | https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv (also OpenML 40945) | Survived | Pclass, Sex, Age, SibSp, Parch, Fare, Embarked | 42 | ✔⬇ |
| DS4 | Adult (Census Income) | Sup · binary, high-card categorical, imbalance | https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data | income >50K | all 14 | 42 | ✔ |
| DS5 | German Credit (credit-g) | Sup · binary, cost-sensitive | OpenML 31 https://www.openml.org/api/v1/json/data/31 | class | 20 mixed | 42 | ✔ |
| DS6 | Credit Card Fraud | Sup · binary, extreme imbalance (0.17 %) | OpenML 1597 https://www.openml.org/api/v1/json/data/1597 | Class | V1–V28, Amount | 42 | ✔ (large, lazy-download) |
| DS7 | Bank Marketing | Sup · binary, categorical-heavy | https://archive.ics.uci.edu/static/public/222/bank+marketing.zip | y | bank-full.csv | 42 | ✔ |
| DS8 | Default of Credit Card Clients (Taiwan) | Sup · binary, finance | https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip | default payment next month | 23 | 42 | ✔ |
| DS9 | Heart Disease (Cleveland) | Sup · binary/multiclass, missing | https://archive.ics.uci.edu/static/public/45/heart+disease.zip | num (0 vs >0) | 13 | 42 | ✔⬇ |
| DS10 | Palmer Penguins | Sup · multiclass, mixed, missing; Unsup | https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv | species | bill/flipper/mass, island, sex | 42 | ✔⬇ |
| DS11 | Wine Quality (red) | Sup · regression or ordinal classification | https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv (sep=';') | quality | 11 numeric | 42 | ✔⬇ |
| DS12 | California Housing | Sup · regression | OpenML 537 (`houses`, target median_house_value); `sklearn.datasets.fetch_california_housing` | median_house_value | 8 numeric | 42 | ✔ |
| DS13 | Ames House Prices | Sup · regression, 80 mixed cols | OpenML 42165 | SalePrice (log) | all | 42 | ✔ |
| DS14 | Auto MPG | Sup · regression, small, missing | https://archive.ics.uci.edu/static/public/9/auto+mpg.zip | mpg | cyl, disp, hp, wt, acc, year, origin | 42 | ✔⬇ |
| DS15 | Concrete Compressive Strength | Sup · regression, non-linear | https://archive.ics.uci.edu/static/public/165/concrete+compressive+strength.zip (.xls) | strength | 8 numeric | 42 | ✔⬇ |
| DS16 | Bike Sharing (day/hour) | Sup · count regression; TS with exog | https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip | cnt | season, weather, temp, hum, windspeed, hr | 42 | ✔⬇ |
| DS17 | Diabetes / Digits / Wine (sklearn built-ins) | Sup · regression / multiclass | `sklearn.datasets.load_*` (bundled, offline) | — | — | 42 | bundled (no URL) |
| DS18 | Mall Customers | Unsup · clustering (k=5) | https://raw.githubusercontent.com/SteffiPeTaffy/machineLearningAZ/master/.../Mall_Customers.csv | — | Age, Annual Income, Spending Score | 42 | ✔⬇ |
| DS19 | Wholesale Customers | Unsup · clustering + anomaly, skewed | https://archive.ics.uci.edu/ml/machine-learning-databases/00292/Wholesale%20customers%20data.csv | — | 6 spend columns (log) | 42 | ✔⬇ |
| DS20 | Online Retail II | Unsup · RFM segmentation | https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip | — | derived R, F, M | 42 | ✔ (large) |
| DS21 | Credit Card Fraud (unlabelled view) | Unsup · anomaly detection with ground truth for evaluation | OpenML 1597 | (Class hidden) | V1–V28 | 42 | ✔ |
| DS22 | Airline Passengers | TS · monthly, multiplicative seasonality | https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv | Passengers | m=12, 144 obs | 42 | ✔⬇ |
| DS23 | Shampoo Sales | TS · short (36), trend | https://raw.githubusercontent.com/jbrownlee/Datasets/master/shampoo.csv | Sales | horizon-guard demo | 42 | ✔⬇ |
| DS24 | Daily Min Temperatures (Melbourne) | TS · daily, m=365 | https://raw.githubusercontent.com/jbrownlee/Datasets/master/daily-min-temperatures.csv | Temp | 3650 obs | 42 | ✔⬇ |
| DS25 | Monthly Sunspots | TS · long cycle (~11 y) | https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-sunspots.csv | Sunspots | 2820 obs | 42 | ✔⬇ |
| DS26 | Mauna Loa CO₂ (NOAA) | TS · trend + seasonality, live-updated | https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv (comment='#') | average | 823 obs | 42 | ✔⬇ |
| DS27 | US Macrodata (statsmodels) | TS · multivariate (VAR/VECM, Granger) | https://raw.githubusercontent.com/statsmodels/statsmodels/main/statsmodels/datasets/macrodata/macrodata.csv | realgdp / infl | 14 series, quarterly | 42 | ✔⬇ |
| DS28 | ETTh1 (Electricity Transformer) | TS · multivariate hourly, DL benchmark | https://raw.githubusercontent.com/zhouhaoyi/ETDataset/main/ETT-small/ETTh1.csv | OT | 6 load features | 42 | ✔⬇ |
| DS29 | Electricity Load Diagrams 2011-2014 | TS · global/multi-series (370 clients) | https://archive.ics.uci.edu/static/public/321/electricityloaddiagrams20112014.zip | per client | hierarchical demo | 42 | ✔ (large) |
| DS30 | NIFTY 50 daily (^NSEI) | Sequential financial · returns regression / triple-barrier classification / GARCH | Yahoo chart API `https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?range=5y&interval=1d` | fwd return / tb label | OHLCV → feature packs (§11.7) | 42 | ✔⬇ (1236 rows, 15 Nov 2021 → 13 Nov 2026) |
| DS31 | S&P 500 (^GSPC), NIFTY constituents (e.g. RELIANCE.NS) | Sequential financial · multi-asset, Portfolio Lab | same Yahoo endpoint with symbol | — | — | 42 | ✔ endpoint 200 (not downloaded; Yahoo terms: research use, cache locally) |
| DS32 | TradingLab bundled samples | Financial · tick/bars, labeling demos | `tradinglab/datasets/sample_loaders.py` (loaders for `data/tradinglab_sample_{tick_prices,equity_prices,dollar_bars}.csv`) | — | — | 42 | from repo |
| DS33 | Synthetic generators | All families (known ground truth) | `make_classification/regression/blobs/moons`, TradingLab `util/generate_dataset.py → get_classification_data` (informative/redundant/noise features for MDI/MDA/SFI demos), ARMA/GARCH simulators | — | — | 42 | code |

Stooq (`stooq.com/q/d/l/`) was tested and **rejected**: it now returns a JavaScript anti-bot challenge instead of CSV.

**Prediction samples (v2.2):** every dataset DS1–DS33 has a target-free prediction file in `data/samples/predict/` (35 files; DS17 has three) plus an illustrative feature contract, generated by `scripts/make_predict_samples.py` (seed 42) and referenced from the manifest and each preset. DS29 rows are schema-derived (the 260 MB archive is not downloaded), DS32 is synthetic (TradingLab is private) and DS33 is synthetic by design; all others come from the real data. Details: §45.9.

---

## 28. Testing & quality strategy

| Layer | Tests |
|---|---|
| Unit (Python, pytest) | every registry entry instantiates with defaults and with every grid point; param validation (zod ↔ pydantic schema parity generated from one source); encoders/imputers fit only on train; metrics vs reference implementations. |
| **Leakage tests** | shuffle-target test (score must collapse to chance); time-index assertion that every train index < every test index (walk-forward) and that purged train sets have no overlap with test label spans; target encoder inside-fold check; scaler fit-count spy. |
| **TradingLab contract tests** | re-run upstream `tradinglab/tests/cross_validation/test_cross_validation.py`, `test_combinatorial_cross_validation.py`, `tests/labeling/test_labels.py` (triple barrier / meta-labels) + all other `tests/labeling/test_labeling_*.py` and `test_trend_scanning_labels.py`, `tests/backtest_sampling/{test_sampling.py, test_sample_weights.py, test_backtest_statistics.py, test_backtests.py, test_bet_sizing.py, test_ef3m.py}`, `tests/features/{test_fractional_differentiation.py, test_filters.py, test_volatility_features.py, test_microstructural_features.py, test_fast_ewma.py}`; plus adapter-level tests asserting identical fold indices, labels, weights and FFD outputs to direct TradingLab calls on the bundled samples; φ(N,k) general formula equals TradingLab N−1 for k=2. |
| PBO | reproduce the Bailey et al. synthetic example (pure-noise strategies → PBO ≈ 0.5+; one true-signal strategy → PBO ≈ 0). |
| Golden datasets | DS1, DS3, DS11, DS12, DS18, DS22, DS30 with stored expected metric bands (seed 42) — regression alarms on drift beyond tolerance. |
| Horizon guard | table-driven tests over (freq, n, model) → expected h_max (e.g. airline n=144 m=12 with W=4, n_min_train=24 → h_max=24; shampoo n=36 → ≤ 9; SARIMA rejected when n < p+q+P+Q+d+mD+1). |
| Uncertainty | empirical coverage of conformal/quantile intervals on hold-out within ±3 pp of nominal (split-conformal on DS12, DS22). |
| Explainability | SHAP additivity (Σφ + base = f(x) within 1e-6 for TreeSHAP); PDP vs ICE mean consistency. |
| AI Insights | prompt-regression suite: fixed artefacts → schema-valid JSON, 100 % citation validity, 0 unmatched numbers; LLM-as-judge + human rubric on golden insights; fallback path when VLM offline. |
| Frontend | Vitest + Testing Library for components; Playwright E2E: upload → EDA → preprocess → train → leaderboard → explain → predict → report on DS3 and DS22 and DS30; visual regression of panels (light/dark); axe accessibility. |
| Performance | Locust: 50 concurrent users, 20 parallel jobs; EDA on 1 M × 50 within 60 s (sampled plots); p95 API < 300 ms. |
| Security | OWASP ZAP baseline, dependency scanning (pip-audit, npm audit), secret scanning, RBAC matrix tests. |

---

## 29. Repository / folder structure

> v2.0: the shipped project kit (`ml-lab-project/`) uses the monorepo layout in §39.6 (`frontend/`, `backend/`, `labcore/`, `supabase/`, `tests/`, `data/samples/`, `docs/`, `.cursor/rules/`, `.github/workflows/`, `render.yaml`). The tree below is the detailed target layout inside those folders; `infra/k8s` is optional (§39.12).

```
ml-lab/
├─ apps/web/                         # Next.js 16 (SP Workstation shell)
│  ├─ src/app/(auth)/login/…         # OTP login (SP pattern)
│  ├─ src/app/api/…                  # BFF route handlers: auth, RBAC, upload signing, short proxy calls (SSE goes to lab-api directly)
│  ├─ src/app/(lab)/layout.tsx       # LabShell: Sidebar + TopBar + AIInsightsPanel
│  ├─ src/app/(lab)/page.tsx         # Home Terminal
│  ├─ src/app/(lab)/{data,eda,preprocess,supervised,unsupervised,timeseries,explain,predict,experiments,reports,learn,admin}/…
│  ├─ src/components/{shell,panels,plots,forms,tables,insights,education}/
│  ├─ src/lib/{modules.ts,api.ts,sse.ts,theme.ts,schemas/}
│  ├─ src/content/explanations/      # KaTeX education registry
│  └─ src/app/globals.css            # SP tokens (gold, panel-luxe, …)
├─ services/lab-core/                # Python 3.12: FastAPI service + ML engine (Celery workers import labcore)
│  ├─ app/{routers,models,schemas,services,deps,security}/   # FastAPI "lab-core" API (§6)
│  └─ labcore/
│     ├─ data/        # ingest, typing, profiling, versioning
│     ├─ eda/         # tables (EDA.T.*) + plots (EDA.P.*)
│     ├─ preprocess/  # imputers, encoders, scalers, outliers, selection, imbalance, recipes
│     ├─ supervised/  # registry (R*, C*, S*), trainers, ensembles, DL (torch)
│     ├─ unsupervised/# D*, K*, A*
│     ├─ timeseries/  # analysis, F* models, backtest, horizon_guard.py
│     ├─ cv/          # all splitters + visualiser
│     ├─ tuning/      # Optuna/sklearn search, presets
│     ├─ finance/     # TradingLab adapters: labeling, weights, purged/cpcv, ffd, features, pbo.py, dsr.py, bet_sizing, portfolio, wfo.py (walk-forward driver, §32), costs.py, montecarlo.py
│     ├─ intake/      # detectors D1–D8, weights.yaml, merge + validator, schema diff / drift (§33)
│     ├─ explain/     # shap, lime, pdp/ice/ale, permutation, counterfactuals
│     ├─ uncertainty/ # calibration, conformal (MAPIE), quantile, ngboost, bootstrap, mc-dropout
│     ├─ insights/    # context builder, prompts/*.md, schema.json, validator, rule engine, provider client via labcore/ai (§40: NVIDIA primary, optional Gemini/OpenRouter/Groq/local OpenAI-compatible)
│     ├─ plots/       # Plotly figure factories + kaleido PNG
│     ├─ registry/    # MLflow wrappers, export (ONNX, script gen)
│     └─ reports/
├─ services/workers/                 # Celery app; queues q.ingest, q.eda, q.train.cpu, q.train.gpu, q.tune, q.explain, q.forecast, q.insights, q.report, q.predict.batch, q.predict.heavy (§3, §8)
├─ vendor/tradinglab/                # git submodule → ShibayanBiswas/ml-for-trading (pinned commit)
├─ samples/                          # dataset presets *.yaml
├─ infra/{docker-compose.yml, k8s/, helm/, grafana/}
├─ tests/{unit,contract_tradinglab,golden,e2e,load}/
└─ docs/{ARCHITECTURE.md, FLOWCHART.md, diagrams/}
```

v2.2 kit additions: `scripts/make_predict_samples.py`, `data/samples/predict/` (+ `contracts/`, `predict_manifest.json`), `docs/contracts/feature_contract.schema.json`, `docs/STRESS_TEST.md`, `tests/unit/test_predict_samples.py`, `tests/db_harness/` (Docker-free migration + pgTAP runner), `CURSOR_KICKOFF.md`.

---

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
| **8 · Deployment** (8.1 after Phase 1; 8.2 after Phase 7) | §39: render.yaml (incl. lab-beat cron), vercel.json, supabase migrations/RLS/storage, GitHub Actions CI/CD, env matrix, smoke tests; 8.2 closes §46 and `docs/STRESS_TEST.md` | §39.13 acceptance criteria; STRESS_TEST items closed |

---

## 31. Open questions & unverified items

1. **Licence/terms:** TabPFN (Prior Labs licence — check commercial terms for v2+), Gemma Terms, MiniCPM registration, Yahoo Finance data terms (research use only; prefer an NSE/vendor feed for production).
2. **VLM benchmarks** are vendor/secondary-source numbers; run the lab's own insight eval (§28) on target hardware before final model pick. Newer families (Gemma 4, Qwen 3.5/3.8) seen in one 2026 source were not verifiable.
3. **PBO / CSCV** is not in TradingLab — implemented fresh (`labcore/finance/pbo.py`); validate against the original paper's examples.
4. TradingLab known issues to patch in the adapter layer: pandas 2.x deprecations (`iteritems`), mutable `RandomState` default arguments, `num_threads` multiprocessing on Windows/Celery (force `num_threads=1` inside workers), `_get_number_of_backtest_paths` N−1 convention.
5. GPU availability for DL + VLM (shared GPU scheduling via separate `q.train.gpu` and `q.insights` queues vs dedicated VLM node).
6. Data residency: whether hosted free-tier LLMs may ever be enabled (default: never for client data).
7. Large datasets (DS6, DS20, DS29) are lazy-downloaded; sklearn built-ins (DS17) are bundled with the library rather than URL-tested.
8. TradingLab has no walk-forward driver; WFO (§32) is lab code built on TradingLab primitives. Intake family weights (§33.6) are initial values to be calibrated on a labelled corpus.
9. **TabPFN licence (re-checked Nov 2026):** v2.5+ weights are non-commercial (code Apache-2.0); TabPFN stays disabled by default (`TABPFN_ENABLED=false`) unless a commercial licence is obtained.
10. **Cursor model names** in CURSOR_PROMPT.md are deliberately generic ("strongest reasoning model in the picker"); model line-ups change monthly.
11. **Render / Vercel / Supabase plans and limits** (§39) were read from vendor pages in Nov 2026; re-check prices and limits before purchase.
12. Suitability thresholds (§37) and decision guards (§38) are initial values to be calibrated on real desk datasets.
13. **Hosted AI terms (§40.2):** the NVIDIA API catalog free key is a trial for development/testing; production use needs an NVIDIA AI Enterprise licence, a paid partner endpoint or another paid provider. Rate limits are per model and not published (~40 RPM observed). Also confirm with compliance that sending aggregate plots/metrics to NVIDIA is acceptable for each data classification.

---

## 32. Walk-Forward Optimisation (WFO) module

> Added after the user's mid-run request: "for the financial type things have all walk forward optimisations end to end". WFO is a first-class module (Supervised → **Walk-Forward**, and reused by Time Series → Backtesting). It complements CPCV (§13.2): WFO answers *"how would this research process — re-tuning and retraining on a schedule — have performed if run live through history?"* (a single, realistic path); CPCV answers *"what is the distribution of OOS performance across many paths and how likely is overfitting?"*. The lab runs both and reconciles them in one report.

### 32.1 Concepts and notation

Let observations be indexed t = 1…T. Each sample i has a label span [t0ᵢ, t1ᵢ] (`samples_info_sets` in TradingLab: index = t0, value = t1; for plain next-bar targets t1 = t0 + h).

| Symbol | Meaning | Default (daily trading data) |
|---|---|---|
| L_IS | in-sample (training + tuning) window length | 504 bars (≈ 2 trading years) |
| L_OOS | out-of-sample (test) window length | 63 bars (≈ 1 quarter) |
| s | step between consecutive windows | s = L_OOS (non-overlapping OOS, so OOS segments stitch into one continuous path) |
| g | gap between IS end and OOS start | g = max(h, feature look-ahead safety) where h = label horizon in bars |
| e | embargo after each OOS block (bars dropped from later training windows when the inner CV or retrain policy would otherwise reuse bars adjacent to tested labels) | e = ⌈0.01·T⌉ (TradingLab `pct_embargo = 0.01`) |
| mode | **anchored** (expanding: IS start fixed at t = 1) or **rolling** (sliding: IS start moves with the window) | rolling for regime-sensitive financial data; anchored when data is short |
| K | number of windows | K = ⌊(T − L_IS − g − L_OOS) / s⌋ + 1 |

Window k (k = 0…K−1):

* **Rolling:** IS_k = [1 + k·s, L_IS + k·s]; OOS_k = [L_IS + k·s + g + 1, L_IS + k·s + g + L_OOS].
* **Anchored:** IS_k = [1, L_IS + k·s]; OOS_k as above.
* **Purging (exact, label-aware):** remove from IS_k every sample i with t1ᵢ ≥ start(OOS_k) (label overlaps the test period). Implemented with TradingLab `cross_validation/time_series_cv.py → ml_get_train_times(samples_info_sets, test_times)`, where `test_times` = the OOS_k samples' t0 → t1 series. The gap g is the coarse version; purging is the exact one, and both are applied.
* **Embargo:** for rolling-with-overlap (s < L_OOS) and for inner CV inside IS, bars in (end(OOS_j), end(OOS_j) + e] are removed from training sets that come after a tested block j, exactly mirroring `PurgedKFold`'s `pct_embargo` behaviour.
* Additional variants: **multi-step OOS** (forecast horizon H > 1 for TS), **calendar-aligned windows** (re-tune on the first trading day of each month/quarter: windows defined by a pandas offset alias instead of bar counts), **anchored with decay** (expanding window but sample weights decay with age via TradingLab `sample_weights/attribution.py → get_weights_by_time_decay(triple_barrier_events, close_series, decay)`), and **event-based windows** (windows defined on CUSUM events from `filters/event_filters.py → cusum_filter`, so each window contains a fixed number of events rather than bars).

### 32.2 Window-spec configuration (one JSON drives engine, UI and report)

```json
{
  "mode": "rolling",                      // rolling | anchored | anchored_decay | calendar | event
  "is_length": 504, "oos_length": 63, "step": 63,
  "units": "bars",                        // bars | calendar (then is_length/oos_length/step are offset aliases e.g. "24M","3M","3M")
  "gap": "auto",                          // auto = max(label_horizon, max_feature_lookahead); or integer bars
  "purge": true, "pct_embargo": 0.01,
  "min_is_samples": 250, "min_oos_samples": 30,
  "retune": {"policy": "every_window", "every_k": 1, "warm_start": true, "n_trials": 40, "timeout_s": 600,
             "inner_cv": {"scheme": "purged_kfold", "n_splits": 4, "pct_embargo": 0.01},
             "objective": "sharpe_net", "robust_lambda": 0.5, "selection": "plateau"},
  "retrain": {"policy": "every_window", "every_k": 1, "calendar": null, "trigger": null, "warm_start_model": false},
  "strategy": {"signal": "proba_threshold", "threshold": 0.5, "bet_sizing": "probability", "long_short": true,
               "max_leverage": 1.0, "rebalance": "bar"},
  "costs": {"commission_bps": 3, "slippage_bps": 2, "spread_bps": "auto_half_spread", "impact": {"model": "sqrt", "k": 0.1},
            "borrow_bps_annual": 0, "stt_bps": 10, "min_ticket": 0},
  "mc": {"method": "stationary_block_bootstrap", "n_sims": 2000, "block": "auto"},
  "seed": 42
}
```

**Frequency defaults** (shown in the window designer; HorizonGuard §20 caps L_OOS for forecasting tasks):

| Data frequency | L_IS | L_OOS | step | gap default | Notes |
|---|---|---|---|---|---|
| Intraday 5-min bars | 20 trading days | 5 trading days | 5 days | h bars | session-aware boundaries (no window splits mid-session) |
| Hourly | 3 months | 2 weeks | 2 weeks | h | |
| Daily (trading) | 504 (2 y) | 63 (3 m) | 63 | h (e.g. triple-barrier vertical barrier) | NIFTY DS30 default |
| Weekly | 156 (3 y) | 13 | 13 | h | |
| Monthly | 120 (10 y) | 12 | 12 | h | macro / fund data |
| Event-based (CUSUM) | 1 000 events | 150 events | 150 events | max t1 overlap | |

Guards: K ≥ 4 required (warn < 8); OOS samples per window ≥ 30 (classification: ≥ 10 per class); total compute estimate = K × (trials × inner folds + 1) fits shown before launch, with ETA from the worker pool; IS:OOS ratio outside 3:1–12:1 triggers a hint (Pardo's practical range).

### 32.3 Per-window pipeline (inner loop)

For each window k (windows are independent given the policy, so they run as a Celery **chord** in parallel on `q.tune`/`q.train.cpu`, except when warm-starting, which forces sequential order):

1. **Slice** IS_k / OOS_k; apply gap, purge (`ml_get_train_times`), embargo.
2. **Labels:** labels were built on the full timeline (triple barrier `labeling/triple_barrier_labeling.py → get_events`, `get_bins`; or fixed-horizon / trend-scanning), but only samples whose t1 ≤ end(IS_k) are trainable — this is what purging enforces. Meta-labelling: the primary (side) model is itself trained inside IS_k.
3. **Fit preprocessing on IS_k only:** imputers/encoders/scalers; **FFD d\* re-estimated per window** (`features/fractional_differentiation.py` — the minimum d whose `frac_diff_ffd` output passes ADF at 95% on IS_k, as in `plot_min_ffd`), then applied to OOS_k with the IS weights; feature selection (incl. clustered MDA via `feature_importance/importance.py → mean_decrease_accuracy` with ONC clusters from `clustering/onc.py`) re-run per window if enabled.
4. **Sample weights on IS_k:** average uniqueness (`sampling/concurrent.py → get_av_uniqueness_from_triple_barrier`) × return attribution (`sample_weights/attribution.py → get_weights_by_return`) × optional time decay.
5. **Re-tune (if the retune policy fires):** Optuna study per window, objective evaluated with **inner purged CV** on IS_k (`PurgedKFold(n_splits=4, samples_info_sets=IS_k t1, pct_embargo)` scored through `ml_cross_val_score(..., sample_weight_train, sample_weight_score)`) or an inner walk-forward. Warm start: `study.enqueue_trial(best_params[k−1])` plus the top-5 previous trials. Objective options: net Sharpe of the inner OOS strategy, log-loss, F1, balanced accuracy, neg-RMSE, IC, custom. Robust objective = mean − λ·std over inner folds. **Selection rule:** `best` (argmax) or `plateau` (choose the trial maximising the average objective over its k-nearest neighbours in normalised parameter space — favours flat, stable optima; k = 5). Every trial's params and score are stored (needed for DSR and PBO).
6. **Train** the final model on IS_k with chosen params (or previous params if no retune this window; or reuse the previous fitted model if no retrain — see 32.4).
7. **Predict OOS_k:** point, probability, calibrated probability (calibrator fitted on the last inner fold of IS_k only), prediction intervals if regression.
8. **Strategy layer** (financial): signal → position. Options: sign of prediction; probability threshold; **bet sizing** via `bet_sizing/bet_sizing_core.py → bet_size_probability(events, prob, num_classes, pred, step_size, average_active)` (discretised, averaged over active bets) or `bet_size_dynamic` / `bet_size_budget` / `bet_size_reserve` (EF3M mixture fit via `bet_sizing/ef3m.py → M2N`); long-only / long-short; leverage cap.
9. **P&L with costs:** for position wₜ and asset return rₜ: gross = w_{t−1}·rₜ; turnover τₜ = |wₜ − w_{t−1}|; cost cₜ = τₜ·(commission + slippage + half-spread + STT/taxes) + impact; impact (sqrt model) = k·σ_daily·√(|Δq|/ADV); borrow = max(−w,0)·borrow_rate/252; **net = gross − cₜ − borrow**. Costs are parameters in bps and also run as a **cost sensitivity sweep** (0, 0.5×, 1×, 2×, 3× costs) and a **break-even cost** (cost multiple at which net Sharpe = 0).
10. **Store** per-window artefacts: params, trials, metrics IS (inner CV mean ± std) and OOS, predictions, positions, returns, feature importance, d\*, timings.

Non-financial tasks (sequential regression/classification, forecasting) skip steps 8–9 and report predictive metrics per window; the same engine powers rolling-origin TS backtests (§19.4).

### 32.4 Re-tuning and retraining schedules

| Policy key | Re-tune hyperparameters | Refit model weights | Use case |
|---|---|---|---|
| `fixed` | never (params from window 0 or user) | every window | fast; tests pure retraining value |
| `every_window` (default) | every window | every window | classic WFO |
| `every_k` | every k windows | every window | cheaper; k = 4 = yearly with quarterly OOS |
| `calendar` | on calendar boundaries (e.g. each Jan & Jul) | on calendar boundaries (e.g. monthly) | matches desk rebalancing calendars |
| `performance_trigger` | when rolling OOS Sharpe (window 63) < threshold or drops by > X% vs IS | when triggered or every window | adaptive |
| `drift_trigger` | when feature PSI > 0.2 on ≥ 20% of features or label-distribution KS p < 0.01 between IS and the latest data | when triggered | regime change |
| `frozen` | never | never (single model trained on the first IS) | baseline: decay of an un-refreshed model |

Warm start of weights: LightGBM/XGBoost `init_model` continuation, CatBoost `init_model`, PyTorch fine-tune N epochs from the previous checkpoint; otherwise cold start. The report always includes the `frozen` and `fixed` baselines alongside the chosen policy so the value of re-tuning is measured, not assumed.

### 32.5 Stitched OOS results

* **Stitched OOS series:** concatenate OOS_0 … OOS_{K−1} predictions (non-overlapping when s = L_OOS; when s < L_OOS overlapping predictions are averaged or the latest-model rule is applied, user choice) → one continuous out-of-sample prediction, position, gross and net return series.
* Equity curve, drawdown and every metric below are computed on the stitched series (headline) and per window (stability).
* Benchmarks on the same OOS dates: buy-and-hold, the `frozen` model, a random-signal model with equal turnover, and (classification) the always-majority predictor.

### 32.6 Metrics

**Walk-forward diagnostics**

| Metric | Formula / definition | Library |
|---|---|---|
| Walk-forward efficiency (return) — Pardo | WFE = (annualised OOS return) / (annualised IS return); IS return measured on the inner-CV OOS of the chosen config, not the in-sample fit. Rule of thumb shown in ExplainCard: WFE ≥ 0.5 acceptable, ≥ 0.6 good; > 1 suspicious (check regime) | TradingLab (strategy_metrics) / numpy |
| WFE (Sharpe) | WFE_SR = SR_OOS / SR_IS per window and pooled | TradingLab (strategy_metrics) / numpy |
| IS→OOS degradation | Δ = metric_IS − metric_OOS per window; slope of OOS on IS across windows (regression, like the PBO degradation plot) | TradingLab / numpy |
| Profitable windows | share of windows with net OOS return > 0; binomial test vs 50% | TradingLab / numpy |
| Consistency | std of per-window OOS Sharpe; worst window; longest losing window streak | TradingLab (strategy_metrics) / numpy |
| Parameter stability | per hyperparameter: coefficient of variation across windows (numeric), mode share (categorical); **normalised parameter distance** d_k = ‖θ̃_k − θ̃_{k−1}‖₂ / √p on [0,1]-scaled params; Kendall τ of trial rankings between consecutive windows; share of windows whose chosen params lie inside the global plateau | pandas / numpy |
| Optimisation surface flatness | per window: (best − median of top-10% trials) / \|best\|; small = robust optimum | optuna trials (thin) |
| Predictive (per window & stitched) | regression: RMSE, MAE, R², IC (Spearman), hit rate; classification: accuracy, balanced accuracy, F1, ROC-AUC, log-loss, Brier, ECE | see §41 / §42 libraries |

**Financial metrics (stitched net and gross, plus per window)** — computed with TradingLab `backtest_statistics/strategy_metrics.py`: `sharpe_ratio(returns, entries_per_year, risk_free_rate)`, `information_ratio(returns, benchmark, entries_per_year)`, `probabilistic_sharpe_ratio(observed_sr, benchmark_sr, number_of_returns, skewness_of_returns, kurtosis_of_returns)`, `deflated_sharpe_ratio(observed_sr, sr_estimates, number_of_returns, skewness_of_returns, kurtosis_of_returns, ...)`, `minimum_track_record_length(...)`, `drawdown_and_time_under_water(returns, dollars)`, `bets_concentration`, `all_bets_concentration`, `average_holding_period`, `timing_of_flattening_and_flips`; plus lab-computed CAGR, annualised vol, Sortino, Calmar, max drawdown, Ulcer index, VaR/CVaR 95/99, hit ratio, profit factor, payoff ratio, expectancy, turnover (annualised), cost drag (gross − net, bps/yr), exposure (time in market), capacity estimate (AUM at which impact halves the Sharpe). Haircut Sharpe and profit hurdle with `backtest_statistics/campbell.py → CampbellBacktesting.haircut_sharpe_ratios(...)` and `.profit_hurdle(...)` (Bonferroni, Holm, BHY, average), with N = total configurations tried.

**DSR in WFO:** the number of trials N = Σ_k (trials in window k) (every configuration evaluated anywhere is a trial — the honest count); V[SR_n] is the variance of the annualised Sharpe across all trials' inner-OOS strategies; the observed SR is the stitched OOS SR. Reported: PSR(0), PSR(SR_benchmark), DSR, MinTRL at 95%.

### 32.7 PBO and CPCV links

* **PBO from WFO (CSCV):** build matrix **M** (T_OOS × C) whose columns are the stitched OOS net returns of C candidate configurations. To get comparable columns, each window evaluates a **shared candidate set**: the union of the top-n trials from every window (n = 10, default, capped at C = 50) re-scored on every OOS window (cheap: train once per window per candidate). Then `labcore/finance/pbo.py` runs CSCV with S = 16 blocks → PBO, logit distribution, degradation slope, probability of loss (§13.2 item 6). Report flags PBO > 0.2 (amber) / > 0.5 (red).
* **CPCV cross-check:** the same pipeline (recipe + model family + tuning budget) is also run with `cross_validation/combinatorial.py → CombinatorialPurgedKFold(n_splits=N, n_test_splits=k, samples_info_sets, pct_embargo)` to obtain φ(N,k) backtest paths. The WFO stitched Sharpe is drawn as a vertical line on the CPCV path-Sharpe distribution; its percentile is reported. A WFO path in the top 10% of the CPCV distribution with high PBO ⇒ "lucky path" warning.
* **Champion rule (financial):** stitched net DSR > 0.95 **and** PBO < 0.2 **and** WFE ≥ 0.5 **and** ≥ 60% profitable windows **and** MC p-value (32.8) < 0.05; otherwise the model is labelled "research only".

### 32.8 Monte Carlo and bootstrap of OOS results

| Method | What it answers | Implementation |
|---|---|---|
| Stationary block bootstrap (Politis-Romano) of stitched net returns | CI for Sharpe, CAGR, max DD, Calmar | `arch.bootstrap.StationaryBootstrap`; mean block length by Politis-White automatic selection (`arch.bootstrap.optimal_block_length`); n_sims = 2 000; seed 42 |
| Trade/bet resampling (with replacement) and trade-order shuffling | distribution of max drawdown and time under water given the same bets | thin wrapper: `numpy.random.Generator` resampling of TradingLab bets (`timing_of_flattening_and_flips` boundaries) |
| Signal-permutation test (Monte Carlo permutation) | is the edge distinguishable from chance? p-value = share of permuted-signal Sharpe ≥ observed | permute positions within each window (preserves exposure & turnover), 1 000 sims |
| Random-entry benchmark | same holding periods, random direction | thin wrapper over TradingLab metrics (`numpy.random.Generator`, seed 42) |
| White's Reality Check / Hansen SPA (optional, Thorough) | data-snooping-robust test across all candidate configs | `arch.bootstrap.SPA` |
| Parameter perturbation | sensitivity of OOS Sharpe to ±10/20% param jitter | re-score OOS with jittered params, 200 sims |
| Probability of ruin / of hitting a drawdown limit | risk sizing | from bootstrap paths: P(maxDD > limit) |

### 32.9 Plots (all interactive; each an artefact with numbers for AI Insights)

| ID | Plot | Library |
|---|---|---|
| WFO.P.TIMELINE | Window timeline (Gantt): IS (ink), purged (hatched red), gap (grey), embargo (amber), OOS (gold) per window; hover shows dates and sample counts | TradingLab splits → Plotly |
| WFO.P.EQUITY | Stitched OOS equity curve (net and gross) with window boundaries, benchmark and frozen-model overlay — lightweight-charts | TradingLab → lightweight-charts |
| WFO.P.UNDERWATER | Drawdown / time-under-water of stitched net returns | TradingLab drawdown |
| WFO.P.IS_OOS_BARS | Per-window IS (inner-CV) vs OOS metric bars (Sharpe or chosen metric) with WFE line on secondary axis | TradingLab strategy_metrics |
| WFO.P.WFE | WFE per window + pooled, with 0.5 / 1.0 reference lines | thin (OOS/IS ratio) |
| WFO.P.IS_OOS_SCATTER | IS vs OOS metric scatter per window with regression line (degradation slope) | TradingLab strategy_metrics |
| WFO.P.PARAM_HEATMAP | **Parameter stability heatmap**: rows = hyperparameters, columns = windows, colour = normalised value; categorical params as discrete colours | optuna / pandas |
| WFO.P.PARAM_DRIFT | **Parameter drift lines**: chosen value per window per param, with trial-distribution ribbons (IQR of top-10% trials) | pandas |
| WFO.P.PARAM_DIST | Normalised parameter distance d_k per window + Kendall τ between consecutive windows | pandas |
| WFO.P.SURFACE_GRID | Small multiples: 2D objective contour (two most important params by fANOVA) per window, chosen point marked | optuna.visualization (contour) |
| WFO.P.ROLLING | Rolling Sharpe / IC / hit rate (window 63) over stitched OOS | TradingLab / pandas rolling |
| WFO.P.MONTHLY | Monthly net-return heatmap (year × month) | pandas resample |
| WFO.P.RET_DIST | Distribution of OOS returns vs normal, with skew/kurtosis (inputs to PSR/DSR) | scipy.stats |
| WFO.P.MC_FAN | Monte Carlo equity fan (5/25/50/75/95 percentiles) with observed path | arch.bootstrap (StationaryBootstrap) |
| WFO.P.MC_HIST | Histograms of bootstrapped Sharpe and max DD with observed marker and CI; permutation-test null distribution with p-value | arch.bootstrap |
| WFO.P.COSTS | Cost decomposition per window (commission, slippage, spread, impact, borrow) + cost-sensitivity curve (net Sharpe vs cost multiple, break-even marked) | TradingLab |
| WFO.P.TURNOVER | Turnover and exposure per window | TradingLab |
| WFO.P.FI_DRIFT | Feature-importance drift heatmap (features × windows; MDA/SHAP) | TradingLab MDA / shap |
| WFO.P.DSTAR | FFD d\* per window (if FFD used) | TradingLab FFD |
| WFO.P.PBO | PBO logit histogram + IS-vs-OOS degradation (from 32.7) | TradingLab (thin PBO/CSCV wrapper) |
| WFO.P.CPCV_VS_WF | CPCV path-Sharpe distribution with the WFO stitched Sharpe marked | TradingLab CPCV |
| WFO.P.PER_WINDOW_DIAG | Per-window predictive diagnostics: confusion matrix / calibration (classification), residuals / pred-vs-actual (regression), selected via window slider | see §41 / §42 libraries |
| WFO.P.REGIME | Stitched equity with regime shading (volatility terciles from `get_daily_vol`, or structural breaks from `structural_breaks/sadf.py → get_sadf`) and per-regime metrics | TradingLab get_daily_vol |
| WFO.P.POLICY_COMPARE | Equity curves of retrain/retune policies side by side (chosen vs fixed vs frozen vs every_k) | TradingLab |

### 32.10 Summary tables

**Per-window table (WFO.T.WINDOWS):** window #, IS start–end, OOS start–end, n_IS (after purge), n_purged, n_embargo, d\*, retuned? (Y/N), retrained? (Y/N), chosen params (compact), inner-CV metric mean ± std, OOS predictive metric, OOS gross return, OOS net return, OOS Sharpe (net), max DD, turnover, cost drag (bps), WFE, param distance d_k, trials, fit time.

**Summary table (WFO.T.SUMMARY):** windows K, mode, L_IS/L_OOS/step/gap/embargo, policy; stitched: CAGR, vol, Sharpe (gross/net), Sortino, Calmar, max DD, time under water, hit ratio, profit factor, turnover, cost drag, break-even cost multiple; WFE (return, Sharpe), % profitable windows (+ binomial p), degradation slope; parameter-stability score (1 − mean d_k); PSR(0), **DSR** (N trials), MinTRL, Campbell haircut Sharpe (BHY), **PBO**, MC Sharpe 95% CI, permutation p-value, CPCV percentile; verdict badge (Champion-eligible / Research only) with the failing rule(s).

### 32.11 AI Insights for WFO

Stage `wfo` (prompt `labcore/insights/prompts/wfo.md`). FACTS include every summary-table value, per-window rows, policy comparison, MC/permutation results, PBO, DSR, CPCV percentile; images: WFO.P.EQUITY, WFO.P.IS_OOS_BARS, WFO.P.PARAM_HEATMAP, WFO.P.PARAM_DRIFT, WFO.P.MC_HIST, WFO.P.COSTS (map-reduce if more). The template asks for: (1) is the edge real (DSR, permutation p, PBO, MC CI)? (2) robustness over time (WFE, % profitable windows, worst windows and their dates/regimes); (3) parameter stability (which params drift, whether drift tracks regimes, plateau vs spike optima); (4) cost sensitivity (break-even multiple vs realistic costs for the instrument); (5) retraining value (chosen policy vs frozen/fixed); (6) recommendations as `apply_patch` (e.g. lengthen L_IS, switch to `every_k`, narrow search space for unstable params, add regularisation, raise threshold to cut turnover). Extra schema fields for this stage: `"wfo_verdict": {"eligible": bool, "failed_rules": [string]}`, `"unstable_params": [string]`, `"weak_windows": [{"window": int, "evidence": [ref]}]`. Validator enforces that every cited window index exists and every number matches FACTS. Disclaimer: research output, not investment advice.

### 32.12 API endpoints

| Method & path | Purpose |
|---|---|
| `POST /api/v1/wfo/plan {experiment_id, spec}` | Validate spec, return windows (dates, counts after purge/embargo), K, compute estimate, guard warnings — no training (drives the live timeline preview) |
| `POST /api/v1/wfo/runs {experiment_id, recipe_id, algorithms:[{key, mode, params, search_space}], spec}` → `202 {job_id, wfo_run_id}` | Launch (chord of window jobs + aggregate job) |
| `GET /api/v1/wfo/runs/{id}` | Status, spec, summary table, verdict |
| `GET /api/v1/wfo/runs/{id}/windows` ; `GET /api/v1/wfo/runs/{id}/windows/{k}` | Per-window rows; one window's params, trials, metrics, artefacts |
| `GET /api/v1/wfo/runs/{id}/stitched?series=pred\|position\|gross\|net\|equity` | Stitched OOS series (Parquet/JSON) |
| `GET /api/v1/wfo/runs/{id}/params` | Parameter matrix (windows × params) + stability metrics |
| `POST /api/v1/wfo/runs/{id}/montecarlo {methods, n_sims, block}` | Run/refresh MC & bootstrap |
| `POST /api/v1/wfo/runs/{id}/costs {costs, multiples}` | Re-price with different costs without retraining (positions are stored) |
| `POST /api/v1/wfo/runs/{id}/pbo {top_n, S}` ; `POST /api/v1/wfo/runs/{id}/cpcv-compare {N, k}` | PBO from shared candidate set; CPCV cross-check |
| `POST /api/v1/wfo/compare {wfo_run_ids}` | Policy / model comparison |
| `GET /api/v1/wfo/runs/{id}/artefacts/{artefact_id}` | Plot/table envelope |
| `GET /api/v1/wfo/runs/{id}/events` (SSE) | Per-window progress, partial stitched curve as windows finish |
| `POST /api/v1/insights {scope:"wfo", ids:[wfo_run_id]}` | AI Insights |
| `POST /api/v1/wfo/runs/{id}/promote` | Train final model on the latest IS window with the latest params → registry (with WFO report attached to the model card) |

### 32.13 Database tables (added to §7)

```sql
CREATE TABLE wfo_runs (
  id UUID PRIMARY KEY, experiment_id UUID REFERENCES experiments(id), recipe_id UUID REFERENCES recipes(id),
  algorithm_key TEXT NOT NULL, spec JSONB NOT NULL, status TEXT NOT NULL, n_windows INT,
  summary JSONB, verdict JSONB, dsr DOUBLE PRECISION, pbo DOUBLE PRECISION, wfe DOUBLE PRECISION,
  seed INT DEFAULT 42, data_hash TEXT, lib_versions JSONB, mlflow_run_id TEXT,
  created_by UUID REFERENCES users(id), created_at TIMESTAMPTZ DEFAULT now(), finished_at TIMESTAMPTZ);
CREATE TABLE wfo_windows (
  id UUID PRIMARY KEY, wfo_run_id UUID REFERENCES wfo_runs(id) ON DELETE CASCADE, k INT NOT NULL,
  is_start TIMESTAMPTZ, is_end TIMESTAMPTZ, oos_start TIMESTAMPTZ, oos_end TIMESTAMPTZ,
  n_is INT, n_purged INT, n_embargoed INT, n_oos INT, d_star DOUBLE PRECISION,
  retuned BOOL, retrained BOOL, params JSONB, inner_cv JSONB, oos_metrics JSONB, fin_metrics JSONB,
  param_distance DOUBLE PRECISION, fit_seconds DOUBLE PRECISION, model_uri TEXT, UNIQUE (wfo_run_id, k));
CREATE TABLE wfo_trials (            -- every configuration evaluated (honest trial count for DSR / PBO)
  id BIGSERIAL PRIMARY KEY, wfo_window_id UUID REFERENCES wfo_windows(id) ON DELETE CASCADE,
  trial_no INT, params JSONB, inner_scores DOUBLE PRECISION[], objective DOUBLE PRECISION, state TEXT);
CREATE TABLE wfo_series (            -- stitched + per-window series stored as Parquet in S3, indexed here
  wfo_run_id UUID REFERENCES wfo_runs(id) ON DELETE CASCADE, kind TEXT, uri TEXT, PRIMARY KEY (wfo_run_id, kind));
CREATE TABLE wfo_mc_results (
  id UUID PRIMARY KEY, wfo_run_id UUID REFERENCES wfo_runs(id) ON DELETE CASCADE, method TEXT, n_sims INT,
  params JSONB, result JSONB, created_at TIMESTAMPTZ DEFAULT now());
CREATE INDEX ON wfo_windows (wfo_run_id, k);
```

Artefacts (plots/tables) go in the existing `artefacts` table with `scope = 'wfo'` and `owner_id = wfo_run_id`.

### 32.14 UI — Supervised → Walk-Forward (also linked from Time Series → Backtesting)

Sub-pages (SP rhythm): **Home · Designer · Runs (live) · Results · Parameters · Robustness · Costs · Compare · Intel (Logic Atlas)**.

```
┌ Walk-Forward ─────────────────────────────────────────────────────────────────┬ AI Insights ┐
│ [Designer]  mode (rolling|anchored|anchored-decay|calendar|event)  IS 504  OOS 63  step 63 │ verdict    │
│             gap auto(=h 10)  purge ☑  embargo 1%  retune: every window  trials 40   │ findings   │
│             inner CV: purged k=4   objective: net Sharpe  selection: plateau      │ apply ▶    │
│             costs: comm 3 bps · slip 2 · spread auto · impact sqrt k=0.1 · STT 10 │            │
│ ── live timeline preview (WFO.P.TIMELINE) — K = 15 windows · est. 12 min ──────── │            │
│ [Results]  KPI tiles: net Sharpe · DSR · PBO · WFE · % profitable · max DD · cost drag      │
│            stitched equity (lightweight-charts) │ IS vs OOS bars + WFE line                   │
│            per-window table (WFO.T.WINDOWS) — click a row → per-window drawer (diagnostics) │
│ [Parameters] stability heatmap │ drift lines │ surface small multiples                       │
│ [Robustness] MC fan │ bootstrap/permutation histograms │ PBO │ CPCV vs WF │ regimes          │
│ [Costs] decomposition │ sensitivity curve with break-even                                    │
└──────────────────────────────────────────────────────────────────────────────┴─────────────┘
```

Each panel: ⓘ ExplainCard (math for WFE, purging, embargo, DSR, PBO, block bootstrap), ✦ insight, export PNG/CSV.

### 32.15 Mapping to ml-for-trading (TradingLab)

TradingLab has **no walk-forward splitter or WFO driver** (its `backtest_statistics/backtests.py` is a deprecated alias of `campbell.CampbellBacktesting`, and `docs/source/implementations/backtesting.md` covers the Campbell & Liu haircut only). The lab therefore implements the WFO driver in `labcore/finance/wfo.py` and **reuses TradingLab for every building block**:

| WFO step | TradingLab file → function |
|---|---|
| Label spans / purging at window boundary | `cross_validation/time_series_cv.py → ml_get_train_times(samples_info_sets, test_times)` |
| Inner CV for per-window tuning | `cross_validation/time_series_cv.py → PurgedKFold(n_splits, samples_info_sets, pct_embargo)`, `ml_cross_val_score(classifier, X, y, cv_gen, sample_weight_train, sample_weight_score, scoring)` |
| Single purged IS/OOS split (K = 1 sanity mode) | `cross_validation/time_series_cv.py → PurgedSplit` |
| CPCV cross-check | `cross_validation/combinatorial.py → CombinatorialPurgedKFold` |
| Events / labels | `filters/event_filters.py → cusum_filter`; `util/volatility.py → get_daily_vol`; `labeling/triple_barrier_labeling.py → add_vertical_barrier, get_events, get_bins` |
| Weights | `sampling/concurrent.py → get_av_uniqueness_from_triple_barrier`; `sample_weights/attribution.py → get_weights_by_return, get_weights_by_time_decay` |
| Per-window stationarity | `features/fractional_differentiation.py → frac_diff_ffd, plot_min_ffd` |
| Per-window feature importance / selection | `feature_importance/importance.py → mean_decrease_impurity, mean_decrease_accuracy, single_feature_importance`; `clustering/onc.py → get_onc_clusters` |
| Sequential bagging model option | `ensemble/sb_bagging.py → SequentiallyBootstrappedBaggingClassifier/Regressor` |
| Position sizing | `bet_sizing/bet_sizing_core.py → bet_size_probability, bet_size_dynamic, bet_size_budget, bet_size_reserve`; `bet_sizing/ef3m.py → M2N` |
| Strategy statistics | `backtest_statistics/strategy_metrics.py → sharpe_ratio, information_ratio, probabilistic_sharpe_ratio, deflated_sharpe_ratio, minimum_track_record_length, drawdown_and_time_under_water, bets_concentration, average_holding_period, timing_of_flattening_and_flips` |
| Multiple-testing haircut | `backtest_statistics/campbell.py → CampbellBacktesting` |
| Regimes | `structural_breaks/sadf.py → get_sadf`; `structural_breaks/cusum.py`, `chow.py` |
| Multi-instrument (futures rolls, baskets) | `multi_product/etf_trick.py → ETFTrick, get_futures_roll_series` |
| Lab-new | WFO driver, window planner, policies, stitching, costs model, WFE, parameter stability, MC/bootstrap (via `arch.bootstrap`), PBO (`labcore/finance/pbo.py`) |

### 32.16 Tests / acceptance (also in CURSOR_PROMPT Phase 5A)

* Window planner property tests (hypothesis): no OOS overlaps another OOS when s = L_OOS; every IS index < every OOS index; after purging no IS label span intersects [start(OOS_k), end(OOS_k)]; embargo removes ⌈pct·T⌉ bars; K matches the closed form.
* Purging parity: lab purge equals `ml_get_train_times` output exactly on TradingLab sample data and DS30.
* Synthetic known-edge series (AR(1) signal + noise): WFE ≈ 1 and DSR significant; pure-noise features: permutation p > 0.1, PBO ≥ 0.4, DSR not significant.
* Cost model: doubling costs on a fixed position series reduces net return by exactly the computed cost drag; break-even multiple solves net Sharpe = 0 within 1e-3.
* Re-pricing costs without retraining reproduces a full re-run bit-for-bit.
* Trial count N in DSR equals the row count of `wfo_trials`.

---

## 33. AI Dataset Intake / Auto-Setup

> Added after the user's mid-run request: "when the dataset is updated it can identify the index and all, infer whether it is a time-series problem, sequential or non-sequential, and filter out the columns to select as features and targets". The Intake runs on every upload and every new version. It **proposes** a complete task setup, with a confidence score and reasons for every decision. **The user always confirms**: the user still chooses the family, and the AI only pre-selects it. This section extends §9, which holds the base type rules.

### 33.1 Pipeline

```
upload / new version / sample load
  └─▶ q.ingest: parse → Parquet → column profiles (§9 + extended stats below)
        └─▶ q.eda (light): detectors D1–D8 (deterministic, fast, always available)
              └─▶ q.insights: LLM adjudicator (optional; text LLM or VLM) → proposal JSON
                    └─▶ validator (hard rules win) → intake_proposals row
                          └─▶ UI: Intake Review screen (editable) → user confirms → task_spec saved on experiment
                                └─▶ downstream: EDA target sections, preprocessing auto-policy, CV default, HorizonGuard
```

The detectors produce **scores and evidence**. The LLM may re-rank and explain, within bounds (33.9). It can never introduce a column that does not exist, and it can never override a hard rule, such as using a constant column, an exact target duplicate or an ID column as a feature. When no LLM is reachable, the proposal comes from the detectors alone and is labelled "rule-based".

### 33.2 Extended column profile (input to all detectors)

For each column, the profile records:
- **Basic counts:** dtype (physical and semantic), n, n_missing, n_unique, unique ratio, top-10 values with frequencies, min, max, mean, std, quantiles, skew, kurtosis.
- **Value-type rates:**
  - share of integer-valued numbers;
  - share of values that parse as datetime, and with which format;
  - share in a plausible epoch range (s/ms/µs/ns between 1990-01-01 and 2100-01-01);
  - share in the Excel serial range 20 000–80 000.
- **Ordering:** monotonic-increasing fraction (share of consecutive non-decreasing pairs) and the share of strictly increasing pairs.
- **Text shape:** mean string length, mean token count, regex hits (email, phone, PAN `[A-Z]{5}[0-9]{4}[A-Z]`, Aadhaar-like 12 digits, IFSC, UUID, hex hash, ISIN `[A-Z]{2}[A-Z0-9]{9}[0-9]`, ticker-like `^[A-Z.&-]{1,15}$`).
- **Name tokens:** snake/camel case split and lower-cased.
- **Relation to other columns:** correlation (or Cramér's V) with every other column, capped at 200 columns via sampling.

Row-level profile:
- duplicate rows;
- candidate key sets (single columns, and pairs with a unique ratio of 1);
- row order versus each datetime candidate.

### 33.3 D1 — Index / datetime detection

**Candidates:** a column is a candidate if any of these holds:
- native datetime dtype;
- string parse rate ≥ 95%;
- integer in the epoch range;
- integer in the Excel serial range **and** the name hints at time;
- composite columns: `year` + `month` [+ `day`], `date` + `time`, `yyyymm` integers, `period` strings such as `2024Q1` or `Jan-24`;
- the pandas index stored in a Parquet file.

**Format disambiguation:**
- dd/mm versus mm/dd: decided by values > 12 in either position. If neither position ever exceeds 12, the column is "ambiguous", the confirm UI asks the user, and the default is the locale setting (India → dd/mm).
- Two-digit years use a pivot of 50.
- Time zones: offsets are parsed; naive values are assumed to be in the workspace zone (Asia/Kolkata by default).

**Score per candidate:**

time_score = 0.30·parse_rate + 0.20·monotonic_fraction + 0.15·uniqueness_ratio(within entity) + 0.15·regularity (33.4) + 0.10·name_hint + 0.10·position_hint (first column / index)

- name_hint = 1 if the name matches `^(date|time|timestamp|datetime|dt|ds|period|month|year|as_?of|trade_?date|obs(ervation)?_?date|day|week|quarter)$` or contains `date`/`time`; otherwise 0.
- **Accept** as the time index when the score is ≥ 0.6 and it is the highest candidate.
- **Ambiguous** when two candidates are within 0.1 of each other, for example `order_date` and `ship_date`. The user picks. Leakage hint: a later-event date, such as `ship_date` after `order_date`, is suggested as a leakage suspect when the target relates to that event.

**Panel detection:** a datetime has duplicates while some column E makes (E, time) unique, with E having 2 ≤ n_unique ≤ n/3. E is then proposed as the **entity/series ID** (`unique_id`). Typical cases are ticker, store_id, customer_id and sensor.

**Index-like integer:** strictly increasing by 1 with no other meaning (row number) → role `row_id`, excluded. A trivial time index such as `t = 1..n` is offered as a time index only if no datetime candidate exists and the user selects Time Series.

### 33.4 D2 — Frequency inference

1. Sort by (entity, time) and take the unique time stamps per entity.
2. Try `pandas.infer_freq` on a ≤ 10k sample. On failure, take the **mode of time differences** Δ.
3. Compute regularity = share of Δ equal to the mode (within a tolerance of 1% of the mode, or 1 second).
4. **Business-day / trading-calendar test:**
   - Weekend share ≈ 0 and Δ ∈ {1 day, 3 days}: frequency `B`.
   - The remaining gaps are compared with exchange calendars (`exchange_calendars`: XNSE/XBOM for India, XNYS, …). If ≥ 90% of the missing business days are exchange holidays, the frequency is labelled "trading days (XNSE)".
5. **Intraday:** the mode Δ is in minutes. The session window is detected from the time-of-day distribution, e.g. 09:15–15:30 IST for NSE. Bars are labelled "5-min session bars".
6. **Irregular / event data:** regularity < 0.6 → frequency "irregular". The Intake suggests resampling to a regular grid (with an aggregation rule per column role: last for price, sum for volume, mean otherwise), or event-based sampling for ticks (TradingLab bars, §11.7).
7. **Outputs:**
   - freq alias, regularity, n_missing_timestamps, duplicated stamps, first/last date, span;
   - **seasonality candidates m:** from the frequency table (§20), confirmed by ACF peaks/periodogram on the most "target-like" numeric column (≥ 2 cycles required).

### 33.5 D3 — Column role inference

Each column gets one primary role with a confidence (softmax over rule scores) and optional tags.

| Role | Detection rules (any strong rule or ≥ 2 weak rules) | Default action |
|---|---|---|
| `time_index` | D1 accepted | sort key; not a feature (calendar features optional) |
| `entity_id` | D1 panel rule; or name in {ticker, symbol, isin, store, sku, customer_id, account, series, unique_id} with low/medium cardinality | group column: GroupKFold or TS global model `unique_id` |
| `row_id` | unique ratio = 1, and (int monotone +1, or UUID/hash pattern, or name `id`, `*_id`, `index`, `unnamed: 0`) | excluded |
| `target_candidate` | see 33.6 | ranked list |
| `feature_numeric` / `feature_categorical` / `feature_ordinal` / `feature_boolean` | §9 type rules | feature, with suggested encoder/scaler |
| `datetime_feature` | a datetime that is not the index | expand to calendar features or durations (e.g. days since) |
| `price_open/high/low/close/adj_close` | names (`open`, `high`, `low`, `close`, `adj close`, `ltp`, `price`, `nav`); high ≥ max(open, close) and low ≤ min(open, close) in ≥ 99% of rows | price block → financial feature packs; raw price never a direct target (33.6) |
| `volume` | name `volume`/`vol`/`qty`/`turnover`; non-negative integer-like; heavy right skew | volume features; log1p |
| `return` | name `ret`/`return`/`pct_change`; mean ≈ 0, mostly in \|x\| < 0.2 | candidate target (sequential) |
| `exog_known_future` | calendar/holiday flags, promotions, planned price; the user confirms | TS exogenous (future known) |
| `exog_past_only` | other numeric series in TS | lagged only |
| `weight` | name `weight`/`w`/`sample_weight`/`exposure`; non-negative | sample_weight |
| `group` | repeated IDs not in time (patients, households) | GroupKFold |
| `text` | mean length > 30 and tokens > 5 | excluded (NLP out of scope) |
| `pii` | regex hits (email, phone, PAN, Aadhaar-like) ≥ 50% or names like `name`, `email`, `mobile`, `address` | excluded; masked in previews and prompts |
| `constant` / `near_constant` | n_unique = 1 / top-value share ≥ 99.5% | excluded (hard) |
| `duplicate_of:<col>` | identical values, or a bijective map (categorical) / Spearman = 1 with no missing (numeric) | excluded (hard), keep first |
| `high_missing` (tag) | missing ≥ 60% | excluded by default, with a "has_missing" indicator suggested |
| `leakage_suspect` (tag) | 33.8 | excluded pending user decision |

### 33.6 D4 — Problem family and task inference (with confidence)

The user still chooses the family. The Intake **pre-selects** it and shows a confidence bar for each of the four families: Time Series, Sequential supervised, Non-sequential supervised, Unsupervised.

**Evidence features x** (all in [0,1]):

| Feature | What it measures |
|---|---|
| `has_time` | D1 accepted |
| `regular` | regularity |
| `n_numeric_series` | share of numeric columns |
| `ohlcv` | price block found |
| `panel` | entity found |
| `target_named` | a target name hint exists |
| `autocorr` | Ljung-Box on the best numeric candidate at lag 10: 1 if p < 0.01 |
| `few_cols_time` | a time index plus ≤ 3 numeric columns |
| `wide_cross_section` | many mixed features and no time |
| `no_target_signal` | no target candidate scoring ≥ 0.4 |
| `row_order_time` | the row order already follows time |

**Scores** (logits; weights versioned in `labcore/intake/weights.yaml`, calibrated on a labelled corpus of ≥ 60 public datasets including DS1–DS33):

| Family | Logit |
|---|---|
| Time Series | 2.5·has_time + 1.5·regular + 1.5·few_cols_time + 1.0·autocorr − 1.0·wide_cross_section |
| Sequential supervised | 2.0·has_time + 2.0·ohlcv + 1.0·target_named + 1.0·autocorr + 0.5·panel − 0.5·few_cols_time |
| Non-sequential supervised | 2.0·target_named + 1.5·wide_cross_section − 2.0·has_time + 0.5 |
| Unsupervised | 2.0·no_target_signal + 1.0·wide_cross_section − 1.5·target_named |

Confidence = softmax(logits). The top family is pre-selected when its confidence is ≥ 0.55. Otherwise the UI shows "Please choose" with the top two families highlighted.

**Financial flag:** `ohlcv` or a return/price/ticker role → "Financial sequential". This switches the defaults to purged CV, the TradingLab label builder, and the WFO and CPCV modules.

**Within supervised:** the task type comes from the §9 rules applied to the chosen target, with confidence. For example, an integer target with 7 levels is shown as multiclass 0.6 / regression 0.4, with the reason "integer-valued, 7 levels, ordered". Imbalance is flagged.

**Time-series specifics:**
- target series (single or multiple);
- univariate vs multivariate;
- global vs local model;
- exogenous roles;
- proposed horizon h_default and h_max from HorizonGuard (§20).

### 33.7 D5 — Target and feature recommendation

**Target candidates** are ranked by:

target_score = 0.35·name_hint + 0.15·is_last_column + 0.15·type_plausibility + 0.15·predictability + 0.10·low_missing + 0.10·not_id

- **name_hint** comes from a weighted vocabulary: `target`, `label`, `y`, `class`, `outcome`, `result`, `churn`, `default`, `fraud`, `survived`, `diagnosis`, `price`, `saleprice`, `sales`, `demand`, `quantity`, `quality`, `score`, `rating`, `revenue`, `return`, `cnt`, `count`, `ot`, `passengers`, `consumption`, `load`.
- **predictability** = max mutual information (MI) from the other columns, computed quickly on a ≤ 20k sample. It is capped, so a near-perfect predictability score also raises a leakage flag rather than more confidence.
- **Financial data:** raw price levels are **never** proposed as a supervised target. The Intake instead proposes **derived targets** with their builder pre-filled:
  - forward log return over h bars;
  - direction sign(fwd return);
  - triple-barrier label (pt = sl = 2×daily vol, vertical barrier 10 bars; CUSUM threshold = 1× daily vol) via TradingLab `labeling/triple_barrier_labeling.py`;
  - trend-scanning label (`labeling/trend_scanning.py`);
  - realised volatility (for GARCH or regression).

**Features:** the Intake proposes the set "all columns with feature roles, minus every excluded role". It then annotates each feature with:
- MI and correlation ranking with the chosen target (top 30 highlighted);
- multicollinearity groups (|r| > 0.9 or VIF > 10; one representative kept per group by default);
- the suggested encoder from the §11.2 auto-policy (e.g. `city` with 312 levels → target encoding, K-fold);
- the suggested transform (skew > 1 → Yeo-Johnson);
- the suggested missing-value strategy.

For sequential/financial data it also proposes:
- feature packs (returns/lags, rolling statistics, volatility estimators, FFD);
- the required look-back;
- the auto gap for CV and WFO, equal to the label horizon.

### 33.8 D6 — Leakage suspects

Each rule produces a severity and evidence, shown in red in the Review screen. Suspects are excluded by default until the user accepts them.

| Rule | Test | Severity |
|---|---|---|
| Near-perfect single-feature predictor | regression: \|Spearman\| ≥ 0.98 or a single-feature tree R² ≥ 0.98; classification: single-feature ROC-AUC ≥ 0.99 or a depth-1 stump accuracy ≥ 0.99 | high |
| Transform of the target | exact duplicate, monotone map (Spearman = 1), linear identity (R² = 1), or arithmetic identity found by a search over pairs (y ≈ a/b, a−b, a+b, a·b with R² ≥ 0.999) | critical |
| Post-outcome name hints | `*_after`, `post_*`, `final_*`, `outcome_*`, `result*`, `settled*`, `closed_*`, `paid*`, `chargeback*`, `recovered*`, `status` (when the target is the event), `days_to_*` | medium (name only) → high when combined with a strong association |
| Later-event timestamps | a datetime column that is later than the time index in ≥ 95% of rows | high |
| Future information in sequential data | lead/lag check: corr(xₜ, yₜ) ≫ corr(xₜ₋₁, yₜ); a feature computed with centred or forward windows (correlates with y_{t+1} more strongly than any past lag); a non-causal rolling window | high |
| Row-order or ID leakage | row_id or ID correlated with the target (\|ρ\| > 0.3) in non-sequential data | medium |
| Group leakage | an entity/group repeats across rows and the target is constant within the group (≥ 90%) | medium → recommend GroupKFold |
| Duplicate rows with conflicting or identical targets | duplicate share > 1% | medium → dedupe or GroupKFold on the duplicate hash |
| Target in features after a join | the same column name with a suffix (`_x`/`_y`) | high |

### 33.9 LLM adjudicator: prompt, schema, validator

**Model:** the §40 `text_reasoning` chain (`nvidia/nemotron-3-super-120b-a12b` primary). It is text-first. When enabled, it also receives 2–4 profile images (missingness matrix, correlation heatmap, time plot of the target candidate).

**Input:**
- the profile JSON per column;
- detector outputs with scores and evidence;
- dataset name and file name;
- **no raw rows**, except up to 5 sanitised example values per non-PII column, truncated to 32 characters.

Column names are passed as data inside a JSON array, never inside instructions, because they could carry prompt-injection text.

**Prompt (`labcore/insights/prompts/intake.md`, abridged):**

> System: "You are the ARW ML Lab data-intake assistant. You receive a JSON profile of a tabular dataset and deterministic detector results. Propose the time index, entity column, frequency, problem family, task type, target(s), feature set, excluded columns with reasons, and leakage suspects. Use only column names present in `columns[].name`. You may change a detector decision only if you cite profile evidence; you must not use any column tagged `hard_exclude` as a feature or target. Give each decision a confidence in [0,1] and one-sentence reasons a non-specialist understands. Output only JSON matching the schema."
>
> User: `{"dataset": {...}, "columns": [...], "detectors": {...}, "rules_version": "intake-1.0"}`

**Output JSON schema:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["time_index", "family", "targets", "features", "excluded", "confidence_overall"],
  "properties": {
    "time_index": {"type": ["object", "null"], "properties": {
        "column": {"type": "string"}, "format": {"type": "string"}, "timezone": {"type": "string"},
        "composite_of": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1}, "reasons": {"type": "array", "items": {"type": "string"}}}},
    "entity_column": {"type": ["object", "null"], "properties": {"column": {"type": "string"}, "confidence": {"type": "number"}, "reasons": {"type": "array", "items": {"type": "string"}}}},
    "frequency": {"type": ["object", "null"], "properties": {"alias": {"type": "string"}, "calendar": {"type": "string"}, "regularity": {"type": "number"}, "seasonal_periods": {"type": "array", "items": {"type": "number"}}, "confidence": {"type": "number"}}},
    "family": {"type": "object", "required": ["proposed", "scores"], "properties": {
        "proposed": {"enum": ["time_series", "supervised_sequential", "supervised_non_sequential", "unsupervised"]},
        "financial": {"type": "boolean"},
        "scores": {"type": "object", "properties": {"time_series": {"type": "number"}, "supervised_sequential": {"type": "number"}, "supervised_non_sequential": {"type": "number"}, "unsupervised": {"type": "number"}}},
        "reasons": {"type": "array", "items": {"type": "string"}}}},
    "task": {"type": ["object", "null"], "properties": {"type": {"enum": ["regression", "binary", "multiclass", "multilabel", "multioutput_regression", "forecast_univariate", "forecast_multivariate", "forecast_global"]}, "confidence": {"type": "number"}, "alternatives": {"type": "array", "items": {"type": "object", "properties": {"type": {"type": "string"}, "confidence": {"type": "number"}}}}, "reasons": {"type": "array", "items": {"type": "string"}}}},
    "targets": {"type": "array", "items": {"type": "object", "required": ["column", "confidence"], "properties": {
        "column": {"type": "string"}, "derived": {"type": ["object", "null"], "description": "e.g. {builder:'triple_barrier', params:{...}} for financial targets"},
        "confidence": {"type": "number"}, "reasons": {"type": "array", "items": {"type": "string"}}}}},
    "features": {"type": "array", "items": {"type": "object", "required": ["column", "role"], "properties": {
        "column": {"type": "string"}, "role": {"type": "string"}, "encoder": {"type": "string"}, "transform": {"type": "string"},
        "imputer": {"type": "string"}, "rank": {"type": "integer"}, "confidence": {"type": "number"}}}},
    "excluded": {"type": "array", "items": {"type": "object", "required": ["column", "reason_code"], "properties": {
        "column": {"type": "string"}, "reason_code": {"enum": ["row_id", "constant", "near_constant", "duplicate", "text", "pii", "high_missing", "leakage_suspect", "time_index", "entity_id", "other"]},
        "detail": {"type": "string"}}}},
    "leakage_suspects": {"type": "array", "items": {"type": "object", "properties": {"column": {"type": "string"}, "rule": {"type": "string"}, "severity": {"enum": ["medium", "high", "critical"]}, "evidence": {"type": "object"}}}},
    "cv_recommendation": {"type": "object", "properties": {"scheme": {"type": "string"}, "params": {"type": "object"}, "reason": {"type": "string"}}},
    "horizon": {"type": ["object", "null"], "properties": {"h_default": {"type": "integer"}, "h_max": {"type": "integer"}}},
    "questions_for_user": {"type": "array", "items": {"type": "string"}},
    "confidence_overall": {"type": "number", "minimum": 0, "maximum": 1}
  }
}
```

**Validator checks** (any failure → one repair round, then fall back to the detectors' proposal):
1. Every column name exists.
2. Roles come from the enum.
3. Hard rules are not overridden.
4. A family change versus the detectors is allowed only if the LLM's confidence − the detector's confidence ≤ 0.15 **and** reasons cite evidence; otherwise the detector's family is kept and the LLM's view is shown as an "alternative".
5. Confidences lie in [0,1].
6. h_max ≤ the HorizonGuard value.
7. Derived financial targets must use a supported builder.

### 33.10 Intake Review UI (Data → Intake Review; opens automatically after upload)

```
┌ Intake Review — nifty50_daily_5y.csv (v3) ───────────────────────────── AI-proposed · confidence 0.87 ┐
│ Family  [Time Series 0.18] [Sequential supervised 0.74 ★ Financial] [Non-sequential 0.05] [Unsup 0.03]│
│ Time index: Date (format %Y-%m-%d, Asia/Kolkata) 0.98 · Frequency: trading days XNSE, regularity 0.99 │
│ Entity: — · Seasonal periods: 5, 21, 252                                                              │
│ Target: ⦿ triple-barrier label (pt=sl=2σ, vertical 10)  ○ fwd log-return h=1  ○ direction  ○ custom   │
│ ┌ Columns ──────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ ☑ name │ role ▾ │ type │ missing │ MI rank │ encoder ▾ │ transform ▾ │ flags │ why (hover)          │ │
│ │ Close   price_close  float  0%  —   —   FFD (d*)  …                                                │ │
│ │ Volume  volume       int    0%  4   —   log1p     …                                                │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│ ⚠ Leakage suspects (0) · Excluded (1: Adj Close duplicate_of Close)                                   │
│ CV: Purged K-fold k=5, embargo 1% · WFO preset: rolling 504/63/63 · CPCV N=6 k=2                      │
│ Questions: none                                                                                       │
│ [Accept all]  [Accept & open EDA]  [Reset to rule-based]  [Compare with previous version]            │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Every cell is editable: role dropdown, include checkbox, encoder/transform overrides, and target choice. Edits are stored as `user_overrides` and used as feedback to calibrate the weights. Each decision has an "ⓘ why" popover listing detector evidence and LLM reasons. Keyboard: `A` accept, `R` reset.

### 33.11 Dataset updates: schema drift and versioning

**Update modes:** `append` (new rows, same schema), `replace` (full new file), `upsert` (by key: time index + entity, or a declared key). Each update creates an immutable **dataset_version** with a parent pointer (lineage). The content hash (xxh3 of Parquet row groups) avoids duplicates.

**Schema diff (D7) against the parent version:**

| Change | Detection | Severity |
|---|---|---|
| Column added / removed | set difference | info / breaking if used by the task or a registered model |
| Column renamed | removed + added pair with name similarity (Jaro-Winkler ≥ 0.85) **and** distribution similarity (KS p > 0.05 numeric / Jensen-Shannon < 0.1 categorical) → proposed rename mapping | warning (user confirms the mapping) |
| Type change | semantic type differs (e.g. numeric → categorical, parse-rate drop) | breaking |
| New category levels | levels not seen in the parent (share of rows) | warning when > 1% of rows |
| Range change | min/max beyond parent ± 3 IQR | warning |
| Distribution drift (D8) | PSI per column (10 quantile bins of the parent), KS (numeric), χ² (categorical) on overlapping columns; PSI > 0.1 amber, > 0.25 red | warning |
| Missingness change | Δ missing share > 10 pp | warning |
| Time-index issues | overlap with the parent's range (append mode), new gaps, frequency change, duplicated stamps, out-of-order rows | breaking (overlap/dup) / warning |
| Target change | target distribution drift; new classes | warning/breaking |

**Actions:**
1. Re-run the Intake on the new version and compare it with the confirmed spec of the parent.
2. If compatible (no breaking changes), carry the task spec forward automatically and show the "Drift report" badge.
3. If breaking, require re-confirmation in the Review screen with the diff highlighted.
4. Notify the owners of experiments and registered models that use the dataset. The model **schema contract** check (input signature vs new columns and types) runs, and an **impact list** is shown (EDA to refresh, models to retrain, WFO to extend with new windows: append mode adds the new OOS windows incrementally).
5. Optional auto-actions per workspace policy: re-run EDA, retrain champions, extend WFO, refresh forecasts (scheduled through Celery beat).

### 33.12 API endpoints

| Method & path | Purpose |
|---|---|
| `POST /api/v1/datasets/{id}/versions {mode: append\|replace\|upsert, upload_ref, key?}` → `202 {job_id, version_id}` | New version + automatic intake |
| `POST /api/v1/intake/{version_id}/run {use_llm: bool, depth}` → `202 {job_id}` | (Re)run detectors + LLM |
| `GET /api/v1/intake/{version_id}` | Latest proposal (detector output, LLM output, merged proposal, validator report) |
| `GET /api/v1/intake/{version_id}/events` (SSE) | Progress + streamed LLM reasoning summary |
| `PATCH /api/v1/intake/{proposal_id} {overrides}` | Save user edits |
| `POST /api/v1/intake/{proposal_id}/confirm {experiment_name?}` → `{experiment_id, task_spec}` | Confirm → create/update the experiment |
| `GET /api/v1/datasets/{id}/versions/{v}/diff?against={parent\|v}` | Schema diff + drift report |
| `GET /api/v1/datasets/{id}/lineage` | Version graph |
| `GET /api/v1/datasets/{id}/impact?version={v}` | Affected experiments/models/WFO runs + suggested actions |
| `POST /api/v1/intake/feedback {proposal_id, accepted, overrides}` | Calibration feedback |

### 33.13 Database tables (added to §7)

```sql
CREATE TABLE intake_proposals (
  id UUID PRIMARY KEY, dataset_version_id UUID REFERENCES dataset_versions(id) ON DELETE CASCADE,
  rules_version TEXT NOT NULL, llm_model TEXT, prompt_version TEXT,
  detector_output JSONB NOT NULL, llm_output JSONB, merged JSONB NOT NULL, validator_report JSONB,
  status TEXT NOT NULL DEFAULT 'proposed',          -- proposed | edited | confirmed | superseded
  user_overrides JSONB, confirmed_by UUID REFERENCES users(id), confirmed_at TIMESTAMPTZ,
  confidence_overall DOUBLE PRECISION, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE column_roles (
  proposal_id UUID REFERENCES intake_proposals(id) ON DELETE CASCADE, column_name TEXT,
  role TEXT, confidence DOUBLE PRECISION, tags TEXT[], reasons JSONB, included BOOL, encoder TEXT, transform TEXT,
  PRIMARY KEY (proposal_id, column_name));
CREATE TABLE schema_diffs (
  id UUID PRIMARY KEY, dataset_id UUID REFERENCES datasets(id), from_version_id UUID, to_version_id UUID,
  changes JSONB NOT NULL, drift JSONB, severity TEXT, breaking BOOL, created_at TIMESTAMPTZ DEFAULT now());
ALTER TABLE dataset_versions ADD COLUMN parent_version_id UUID REFERENCES dataset_versions(id),
  ADD COLUMN update_mode TEXT, ADD COLUMN content_hash TEXT, ADD COLUMN row_count BIGINT;
CREATE TABLE intake_feedback (
  id BIGSERIAL PRIMARY KEY, proposal_id UUID REFERENCES intake_proposals(id), accepted BOOL, overrides JSONB,
  created_by UUID REFERENCES users(id), created_at TIMESTAMPTZ DEFAULT now());
```

### 33.14 Expected Intake results on sample datasets (golden tests)

| Dataset | Expected proposal |
|---|---|
| DS3 Titanic | family non-sequential supervised (≥ 0.7); target `Survived` binary; `PassengerId` row_id; `Name` text/PII → excluded; `Ticket` high-cardinality; `Cabin` high_missing (77%) |
| DS12 California Housing | non-sequential; target `median_house_value` regression |
| DS18 Mall Customers | unsupervised (top); `CustomerID` row_id; `Gender` categorical |
| DS22 Airline | time series (≥ 0.8); index `Month` monthly; m = 12; target `Passengers`; h_max 24 |
| DS24 Daily min temperatures | time series; daily; m = 7 and 365.25 candidates |
| DS27 Macrodata | time series multivariate; composite index `year` + `quarter` → quarterly |
| DS28 ETTh1 | time series; hourly; target `OT`; others exog past-only |
| DS30 NIFTY 50 | sequential supervised, financial (≥ 0.7); trading days XNSE; OHLCV roles; raw `Close` not a target; derived triple-barrier target proposed |
| Synthetic leak | a column `y_copy = 2·y + 1` flagged critical (linear identity); `ship_date` after `order_date` flagged |

---

## 34. Deep Learning — full specification (tabular and sequential)

> Round-2 expansion. This section supersedes the short DL rows in §12 (R43–R51, C33–C35, S2–S10). It covers every architecture, its math, its hyperparameters with defaults and search spaces, the training engine, the DL-specific plots and tables, uncertainty, and CPU/GPU handling.
>
> Libraries: PyTorch 2.x + Lightning 2.x as the common engine; `pytorch-tabular` for CategoryEmbedding (MLP), GANDALF, GATE, NODE, TabNet, AutoInt, DANet, FT-Transformer, TabTransformer and MDN; ResNet-MLP, DCN-v2 and SAINT are optional/off by default (no maintained library compatible with numpy 2 / scikit-learn 1.9, §43.4); `tabpfn` (licence-gated); sequential models are composed from built-in `torch.nn` layers plus `pytorch-tcn`, `pytorch-forecasting` and `neuralforecast` (§43.3); `neuralforecast` for TS DL (§35).

### 34.1 Common building blocks and notation

| Block | Math | Notes | Library |
|---|---|---|---|
| Dense layer | h = φ(Wx + b) | φ ∈ {ReLU, GELU, SiLU/Swish, Mish, LeakyReLU(0.01), ELU, SELU, Tanh} | torch.nn.Linear |
| Categorical embedding | e_j = E_j[c_j], E_j ∈ ℝ^{\|C_j\|×d_j} | default d_j = min(50, ⌈(\|C_j\|+1)/2⌉) (pytorch-tabular rule); `embedding_dropout` | torch.nn.Embedding (pytorch-tabular) |
| Numeric embedding | piecewise-linear encoding PLE(x) with quantile bins, or periodic (sin/cos with learned frequencies) — Gorishniy et al. 2022 | improves MLP/Transformer on numeric features | pytorch-tabular / thin torch.nn |
| BatchNorm | x̂ = (x − μ_B)/√(σ²_B + ε); y = γx̂ + β | Ghost BN (virtual batch) for TabNet | torch.nn.BatchNorm1d |
| LayerNorm | normalise over features per sample | Transformers, RNN outputs | torch.nn.LayerNorm |
| Dropout | h ⊙ m / (1 − p), m ~ Bernoulli(1 − p) | also used for MC dropout at inference | torch.nn.Dropout |
| Residual block | x + Dropout(Linear(φ(Linear(Norm(x))))) | ResNet-MLP, Transformers | torch.nn (composition) |
| Multi-head attention | Attn(Q,K,V) = softmax(QKᵀ/√d_k)V; heads concatenated → W_O | FT-Transformer, SAINT, AutoInt, sequence Transformer | torch.nn.MultiheadAttention |
| Sparsemax / Entmax | projection of logits onto the simplex (sparse weights) | TabNet masks, NODE choice functions | pytorch-tabular (bundled entmax) |
| GLU | GLU(x) = (W₁x) ⊙ σ(W₂x) | TabNet feature transformer, GANDALF GFLU | torch.nn.GLU |

**Losses.**

| Loss | Formula | Library |
|---|---|---|
| MSE | (1/n)Σ(y − ŷ)² | torch.nn.MSELoss |
| MAE / L1 | (1/n)Σ\|y − ŷ\| | torch.nn.L1Loss |
| Huber (δ) | ½r² if \|r\| ≤ δ else δ(\|r\| − ½δ) | torch.nn.HuberLoss |
| Log-cosh | Σ log cosh(r) | thin (torch ops) |
| Quantile / pinball (τ) | Σ max(τr, (τ−1)r) — multi-quantile heads give prediction intervals | neuralforecast / pytorch-forecasting QuantileLoss |
| Gaussian NLL | ½ log σ² + (y − μ)²/(2σ²) — heteroscedastic regression (μ, σ heads) | torch.nn.GaussianNLLLoss |
| Poisson / Tweedie NLL | count or zero-inflated targets | torch.nn.PoissonNLLLoss; Tweedie: pytorch-forecasting TweedieLoss |
| Cross-entropy | −Σ_c y_c log p_c; label smoothing ε replaces y with (1−ε)y + ε/C | torch.nn.CrossEntropyLoss |
| Weighted CE | class weights w_c = n / (C·n_c) ("balanced") or user-set | torch.nn.CrossEntropyLoss(weight=…) |
| Focal loss (γ, α) | −α(1−p_t)^γ log p_t — for heavy imbalance | thin (torch ops; standard formula) |
| BCE-with-logits | multi-label | torch.nn.BCEWithLogitsLoss |
| Ordinal (CORAL/CORN) | ordinal targets | optional thin (torch ops) |
| Sharpe-style differentiable loss (financial, optional) | −mean(w·r)/std(w·r) on positions w = tanh(f(x)) | thin (torch ops, TradingLab formula) |

**Optimisers.** Adam, AdamW (default), RAdam, NAdam, SGD + Nesterov momentum, Adagrad, RMSprop, Lion; optional Lookahead wrapper. Update for AdamW: m ← β₁m + (1−β₁)g; v ← β₂v + (1−β₂)g²; θ ← θ − η(m̂/(√v̂ + ε) + λθ).

**LR schedules.**

| Schedule | Formula / behaviour | Library |
|---|---|---|
| Constant | η | torch.optim.lr_scheduler |
| Step / MultiStep | η·γ^{⌊epoch/s⌋} | torch.optim.lr_scheduler.StepLR / MultiStepLR |
| Exponential | η·γ^t | torch.optim.lr_scheduler.ExponentialLR |
| Cosine annealing (+ warm restarts) | η_min + ½(η − η_min)(1 + cos(πt/T)) | torch.optim.lr_scheduler.CosineAnnealingWarmRestarts |
| One-cycle (default for MLPs) | warm-up to η_max over 30% of steps, then cosine down to η_max/10⁴ | torch.optim.lr_scheduler.OneCycleLR |
| Linear warm-up + cosine (default for Transformers) | linear for warm-up steps (5% of total), then cosine | torch.optim.lr_scheduler (LinearLR + CosineAnnealingLR via SequentialLR) |
| ReduceLROnPlateau | multiply η by `factor` (0.5) after `patience` (5) epochs without val improvement | torch.optim.lr_scheduler.ReduceLROnPlateau |
| Polynomial decay | η(1 − t/T)^p | torch.optim.lr_scheduler.PolynomialLR |
| LR finder | Smith range test: exponentially increase η from 1e-7 to 1; choose η at the steepest loss descent (or min-loss/10); used when `lr = "auto"` | lightning Tuner.lr_find |

**Regularisation.** Weight decay λ, dropout, embedding dropout, batch/layer norm, early stopping, gradient clipping (norm 1.0), mixup/cutmix for tabular (optional), stochastic weight averaging (SWA, optional), label smoothing.

**Imbalance.** Class weights (balanced), focal loss, weighted random sampler, oversampling inside the training fold only (SMOTE before DL only via `imblearn` pipeline), threshold tuning on validation.

### 34.2 Training engine (one engine for every DL model)

* `labcore/supervised/dl/engine.py` wraps a `LightningModule` with: seed control (`seed_everything(42, workers=True)`, `torch.use_deterministic_algorithms(True)` when "reproducible" is on, cuDNN deterministic), device selection, mixed precision (`bf16-mixed` on Ampere+ GPUs, `16-mixed` on older CUDA, `32-true` on CPU), gradient accumulation, gradient clipping, early stopping (monitor `val_loss` or the primary metric, `patience` 10, `min_delta` 1e-4, restore best weights), model checkpointing (best + last), LR monitor, and a metrics logger that writes per-epoch values to MLflow **and** to the artefact store (for plots and the VLM).
* Validation: an inner validation slice of the training fold only (random 15% for i.i.d.; the last 15% in time for sequential, with a gap equal to the label horizon). Never the CV test fold.
* Inputs: the preprocessing recipe still runs (§11) but DL defaults change: numeric → quantile-normal or standard scaling (DL needs scaled inputs); categoricals → integer codes for embeddings (instead of one-hot) with an "unknown" index 0; missing → mean/median imputation + missing-indicator columns.
* Batch sampler: shuffled for i.i.d.; ordered windows for sequential (shuffle windows within the training fold only — they are already causal).
* Callbacks for diagnostics (every N = 1 epoch, sampled): gradient global norm per layer, weight and activation histograms (every 5 epochs), learning-rate trace, throughput, GPU memory.
* Hard limits: max epochs by preset (Quick 30 / Balanced 100 / Thorough 300), wall-clock timeout per trial (Quick 2 min, Balanced 10 min, Thorough 30 min, configurable), Optuna pruning (`PyTorchLightningPruningCallback` with `HyperbandPruner`) on intermediate validation scores.

### 34.3 Tabular deep-learning architectures

| ID | Model | Architecture and math (summary) | Library | Best for |
|---|---|---|---|---|
| T1 | **MLP** (CategoryEmbedding) | embeddings ⊕ numeric → L × [Linear → (BN) → φ → Dropout] → head | pytorch-tabular `CategoryEmbeddingModelConfig` | baseline |
| T2 | **ResNet-MLP** | x₀ = Linear(input); x_{l+1} = x_l + Dropout(Linear(Dropout(φ(Linear(BN(x_l)))))) ; head = Linear(φ(BN(x_L))) — Gorishniy et al. 2021 | **optional, off by default** (no maintained library compatible with the stack, §43.4) | strong baseline |
| T3 | **TabNet** | N_steps sequential decision steps; attentive transformer gives mask M_i = sparsemax(P_{i−1} ⊙ h_i(a_{i−1})), prior P_i = Π(γ − M_j); feature transformer (shared + step GLU blocks); output = Σ ReLU(d_i); sparsity loss λ_sparse·Σ M log M — Arık & Pfister 2021 | pytorch-tabular `TabNetModelConfig` | interpretable masks |
| T4 | **FT-Transformer** | feature tokenizer T_j = b_j + x_j W_j (numeric) / b_j + e_j (categorical); prepend [CLS]; L Transformer blocks (PreNorm MHSA + FFN with ReGLU); prediction from [CLS] — Gorishniy et al. 2021 | pytorch-tabular `FTTransformerConfig` | strong general DL |
| T5 | **TabTransformer** | Transformer only over categorical embeddings (column embedding added), numeric features layer-normed and concatenated to the contextual embeddings → MLP — Huang et al. 2020 | `TabTransformerConfig` | categorical-heavy |
| T6 | **SAINT** | row (inter-sample) attention + column self-attention per block; optional contrastive pre-training (CutMix + mixup in embedding space) — Somepalli et al. 2021 | **optional, off by default** (no maintained library compatible with the stack, §43.4) | mid-size data, semi-supervised |
| T7 | **NODE** | ensembles of differentiable oblivious decision trees: feature choice via entmax over features, threshold comparisons with entmoid; layers densely connected — Popov et al. 2020 | `NodeConfig` | GBDT-like DL |
| T8 | **AutoInt** | embeddings → stacked multi-head self-attention interacting layers with residual connections → learns high-order feature interactions — Song et al. 2019 | `AutoIntConfig` | interactions |
| T9 | **DCN-v2** | cross layer x_{l+1} = x₀ ⊙ (W_l x_l + b_l) + x_l (full-rank or low-rank mixture-of-experts W) stacked/parallel with a deep MLP — Wang et al. 2021 | **optional, off by default** (no maintained tabular library, §43.4) | explicit crosses (credit scoring) |
| T10 | **GANDALF** | Gated Feature Learning Units (GFLU): learnable feature mask (t-softmax) + GRU-like gating over several stages → simple head — Joseph & Raj 2022 | `GANDALFConfig` | efficient, interpretable |
| T11 | **GATE** | GFLU feature learning + ensemble of differentiable non-linear trees re-weighted with self-attention | `GatedAdditiveTreeEnsembleConfig` | |
| T12 | **DANet** | abstract layers (AbstLay) that group correlated features with learnable sparse masks; stacked basic blocks with shortcut | `DANetConfig` | |
| T13 | **TabPFN** | prior-fitted Transformer: in-context learning; train rows + test rows go in one forward pass; no gradient training. Limits (by version): v2 10k rows / 500 features / 10 classes; v2.5 50k / 2k / 10; newer versions larger (GPU). **Licence: TabPFN-2.5 and later weights are non-commercial**; v2 weights use the Prior Labs licence → disabled by default in the company deployment; admin can enable for research/evaluation only | `tabpfn` | small data, strong zero-tuning baseline |
| T14 | **Mixture Density Network (MDN)** | backbone → K-component Gaussian mixture (π_k, μ_k, σ_k); NLL loss; full predictive distribution | `MDNConfig` | multimodal regression |
| T15 | **Stacked DL** | concatenation of several backbones (e.g. NODE + GANDALF) → head | `StackingModelConfig` | ensembles |
| T16 | **Self-supervised pre-training** (optional) | denoising autoencoder / contrastive pre-training on all rows (including unlabelled) → fine-tune | pytorch-tabular SSL | few labels |

### 34.4 Sequential deep-learning architectures (supervised on windows)

Input: windows X_t = [x_{t−L+1}, …, x_t] ∈ ℝ^{L×p} (lookback L), target y_{t+h} (or a sequence for multi-output). Windows are built after the train/validation/test split so no window crosses a boundary (plus the gap).

| ID | Model | Equations / design | Key options | Library |
|---|---|---|---|---|
| Q1 | **Vanilla RNN** | h_t = tanh(W_x x_t + W_h h_{t−1} + b) | layers, hidden, nonlinearity | torch.nn.RNN + lightning |
| Q2 | **LSTM** | i,f,o = σ(W·[h_{t−1}, x_t] + b); c̃ = tanh(…); c_t = f⊙c_{t−1} + i⊙c̃; h_t = o⊙tanh(c_t) | layers 1–4, hidden 16–512, dropout between layers, forget-gate bias 1.0 | torch.nn.LSTM + lightning |
| Q3 | **GRU** | z,r = σ(…); h̃ = tanh(W[r⊙h_{t−1}, x_t]); h_t = (1−z)⊙h_{t−1} + z⊙h̃ | as LSTM | torch.nn.GRU + lightning |
| Q4 | **BiLSTM / BiGRU** | forward and backward passes concatenated. **Only valid when the whole window is in the past** (it never sees beyond t) — guard prevents use with future-leaking windows | | torch.nn.LSTM/GRU(bidirectional) + lightning |
| Q5 | **Stacked LSTM + attention** | additive (Bahdanau) α_t = softmax(vᵀ tanh(W h_t + U s)) or dot-product attention over hidden states; context = Σ α_t h_t | attention type, attention dim | torch.nn.LSTM + nn.MultiheadAttention |
| Q6 | **1D-CNN** | Conv1d stacks (kernel k, channels C, stride, dilation) + pooling (max/avg/global) → dense | kernels 2–9, channels 16–256 | torch.nn.Conv1d + lightning |
| Q7 | **TCN** | causal dilated convolutions, dilation d = 2^l, residual blocks with weight norm + dropout; receptive field R = 1 + 2(k−1)(2^L − 1) — Bai et al. 2018 | kernel 2–7, levels so R ≥ L | pytorch-tcn |
| Q8 | **CNN-LSTM** | Conv1d feature extractor → LSTM → dense | | torch.nn.Conv1d + nn.LSTM |
| Q9 | **Transformer encoder** | linear input projection + sinusoidal or learned positional encoding; causal mask; L blocks (MHSA + FFN, PreNorm); pooling = last token / mean / [CLS] | d_model 32–256, heads 2–8, layers 1–6, FFN 2–4×d_model | torch.nn.TransformerEncoder |
| Q10 | **Informer-style / PatchTST-style encoder** | patching (patch length P, stride S) → Transformer over patches; channel independence | patch 8–32 | neuralforecast (PatchTST/Informer) |
| Q11 | **TFT (for supervised windows)** | variable-selection networks, gated residual networks, LSTM encoder, interpretable multi-head attention, quantile outputs | via neuralforecast/pytorch-forecasting | pytorch-forecasting / neuralforecast TFT |
| Q12 | **xLSTM / Mamba-style SSM** (optional, Thorough) | sLSTM/mLSTM blocks; selective state-space scan | GPU only | xlstm / mamba-ssm (optional GPU) |
| Q13 | **Sequentially-bootstrapped DL bagging** | K networks trained on TradingLab `sampling/bootstrapping.py → seq_bootstrap` samples (uniqueness-aware) | financial | TradingLab sequential bootstrap + lightning |

### 34.5 Hyperparameters, defaults and search spaces

Every row is a `ParamSpec` (§14.2): "Use defaults" = Default column; "Customise" = any value; tuning uses the Balanced search space (Thorough widens ranges by about 2× on log scales).

**Shared training hyperparameters (all DL models)**

| Param | Default | Balanced search space |
|---|---|---|
| optimiser | AdamW | {AdamW, Adam, RAdam, SGD-Nesterov} |
| learning_rate | 1e-3 (or `auto` = LR finder) | log-uniform [1e-5, 1e-2] |
| weight_decay | 1e-5 | log-uniform [1e-7, 1e-2] |
| lr_schedule | one-cycle (MLP/CNN/RNN), warm-up + cosine (Transformers) | {one-cycle, cosine, plateau, step, constant} |
| warmup_ratio | 0.05 | [0, 0.15] |
| batch_size | 256 (tabular), 64 (sequential) | {64, 128, 256, 512, 1024} / {16, 32, 64, 128} |
| max_epochs | 100 (Balanced) | fixed by preset; early stopping decides |
| early_stopping_patience | 10 | {5, 10, 20} |
| gradient_clip_norm | 1.0 | {0.5, 1, 5, none} |
| dropout | 0.1 | [0, 0.5] |
| embedding_dropout | 0.0 | [0, 0.3] |
| activation | ReLU (MLP), GELU (Transformers) | {ReLU, GELU, SiLU, Mish, LeakyReLU} |
| normalisation | BatchNorm (MLP), LayerNorm (Transformers, RNN) | {BN, LN, none} |
| loss | MSE (regression), CE (classification) | regression {MSE, Huber δ∈[0.1,10], L1, quantile}; classification {CE, weighted CE, focal γ∈[0.5,5]} |
| class_weight | balanced if minority share < 20% | {none, balanced} |
| label_smoothing | 0.0 | [0, 0.2] |
| numeric_embedding | none | {none, PLE (bins 8–64), periodic (k 8–64)} |
| precision | auto (bf16 on GPU, fp32 on CPU) | not tuned |

**Model-specific hyperparameters**

| Model | Param: default (search space) |
|---|---|
| T1 MLP | layers: "512-256-128" ({1–5 layers}, units {32…1024} log2, funnel or constant); use_batch_norm: True |
| T2 ResNet-MLP | n_blocks 3 ([1,8]); d_main 256 ([64,512]); d_hidden_factor 2 ([1,4]); hidden_dropout 0.2 ([0,0.5]); residual_dropout 0.0 ([0,0.2]) |
| T3 TabNet | n_d = n_a 16 ({8,16,32,64}); n_steps 4 ([3,10]); γ 1.3 ([1.0,2.0]); n_independent 2 ([1,4]); n_shared 2 ([1,4]); λ_sparse 1e-3 (log [1e-6,1e-2]); virtual_batch_size 128; mask_type sparsemax ({sparsemax, entmax}); momentum 0.02 |
| T4 FT-Transformer | d_token 192 ({64,96,128,192,256}); n_blocks 3 ([1,6]); attention_heads 8 ({4,8}); attention_dropout 0.2 ([0,0.5]); ffn_factor 4/3 ([2/3, 8/3]); ffn_dropout 0.1 ([0,0.5]); residual_dropout 0.0 ([0,0.2]); lr 1e-4 (log [3e-5,1e-3]); weight_decay 1e-5 |
| T5 TabTransformer | input_embed_dim 32 ({16,32,64}); num_heads 8; num_attn_blocks 6 ([2,8]); attn_dropout 0.1; ff_dropout 0.1; out_ff_layers "128-64" |
| T6 SAINT | dim 32 ({16,32,64}); depth 6 ([1,6]); heads 8; attention type "colrow" ({col, row, colrow}); attn/ff dropout 0.1; pretrain epochs 0 ({0, 25, 50}) |
| T7 NODE | num_layers 1 ([1,4]); num_trees 512 ({256,512,1024,2048}); depth 6 ([4,8]); additional_tree_output_dim 3; choice_function entmax15; bin_function entmoid15 |
| T8 AutoInt | attn_embed_dim 32; num_heads 2 ({1,2,4}); num_attn_blocks 3 ([1,6]); attn_dropouts 0.0; has_residuals True; deep_layers False |
| T9 DCN-v2 | cross_layers 3 ([1,6]); cross_type "matrix" ({vector, matrix, low-rank r∈{16,32,64}}); structure "stacked" ({stacked, parallel}); deep "512-256" |
| T10 GANDALF | gflu_stages 6 ([2,12]); gflu_dropout 0.0; gflu_feature_init_sparsity 0.3 ([0.1,0.9]); learnable_sparsity True |
| T11 GATE | gflu_stages 6; num_trees 20 ([5,50]); tree_depth 5 ([3,8]); binning_activation entmoid; chain_trees True |
| T12 DANet | n_layers 8 ({8,20,32}); abstlay_dim_1 32; k 5; dropout_rate 0.1 |
| T13 TabPFN | n_estimators 4 (ensemble size); softmax_temperature 0.9; balance_probabilities False; no tuning |
| T14 MDN | num_gaussian 2 ([1,8]); backbone = MLP config |
| Q1–Q4 RNN/LSTM/GRU/Bi | lookback L = auto (min(3h, 60) bars; search {10,20,40,60,120}); layers 2 ([1,4]); hidden 64 ({16,32,64,128,256}); dropout 0.2 ([0,0.5]); bidirectional False (guarded); head "dense-32" |
| Q5 Attention-LSTM | as Q2 + attention {additive, dot, general}; attention_dim 64 |
| Q6 CNN-1D | conv_layers 2 ([1,4]); channels 64 ({16…256}); kernel 3 ({2,3,5,7}); pooling max; dilation 1 |
| Q7 TCN | kernel 3 ({2,3,5,7}); channels 64; levels auto (receptive field ≥ L); dropout 0.1; weight_norm True |
| Q9 Transformer | d_model 64 ({32,64,128,256}); heads 4 ({2,4,8}); layers 2 ([1,6]); ffn 4×d_model; dropout 0.1; positional "sinusoidal" ({sinusoidal, learned}); pooling "last" |
| Q10 Patch encoder | patch_len 16 ({8,16,32}); stride 8; d_model 128; layers 3; revin True |

### 34.6 DL-specific tables

| Table ID | Columns | Library |
|---|---|---|
| DL.T.ARCH | layer #, layer type, input shape, output shape, parameters, trainable (Y/N), activation, dropout — plus totals (params, trainable params, model size MB, FLOPs per sample estimate via `fvcore`/`thop`) | lightning ModelSummary |
| DL.T.HPARAMS | parameter, value used, default, search range, source (default / user / tuned), importance (fANOVA) | pytorch-tabular config / optuna |
| DL.T.EPOCHS | epoch, train loss, val loss, train metric, val metric, learning rate, grad norm (global), epoch time (s), GPU memory (MB), best-so-far flag | lightning CSVLogger |
| DL.T.EARLYSTOP | best epoch, stopped epoch, patience, monitored metric, best value, restore-best (Y/N) | lightning EarlyStopping |
| DL.T.FOLDS | fold, best epoch, val metric at best, test-fold metric, train time, epochs run | sklearn splitters + lightning |
| DL.T.TRIALS | Optuna trial, params, pruned at epoch, objective, duration, state | optuna |
| DL.T.UNCERT | row, prediction mean, std (MC dropout T passes), deep-ensemble std, epistemic share, interval [l, u], predictive entropy (classification), mutual information (BALD) | torch (MC dropout) / numpy |
| DL.T.RESOURCES | device, precision, batch size, throughput (samples/s), peak memory, total GPU/CPU seconds, cost estimate | lightning / psutil |
| DL.T.ATTENTION (Transformers/TabNet) | feature, mean attention or mask weight, std across rows, rank (global importance from TabNet masks / FT-Transformer [CLS] attention) | pytorch-tabular / pytorch-forecasting interpret outputs |

### 34.7 DL training and diagnostic plots

| Plot ID | Shows | Axes | When | Library |
|---|---|---|---|---|
| DL.P.LOSS | train vs validation loss per epoch, best epoch marked, early-stop line | x epoch, y loss (log optional) | every DL run | Plotly |
| DL.P.METRIC | train vs validation metric per epoch | x epoch, y metric | every run | Plotly |
| DL.P.LRFINDER | loss vs learning rate in the range test, suggested LR marked | x LR (log), y smoothed loss | when lr = auto | Plotly |
| DL.P.LRTRACE | learning-rate schedule actually applied | x step, y LR | every run | Plotly |
| DL.P.GRADNORM | global and per-layer gradient norms | x step, y norm (log) | every run (sampled) | Plotly |
| DL.P.WEIGHTHIST | weight / bias distributions per layer over epochs (ridgeline) | x value, y epoch | every 5 epochs | Plotly |
| DL.P.ACTHIST | activation distributions per layer; dead-ReLU share | x activation, y density | diagnostics | Plotly |
| DL.P.ATTN_FEATURE | FT-Transformer / AutoInt attention map (feature × feature or [CLS] → feature) averaged over rows; per-row attention on demand | heatmap | Transformer models | Plotly |
| DL.P.ATTN_TIME | attention over time steps for sequential attention models / TFT | x lag, y head or sample | sequential | Plotly |
| DL.P.TABNET_MASKS | TabNet step masks (rows × features) and aggregate feature importance | heatmap + bar | TabNet | Plotly |
| DL.P.EMBED | learned categorical embedding vectors projected with PCA/UMAP, coloured by target rate | 2D/3D scatter | categoricals with ≥ 10 levels | Plotly |
| DL.P.LATENT | penultimate-layer representation projected (UMAP), coloured by class/target | 2D scatter | classification | Plotly |
| DL.P.TRIALS | Optuna history, parallel coordinates, param importance, pruning epochs | standard | tuning | Plotly |
| DL.P.FOLDCURVES | loss curves of all folds overlaid | x epoch | CV | Plotly |
| DL.P.UNCERT | predictive std vs \|error\| scatter; interval coverage by bin; entropy histogram | | MC dropout / ensembles | Plotly |
| DL.P.SALIENCY | integrated gradients / gradient × input per feature (tabular) or per time step (sequential) via Captum | bar / heatmap | explainability | Captum + Plotly |
| DL.P.ARCH | architecture diagram generated from DL.T.ARCH (boxes and arrows) | diagram | every model | lightning ModelSummary → SVG |

### 34.8 Uncertainty for DL

* **MC dropout** (Gal & Ghahramani 2016): keep dropout on at inference, T = 50 passes; mean μ̂ = (1/T)Σ f_t(x), variance σ̂² = (1/T)Σ(f_t − μ̂)² (+ aleatoric σ² if a Gaussian NLL head is used); classification: predictive entropy H = −Σ p̄ log p̄ and mutual information MI = H − (1/T)Σ H(p_t).
* **Deep ensembles** (Lakshminarayanan et al. 2017): M = 5 networks with different seeds (42…46), optionally different architectures; mixture mean and variance; usually better calibrated than MC dropout.
* **Quantile heads** (pinball loss at τ ∈ {0.05, 0.5, 0.95}) and **Gaussian NLL heads**; **conformal wrapping** (§21) on top of any of these for finite-sample coverage.
* **Calibration** for classifiers: temperature scaling fitted on the inner validation slice.
* The uncertainty plots and table (DL.T.UNCERT) feed the confidence score (§21, §22).

### 34.9 CPU / GPU handling

| Situation | Behaviour |
|---|---|
| GPU worker available (`q.train.gpu`) | DL jobs routed there; mixed precision; `num_workers` = CPU cores − 1 for data loading; pinned memory |
| No GPU | CPU fallback with limits: Quick preset only for Transformers/SAINT/NODE above 50k rows; batch size raised for throughput; `torch.set_num_threads(cores)`; ETA shown and the user must confirm long jobs |
| Out-of-memory | automatic retry with batch size halved (up to 3 times), then gradient accumulation to keep the effective batch size |
| Multiple GPUs (optional) | Lightning DDP for a single large model; otherwise one trial per GPU (Optuna parallel) |
| Reproducibility mode | deterministic algorithms on; may be slower; recorded in the run |
| Model export | TorchScript and ONNX (opset 17+) with a parity test; state dict + config in MLflow |
| Hosted deployment (§39) | Render CPU workers run the Quick/Balanced presets for MLP/ResNet/TabNet/GANDALF and small sequential models; Transformers/SAINT/large TS DL are routed to an optional external GPU worker; the UI greys out GPU-only models when no GPU worker is registered |

---

## 35. Time Series — full specification (EDA, models, strategies, backtesting, metrics, diagnostics)

> Round-2 expansion. This section supersedes the summary in §19. It keeps the IDs F1–F54 and adds every hyperparameter with default and search space, the full TS EDA, multi-step strategies, exogenous handling, hierarchical/multivariate forecasting, backtesting set-ups, the complete metrics table, plots, diagnostics tables and leaderboard tables. Horizon rules remain in §20.

### 35.1 Time-series EDA (Time Series → Analysis)

**Tables**

| Table ID | Columns | Library |
|---|---|---|
| TS.T.SUMMARY | series id, start, end, n, frequency, regularity, missing timestamps, duplicates, mean, std, min, max, CV, zeros %, intermittency (ADI, CV²), trend strength F_T, seasonal strength F_S, spectral entropy, Hurst exponent, ACF₁, ACF₁₀ sum of squares | pandas |
| TS.T.STATIONARITY | test, regression spec (c / ct / n), lags (method), statistic, p-value, critical values 1/5/10%, conclusion, note. Rows: **ADF** (H₀ unit root; `statsmodels.adfuller`, autolag AIC), **KPSS** level and trend (H₀ stationary; `kpss`, nlags auto), **Phillips-Perron** (H₀ unit root; `arch.unitroot.PhillipsPerron`), **Zivot-Andrews** (H₀ unit root with one structural break; `statsmodels.zivot_andrews`, reports break date), **DF-GLS** (`arch.unitroot.DFGLS`), **variance ratio** (`arch.unitroot.VarianceRatio`), seasonal unit roots (**OCSB**, **Canova-Hansen** via pmdarima `nsdiffs`) | statsmodels (adfuller, kpss, zivot_andrews) / arch.unitroot (PhillipsPerron, DFGLS) |
| TS.T.STATIONARITY_VERDICT | combined decision matrix: ADF reject & KPSS not reject → stationary; ADF not reject & KPSS reject → unit root (difference); both reject → difference-stationary vs trend-stationary ambiguity (check ZA/break); neither → insufficient power; recommended d (`ndiffs` by ADF/KPSS/PP) and D (`nsdiffs`) | thin rule over statsmodels / arch outputs |
| TS.T.SEASONALITY | candidate period m, source (frequency / periodogram peak / ACF peak), spectral power, ACF at m, seasonal strength, accepted (Y/N) | scipy.signal / statsmodels acf / pmdarima (OCSB, CH) |
| TS.T.BREAKS | method (Chow at a given date, CUSUM / CUSUM-of-squares (`statsmodels.breaks_cusumolsresid`), Bai-Perron / PELT via `ruptures` (penalty BIC), Zivot-Andrews break, TradingLab `structural_breaks` SADF / Chu-Stinchcombe-White), break date(s), statistic, p-value / critical value, segment means and variances | statsmodels (breaks_cusumolsresid) / ruptures / TradingLab |
| TS.T.HETERO | test, statistic, p-value, conclusion. Rows: **ARCH-LM** (Engle; `het_arch`, lags 12), **Breusch-Pagan**, **White**, **Goldfeld-Quandt**, McLeod-Li (Ljung-Box on squared series) | statsmodels het_arch / het_breuschpagan |
| TS.T.NORMALITY | Jarque-Bera, Shapiro-Wilk (n ≤ 5 000), D'Agostino K², Anderson-Darling — statistic, p-value, skew, excess kurtosis | scipy.stats |
| TS.T.AUTOCORR | lag, ACF, PACF, 95% band ±1.96/√n, Ljung-Box Q and p at lags 1…max(2m, 20), Box-Pierce | statsmodels acf / pacf / acorr_ljungbox |
| TS.T.GRANGER | cause → effect, lag order (chosen by AIC up to p_max), F-statistic, p-value (ssr F-test), χ² p-value, conclusion; matrix form for all pairs (`grangercausalitytests` on stationary transforms) | statsmodels grangercausalitytests |
| TS.T.CCF | pair, lag of maximum \|cross-correlation\|, value, significance band, interpretation (leading / lagging) after pre-whitening | statsmodels ccf |
| TS.T.COINT | Engle-Granger (pair), Johansen (trace and max-eigen statistics, rank r) for multivariate sets | statsmodels coint / coint_johansen |
| TS.T.OUTLIERS | timestamp, value, method (STL residual robust z > 3.5, Hampel filter, IQR on residuals), type (additive / level shift / transient), suggested treatment | statsmodels STL + scipy (Hampel via pandas rolling median) |
| TS.T.FEATURES | tsfeatures-style table: entropy, lumpiness, stability, crossing points, flat spots, max level shift, max var shift, curvature, linearity, nonlinearity (Teräsvirta), x_acf1, diff1_acf1, seas_acf1 | tsfel / tsfresh (tsfeatures-style) |

**Plots**

| Plot ID | Shows | Axes | When | Library |
|---|---|---|---|---|
| TS.P.LINE | series with range slider, missing gaps shaded, outliers marked | time × value | always | pandas → Plotly |
| TS.P.CANDLE | OHLC candles + volume | time | OHLCV data (lightweight-charts) | pandas → lightweight-charts |
| TS.P.ROLLING | rolling mean, rolling std (and rolling quantiles), windows selectable (m, 2m, 4m) | time | always | pandas rolling |
| TS.P.DECOMP_CLASSICAL | additive / multiplicative classical decomposition (trend, seasonal, residual) | 4 stacked panels | seasonal data | statsmodels.tsa.seasonal_decompose |
| TS.P.DECOMP_STL | STL (robust, seasonal window 7/13/periodic, trend window auto) | panels | default decomposition | statsmodels.tsa.STL |
| TS.P.DECOMP_MSTL | MSTL for multiple seasonalities (e.g. 24 and 168 hourly) | panels | multiple m | statsmodels.tsa.MSTL |
| TS.P.DECOMP_X13 | X-13ARIMA-SEATS (if binary available) | panels | monthly/quarterly economic data | statsmodels x13_arima_analysis (needs X-13 binary; optional) |
| TS.P.ACF / TS.P.PACF | correlograms with confidence bands (Bartlett for ACF) | lag × correlation | always | statsmodels.tsa.stattools.acf / pacf |
| TS.P.LAG | lag scatter y_t vs y_{t−k} for k = 1…12 (small multiples) | | always | pandas shift |
| TS.P.SEASONAL | seasonal plot (one line per year/week) | season position × value | seasonal data | pandas |
| TS.P.SUBSERIES | seasonal subseries (mini line per season position with mean) | | seasonal data | pandas |
| TS.P.BOX_SEASON | box plots by month / weekday / hour | | | pandas |
| TS.P.PERIODOGRAM | periodogram and Welch spectral density, peaks annotated with period | frequency × power | always | scipy.signal.periodogram / welch |
| TS.P.SPECTROGRAM | short-time Fourier spectrogram | time × frequency | long high-frequency data | scipy.signal.spectrogram |
| TS.P.WAVELET | continuous wavelet power (optional, `pywt`) | time × scale | optional | PyWavelets (optional) |
| TS.P.HEATMAP_CAL | calendar heatmap (day-of-year × year) | | daily | pandas |
| TS.P.DIFF | series after d / D differencing and its ACF | | when non-stationary | pandas diff + statsmodels acf |
| TS.P.BOXCOX | Box-Cox λ profile (Guerrero) and transformed series | | variance grows with level | scipy.stats.boxcox / coreforecast Guerrero |
| TS.P.BREAKS | series with detected break points and segment means | | | ruptures |
| TS.P.VOLCLUSTER | r_t, \|r_t\|, r_t² and their ACFs | | returns / ARCH effects | pandas / arch |
| TS.P.QQ | Q-Q plot of the series or returns vs normal | | | statsmodels ProbPlot |
| TS.P.CCF | cross-correlation function with bands per pair | lag × correlation | multivariate | statsmodels.tsa.stattools.ccf |
| TS.P.GRANGER_HEAT | Granger p-value matrix | cause × effect | multivariate | statsmodels grangercausalitytests |
| TS.P.CORR_ROLL | rolling correlation between two series | | multivariate | pandas rolling corr |
| TS.P.MISSING | timestamp gap chart | | irregular data | pandas |

### 35.2 Forecasting families: hyperparameters, defaults and search spaces

All statistical models fit per series (local); ML and DL models can fit across series (global, with `unique_id`). The default search uses Optuna or the library's Auto* search; the user can switch any model to "Customise".

| ID(s) | Model | Hyperparameters: default (search space) | Library |
|---|---|---|---|
| F1–F4 | Naive, Seasonal naive, Drift, Window averages | season_length = m; window_size 2m ({m, 2m, 4m}) | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F5–F7 | SES, Holt (damped), Holt-Winters | α, β, γ, φ estimated by MLE (or fixed in [0,1]); trend {None, add, add-damped}; seasonal {None, add, mul}; damped True; use_boxcox {False, True, λ by Guerrero}; initialization {estimated, heuristic} | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F8 | ETS / AutoETS | model "ZZZ" (all 30 combos searched by AICc; excludes unstable mul-trend combos); damped {None→auto}; season_length m; restrict True | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F9–F12 | ARIMA / SARIMA / SARIMAX / AutoARIMA | p ∈ [0,5], d ∈ [0,2] (by KPSS/ADF), q ∈ [0,5], P ∈ [0,2], D ∈ [0,1] (by OCSB/CH), Q ∈ [0,2], m; trend {n, c, t, ct}; information criterion AICc (AIC, BIC); stepwise True (Thorough: exhaustive); approximation for n > 150; method CSS-ML; max_order 5; enforce_stationarity/invertibility True | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F13 | ARIMA + Fourier | K Fourier pairs per season ∈ [1, m/2] chosen by AICc; ARMA errors via AutoARIMA | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F14 | Theta family | theta 2 ([0.5, 3] for Optimised); decomposition_type {multiplicative, additive}; season_length m | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F15 | AutoCES | model {N, S, P, F} by AIC | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F16 | TBATS / BATS | use_box_cox auto; use_trend auto; use_damped_trend auto; seasonal_periods auto (multiple); use_arma_errors True | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F17 | MSTL | season_length list; trend_forecaster AutoETS(model "ZZN"); stl_kwargs robust True | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F18 | MFLES | seasonal_period m; max_rounds 50; changepoints True; smoother False | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F19 | UCM (structural) | level {local level, local linear trend, smooth trend, random walk w/ drift}; cycle {False, True}; stochastic seasonal {True}; freq_seasonal Fourier terms; autoregressive order 0–2 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F20 | Prophet | growth {linear, logistic, flat}; changepoint_prior_scale 0.05 (log [0.001, 0.5]); seasonality_prior_scale 10 (log [0.01, 10]); holidays_prior_scale 10; seasonality_mode {additive, multiplicative}; n_changepoints 25; changepoint_range 0.8; yearly/weekly/daily auto; country holidays "IN" (configurable); interval_width 0.8 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F21–F23 | VAR / VARMAX / VECM | maxlags by AIC (≤ 15 or 12·(n/100)^{1/4}); trend {c, ct, n}; VECM coint rank by Johansen trace (det_order 0) and k_ar_diff by AIC; VARMAX (p, q) ≤ (2, 2) | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F24 | GARCH family (arch) | vol {GARCH, EGARCH, GJR-GARCH, TARCH, FIGARCH, HARCH, APARCH}; p 1 ([1,3]), o 0/1, q 1 ([1,3]); mean {Constant, Zero, AR(l), HAR}; dist {normal, t, skewt, ged}; rescale True; returns in % | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F25 | Croston / SBA / TSB / ADIDA / IMAPA | α 0.1 ([0.05, 0.3]) for Croston-optimised; TSB α_d, α_p ([0.05, 0.3]) | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F26 | Kalman local level / state space | observation and state noise estimated by MLE | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F27 | ML with lag features (mlforecast) | models {LightGBM, XGBoost, CatBoost, RandomForest, ExtraTrees, Ridge, Lasso, KNN}; lags auto = {1…p} ∪ {m, 2m} (p by PACF cut-off, ≤ 3m); lag transforms {rolling mean/std/min/max windows (7, 14, 28 or m, 2m), expanding mean, EWM α 0.3/0.7}; date features {month, dayofweek, hour, weekofyear, is_month_end, holidays}; target transforms {Differences([1, m]), LocalStandardScaler, LocalBoxCox}; strategy {recursive, direct} (§35.3); model hyperparameters from §12 presets (LightGBM: num_leaves [15,255], lr log[0.01,0.3], n_estimators [100,2000], min_child_samples [5,100], feature_fraction [0.5,1], lambda_l1/l2 log[1e-8,10]) | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F29–F33 | RNN, LSTM, GRU, DilatedRNN, xLSTM (neuralforecast) | input_size 3h ({2h, 3h, 5h, 7h}); encoder_n_layers 2 ([1,4]); encoder_hidden_size 128 ({32,64,128,256}); decoder_hidden_size 128; decoder_layers 2; context_size 10; learning_rate 1e-3 (log [1e-4, 1e-2]); max_steps 1000 ({500…3000}); batch_size 32; scaler_type "robust" ({standard, robust, minmax, identity}); loss MAE ({MAE, MSE, MQLoss, DistributionLoss(Normal/StudentT)}) ; early_stop_patience_steps 10 with val_check_steps 100 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F34–F35 | TCN, BiTCN | kernel_size 2 ({2,3,5}); dilations [1,2,4,8,16]; encoder_hidden_size 128; context_size 10 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F36 | DeepAR | lstm_n_layers 2; lstm_hidden_size 128; lstm_dropout 0.1; distribution loss StudentT ({Normal, StudentT, NegativeBinomial}); trajectory_samples 100 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F38–F41 | MLP, N-BEATS, N-BEATSx, N-HiTS | N-BEATS: stack_types ["identity", "trend", "seasonality"] (interpretable) or generic; n_blocks [1,1,1]; mlp_units 3×[512, 512]; n_harmonics 2; n_polynomials 2. N-HiTS: n_pool_kernel_size [2,2,1] ({[2,2,2],[4,4,4],[8,4,1],[16,8,1]}); n_freq_downsample [4,2,1] ({[168,24,1],[24,12,1],[1,1,1]}); mlp_units 3×[512,512]; dropout 0.0; interpolation_mode linear | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F42 | DLinear / NLinear | moving_avg_window 25 ({7, 13, 25}) | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F43 | TiDE | hidden_size 256; decoder_output_dim 32; temporal_decoder_dim 128; num_encoder_layers 1; dropout 0.3 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F44 | TFT | hidden_size 128 ({64,128,256}); n_head 4 ({1,4,8}); attn_dropout 0.0; dropout 0.1; loss MQLoss quantiles [0.1, 0.5, 0.9]; uses static + historic + future exog | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F45–F47 | Transformer, Informer, Autoformer/FEDformer | hidden_size 128; n_head 4; encoder_layers 2; decoder_layers 1; factor 3; conv_hidden_size 32; MovingAvg_window 25 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F48 | PatchTST | patch_len 16 ({8,16,24,32}); stride 8; encoder_layers 3; n_heads 16; hidden_size 128; linear_hidden_size 256; revin True; dropout 0.2 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F49 | iTransformer | n_series (all); hidden_size 512; n_heads 8; e_layers 2; d_ff 2048 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F50 | TimesNet | top_k 5; num_kernels 6; hidden_size 64; conv_hidden_size 64; encoder_layers 2 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F51 | TSMixer / TimeMixer / SOFTS / TimeXer / StemGNN / KAN | library defaults with input_size 3h; ff_dim 64; n_block 2 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F52 | Auto* neural models | `AutoNHITS`, `AutoLSTM`, … with the library's default search spaces, `num_samples` 20 (Quick 8 / Thorough 60), Optuna backend, seed 42 | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F53 | Foundation zero-shot (optional) | Chronos-Bolt (small/base), TimesFM, Moirai — context length up to model max; `num_samples` 20; no training; self-hosted only | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |
| F54 | Ensembles | simple mean, median, inverse-MASE weighted, stacking (ridge on backtest predictions), FFORMA-style meta-learning (optional) | per model as in §19.2 Library column (statsforecast / statsmodels / neuralforecast / mlforecast / prophet / arch) |

### 35.3 Multi-step forecasting strategies

| Strategy | Definition | Pros / cons | Where | Library |
|---|---|---|---|---|
| **Recursive (iterated)** | one model f predicts y_{t+1}; its output is fed back as a lag to predict t+2 … t+h | one model; errors accumulate | default for ML (mlforecast `recursive`), statistical models are recursive by nature | mlforecast / skforecast ForecasterRecursive |
| **Direct** | h separate models f_k, each predicting y_{t+k} from information at t | no error feedback; h× cost; incoherent paths | mlforecast `max_horizon=h` | mlforecast (max_horizon) / skforecast ForecasterDirect |
| **DirRec** | model f_k uses the original lags plus predictions of f_1…f_{k−1} | hybrid | thin wrapper | skforecast / thin |
| **MIMO (multi-output)** | one model outputs the whole vector (y_{t+1}, …, y_{t+h}) | captures dependence between steps; default for DL (N-BEATS, N-HiTS, TFT, PatchTST) | neuralforecast, sklearn MultiOutput | sklearn.multioutput / neuralforecast |
| **DIRMO** | MIMO on blocks of s steps, direct across blocks | trade-off | thin wrapper (Thorough) | thin over sklearn MultiOutputRegressor |
| **Rectify** | recursive base + direct correction models on its residuals | reduces bias | thin wrapper (optional) | thin over mlforecast / skforecast outputs |

The strategy is a parameter of every ML forecaster; the leaderboard shows strategy as a column so the user can compare them.

### 35.4 Exogenous variables

| Type | Examples | Handling | Library |
|---|---|---|---|
| Static | store type, region, sector | embeddings (DL), one-hot/target encoding (ML), ignored by local statistical models | statsforecast / mlforecast / neuralforecast (exog support) |
| Historic-only (past-observed) | volume, other prices, sensor readings | only lagged values (lag ≥ h for direct, or ≥ 1 for recursive with their own forecasts unavailable → auto-shift by h); never contemporaneous | statsforecast / mlforecast / neuralforecast (exog support) |
| Known-future | calendar, holidays, planned promotions, prices set in advance | allowed at t+k; the user must upload or generate future values for the horizon; Predict → Forecast asks for them | statsforecast / mlforecast / neuralforecast (exog support) |
| Generated | calendar features, Fourier terms, holiday flags (`holidays` package; NSE trading calendar), time index | created by the lab for any horizon | statsforecast / mlforecast / neuralforecast (exog support) |

Checks: leakage guard (an exog marked past-only must not appear un-lagged); coverage check (known-future values present for the whole horizon); Granger and CCF results shown to suggest useful exogenous series; for ARIMA the model becomes SARIMAX/regression with ARIMA errors; Prophet uses `add_regressor`; N-BEATSx/TFT/TiDE accept static/historic/future lists.

### 35.5 Multivariate and hierarchical forecasting

* **Multivariate (joint) models**: VAR/VARMAX/VECM (F21–F23), iTransformer, StemGNN, TSMixerx, multivariate MLP; impulse responses and FEVD for VAR family.
* **Global models over many series**: mlforecast and neuralforecast fit one model across `unique_id`s (panel); per-series scaling.
* **Hierarchical / grouped series** (e.g. total → region → branch → product): structure defined by the user in Intake (§33) or uploaded as an aggregation matrix S. Base forecasts from any model, then **reconciliation** with `hierarchicalforecast`: BottomUp, TopDown (forecast proportions / average historical proportions), MiddleOut, **MinTrace** (ols, wls_struct, wls_var, mint_shrink), ERM; coherent prediction intervals (bootstrap, normality, PERMBU). Plots: hierarchy tree with metrics, coherence errors before/after.
* **Cross-learning foundation models** (F53) for many short series.

### 35.6 Backtesting set-ups

| Set-up | Parameters (defaults) | Notes | Library |
|---|---|---|---|
| Single hold-out | last h points | quick sanity only | sktime.split.SingleWindowSplitter / pandas |
| Rolling origin, expanding window | n_windows 5 (Quick 3 / Thorough 10), step_size h, refit True | **default**; statsforecast/neuralforecast/mlforecast `cross_validation(h, n_windows, step_size, refit)` | StatsForecast.cross_validation / sktime ExpandingWindowSplitter |
| Rolling origin, sliding window | window length 3–5 seasons | regime-sensitive data | sktime SlidingWindowSplitter / cross_validation(window size) |
| Refit policy | refit every window / every k windows / never (update state only) | cost vs realism | StatsForecast.cross_validation(refit=…) |
| Gap | 0 (or publication lag, e.g. 1 month for macro data) | avoids look-ahead | sktime.split / TradingLab embargo |
| Walk-forward optimisation | full module §32 | financial | TradingLab / sktime.split (thin WFO driver, §32) |
| Blocked / hv-block CV | §13.1 | ML models on lagged features | sklearn KFold(shuffle=False) + thin gap wrapper |
| Multiple horizons | metrics reported for every step 1…h and pooled | error-by-horizon curve | utilsforecast.evaluation |

### 35.7 Forecast metrics (complete)

Notation: y_t actual, ŷ_t forecast, e_t = y_t − ŷ_t, n test points, m season, training sample y_1…y_T, quantile forecasts q̂_τ, interval [l_t, u_t] at nominal 1 − α.

| Metric | Formula | Interpretation | Library |
|---|---|---|---|
| ME (bias) | (1/n)Σ e_t | sign shows systematic over/under-forecasting | utilsforecast.losses / sktime.performance_metrics |
| MAE | (1/n)Σ\|e_t\| | scale-dependent; median-optimal | utilsforecast.losses / sktime.performance_metrics |
| MSE / RMSE | (1/n)Σe_t² ; √MSE | scale-dependent; mean-optimal; penalises large errors | utilsforecast.losses / sktime.performance_metrics |
| MAPE | (100/n)Σ\|e_t / y_t\| | undefined at 0, asymmetric; hidden when any y_t = 0 | utilsforecast.losses / sktime.performance_metrics |
| sMAPE | (100/n)Σ 2\|e_t\| / (\|y_t\| + \|ŷ_t\|) | bounded 0–200; still unstable near 0 | utilsforecast.losses / sktime.performance_metrics |
| WAPE | Σ\|e_t\| / Σ\|y_t\| | volume-weighted percentage; good for intermittent/retail | utilsforecast.losses / sktime.performance_metrics |
| MASE | MAE / [(1/(T−m))Σ_{t=m+1}^{T}\|y_t − y_{t−m}\|] | < 1 beats in-sample seasonal naive; scale-free (Hyndman & Koehler 2006) | utilsforecast.losses / sktime.performance_metrics |
| RMSSE | √( MSE / [(1/(T−m))Σ(y_t − y_{t−m})²] ) | squared version of MASE (M5) | utilsforecast.losses / sktime.performance_metrics |
| MSIS | (1/n)Σ[(u_t − l_t) + (2/α)(l_t − y_t)1{y_t < l_t} + (2/α)(y_t − u_t)1{y_t > u_t}] / scale, scale = in-sample seasonal naive MAE | interval quality (M4); lower is better | utilsforecast.losses / MAPIE |
| Winkler / interval score | same numerator without scaling | | utilsforecast.losses / MAPIE |
| Coverage (PICP) | (1/n)Σ1{l_t ≤ y_t ≤ u_t} | should be close to 1 − α | utilsforecast.losses / MAPIE |
| Mean interval width (MPIW) | (1/n)Σ(u_t − l_t) | sharpness | MAPIE / numpy |
| Pinball loss (τ) | (1/n)Σ max(τ(y − q̂_τ), (τ − 1)(y − q̂_τ)) | quantile accuracy; averaged over τ = scaled quantile loss | utilsforecast.losses / MAPIE |
| CRPS | ∫(F̂(z) − 1{z ≥ y})² dz (sample-based via `scoringrules`/properscoring; ≈ 2 × mean pinball over a dense τ grid) | full distribution accuracy; reduces to MAE for point forecasts | scoringrules / properscoring |
| Theil's U1 | √(Σe²/n) / (√(Σy²/n) + √(Σŷ²/n)) | 0 = perfect, bounded [0,1] | numpy (thin, formula on library errors) |
| Theil's U2 | √(Σ((ŷ_{t+1} − y_{t+1})/y_t)²) / √(Σ((y_{t+1} − y_t)/y_t)²) | < 1 beats the naive no-change forecast | numpy (thin, formula on library errors) |
| Directional accuracy | (1/n)Σ1{sign(ŷ_{t+1} − y_t) = sign(y_{t+1} − y_t)} | trend / trading relevance | numpy (TradingLab metric) |
| R² (out-of-sample, vs naive) | 1 − Σe²/Σ(y_t − ŷ^{naive}_t)² | | sklearn.metrics.r2_score / numpy |
| Relative MAE / geometric mean relative AE | MAE_model / MAE_benchmark | model vs benchmark | utilsforecast.losses / numpy (thin) |
| QLIKE (volatility) | σ²/σ̂² − ln(σ²/σ̂²) − 1 | robust loss for variance forecasts | arch / numpy (thin) |
| VaR backtests | Kupiec POF (unconditional coverage), Christoffersen independence and conditional coverage | GARCH / risk models | arch |
| Information criteria (in-sample) | AIC = 2k − 2ln L; AICc = AIC + 2k(k+1)/(T − k − 1); BIC = k ln T − 2ln L | model order selection only, not cross-model comparison across different data transforms | statsmodels / statsforecast model attributes |

### 35.8 Residual diagnostics

| Table ID | Columns | Library |
|---|---|---|
| TS.T.RESID_TESTS | model, **Ljung-Box** Q and p at lags 10 and 2m (df adjusted by p+q), Box-Pierce, **Jarque-Bera** stat and p, skew, kurtosis, **ARCH-LM** stat and p (lags 12), **Breusch-Godfrey** (regression models), Durbin-Watson, runs test p, mean residual and t-test of zero mean, verdict (white noise / autocorrelated / heteroscedastic / non-normal) | statsmodels.stats.diagnostic |
| TS.T.RESID_ACF | lag, residual ACF, band, flagged | statsmodels.tsa.stattools.acf |
| TS.T.PARAMS | parameter, estimate, std error, z, p, 95% CI (statistical models), plus AIC/AICc/BIC, log-likelihood, σ² | statsmodels results / statsforecast model params |

Residual plots: residuals over time, residual ACF/PACF, histogram + KDE vs normal, Q-Q, residuals vs fitted, squared-residual ACF (ARCH), cumulative sum of residuals (CUSUM) with bands.

### 35.9 Forecast plots

| Plot ID | Shows | Library |
|---|---|---|
| TS.P.FORECAST | history + point forecast + 80/95% fan, test actuals overlaid, horizon cap and h* (dashed beyond h*) | statsforecast / neuralforecast outputs |
| TS.P.BACKTEST | small multiples per backtest window (actual vs forecast) | StatsForecast.cross_validation outputs |
| TS.P.ERR_H | error metric by horizon step (MASE/RMSE vs h) for all models | utilsforecast.evaluation |
| TS.P.MODEL_OVERLAY | forecasts of the top-5 models overlaid | statsforecast / neuralforecast outputs |
| TS.P.ACTUAL_FITTED | in-sample fitted vs actual | statsforecast (fitted=True) |
| TS.P.QUANTILES | quantile fan (5…95) and PIT histogram (calibration) | neuralforecast / statsforecast quantiles + scipy |
| TS.P.COVERAGE | empirical coverage by horizon vs nominal | utilsforecast.losses (coverage) |
| TS.P.COMPONENTS | Prophet trend/seasonality/holiday components; N-BEATS interpretable stacks; TFT variable importance and attention | prophet / neuralforecast NBEATS |
| TS.P.IRF / TS.P.FEVD | impulse responses with bands; forecast-error variance decomposition (VAR family) | statsmodels VARResults.irf / fevd |
| TS.P.VOL | conditional volatility vs realised; VaR line with breaches marked | arch |
| TS.P.HIER | hierarchy tree coloured by MASE; coherence before/after reconciliation | hierarchicalforecast |
| TS.P.DM | Diebold-Mariano p-value matrix between models | scipy.stats (thin DM-HLN) |
| TS.P.RANK | average rank across windows/series (critical-difference style) | scikit-posthocs |
| TS.P.EXOG_IMPORTANCE | feature importance for ML forecasters (gain / SHAP by lag) | lightgbm feature_importances_ / shap |

### 35.10 Model comparison and leaderboard tables

| Table ID | Columns | Library |
|---|---|---|
| TS.T.LEADERBOARD | rank, model, family (baseline / statistical / ML / DL / foundation / ensemble), strategy, exog used, MASE, RMSSE, sMAPE, WAPE, RMSE, MAE, coverage 80/95, MSIS, CRPS, directional accuracy, useful horizon h*, fit time, predict time, backtest windows, beats seasonal naive (Y/N), residual verdict | utilsforecast.evaluation |
| TS.T.BY_HORIZON | model × horizon step matrix of the primary metric | utilsforecast.evaluation |
| TS.T.BY_WINDOW | model × backtest window matrix (stability) | utilsforecast.evaluation |
| TS.T.BY_SERIES | per-series metrics for panels (best model per series, share of series where each model wins) | utilsforecast.evaluation |
| TS.T.DM | Diebold-Mariano statistic and p for each pair (HLN small-sample correction) | scipy.stats (thin Diebold–Mariano with HLN correction) |
| TS.T.ENSEMBLE | members, weights, ensemble metric vs best single | sktime / darts ensembles |

Selection rule (default): lowest mean MASE across backtest windows, among models whose residuals pass Ljung-Box (p > 0.05) and whose 95% coverage is within ±5 pp; ties (DM p > 0.05) broken by simplicity then speed.

---

## 36. Per-family catalogue: metrics, tables and plots

> Round-2 addition. For every family: (a) scores and metrics with formula and interpretation, (b) every table with exact columns, (c) every plot with what it shows, axes, when it is used and the library. Plots are Plotly unless stated (lightweight-charts for price/equity charts). Deep learning is in §34.6–34.7 and time series in §35; those sections are part of this catalogue.

### 36.1 Supervised regression

> Superseded in detail by **§42 Regression Evaluation Suite** (IDs `REE.*`; the `REG.T.*` IDs below are aliases).

**(a) Metrics**

| Metric | Formula | Interpretation | Library |
|---|---|---|---|
| MAE | (1/n)Σ\|yᵢ − ŷᵢ\| | average absolute error in target units; robust to outliers | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| MSE | (1/n)Σ(yᵢ − ŷᵢ)² | penalises large errors; units² | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| RMSE | √MSE | same units as y; default primary metric | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| RMSLE | √[(1/n)Σ(ln(1+yᵢ) − ln(1+ŷᵢ))²] | relative error for positive skewed targets | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| MedAE | median\|yᵢ − ŷᵢ\| | typical error, outlier-proof | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Max error | max\|yᵢ − ŷᵢ\| | worst case | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| MAPE / sMAPE / WAPE | §35.7 | percentage errors (avoid when y ≈ 0) | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| R² | 1 − SS_res/SS_tot | share of variance explained; can be < 0 on test | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Adjusted R² | 1 − (1 − R²)(n − 1)/(n − p − 1) | penalises features | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Explained variance | 1 − Var(y − ŷ)/Var(y) | ignores bias, unlike R² | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Pearson r / Spearman ρ / Kendall τ | correlation of y and ŷ | ranking quality | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Concordance correlation (Lin's CCC) | 2ρσ_yσ_ŷ / (σ_y² + σ_ŷ² + (μ_y − μ_ŷ)²) | agreement, penalises bias and scale | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Poisson / Gamma / Tweedie deviance | D(y, ŷ) per GLM family | count / positive targets | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| D² score | 1 − D(model)/D(null) | deviance R² | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Pinball loss, PICP, MPIW, interval score, CRPS | §15.1 and §35.7 | probabilistic regression | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| AIC / BIC | 2k − 2 ln L ; k ln n − 2 ln L | linear/GLM model selection | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Bias (ME) and calibration slope | mean(ŷ − y); slope of y on ŷ | < 1 slope = over-confident spread | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |

**(b) Tables**

| Table ID | Columns | Library |
|---|---|---|
| REG.T.METRICS | metric, train, CV mean, CV std, CV min, CV max, test, test 95% CI (bootstrap), best (✓) | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| REG.T.FOLDS | fold, n_train, n_val, each metric, fit time | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| REG.T.LEADERBOARD | rank, model, recipe, primary metric mean ± std, all other metrics, CD group, fit time, predict latency (ms/row), model size (MB), params tuned (Y/N) | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| REG.T.COEF (linear) | feature, coefficient, std error, t, p, 95% CI, standardised coefficient, VIF | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| REG.T.RESID_STATS | mean residual, std, skew, kurtosis, Shapiro/JB p, Breusch-Pagan p, Durbin-Watson, % residuals beyond ±2σ | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| REG.T.ERR_SEGMENT | segment (decile of ŷ or category), n, MAE, RMSE, bias | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| REG.T.WORST | row id, y, ŷ, residual, leverage, Cook's D, top-3 SHAP reasons | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| REG.T.INTERVALS | method, nominal coverage, empirical coverage, mean width, interval score | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |

**(c) Plots**

| Plot | Shows | Axes | When | Library |
|---|---|---|---|---|
| Predicted vs actual | agreement with y = x line, R² label | x actual, y predicted (hexbin if n > 5 000) | always | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Residuals vs fitted | non-linearity, heteroscedasticity (LOWESS line) | x ŷ, y residual | always | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Residual histogram + KDE | error distribution vs normal | x residual | always | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Residual Q-Q | normality of residuals | theoretical vs sample quantiles | always | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Scale-location | √\|standardised residual\| vs ŷ | | linear models | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Residuals vs leverage + Cook's distance | influential points | x leverage, y std residual | linear models | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Residuals vs each feature | missing non-linearity per feature | small multiples | on demand | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Residuals over time / ACF of residuals | autocorrelation left in errors | | sequential | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Error by segment | MAE per decile/category | bars | always | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Prediction-interval band | sorted ŷ with intervals and actuals | x rank, y value | uncertainty on | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Coverage by bin / PIT histogram | calibration of intervals | | uncertainty on | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Coefficient forest plot | coefficients with 95% CI | | linear | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Regularisation path | coefficients vs log α | | Lasso/Ridge/ElasticNet | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Learning curve | train vs CV score vs n samples ±σ | | always | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Validation curve | score vs one hyperparameter | | tuning | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |
| Model comparison bars + CD diagram | §16 leaderboard plots | | leaderboard | per-artefact library in §42 (sklearn / statsmodels / MAPIE / scipy) |

### 36.2 Supervised classification

> Superseded in detail by **§41 Classification Evaluation Suite** (IDs `CLE.*`; the `CLF.T.*` IDs below are aliases). §41 adds the three confusion-matrix normalisations, per-fold and CV-aggregated matrices, the full classification report with macro/micro/weighted/samples rows, threshold optimisation, imbalance reporting and statistical tests.

**(a) Metrics** (binary unless noted; multiclass uses macro / micro / weighted averages)

| Metric | Formula | Interpretation | Library |
|---|---|---|---|
| Accuracy | (TP + TN)/n | misleading under imbalance | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Balanced accuracy | ½(TPR + TNR) | robust to imbalance | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Precision (PPV) | TP/(TP + FP) | trust in positive calls | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Recall (TPR, sensitivity) | TP/(TP + FN) | share of positives caught | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Specificity (TNR) | TN/(TN + FP) | | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| NPV, FPR, FNR | TN/(TN+FN), FP/(FP+TN), FN/(FN+TP) | | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| F1 / Fβ | (1 + β²)PR/(β²P + R) | precision-recall balance | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| MCC | (TP·TN − FP·FN)/√((TP+FP)(TP+FN)(TN+FP)(TN+FN)) | single best summary under imbalance (−1…1) | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Cohen's κ | (p_o − p_e)/(1 − p_e) | agreement beyond chance | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| ROC-AUC | P(score⁺ > score⁻) | ranking quality, threshold-free | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| PR-AUC / average precision | Σ(R_k − R_{k−1})P_k | preferred for rare positives | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Log-loss | −(1/n)ΣΣ y log p | probability quality | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Brier score (+ decomposition) | (1/n)Σ(p − y)² = reliability − resolution + uncertainty | calibration + sharpness | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| ECE / MCE | Σ_b (n_b/n)\|acc_b − conf_b\| ; max_b | calibration error | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Gini | 2·AUC − 1 | credit scoring convention | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| KS statistic | max_t\|F₁(t) − F₀(t)\| | separation of score distributions | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Lift@k, Gain@k | precision in top k% / base rate; captured positives | campaign targeting | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Youden J, optimal threshold | max_t(TPR − FPR); or cost-optimal t* = argmin expected cost | threshold choice | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Expected cost | Σ C_ij N_ij | business cost matrix | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Top-k accuracy | 1{y ∈ top-k} | multiclass | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Hamming loss, Jaccard, subset accuracy | multi-label | | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Information value (IV) per feature | Σ(%good − %bad)·WOE | credit scoring feature strength | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |

**(b) Tables**

| Table ID | Columns | Library |
|---|---|---|
| CLF.T.METRICS | metric, train, CV mean ± std, test, 95% CI | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| CLF.T.REPORT | class, precision, recall, F1, support, specificity, AUC (OvR) + macro / weighted / micro rows | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| CLF.T.CONFUSION | true class × predicted class counts, row %, column % | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| CLF.T.THRESHOLD | threshold, TP, FP, TN, FN, precision, recall, F1, MCC, expected cost (step 0.01), chosen ✓ | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| CLF.T.CALIBRATION | bin, mean predicted probability, observed frequency, count, gap | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| CLF.T.GAINS | decile, n, positives, cumulative positives %, gain, lift, KS | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| CLF.T.LEADERBOARD | rank, model, primary metric mean ± std, ROC-AUC, PR-AUC, F1, MCC, log-loss, Brier, ECE, CD group, time, latency | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| CLF.T.MISCLASSIFIED | row id, true, predicted, p(pred), p(true), top-3 SHAP reasons | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| CLF.T.WOE_IV (binary) | feature, bin, count, events, non-events, WOE, IV contribution, total IV | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |

**(c) Plots**

| Plot | Shows | Axes | When | Library |
|---|---|---|---|---|
| Confusion matrix (counts and normalised) | error structure | true × predicted heatmap | always | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| ROC curves (per class OvR, micro, macro) + AUC CI | ranking ability | x FPR, y TPR | always | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Precision-recall curves with iso-F1 lines | performance on positives | x recall, y precision | always; primary under imbalance | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Threshold sweep | precision, recall, F1, MCC, cost vs threshold | x threshold | binary | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Reliability diagram + probability histogram | calibration | x mean predicted p, y observed frequency | probabilistic models | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Cumulative gains / lift / KS chart | targeting value | x % population | binary | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| DET curve | FNR vs FPR on normal deviate scale | | binary | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Score distribution by class | separation | density of p by class | always | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Decision boundary (2D PCA/UMAP projection) | geometry of decisions | 2D | ≤ 10 classes | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Cost curve | expected cost vs threshold/prior | | cost matrix given | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Class balance before/after resampling | effect of SMOTE etc. | bars | imbalance handling | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Multiclass ROC/PR grid | one panel per class | small multiples | multiclass | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |
| Learning / validation curves, CD diagram | as §36.1 | | | per-artefact library in §41 (sklearn / imbalanced-learn / netcal / scipy) |

### 36.3 Deep learning

Metrics: the regression/classification metrics above plus training-specific scores — best validation loss, best epoch, generalisation gap (train loss − val loss at the best epoch), epochs to converge, throughput, calibration after temperature scaling, predictive entropy, mutual information, MC-dropout/ensemble std, interval coverage. Tables: DL.T.* (§34.6). Plots: DL.P.* (§34.7).

### 36.4 Time series

Metrics §35.7; tables TS.T.* (§35.1, §35.8, §35.10); plots TS.P.* (§35.1, §35.9).

### 36.5 Dimensionality reduction

**(a) Metrics and tests**

| Metric / test | Formula / definition | Interpretation | Library |
|---|---|---|---|
| Eigenvalue λ_k / explained variance ratio | λ_k / Σλ | variance captured by component k | sklearn.decomposition.PCA explained_variance_ |
| Cumulative explained variance | Σ_{j≤k} λ_j / Σλ | choose k at 80/90/95% | sklearn.decomposition.PCA (+ numpy) |
| Kaiser criterion | keep λ > 1 (on correlation matrix) | rule of thumb | sklearn PCA explained_variance_ |
| Broken-stick | b_k = (1/p)Σ_{i=k}^{p} 1/i; keep λ_k/Σλ > b_k | conservative selection | numpy (thin) |
| Horn's parallel analysis | keep components whose λ exceeds the 95th percentile of λ from random data of the same shape | best simple rule | sklearn PCA on permuted data (thin) |
| Velicer's MAP | minimum average squared partial correlation | factor count | numpy (thin, partial correlations) |
| **KMO** (Kaiser-Meyer-Olkin) | Σr²_ij / (Σr²_ij + Σa²_ij) over i ≠ j (a = partial correlations); per-variable MSA too | sampling adequacy for PCA/FA: ≥ 0.8 great, 0.6–0.8 acceptable, < 0.5 unacceptable | thin (numpy/scipy formulas; factor_analyzer as dev-only oracle) |
| **Bartlett's test of sphericity** | χ² = −(n − 1 − (2p + 5)/6) ln\|R\|, df = p(p − 1)/2 | H₀: correlation matrix = identity; must reject to justify PCA/FA | thin (numpy/scipy formulas; factor_analyzer as dev-only oracle) |
| Communality h²_j | Σ_k loading²_jk | share of a variable's variance explained by retained components/factors | sklearn FactorAnalysis components_ |
| Uniqueness | 1 − h²_j | | sklearn FactorAnalysis.noise_variance_ |
| Loadings | eigenvector × √λ (correlation of variable with component) | interpretation of components | sklearn.decomposition components_ |
| cos² (quality of representation) | squared cosine of an observation/variable with a component | | sklearn.decomposition / prince |
| Contribution | (loading²_jk / λ_k) × 100 | which variables drive a component | sklearn.decomposition / prince |
| Reconstruction error | (1/n)‖X − X̂_k‖²_F (PCA, KPCA pre-image, NMF, autoencoders); relative = ‖X − X̂‖²/‖X‖² | information lost | sklearn (inverse_transform) / pyod |
| **Trustworthiness** T(k) | 1 − 2/(nk(2n − 3k − 1)) Σᵢ Σ_{j ∈ U_k(i)} (r(i,j) − k) | are embedding neighbours true neighbours? (sklearn `trustworthiness`) | sklearn.manifold.trustworthiness |
| **Continuity** C(k) | same with roles of input and embedding swapped | are true neighbours kept? | sklearn.manifold.trustworthiness (spaces swapped) |
| Neighbourhood preservation / LCMC | share of k-NN shared between spaces | local structure | sklearn.neighbors (thin) |
| Stress (Kruskal) | √(Σ(d_ij − d̂_ij)² / Σd_ij²) | MDS fit (< 0.1 good) | sklearn.manifold.MDS (stress_) |
| Shepard correlation | Spearman between original and embedded distances | global distance preservation | sklearn.manifold.MDS / scipy.spatial.distance |
| t-SNE KL divergence | KL(P‖Q) at convergence | compare runs with the same perplexity | openTSNE / sklearn.manifold.TSNE |
| Factor-analysis fit | log-likelihood, AIC/BIC, RMSEA, TLI (via `factor_analyzer`) | FA model adequacy | sklearn FactorAnalysis.score / statsmodels Factor |
| Supervised DR quality | k-NN accuracy (5-fold) in the embedding using the target | downstream usefulness | sklearn.model_selection.cross_val_score |

**(b) Tables**

| Table ID | Columns | Library |
|---|---|---|
| DR.T.SUITABILITY | KMO overall, MSA per variable, Bartlett χ², df, p, verdict | thin (numpy/scipy formulas; factor_analyzer as dev-only oracle) |
| DR.T.EIGEN | component, eigenvalue, % variance, cumulative %, Kaiser (✓), broken-stick value, parallel-analysis 95th pct, retained (✓) | sklearn.decomposition.PCA (+ numpy for broken-stick/parallel analysis) |
| DR.T.LOADINGS | variable × component loadings (rotated if FA: varimax/promax/oblimin), with \|loading\| > 0.4 highlighted | sklearn.decomposition (PCA, FactorAnalysis rotation) |
| DR.T.COMMUNALITIES | variable, communality h², uniqueness, MSA | sklearn.decomposition.FactorAnalysis |
| DR.T.CONTRIB | variable, contribution % per component, cos² per component | prince / numpy |
| DR.T.SCORES | row id, component scores (first k), cos², contribution (exportable) | sklearn.decomposition / prince |
| DR.T.QUALITY | method, params, trustworthiness@k (k = 5, 10, 30), continuity@k, Shepard ρ, stress, reconstruction error, k-NN accuracy, runtime | sklearn.manifold.trustworthiness / scipy.spatial.distance |
| DR.T.METHOD_COMPARE | rows = methods, columns = the quality metrics → ranking | sklearn.manifold / numpy |

**(c) Plots**

| Plot | Shows | Axes | When | Library |
|---|---|---|---|---|
| Scree plot | eigenvalues with Kaiser line, parallel-analysis curve, broken-stick | x component, y eigenvalue | PCA/FA | sklearn.decomposition.PCA (+ numpy) |
| Cumulative explained variance | with 80/90/95% markers | x k, y cumulative % | PCA family | sklearn.decomposition.PCA (+ numpy) |
| Biplot | scores + loading arrows | PC_i × PC_j | PCA | sklearn.decomposition / prince |
| Correlation circle | variable vectors in the unit circle | PC1 × PC2 | PCA/FA on standardised data | sklearn.decomposition / prince |
| Loadings heatmap | variables × components | heatmap (diverging) | PCA/FA/ICA/NMF | sklearn.decomposition components_ |
| Loadings bar per component | top contributing variables | bars | | sklearn.decomposition components_ |
| Contribution and cos² bars | quality per variable/observation | bars | | sklearn.decomposition / prince |
| 2D / 3D embedding scatter | structure coloured by target, cluster or any column; hover shows row | 2D/3D | every method | sklearn.decomposition / sklearn.manifold |
| Embedding small multiples | t-SNE perplexity grid (5, 30, 50, 100); UMAP n_neighbors × min_dist grid | | t-SNE/UMAP tuning | umap-learn / openTSNE |
| Shepard diagram | original vs embedded distances (hexbin) + isotonic fit | x original, y embedded | MDS/Isomap/t-SNE/UMAP | sklearn.manifold.MDS / scipy.spatial.distance |
| Trustworthiness/continuity vs k | local quality curves per method | x k | method comparison | sklearn.manifold.trustworthiness |
| Reconstruction error vs n_components | elbow for k | | PCA/KPCA/NMF/AE | sklearn.decomposition (inverse_transform) |
| Autoencoder loss curves / latent traversal | training + VAE latent grid | | AE/VAE | torch + lightning (optional models) |
| ICA sources / NMF components | recovered signals or parts | | ICA/NMF | sklearn.decomposition |
| Factor diagram | variables → factors with loadings | diagram | FA | sklearn.decomposition.FactorAnalysis |
| KMO/MSA bar | sampling adequacy per variable | bars | before PCA/FA | thin (numpy/scipy formulas; factor_analyzer as dev-only oracle) |

### 36.6 Clustering

**(a) Metrics**

| Metric | Formula | Interpretation | Library |
|---|---|---|---|
| Inertia / WCSS | Σ_k Σ_{x∈C_k}‖x − μ_k‖² | elbow method (Kneedle knee detection) | sklearn.cluster + kneed |
| Silhouette s(i) | (b(i) − a(i)) / max(a(i), b(i)); overall = mean | −1…1, > 0.5 strong, < 0.25 weak | sklearn.metrics |
| Calinski-Harabasz | [tr(B_k)/(k − 1)] / [tr(W_k)/(n − k)] | higher is better | sklearn.metrics |
| Davies-Bouldin | (1/k)Σ_i max_{j≠i} (σ_i + σ_j)/d(c_i, c_j) | lower is better | sklearn.metrics |
| Dunn index | min inter-cluster distance / max intra-cluster diameter | higher is better; sensitive to outliers | thin (numpy on sklearn pairwise_distances) |
| Gap statistic | Gap(k) = E*[log W_k] − log W_k (B = 50 reference sets); choose smallest k with Gap(k) ≥ Gap(k+1) − s_{k+1} | Tibshirani 2001 | sktime.split / TradingLab embargo |
| BIC / AIC (GMM) | −2 ln L + p ln n ; −2 ln L + 2p | choose components and covariance type | sklearn GaussianMixture / statsmodels |
| DBCV | density-based validity | for DBSCAN/HDBSCAN (−1…1) | hdbscan.validity.validity_index |
| Cophenetic correlation | corr(original distances, dendrogram heights) | hierarchical fit (> 0.75 good) | scipy.cluster.hierarchy |
| Stability (bootstrap) | mean ARI / Jaccard between clusterings of bootstrap resamples (B = 50) matched by Hungarian algorithm | > 0.85 stable, < 0.6 unstable (Hennig) | sklearn.utils.resample + sklearn.metrics.adjusted_rand_score |
| Noise share | % points labelled −1 | DBSCAN/HDBSCAN/OPTICS | numpy |
| External (labels known): ARI | (RI − E[RI])/(max RI − E[RI]) | agreement corrected for chance | sklearn.metrics |
| NMI / AMI | I(U;V)/mean(H(U), H(V)); adjusted for chance | | sklearn.metrics |
| Homogeneity / completeness / V-measure | 1 − H(C\|K)/H(C); 1 − H(K\|C)/H(K); harmonic mean | | sklearn.metrics |
| Fowlkes-Mallows (FMI) | TP/√((TP+FP)(TP+FN)) on pairs | | sklearn.metrics |
| Purity, contingency matrix | majority-class share per cluster | | sklearn.metrics |

**(b) Tables**

| Table ID | Columns | Library |
|---|---|---|
| CLU.T.KSELECT | k, inertia, silhouette, CH, DB, Dunn, gap ± s, BIC, AIC, stability ARI, chosen (✓ per criterion), consensus k | sklearn.metrics (silhouette, CH, DB) / sklearn GaussianMixture (BIC/AIC) / kneed |
| CLU.T.SIZES | cluster, n, %, noise flag, mean silhouette, stability Jaccard | numpy / sklearn.metrics.silhouette_samples |
| CLU.T.CENTROIDS | cluster × features (original units; medoid for K-Medoids; modes for K-Modes) | sklearn.cluster (cluster_centers_) |
| CLU.T.PROFILE | cluster × feature: mean, median, std, z-score vs overall, top categories with share and lift; highlighted distinctive features (\|z\| > 0.5) | pandas groupby |
| CLU.T.DISTINCT | cluster, top 5 distinguishing features (ANOVA F / χ² / surrogate-tree SHAP), direction | sklearn.feature_selection (f_classif, chi2) / sklearn.tree |
| CLU.T.ALGO_COMPARE | algorithm, params, k found, silhouette, CH, DB, DBCV, stability, noise %, runtime, ARI vs other algorithms | sklearn.metrics / hdbscan (DBCV validity_index) |
| CLU.T.EXTERNAL (if labels) | ARI, AMI, NMI, homogeneity, completeness, V-measure, FMI, purity + contingency matrix | sklearn.metrics |
| CLU.T.MEMBERSHIP | row id, cluster, probability/soft membership (GMM/HDBSCAN), silhouette, distance to centroid, outlier score | sklearn GaussianMixture.predict_proba / hdbscan.all_points_membership_vectors |
| CLU.T.RULES | surrogate decision-tree rules describing each cluster with precision/coverage | sklearn.tree (DecisionTreeClassifier, export_text) |

**(c) Plots**

| Plot | Shows | Axes | When | Library |
|---|---|---|---|---|
| Elbow (inertia vs k) with knee | k selection | x k, y WCSS | K-Means family | sklearn.cluster + kneed |
| Silhouette / CH / DB / Dunn / gap / BIC-AIC vs k | k selection panel | x k | always | sklearn.metrics |
| Silhouette plot ("knife") | per-sample silhouettes grouped by cluster with mean line | x silhouette, y samples | partitioning methods | sklearn.metrics |
| Dendrogram (truncated, colour threshold) + cophenetic value | hierarchy and cut | x samples/clusters, y distance | agglomerative | scipy.cluster.hierarchy |
| Clustermap | heatmap of data reordered by dendrograms | | hierarchical, ≤ 2 000 rows | scipy.cluster.hierarchy |
| k-distance plot | sorted k-NN distance, knee → eps | x points, y distance | DBSCAN | sklearn.cluster + kneed |
| OPTICS reachability plot | valleys = clusters | x ordering, y reachability | OPTICS | sklearn.neighbors / sklearn.cluster.OPTICS |
| HDBSCAN condensed tree / single-linkage tree | cluster persistence | | HDBSCAN | scipy.cluster.hierarchy |
| Cluster scatter on PCA / UMAP / t-SNE (2D/3D) | separation with centroids, convex hulls, GMM ellipses | 2D/3D | always | openTSNE / sklearn.manifold.TSNE |
| Cluster sizes bar | balance | | always | numpy |
| Profile heatmap (z-scored means) | what defines each cluster | cluster × feature | always | pandas groupby |
| Parallel coordinates by cluster | multivariate profile | features × value | ≤ 15 features | pandas |
| Radar / spider chart per cluster | profile shape | | ≤ 12 features | pandas |
| Box/violin of features by cluster | distributions | | | pandas |
| Categorical composition stacked bars | category shares per cluster | | categorical features | pandas crosstab |
| Sankey of membership across k or across algorithms | stability/consensus | | comparison | pandas crosstab |
| Co-association (consensus) matrix | bootstrap co-clustering frequency | heatmap | stability | numpy over sklearn label vectors |
| ARI/NMI heatmap between algorithms | agreement | | comparison | sklearn.metrics |
| GMM membership probability histogram | soft assignment certainty | | GMM | sklearn GaussianMixture.predict_proba |
| SOM U-matrix and component planes | topology | grid | SOM | minisom (distance_map) |

### 36.7 Anomaly detection

**(a) Metrics**

| Metric | Definition | Interpretation | Library |
|---|---|---|---|
| Anomaly score | method-specific (isolation path length → s(x) = 2^{−E[h(x)]/c(n)}; LOF ratio; reconstruction error; ECOD tail probability) | higher = more anomalous | pyod decision_function |
| Contamination / threshold | quantile of scores (user contamination, default 1%) or POT (EVT) threshold | | pyod (contamination) / pythresh |
| Score separation | (mean score of flagged − mean of rest) / pooled std | clarity of flagged set | scipy.stats |
| Stability | Jaccard of top-k flagged sets across seeds/bootstrap | robustness | sklearn.utils.resample + sklearn.metrics |
| Rank agreement | Kendall τ / overlap@k between methods | consensus | scipy.stats.kendalltau |
| With labels: ROC-AUC, PR-AUC (average precision), precision@n, recall@k, F1 at threshold, MCC | as classification | evaluation on labelled data (e.g. DS21) | sklearn.metrics.roc_curve / roc_auc_score |
| Excess-mass / mass-volume curves (unlabelled) | Goix 2016 | unsupervised model selection | optional thin (numpy on pyod scores) |

**(b) Tables**

| Table ID | Columns | Library |
|---|---|---|
| ANO.T.TOP | rank, row id, score, percentile, flagged, top contributing features (SHAP on surrogate / COPOD dimension scores), raw values | pyod (decision_scores_) + shap |
| ANO.T.SUMMARY | method, params, contamination, threshold, n flagged, separation, stability, runtime | pyod / pythresh |
| ANO.T.COMPARE | method × method overlap@k and Kendall τ; ensemble score | scipy.stats.kendalltau / numpy |
| ANO.T.LABELLED (if labels) | method, ROC-AUC, PR-AUC, precision@n, recall@k, F1, MCC | sklearn.metrics |
| ANO.T.TS (time series anomalies) | timestamp, value, expected value, residual z, type, method | statsmodels STL / stumpy / ruptures |

**(c) Plots**

| Plot | Shows | Axes | When | Library |
|---|---|---|---|---|
| Score histogram with threshold | separation of anomalies | x score | always | pyod / pythresh |
| Ranked score plot (Pareto) | elbow in scores | x rank, y score | always | pyod decision_scores_ |
| Embedding scatter with anomalies highlighted | where anomalies sit | PCA/UMAP 2D/3D | always | umap-learn / sklearn PCA |
| Feature contribution bars per anomaly | why a row is anomalous | | per row | shap |
| Pairwise scatter of top features with anomalies | | | | pyod / sklearn |
| Time-series overlay | anomalies on the series with expected band | time × value | sequential | pandas |
| ROC / PR curves, precision@k curve | evaluation | | labels available | sklearn.metrics.roc_curve / roc_auc_score |
| Method agreement heatmap / UpSet of flagged sets | consensus | | multiple methods | upsetplot / numpy |
| Reconstruction error over samples | | | autoencoder detectors | sklearn (inverse_transform) / pyod |

### 36.8 Catalogue counts (updated in round 3)

| Family | Algorithms | Metrics | Tables | Plots |
|---|---|---|---|---|
| Regression | 62 (R1–R62, §43.2) | 40 (§42.3) | 17 (§42.4) | 36 (§42.5) |
| Classification | 45 (C1–C45, §43.2) | 55 (§41.4) | 42 (§41.2–§41.11) | 45 (§41.5) |
| Deep learning | 16 tabular (T1–T16) + 13 sequential (Q1–Q13) | regression/classification set + training/uncertainty scores (best val loss, best epoch, generalisation gap, epochs to converge, throughput, ECE after temperature scaling, predictive entropy, mutual information, ensemble std, coverage) | 9 | 17 |
| Time series | 67 (F1–F67, §43.6) + 6 multi-step strategies + 5 reconciliation methods | 22 (incl. AIC/AICc/BIC, VaR tests) | 22 | 41 TS.P.* + 7 residual plots |
| Dimensionality reduction | 28 (D1–D28, §43.5) | 20 | 8 | 16 |
| Clustering | 23 (K1–K23, §43.5) | 16 | 9 | 20 |
| Anomaly detection | 23 (A1–A23, §43.5) | 7 | 5 | 9 |
| Financial suitability (§37) | 20 checks FS1–FS20, 4 labelling methods | — | report + grid | 10 FS.P.* |
| VLM decision agent (§38) | 12 decision points VD1–VD12 | agreement rate, guard violations | decisions, decision_feedback | decision cards + agent timeline |

(Tables count TS.T.* in §35.1, §35.8 and §35.10; time-series plots count TS.P.* in §35.1 and §35.9; EDA, explainability, walk-forward and financial plots are catalogued separately in §10, §17, §32.9 and §16.)

---

## 37. Financial labelling suitability check (runs before any financial label)

> Round-2 addition. Before the lab offers triple-barrier, meta-labelling, fixed-horizon return labels or trend-scanning (§16, TradingLab `labeling`), it checks whether the dataset can support them. The check is deterministic (Python rules) and produces a **Suitability Report**. The VLM (§38) may comment on the plots but **cannot override a FAIL**. If the data is not suitable, the lab falls back to standard targets.

### 37.1 When it runs

* Automatically after Intake (§33) when the detected or chosen family is **Supervised → Sequential (financial)**, or when the user picks any financial label in the Target step.
* Re-runs when the user changes the price column, the frequency, the barrier parameters or the date range.
* Job queue `q.eda`; typical runtime < 10 s on 10 years of daily data (the trial labelling uses vectorised TradingLab functions).

### 37.2 Inputs detected

| Input | Detection rule |
|---|---|
| Datetime index | Intake role `index` (D1); strictly increasing after sort; duplicates flagged |
| Price column | name matches `close\|adj_close\|price\|px_last\|ltp\|nav` **or** strictly positive, high autocorrelation (ACF₁ > 0.95), level-like (ADF fails to reject) |
| Returns column | name matches `ret\|return\|pct_change\|log_ret` **or** mean ≈ 0, \|values\| < 1 for 99% of rows, ACF₁ < 0.3 |
| OHLCV | columns mapping to open/high/low/close/volume with consistency high ≥ max(open, close), low ≤ min(open, close), volume ≥ 0 |
| Frequency | median Δt → {tick, 1-min, 5-min, 15-min, hourly, daily, weekly, monthly}; NSE trading calendar allowed (weekends/holidays are not gaps) |
| Asset identifier | column with few unique values and repeated timestamps → panel of assets (check runs per asset) |

If only returns are present, the lab reconstructs a price index P_t = P_0·Π(1 + r_t) (P_0 = 100) and records that it did so.

### 37.3 Checks, thresholds and verdicts

Each check returns PASS, WARN or FAIL. Thresholds are defaults the user can edit (stored with the report).

| # | Check | Metric | PASS | WARN | FAIL | Why it matters | Library |
|---|---|---|---|---|---|---|---|
| FS1 | Time index | sorted, unique, parseable | all true | < 0.5% duplicates (auto-dropped) | unparseable / no index | barriers are defined in time | pandas (DatetimeIndex checks) |
| FS2 | Price or returns series | detection in §37.2 | price found | only returns (index reconstructed) | neither | barriers need a price path | pandas / TradingLab |
| FS3 | Positivity / sanity | min price > 0; no \|r\| > 50% on daily data unless confirmed | ok | ≤ 3 extreme jumps (likely splits) | negative/zero prices | log returns and volatility | pandas |
| FS4 | OHLCV | presence + consistency | full OHLCV consistent | close only (high/low barriers and Parkinson vol unavailable) | inconsistent OHLC in > 1% rows | intrabar barrier touches, volume bars | pandas |
| FS5 | Frequency regularity | share of missing expected bars | < 2% | 2–10% | > 10% or irregular without a calendar | vertical barrier in bars | pandas.infer_freq |
| FS6 | Length | number of bars n | ≥ 1 000 | 500–999 | < 500 | enough events for CV with purging | pandas |
| FS7 | Volatility estimable | `get_daily_vol(close, span=100)` non-null share; vol > 0 | ≥ 95% non-null after warm-up | 80–95% | < 80% or zero vol (stale prices) | barrier widths = multiple of σ | TradingLab get_daily_vol |
| FS8 | Stale prices | share of zero returns | < 5% | 5–20% | > 20% | illiquid series give degenerate labels | pandas |
| FS9 | Event count | CUSUM events `cusum_filter(close, h = σ̄_daily)` | ≥ 300 events | 100–299 | < 100 | samples available to learn from | TradingLab cusum_filter |
| FS10 | Class balance after trial labelling | trial triple barrier pt_sl = [1, 1], vertical barrier 5 bars (daily) / scaled to frequency, min_ret 0; label shares | minority ≥ 15% | 5–15% | < 5% or one class | learnability | TradingLab triple-barrier labels + pandas |
| FS11 | Vertical-barrier share | % events ended by the time barrier (label 0 / sign of return) | < 60% | 60–85% | > 85% | barriers too wide for the volatility | TradingLab get_events / get_bins |
| FS12 | Average uniqueness | `get_av_uniqueness_from_triple_barrier` mean ū | ≥ 0.3 | 0.1–0.3 | < 0.1 | heavy overlap → few effective samples; sample weights and sequential bootstrap required | TradingLab sampling (average uniqueness) |
| FS13 | Effective sample size | n_events × ū | ≥ 200 | 50–199 | < 50 | statistical power | TradingLab sampling |
| FS14 | Return autocorrelation | Ljung-Box on returns (lags 10) and variance ratio | informational | | | predictability hint; reported, never FAIL | statsmodels acf / acorr_ljungbox |
| FS15 | Stationarity of features | ADF on log price (expect unit root) and on returns; min fractional d by `plot_min_ffd` | d* ≤ 0.6 found | d* > 0.6 | none < 1 | memory-preserving stationary features | statsmodels adfuller / TradingLab FFD |
| FS16 | Structural breaks / regimes | SADF (`get_sadf`) and Chu-Stinchcombe-White | informational (flags bubbles) | | | splitting and regime features | TradingLab structural_breaks (SADF, Chow) / ruptures |
| FS17 | Trend-scanning feasibility | t-values over windows L ∈ [5, 20] bars; share with \|t\| > 2 | ≥ 20% | 5–20% | < 5% | trend-scanning labels informative | TradingLab trend_scanning_labels |
| FS18 | Meta-labelling prerequisite | a primary model or rule exists (user rule, e.g. MA cross, or a trained primary) with ≥ 100 signals | present | < 100 signals | none | meta-labels size bets of a primary model | TradingLab meta-labelling + sklearn.metrics |
| FS19 | Fixed-horizon feasibility | horizon h ≤ n/10 and threshold τ (default 0.5σ) gives minority ≥ 15% | ok | 5–15% | otherwise | simplest financial label | TradingLab fixed_time_horizon |
| FS20 | Leakage risk | features aligned at bar close; no future-dated columns (Intake leakage rules §33.5) | none | suspicious columns | confirmed future columns | label integrity | TradingLab purging checks + pandas |

### 37.4 Verdict per labelling method

| Method | Required PASS | Allowed WARN | Verdict logic |
|---|---|---|---|
| Triple barrier | FS1, FS2, FS3, FS6, FS7, FS9, FS10, FS20 | FS4, FS5, FS8, FS11, FS12 | any FAIL in required → **Not suitable** |
| Meta-labelling | triple-barrier requirements + FS18 | | |
| Fixed-horizon | FS1, FS2, FS6, FS19, FS20 | FS5, FS7 | |
| Trend-scanning | FS1, FS2, FS6, FS17, FS20 | FS5 | |
| Sample weighting (uniqueness/return/time decay) | FS12 ≥ WARN | | recommended whenever FS12 < PASS |

Overall status: **Suitable** (all required PASS), **Suitable with cautions** (required PASS, some WARN), **Not suitable** (any required FAIL).

### 37.5 Recommendations engine (deterministic)

| Condition | Recommendation |
|---|---|
| FS9 FAIL on daily data | lower CUSUM threshold to 0.5σ̄, or use every bar as an event; or switch to fixed-horizon |
| FS10 WARN/FAIL | adjust pt_sl asymmetry, widen/narrow vertical barrier, set min_ret; use class weights; show the barrier grid (pt × sl × vertical) with resulting class balance |
| FS11 high | barriers too wide → reduce pt_sl multiples or extend vertical barrier |
| FS12 low | enable sequential bootstrap (`seq_bootstrap`) and uniqueness weights; use purged CV with embargo ≥ 1% |
| FS4 close-only | volatility via close-to-close EWM; dollar/volume bars disabled |
| FS5 gaps | forward-fill limited to 1 bar or resample to a coarser frequency |
| FS15 d* > 0.6 | prefer returns/ratios over fractional differencing |
| Not suitable overall | **fallback**: standard targets — next-period return regression, sign classification with a dead-zone, or ordinary time-series forecasting (§35); the UI pre-selects the fallback and explains why |

### 37.6 Parameter grid preview

A small grid (pt_sl ∈ {[1,1],[1,2],[2,1],[2,2]}, vertical ∈ {5, 10, 20} bars, CUSUM h ∈ {0.5, 1, 2}·σ̄) is labelled in the background (36 trial labellings) so the user sees class balance, vertical share, ū and event count for each combination in a heatmap before choosing. Default chosen = the cell maximising effective sample size subject to minority ≥ 15%.

### 37.7 Report schema (JSON, stored in `suitability_reports`)

```json
{
  "dataset_version_id": "uuid",
  "asset": "NIFTY50",
  "frequency": "1D",
  "n_bars": 1236,
  "detected": {"price_col": "close", "ohlcv": true, "returns_reconstructed": false},
  "checks": [
    {"id": "FS9", "name": "event_count", "value": 412, "pass": ">=300", "warn": "100-299", "status": "PASS", "detail": "CUSUM h = 0.0112"}
  ],
  "methods": {
    "triple_barrier": {"status": "SUITABLE_WITH_CAUTIONS", "failed": [], "warned": ["FS12"]},
    "meta_labeling": {"status": "NOT_SUITABLE", "failed": ["FS18"]},
    "fixed_horizon": {"status": "SUITABLE"},
    "trend_scanning": {"status": "SUITABLE"}
  },
  "grid": [{"pt_sl": [1, 1], "vertical": 10, "cusum_mult": 1.0, "minority_share": 0.31, "vertical_share": 0.42, "avg_uniqueness": 0.27, "n_events": 412}],
  "recommendations": ["Enable sequential bootstrap and uniqueness weights (FS12 = 0.27)."],
  "fallback": null,
  "thresholds_version": "1.0",
  "seed": 42,
  "created_at": "2026-11-14T17:30:00Z"
}
```

### 37.8 Plots

FS.P.PRICE (price with CUSUM events), FS.P.VOL (daily volatility estimate), FS.P.BARRIERS (sample events drawn with their three barriers), FS.P.LABEL_BALANCE (label share bar), FS.P.GRID (heatmap of minority share / effective n over the parameter grid), FS.P.UNIQUENESS (histogram of uniqueness and concurrency over time), FS.P.HOLDING (holding-period distribution), FS.P.MIN_FFD (ADF statistic vs d from `plot_min_ffd`), FS.P.SADF (SADF statistic over time), FS.P.TRENDSCAN (t-value series).

### 37.9 API, data and UI

* `POST /api/v1/datasets/{id}/financial-suitability` → job id; `GET /api/v1/suitability/{report_id}`.
* DDL: `suitability_reports(id uuid pk, workspace_id uuid, dataset_version_id uuid, asset text, status text, report jsonb, thresholds jsonb, created_by uuid, created_at timestamptz)` with RLS by workspace (§39).
* UI: **Financial → Label suitability** card before the Labels step: traffic-light table of FS1–FS20, per-method verdict chips, grid heatmap, recommendations list, buttons "Use recommended settings", "Customise", "Fall back to standard target". Financial labels stay disabled while the status is Not suitable unless an admin sets `allow_override` (logged).
* Tests: golden datasets — NIFTY50 daily (DS30, expect Suitable), airline passengers (not prices, expect Not suitable → forecasting fallback), synthetic stale-price series (FS8 FAIL), 300-bar series (FS6 FAIL).

---

## 38. VLM decision agent — the model looks at plots and drives decisions

> Round-2 addition. §23 makes the VLM *explain*. This section makes it *decide*: at fixed decision points the agent renders the relevant plots, sends the images plus a FACTS JSON to the VLM, receives a structured **proposal**, checks it against deterministic **guards**, shows it to the user for **approval**, applies it as a new versioned config, and logs everything. The user can switch each decision point between **Auto-propose (default)**, **Auto-apply when guards pass and confidence is high** (off by default, admin-enabled per workspace) and **Manual**.

### 38.1 Principles

1. **Numbers beat pictures.** Every decision has a rule-based baseline computed first; the VLM may agree, refine or disagree, but must cite FACTS. If its proposal violates a guard, the guard wins.
2. **Human approval by default.** No decision changes a dataset, recipe, model or report without an Approve click (or an explicit auto-apply policy).
3. **Bounded action space.** The VLM chooses from enumerated options produced by the lab (e.g. k ∈ {2…10}, scaler ∈ registry), never free-form code.
4. **Reproducible.** Inputs hashed (images + FACTS + prompt version + model + seed); identical inputs return the cached decision.
5. **Graceful degradation.** No VLM reachable → the rule baseline is shown as the proposal, labelled "numbers-only".

### 38.2 Decision points

| ID | Decision | When | Images sent | FACTS sent | Options (action space) | Rule baseline | Guards (hard) |
|---|---|---|---|---|---|---|---|
| VD1 | Task family & roles confirmation | after Intake (§33) | missingness matrix, line plot of candidate index, target distribution | intake profile, D1–D8 scores | family ∈ {supervised-tabular, supervised-sequential, financial, unsupervised, time series}; role per column | §33 softmax | leakage rules §33.5; user-locked roles never changed |
| VD2 | Preprocessing recipe | after EDA | histograms (skewed cols), box plots, missingness heatmap, correlation heatmap, VIF bar, class balance | skew, kurtosis, missing %, MCAR test, VIF, cardinality, outlier %, imbalance ratio | per column: imputer, transform, encoder, scaler, outlier action; imbalance method; drop | §23.3 rule engine | no target-aware step outside CV; no drop of target/index; encoders compatible with chosen models; leakage-safe order |
| VD3 | Model families to run | after preprocessing | learning curve of a quick baseline, PCA 2D, target vs top features | n, p, p/n, categorical share, linearity test (RESET), nonlinearity hint from baseline gap (linear vs GBM), class count, imbalance, time budget, GPU available | subset of registry families + depth preset (Quick/Balanced/Thorough) | size/shape heuristics table (§12) | TabPFN only if licence flag on; GPU-only models only if a GPU worker exists; time budget respected |
| VD4 | CV scheme | with VD3 | timeline plot of index, ACF of target, group sizes | sequential flag, groups, label horizon, n | from §13 registry | §13 decision rules | sequential data → never shuffled K-fold; financial → purged/CPCV with embargo ≥ label horizon |
| VD5 | Forecast horizon h and season m | TS setup | line plot, ACF/PACF, periodogram, STL | n, frequency, detected periods, horizon guard numbers (§20) | h ∈ [1, h_max]; m ∈ candidate periods | §20 HorizonGuard h* | h ≤ h_max (§20) always; m must be a candidate with evidence |
| VD6 | Differencing / transform for TS | TS analysis | ACF before/after differencing, rolling std, Box-Cox profile | ADF/KPSS/PP/ZA table, ndiffs/nsdiffs, Guerrero λ | d ∈ {0,1,2}, D ∈ {0,1}, Box-Cox λ or none | stationarity verdict matrix (§35.1) | d + D ≤ 2; λ only for positive series |
| VD7 | Number of components (DR) | DR results | scree, cumulative variance, parallel analysis, reconstruction error curve | eigenvalues, Kaiser, broken-stick, parallel analysis, KMO/Bartlett | k ∈ [1, min(p, 50)] | parallel analysis k | Bartlett p < 0.05 required for PCA/FA recommendation; KMO < 0.5 → propose "DR not advised" |
| VD8 | Number of clusters k and algorithm | clustering k-scan | elbow, silhouette/CH/DB/gap vs k, silhouette plot for top-2 k, UMAP scatter coloured by top-2 k, k-distance | CLU.T.KSELECT, stability ARI | k ∈ [2, 15] (or "density-based, k free"); algorithm ∈ run set | majority vote of criteria with stability ≥ 0.75 | chosen k must have stability ≥ 0.6 and no cluster < 2% of rows (unless anomaly use) |
| VD9 | Financial label suitability and label parameters | after §37 | FS.P.GRID, FS.P.BARRIERS, FS.P.LABEL_BALANCE, FS.P.VOL | suitability report | method ∈ suitable methods; grid cell; or fallback | §37.6 default cell | any required FAIL → financial labels not selectable; VLM can only choose among SUITABLE / cautions methods |
| VD10 | Champion model | after leaderboard | leaderboard bars, CD diagram, calibration/residual plots of top-3, learning curves of top-3 | leaderboard table, Friedman/Nemenyi or DM results, DSR/PBO for financial, latency, size | champion + challenger among top-N | best mean primary metric | statistically indistinguishable (CD group / DM p > 0.05) → prefer simpler/faster unless justified; financial: champion rule §32.7 (DSR > 0.95, PBO < 0.2, WFE ≥ 0.5…) must pass |
| VD11 | Calibration / threshold | after champion | CLE.P.RELIABILITY, CLE.P.THRESHOLD_METRICS, CLE.P.COST_CURVE, CLE.P.THRESHOLD_STABILITY (§41) | CLE.T.CALIBRATION_TESTS, CLE.T.THRESHOLD_CHOICE, cost matrix | calibrator ∈ {none, sigmoid, isotonic, temperature, Venn–Abers}; threshold method from §41.6 and t | min expected cost / Youden | calibrator and threshold fitted on training OOF only; test split never read |
| VD12 | Retrain / drift action | prediction monitoring | PSI per feature bar, score distribution over time | PSI, KS, performance decay | {no action, recalibrate, retrain, alert} | PSI > 0.25 → retrain | never auto-retrain in production without approval |

### 38.3 Agent loop

```
for decision_point in pipeline.enabled_decisions:
    1. OBSERVE    render required plots (kaleido PNG 1024×640 sized per §40.4, tiles for grids) + build FACTS (fact_id → value)
    2. BASELINE   rule engine → baseline proposal + reasons
    3. PROPOSE    hosted VLM call (§40 vision_standard chain): system prompt + decision template + FACTS + images + option list + baseline
                  → JSON (schema §38.5), constrained decoding, temperature 0.2, seed 42
    4. VERIFY     schema validation; numbers in rationale must match FACTS; option must be in action space;
                  one repair round on failure, else fall back to baseline
    5. GUARD      run hard guards; violations → proposal marked BLOCKED with reasons, baseline offered
    6. REVIEW     UI decision card: baseline vs VLM proposal side by side, images, cited facts,
                  confidence, diff of the config change → [Approve] [Edit & approve] [Reject] [Use baseline]
                  (auto-apply only if policy on AND guards pass AND confidence = high AND VLM == baseline or within tolerance)
    7. APPLY      write a new versioned config (recipe / task_spec / training plan); downstream jobs enqueued
    8. LOG        decisions table: inputs hash, images ids, FACTS, prompt version, model, raw output,
                  guard results, user action, final config diff, latency
    9. LEARN      user edits stored as feedback (intake_feedback / decision_feedback) for prompt few-shot examples
```

Optional **reflection step** (Thorough mode): after APPLY and the downstream job completes, the agent receives the new plots (e.g. post-transform histograms, new leaderboard) and checks whether the expected effect happened ("skew reduced from 2.4 to 0.3"); if not it proposes a revert. Maximum 2 iterations per decision point to bound cost.

### 38.4 Prompt template (example VD8 — number of clusters)

```
SYSTEM: You are the ARW ML Lab decision assistant. You see charts and a FACTS JSON.
Choose ONE option from OPTIONS. Use only numbers present in FACTS and cite fact_ids.
If the charts and FACTS disagree, trust FACTS. If no option is well supported, choose
"defer_to_baseline". Output JSON matching the schema exactly.

USER:
DECISION: VD8 number_of_clusters
CONTEXT: dataset "mall_customers" v2, 200 rows, 3 numeric features scaled (standard), seed 42.
BASELINE: {"k": 5, "algorithm": "kmeans", "reason": "silhouette max (F3) and stability 0.91 (F9)"}
OPTIONS: k in [2..10]; algorithm in ["kmeans","gmm_full","agglomerative_ward","hdbscan"]
FACTS: {"F1":{"k":4,"silhouette":0.405}, "F2":{"k":5,"silhouette":0.444}, ... }
IMAGES: [1] elbow, [2] silhouette vs k, [3] gap statistic, [4] silhouette plot k=5, [5] UMAP coloured k=5, [6] UMAP coloured k=6
TASK: Look at the charts. Is the elbow clear? Are clusters separated in [5]? Any cluster with mostly negative silhouettes in [4]? Recommend k and algorithm.
```

### 38.5 Decision output schema (shared by all decision points)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["decision_id", "choice", "agrees_with_baseline", "rationale", "evidence", "confidence"],
  "properties": {
    "decision_id": {"enum": ["VD1","VD2","VD3","VD4","VD5","VD6","VD7","VD8","VD9","VD10","VD11","VD12"]},
    "choice": {"type": "object", "description": "decision-specific payload validated by a per-decision sub-schema, e.g. {\"k\":5,\"algorithm\":\"kmeans\"}"},
    "agrees_with_baseline": {"type": "boolean"},
    "alternatives": {"type": "array", "maxItems": 3, "items": {"type": "object", "required": ["choice", "why_not"], "properties": {"choice": {"type": "object"}, "why_not": {"type": "string"}}}},
    "rationale": {"type": "string", "maxLength": 1200},
    "visual_observations": {"type": "array", "items": {"type": "object", "required": ["image_index", "observation"], "properties": {"image_index": {"type": "integer"}, "observation": {"type": "string"}}}},
    "evidence": {"type": "array", "minItems": 1, "items": {"type": "string", "description": "fact_id or artefact_id"}},
    "risks": {"type": "array", "items": {"type": "string"}},
    "expected_effect": {"type": "string", "description": "checked by the reflection step"},
    "confidence": {"enum": ["low", "medium", "high"]}
  }
}
```

Per-decision `choice` sub-schemas (examples):

| Decision | `choice` sub-schema |
|---|---|
| VD2 | `{"steps":[{"columns":[str],"step":enum(registry),"params":object}], "imbalance": enum\|null, "drop":[str]}` |
| VD3 | `{"families":[enum], "preset": enum("quick","balanced","thorough"), "max_models": int ≤ 40}` |
| VD5 | `{"h": int, "m": int, "reason_h_below_cap": str}` |
| VD7 | `{"k": int, "method": enum("pca","fa","ica","nmf","umap",...), "rotation": enum\|null}` |
| VD8 | `{"k": int\|null, "algorithm": enum}` |
| VD9 | `{"method": enum("triple_barrier","meta_labeling","fixed_horizon","trend_scanning","fallback"), "pt_sl":[num,num], "vertical_bars": int, "cusum_mult": num}` |
| VD10 | `{"champion": model_id, "challenger": model_id\|null, "ensemble": [model_id]\|null}` |

### 38.6 Data, API, UI

* DDL: `decisions(id uuid pk, workspace_id, run_id, decision_point text, status text check in ('proposed','blocked','approved','edited','rejected','auto_applied','reverted'), baseline jsonb, proposal jsonb, guard_results jsonb, final_choice jsonb, inputs_hash text, image_artefact_ids uuid[], prompt_version text, model_name text, latency_ms int, decided_by uuid, decided_at timestamptz, created_at timestamptz)`; `decision_feedback(decision_id, user_edit jsonb, comment text)`.
* API: `POST /api/v1/runs/{id}/decisions/{point}:propose`, `GET /api/v1/decisions/{id}`, `POST /api/v1/decisions/{id}:approve|reject|edit`, `GET /api/v1/runs/{id}/decisions` (audit trail).
* UI: **Decision cards** appear inline in the workflow (stepper) and in an **Agent timeline** drawer (every decision with status chips, images, diff). A workspace setting page lists the 12 decision points with mode toggles (Manual / Propose / Auto-apply).
* Queue: `q.insights` (hosted AI calls, §40); concurrency 2 per worker under the shared provider rate limit; timeout 90 s per call (Deep 180 s); total per decision ≤ 3 calls.
* Evaluation harness: golden decision set (DS1–DS33 with expected decisions, e.g. airline m = 12, mall_customers k = 5, iris DR k = 2) → agreement rate with baseline and with expected answers tracked per model/prompt version; promotion of a new VLM or prompt requires ≥ the previous agreement and zero guard violations.

---

## 39. Deployment — GitHub monorepo, Vercel, Render and Supabase (primary path)

> Round-2 addition (deployment steering). This is now the **primary deployment path** and replaces the Kubernetes/KEDA plan in §4 and §8. Kubernetes stays as an optional later scale-out (§39.12). Plan sizes and limits were checked on vendor pages in Nov 2026; re-check before buying (§31).

### 39.1 Topology

```
                         GitHub monorepo (arw-ml-lab)
               ┌──────────────┼───────────────────────────┐
               ▼              ▼                           ▼
      Vercel (frontend/)   Render Blueprint (render.yaml)  Supabase project
      Next.js 16 BFF       ├─ web: lab-api (FastAPI)        ├─ Postgres 17 (+ RLS)
      UI, auth session,    ├─ worker: lab-worker-light       ├─ Auth (email OTP / magic link, SSO later)
      thin API proxy       │   (q.ingest, q.eda, q.insights, ├─ Storage buckets: datasets, artefacts,
      NO heavy compute     │    q.report, q.predict.batch)   │   models, reports, plots
               │           ├─ worker: lab-worker-train       └─ CLI migrations (supabase/migrations)
               │           │   (q.train.cpu, q.tune,
               │           │    q.explain, q.forecast)
               │           ├─ worker (optional): lab-beat (Celery beat schedules)
               │           └─ keyvalue: lab-kv (Celery broker + result cache, noeviction)
               │                        │
               └── HTTPS (JWT) ─────────┘
                                        ├── HTTPS → NVIDIA API catalog (integrate.api.nvidia.com/v1)
                                        │          VLM + text LLM, NVIDIA_API_KEY on Render only (§40)
                                        └── optional: external GPU worker for q.train.gpu (heavy DL only)
```

Browser → Vercel (pages, BFF routes) → Render `lab-api` (REST + SSE progress) → Celery on Render Key Value → workers read/write Supabase Postgres and Storage. File uploads go **directly from the browser to Supabase Storage** using signed upload URLs (resumable/TUS for large files) — they never pass through a Vercel function.

### 39.2 Responsibilities by platform

| Concern | Platform | Notes |
|---|---|---|
| UI, routing, server components, session cookie | Vercel | Next.js 16 app in `frontend/` (project Root Directory = `frontend`) |
| BFF API routes | Vercel functions | only auth checks, proxying, signed URL issuance, light aggregation; each < 10 s; no pandas/sklearn |
| Lab REST API + SSE | Render web service `lab-api` | FastAPI + uvicorn workers; validates JWT from Supabase; enqueues jobs |
| Training, tuning, EDA, explainability, forecasting | Render background workers | Celery 5; two pools split by weight |
| Broker / cache | Render Key Value | Valkey/Redis-compatible; `maxmemoryPolicy: noeviction` (required for a queue); internal-only (`ipAllowList: []`) |
| Relational data | Supabase Postgres | all §7, §32, §33, §37, §38 tables; RLS by workspace |
| Auth | Supabase Auth | email OTP / magic link (company domain allow-list), optional Google/Microsoft SSO; replaces the custom OTP + jose flow from sp-workstation (the UI keeps the sp-workstation look) |
| Object storage | Supabase Storage | replaces MinIO; S3-compatible endpoint used by MLflow and boto3 |
| Experiment tracking | Render web service (optional) | MLflow 3 tracking server **optional** as a small Render web service (backend store = Supabase Postgres schema `mlflow`, artefacts = Supabase Storage S3 endpoint); default = the lab's own registry tables (§25) to save cost |
| VLM / LLM | hosted NVIDIA API catalog (+ optional fallback providers), called from Render only | see §39.8 and §40 |
| GPU training | external GPU worker (optional) | same Celery app, listens on `q.train.gpu` only |

### 39.3 Render sizing (compute plans, Nov 2026)

| Service | Recommended plan | Why | Scale |
|---|---|---|---|
| `lab-api` (web) | `1c-2g` (≈ $25/mo) for pilot; `2c-4g` (≈ $85) for team use | API is I/O-bound; no training in-process | autoscale 1–3 instances on CPU 70% (paid workspace) |
| `lab-worker-light` (worker) | `2c-4g` | EDA on ≤ 1 M rows, profiling, report rendering (kaleido), insights orchestration | concurrency 2 |
| `lab-worker-train` (worker) | `4c-16g` (≈ $225) default; `8c-32g` (≈ $450) for Thorough tuning, large GBM/RF grids, CPCV with many paths | sklearn/LightGBM/XGBoost/CatBoost and small CPU DL (MLP, small LSTM/TCN, N-HiTS) | concurrency = 1 job per 4 vCPU (`--concurrency 1`, `n_jobs = cpu_count`), prefetch multiplier 1, `acks_late` |
| `lab-beat` (cron job) | `0.5c-512mb` Render cron job, hourly | cleanup: expired prediction files (`expired_prediction_jobs()`), stale-heartbeat reaper, storage lifecycle; drift checks later (v2.2: required, defined in `render.yaml`) | single run at a time |
| `lab-kv` (Key Value) | `1g` (≈ $20) | broker + result backend + small caches; paid tiers persist to disk | upgrade to 3g with many concurrent runs |
| MLflow (optional web) | `0.5c-512mb` – `1c-2g` | UI + tracking API only | |

Free Render plans are not used for workers (not available for background workers) and the free Key Value tier (25 MB, no persistence) is only for demos.

**Job limits** (Celery): soft/hard time limits per queue — q.eda 15/20 min; q.train.cpu 90/120 min; q.tune 4/5 h (Optuna study checkpointed every trial in Postgres → resumable); q.explain 30/40 min; q.forecast 60/90 min; q.insights 5/6 min; q.report 10/15 min; q.ingest 10/15 min; q.predict.batch 30/45 min; q.predict.heavy 60/90 min (v2.2, §46.2). Memory guard: workers check estimated RAM (rows × cols × 8 B × model factor) before starting and refuse with a clear message ("needs ~22 GB; current worker 16 GB; choose Quick mode or sample") instead of being OOM-killed. `worker_max_tasks_per_child = 20` and `worker_max_memory_per_child` to recycle leaky processes. Graceful shutdown: `maxShutdownDelaySeconds: 300` so deploys do not kill a running trial mid-write.

**Artefacts**: workers never rely on local disk (Render instance disks are ephemeral); every model (`joblib`/`skops`/ONNX/TorchScript), plot JSON/PNG, report and dataset parquet is written to Supabase Storage under `workspace_id/…`; Postgres keeps only metadata and paths.

### 39.4 Vercel constraints and rules

| Limit (Nov 2026) | Value | Rule in the lab |
|---|---|---|
| Request/response body | 4.5 MB | uploads via Supabase signed upload URL (TUS resumable for > 6 MB); large downloads via signed download URLs |
| Function duration | Hobby 300 s; Pro 800 s default max | BFF routes must finish < 10 s; long work is always a Render job + SSE |
| Function memory/CPU | Hobby 2 GB / 1 vCPU; Pro up to 4 GB / 2 vCPU | no data processing on Vercel |
| Bundle size | 250 MB uncompressed (Node) | no Python on Vercel |
| SSE | streaming supported, but long streams count as duration | the browser connects **directly** to `lab-api` SSE (CORS allow-list), not through Vercel |

Plan: Vercel Pro is recommended for a company deployment (team access, higher limits); Hobby is for personal, non-commercial use only per Vercel's terms.

### 39.5 Supabase design

* **Plan**: Pro ($25/mo base; 8 GB disk included, 100 GB storage, daily backups; no pausing). Free tier pauses after a week of inactivity and caps files at 50 MB → demo only.
* **Schemas**: `public` (app tables), `lab` (heavy run tables if separated), `mlflow` (optional), `storage` (managed).
* **Migrations**: `supabase/migrations/<timestamp>_<name>.sql`, created with `supabase migration new`, tested locally with `supabase start` + `supabase db reset`, applied by CI with `supabase link --project-ref $SUPABASE_PROJECT_ID` + `supabase db push --remote --yes`. Never edit applied migrations; add new ones.
* **RLS**: enabled on every table. Membership table `workspace_members(workspace_id, user_id, role)`; helper `is_member(ws uuid)` (SECURITY DEFINER, stable) used in policies `using (is_member(workspace_id))`; writes restricted by role (`viewer` read-only, `analyst` create runs, `admin` manage settings/overrides). The Render backend uses the **service-role key** only server-side and still sets `workspace_id` explicitly; the frontend uses the anon/publishable key + user JWT so RLS applies.
* **Storage buckets** (private): `datasets` (max 5 GB/object on Pro with resumable upload), `artefacts`, `models`, `reports`, `plots`. Object path convention `{workspace_id}/{entity}/{id}/{file}`; storage policies check `is_member((storage.foldername(name))[1]::uuid)`.
* **Auth**: email OTP with allowed domain list (`@rathi.com` etc., configurable), JWT verified in FastAPI with the project JWKS (asymmetric signing keys) — no shared secret in the API. Custom claims (workspace roles) via an Auth hook or looked up per request.
* **Connection**: backend uses the Supavisor pooler (transaction mode, port 6543) for short API queries and a session-mode/direct connection for long worker transactions and Optuna storage; SQLAlchemy `pool_pre_ping`, small pools (API 5, worker 2) to stay within connection limits.
* **Realtime (optional)**: job status rows can also be pushed via Supabase Realtime to the UI as a fallback to SSE.

### 39.6 Repository layout (monorepo)

```
arw-ml-lab/
├─ frontend/            Next.js 16 app (Vercel Root Directory), vercel.json
├─ backend/             FastAPI app (lab-api), Celery app + task modules, Dockerfile
├─ labcore/             pure-Python ML library (registry, recipes, CV, metrics, plots, insights, financial)
├─ supabase/            config.toml, migrations/*.sql, seed.sql, policies
├─ tests/               unit, contract, golden, e2e (Playwright)
├─ data/samples/        sample datasets + manifest; predict/ (prediction samples + contracts, §45.9)
├─ scripts/             make_predict_samples.py
├─ docs/                ARCHITECTURE.md, FLOWCHART.md, diagrams/
├─ .cursor/rules/       Cursor project rules (*.mdc)
├─ .github/workflows/   ci.yml, deploy.yml
├─ render.yaml          Render Blueprint
├─ AGENTS.md, CURSOR_PROMPT.md, README.md, .env.example, .gitignore
```

### 39.7 render.yaml (blueprint, abridged — the full file ships in the kit)

```yaml
services:
  - type: web
    name: lab-api
    runtime: docker
    rootDir: .
    dockerfilePath: ./backend/Dockerfile
    dockerCommand: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 2
    plan: 1c-2g
    region: singapore
    healthCheckPath: /healthz
    autoDeployTrigger: "off"   # deploy.yml deploys after migrations (§46.2 OPS-11)
    envVars:
      - fromGroup: lab-shared
      - key: REDIS_URL
        fromService: {type: keyvalue, name: lab-kv, property: connectionString}
  - type: worker
    name: lab-worker-light
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    dockerCommand: celery -A backend.worker.celery_app worker -Q q.ingest,q.eda,q.insights,q.report,q.predict.batch --concurrency 2 --prefetch-multiplier 1
    plan: 2c-4g
    region: singapore
    maxShutdownDelaySeconds: 300
    envVars: [...]
  - type: worker
    name: lab-worker-train
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    dockerCommand: celery -A backend.worker.celery_app worker -Q q.train.cpu,q.tune,q.explain,q.forecast,q.predict.heavy --concurrency 1 --prefetch-multiplier 1
    plan: 4c-16g
    region: singapore
    maxShutdownDelaySeconds: 300
    envVars: [...]
  - type: keyvalue
    name: lab-kv
    plan: 1g
    region: singapore
    maxmemoryPolicy: noeviction
    ipAllowList: []
envVarGroups:
  - name: lab-shared
    envVars:
      - {key: SUPABASE_URL, sync: false}
      - {key: SUPABASE_SERVICE_ROLE_KEY, sync: false}
      - {key: DATABASE_URL, sync: false}
      - {key: NVIDIA_API_KEY, sync: false}
      - {key: AI_PROVIDER_PRIMARY, value: nvidia}
```

Region: Singapore is the closest Render region to India; choose the Supabase project region `ap-south-1` (Mumbai) or Singapore to keep latency low — keep Render and Supabase in nearby regions because workers move large data.

### 39.8 AI (VLM/LLM) in the hosted deployment

No model is hosted by the lab. Render workers call the **NVIDIA API catalog** over HTTPS (`AI_BASE_URL=https://integrate.api.nvidia.com/v1`, `NVIDIA_API_KEY` as a Render secret on `lab-api` and the workers only). Fallback providers (Gemini, OpenRouter, Groq) are optional and off by default. When no provider is reachable, budgets are exhausted or the workspace is `restricted`, the lab uses **numbers-only mode** (rule engine + rule baselines). Full design in §40. This removes the need for any GPU host for AI features; a GPU worker is only an option for heavy DL training (§34.9).

### 39.9 CI/CD (GitHub Actions)

| Workflow | Trigger | Jobs |
|---|---|---|
| `ci.yml` | pull request, push | **frontend**: pnpm install, lint (eslint), typecheck (tsc), unit (vitest), build. **backend**: uv sync, ruff, mypy, pytest (unit + contract + golden on small samples, seed 42). **supabase**: `supabase start` (Docker), `supabase db reset` (applies all migrations), RLS tests (pgTAP via `supabase test db`). **e2e** (nightly or label): Playwright against a preview stack |
| `deploy.yml` | push to `main` after CI passes | 1. `supabase link` + `supabase db push --remote --yes` (migrations first); 2. trigger Render deploys via deploy hooks (`RENDER_DEPLOY_HOOK_API`, `_WORKER_LIGHT`, `_WORKER_TRAIN`) (services use `autoDeployTrigger: "off"` so they never deploy before the migrations); 3. Vercel deploy via Git integration (preferred) or `vercel deploy --prod --token $VERCEL_TOKEN`; 4. smoke tests: `GET /healthz`, auth round-trip, enqueue a 5-second sample EDA job on DS1 and wait for success |

Preview environments: Vercel preview per PR (points to a staging API); Render preview environments optional (paid); Supabase branching optional. Secrets live in GitHub Actions secrets, Vercel and Render env settings — never in the repo.

### 39.10 Environment-variable matrix

| Variable | Vercel (frontend) | Render api | Render workers | GitHub Actions | Local `.env` |
|---|---|---|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | ✔ | | | | ✔ |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` (publishable) | ✔ | | | | ✔ |
| `NEXT_PUBLIC_LAB_API_URL` | ✔ | | | | ✔ |
| `SUPABASE_URL` | | ✔ | ✔ | | ✔ |
| `SUPABASE_SERVICE_ROLE_KEY` (secret) | | ✔ | ✔ | | ✔ |
| `SUPABASE_JWKS_URL` | | ✔ | | | ✔ |
| `DATABASE_URL` (pooler, transaction) | | ✔ | | | ✔ |
| `DATABASE_URL_SESSION` (session/direct) | | | ✔ | | ✔ |
| `SUPABASE_S3_ENDPOINT`, `SUPABASE_S3_ACCESS_KEY_ID`, `SUPABASE_S3_SECRET_ACCESS_KEY`, `SUPABASE_S3_REGION` | | ✔ | ✔ | | ✔ |
| `STORAGE_BUCKET_*` (datasets, artefacts, models, reports, plots, predictions) | | ✔ | ✔ | | ✔ |
| `REDIS_URL` | | ✔ (from Key Value) | ✔ | | ✔ |
| `CORS_ALLOWED_ORIGINS` | | ✔ | | | ✔ |
| `AI_ENABLED`, `AI_PROVIDER_PRIMARY=nvidia`, `AI_BASE_URL`, `AI_VISION_CHAIN`, `AI_TEXT_CHAIN`, `AI_RPM_LIMIT`, `AI_DAILY_REQUEST_CAP` | | ✔ | ✔ | | ✔ |
| `NVIDIA_API_KEY` (secret; **backend only**) | ✘ never | ✔ | ✔ | (optional, for a manual live smoke test) | ✔ |
| `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `GROQ_API_KEY` (optional fallbacks, secrets) | ✘ never | ✔ | ✔ | | ✔ |
| `MLFLOW_TRACKING_URI` (optional) | | ✔ | ✔ | | ✔ |
| `LAB_DEFAULT_SEED=42`, `LAB_MAX_ROWS`, `LAB_JOB_SOFT_LIMIT_*`, `LAB_JOB_HARD_LIMIT_*` | | ✔ | ✔ | | ✔ |
| `LAB_PREDICT_MAX_MB`, `LAB_PREDICT_MAX_ROWS`, `LAB_PREDICT_CHUNK_ROWS`, `LAB_PREDICT_RETENTION_DAYS` (§45.8) | | ✔ | ✔ | | ✔ |
| `AI_USER_DAILY_REQUEST_CAP`, `AI_IMAGE_MAX_B64_BYTES`, `AI_VISION_FAST_CHAIN`, `AI_TEXT_DEEP_CHAIN` (defaults in code; override only) | | ✔ | ✔ | | ✔ |
| `TABPFN_ENABLED=false`, `TABPFN_TOKEN` | | | ✔ | | ✔ |
| `SENTRY_DSN` (optional, backend) | | ✔ | ✔ | | ✔ |
| `NEXT_PUBLIC_SENTRY_DSN` (optional, browser; public by design), `SENTRY_ENVIRONMENT` | ✔ | ✔ | ✔ | | ✔ |
| `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, `SUPABASE_PROJECT_ID` | | | | ✔ | |
| `RENDER_DEPLOY_HOOK_*`, `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` | | | | ✔ | |
| `LAB_API_URL` (GitHub Actions variable for the deploy smoke test) | | | | ✔ | |

### 39.11 Security notes

Service-role key only on Render (never `NEXT_PUBLIC_*`); RLS tested in CI; signed URLs expire in 10 min (upload) / 60 min (download); Key Value internal-only; CORS allow-list = Vercel production + preview domains; rate limiting on `lab-api` (per user, per IP); audit log table for decisions/overrides; PII columns redacted before any VLM call; backups via Supabase daily backups (PITR add-on for production).

### 39.12 Optional later scale-out (Kubernetes)

When concurrent heavy training outgrows Render workers (e.g. > 4 simultaneous Thorough runs or regular GPU training), move only the **workers** to Kubernetes (GKE/EKS/AKS or on-prem) with KEDA scaling on Redis queue length and a GPU node pool for `q.train.gpu`; keep Vercel, Supabase and `lab-api` unchanged. The earlier K8s/KEDA notes in §4 and §8 describe this path.

### 39.13 Deployment acceptance criteria

1. `render.yaml` validates (Render Blueprint sync succeeds) and creates lab-api, two workers, the `lab-beat` cron job and lab-kv.
2. `supabase db push` applies all migrations to an empty project; `supabase test db` RLS tests pass (a user cannot read another workspace's rows or objects).
3. Vercel production build succeeds with Root Directory `frontend`; no server bundle imports Python or data libraries.
4. Upload of a 200 MB CSV goes browser → Supabase Storage (resumable) without touching Vercel functions.
5. Sample flow on DS1 (EDA → train Quick → leaderboard → explain → predict) completes on the hosted stack; artefacts appear in Storage; job status streams over SSE.
6. Killing a worker mid-tuning and restarting resumes the Optuna study.
7. With the AI provider unreachable (or `NVIDIA_API_KEY` unset), insights and decisions fall back to numbers-only within 10 s; `NVIDIA_API_KEY` is absent from the Vercel project and from every client bundle (CI grep test).
8. CI blocks merge on lint/type/test/RLS failures; deploy workflow runs migrations before services.
9. The Supabase project is on Pro with the global file size limit ≥ 2 GB (Free caps uploads at 50 MB); bucket limits match `supabase/config.toml` (datasets 500 MB, predictions 50 MB, models 2 GB).

---

## 40. AI provider layer — hosted VLM/LLM via NVIDIA API catalog (primary), swappable providers

> Round-2 change (user decision, 14 Nov 2026): the lab does **not** self-host the vision-language model. AI Insights (§23), the Intake adjudicator (§33.9) and the VLM decision agent (§38) call a **hosted, OpenAI-compatible API**. The primary provider is the **NVIDIA API catalog** (build.nvidia.com, NIM endpoints at `https://integrate.api.nvidia.com/v1`). A provider abstraction allows Google Gemini API, OpenRouter, Groq or any OpenAI-compatible endpoint to be added as fallbacks. **Numbers-only mode** (rule engine, no model) stays as the offline fallback. As a result no GPU host is needed for AI features; Ollama/vLLM self-hosting is removed from the primary design (kept only as an optional provider entry, §40.3).

### 40.1 What NVIDIA hosts (checked live on 14 Nov 2026, IST)

The public model list `GET https://integrate.api.nvidia.com/v1/models` (83 models) and the build.nvidia.com catalog / API reference were checked on 14 Nov 2026. Vision-capable chat models relevant to chart and table reading:

| Model ID (on `/v1/models`) | Publisher / size | Inputs | Licence / terms (model card) | Role in the lab |
|---|---|---|---|---|
| `nvidia/nemotron-3.5-super-vl-120b-a12b` | NVIDIA, 120B MoE (12B active), Mamba-2/Transformer hybrid, C-RADIO vision encoder, context up to 1M | text, image, video | OpenMDW-1.1; "ready for commercial or non-commercial use"; trial governed by NVIDIA API Trial Terms | **Primary VLM** (deep/standard insights, decisions) |
| `google/gemma-4-31b-it` | Google DeepMind, 30.7B dense, 256K context, visual token budgets 70–1120 | text, image, video frames | NVIDIA Open Model License + Apache-2.0; commercial/non-commercial | **Fallback VLM 1** (use visual budget 1120 for small chart text) |
| `meta/llama-3.2-90b-vision-instruct` | Meta, 90B | text, image | Llama Community Licence | **Fallback VLM 2** |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | NVIDIA, 30B MoE (3B active) | text, image, video, audio | NVIDIA open model licence | **Fast tier** (brief insights, per-artefact map step) |
| `google/gemma-3-12b-it`, `microsoft/phi-3-vision-128k-instruct`, `nvidia/cosmos-reason2-8b`, `mistralai/mistral-large-4-1t-a52b`, `z-ai/glm-5.3-flash`, `stepfun-ai/step-5-preview`, `meta/muse-glimmer-30b` | various | image + text | per card | watch-list / alternates (config only) |
| `google/deplot` | Google | chart image → data table | per card | optional cross-check: extract the table from a chart and compare to the artefact `numbers` |
| `nvidia/nemotron-parse-2.0` | NVIDIA | page image → text/tables | per card | optional: reading uploaded PDF/scan tables (not core) |

Text reasoning LLMs (for numbers-heavy stages, the Intake adjudicator in text mode, report narratives, chat):

| Model ID | Role |
|---|---|
| `nvidia/nemotron-3-super-120b-a12b` | **Primary text reasoning LLM** |
| `deepseek-ai/deepseek-v4.1-flash` | Fallback text LLM 1 (fast) |
| `nvidia/nemotron-3-ultra-550b-a55b` | "Deep" mode for leaderboard / WFO verdict narratives (higher latency) |
| `openai/gpt-oss-20b` | Fallback text LLM 2 (light) |

Notes: `meta/llama-3.2-11b-vision-instruct` appears in the web catalog but not in the `/v1/models` list returned on 14 Nov 2026, so it is not used. NVIDIA forum reports show that some listed models can return 404 "not found for account" for particular keys, so the lab **probes every configured model at startup** (§40.6) and drops unavailable ones from the chain. Model IDs change when NVIDIA updates versions; they live in config, never in code.

### 40.2 Terms, limits and cost (what is known)

* **Free access:** an NVIDIA Developer account gives an API key with no credit card. Per NVIDIA staff on the developer forum (Sep 2025), the old credit system was replaced by **per-model rate limits that NVIDIA does not publish**; the account's limit is shown on build.nvidia.com. Third-party reports in Oct–Nov 2026 still mention ~1,000 credits/month and **~40 requests/minute** observed on free accounts. Design for **≤ 40 RPM and occasional 429s**.
* **Trial scope:** the free API is a **trial for prototyping, research, development and testing**. Moving to production requires an **NVIDIA AI Enterprise licence**, a paid partner endpoint from the model's "Deploy" tab, or another paid provider. ⚠ This is an open item for the user (§31): the hosted free tier is fine for the build and pilot; production use needs a licence decision.
* **Data egress:** hosted calls send prompts and images to NVIDIA (or the fallback provider). The lab only sends rendered **aggregate** plots and FACTS JSON (no raw rows, PII redacted, §40.8). Workspaces classified "restricted" use numbers-only mode.
* **Images:** for inline base64 images NVIDIA documents a **180 KB limit per image, measured on the base64 string**; larger images must be uploaded through the NVCF Assets API and referenced by asset ID. Only PNG/JPG/JPEG are accepted.
* **Structured output:** NIM supports `response_format: {type: "json_schema", …}` and `nvext` guided decoding (`guided_json`, `guided_choice`, `guided_regex`). Support can differ by hosted model, so the client sends `response_format` when the provider entry says `supports_json_schema: true` and **always** validates the result locally (§23.3 step 5).
* **Sampling:** the Nemotron 3.5 Super VL card recommends temperature 0.6 / top_p 0.95 for vision; the lab uses **temperature 0.2, top_p 0.9** for grounded JSON (lower variance) and records the values with every call. Reasoning ("thinking") is off by default for insights (`enable_thinking=false` via chat-template kwargs) and on for Deep mode and decisions VD3/VD10.

### 40.3 Provider abstraction

```
labcore/ai/
  providers.yaml          # provider registry (no secrets)
  client.py               # OpenAICompatClient (openai SDK, base_url per provider)
  router.py               # chain selection, health, circuit breakers, budgets
  images.py               # plot → PNG/JPEG sized for the provider's inline limit
  cache.py                # content-hash cache (Postgres insights/decisions tables + Key Value hot cache)
  budget.py               # token/request accounting per workspace/day
```

`providers.yaml` (defaults):

```yaml
providers:
  nvidia:
    base_url: https://integrate.api.nvidia.com/v1
    api_key_env: NVIDIA_API_KEY
    rpm_limit: 35                 # stay under the ~40 RPM observed on free accounts
    inline_image_max_b64_bytes: 180000
    image_formats: [png, jpeg]
    supports_json_schema: true
    extra_body_style: nvext       # guided_json via nvext when response_format is rejected
    enabled: true
  gemini:
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: GEMINI_API_KEY
    rpm_limit: 10
    enabled: false                # free tier content may be used by Google to improve products
  openrouter:
    base_url: https://openrouter.ai/api/v1
    api_key_env: OPENROUTER_API_KEY
    rpm_limit: 20                 # free models: 20 RPM, 50 req/day (1,000/day after a one-time credit purchase)
    enabled: false
  groq:
    base_url: https://api.groq.com/openai/v1
    api_key_env: GROQ_API_KEY
    rpm_limit: 30                 # image counts as ~2,048 input tokens; 8K TPM free → ~3 images/min
    enabled: false
  local_openai_compat:            # optional: any self-hosted OpenAI-compatible server (Ollama/vLLM) if ever wanted
    base_url_env: LOCAL_LLM_BASE_URL
    enabled: false

chains:                           # tried in order; each entry = provider:model
  vision_standard: [nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b, nvidia:google/gemma-4-31b-it, nvidia:meta/llama-3.2-90b-vision-instruct]
  vision_fast:     [nvidia:nvidia/nemotron-3-nano-omni-30b-a3b-reasoning, nvidia:google/gemma-4-31b-it]
  text_reasoning:  [nvidia:nvidia/nemotron-3-super-120b-a12b, nvidia:deepseek-ai/deepseek-v4.1-flash, nvidia:openai/gpt-oss-20b]
  text_deep:       [nvidia:nvidia/nemotron-3-ultra-550b-a55b, nvidia:nvidia/nemotron-3-super-120b-a12b]
  # fallback providers are appended only when enabled AND the workspace allows that provider
```

Which chain each feature uses:

| Feature | Chain | Images per call |
|---|---|---|
| EDA / model / explain / TS per-artefact insight (map step) | vision_fast | 1–2 |
| Stage summary, leaderboard, financial, WFO verdict (reduce step) | vision_standard (Deep: text_deep with per-artefact JSON) | ≤ 4 |
| Decisions VD1–VD12 (§38) | vision_standard | ≤ 6 |
| Intake adjudicator (§33.9) | text_reasoning (+ vision_fast for 2–4 profile plots) | 0–4 |
| Chat over FACTS, report narrative | text_reasoning | 0 |

### 40.4 Image sizing and encoding for plots

1. Render each artefact with kaleido at **1024 × 640** (scale 1), light theme, font ≥ 12 px, axis labels and titles on, legends inside the plot area, no hover-only information.
2. Encode PNG with palette quantisation (≤ 256 colours, `optimize=True`); if the base64 length exceeds **170,000** bytes (margin under 180 KB), re-encode as JPEG quality 85, then step down width (1024 → 896 → 768) until it fits.
3. Large grids (pair plots, small multiples, correlation heatmaps > 30 × 30) are **tiled** into ≤ 4 sub-images with a caption each, or replaced by a top-k view (e.g. top-25 correlated features).
4. If an image still does not fit, upload it through the NVCF Assets API (`createAsset` → presigned PUT → reference the asset ID, header `NVCF-INPUT-ASSET-REFERENCES`) — implemented but off by default; the default is to shrink or tile.
5. Each image is sent as an OpenAI `image_url` part with a data URI (`data:image/png;base64,…`), placed **before** the text part (Gemma 4 guidance), with `image_index` captions in the text so the model can cite images.
6. The image hash (sha256 of bytes) is part of the cache key.

### 40.5 Retries, back-off and rate limiting

* Client-side token bucket per provider (`rpm_limit`) shared across workers via Render Key Value; `q.insights` concurrency 2 per worker.
* Retry on 429, 500, 502, 503, 504 and timeouts: exponential back-off with full jitter (base 2 s, factor 2, max 60 s, **max 4 attempts**); honour `Retry-After` / provider retry hints (Gemini `retryDelay`, Groq `retry-after`).
* Do **not** retry on 400/401/403/404/413/422 — 404 "not found for account" or 403 marks that model unavailable for 1 h and moves to the next chain entry; 413 triggers image shrinking/tiling and one retry.
* **Circuit breaker** per provider:model — open after 3 consecutive failures for 5 min; half-open probe afterwards.
* Per-call timeout 90 s (Deep 180 s); total budget per insight request 4 min, per decision 3 calls; after that the rule baseline / numbers-only result is returned.
* Streaming (SSE) is used for long narratives only; JSON outputs are requested non-streamed so they can be validated in one piece.

### 40.6 Health checks and model availability

At worker start and every 30 min: `GET /v1/models` per enabled provider; a 1-token text probe per configured model; a tiny 64 × 64 PNG probe per vision model. Results are stored in `ai_model_health(provider, model, ok, latency_ms, error, checked_at)` and shown on Admin → AI providers. Unavailable models are skipped in their chains; if a chain is empty the feature runs in numbers-only mode and the UI says why.

### 40.7 Cost and usage controls

* **Cache first:** key = sha256(provider-agnostic prompt version + FACTS + image hashes + task); hit → no API call (Postgres `insights`/`decisions`, hot copy in Key Value for 24 h). Identical artefacts across re-runs never call the API twice.
* **Lazy generation:** insights are generated when a panel is opened or a report requests them, not for every artefact of every run; "Generate all" is an explicit button with a count and estimated calls.
* **Map-reduce with small models:** per-artefact calls use the fast tier; only summaries and decisions use the standard tier.
* **Budgets:** per-workspace daily caps (default 500 requests/day, 2 M input tokens/day) and per-user caps (default 150 requests/day), configurable by admins; soft warning at 80%, hard stop → numbers-only with a banner. Usage table `ai_usage(workspace_id, user_id, provider, model, feature, prompt_tokens, completion_tokens, images, latency_ms, cached, status, created_at)`.
* **Max tokens:** `max_tokens` 1,200 (brief 400, deep 3,000); FACTS trimmed to the top-N rows (default 25) per table.
* **Paid fallback guard:** a provider with paid billing is never added to a chain unless an admin enables it with a monthly spend cap.

### 40.8 Data protection for hosted calls

* Only aggregate artefacts are sent: rendered plots, metric tables, profile statistics and FACTS. **Raw rows are never sent** (Intake sends ≤ 5 sanitised example values per non-PII column, §33.9).
* PII columns (name/email/phone/PAN/Aadhaar/account patterns) are redacted from FACTS and plot labels before rendering for AI; client identifiers are hashed.
* Workspace data classification: `public` → all enabled providers; `internal` (default) → NVIDIA only; `restricted` → numbers-only (no external calls).
* Provider terms are recorded per provider entry (training-use policy, retention); the Gemini free tier stays disabled by default because Google states free-tier content may be used to improve its products.
* `NVIDIA_API_KEY` and any other provider keys exist **only** in the Render backend (`lab-api` and workers) and local `.env`; never in Vercel, never in `NEXT_PUBLIC_*`, never in the browser, never logged. The browser only talks to `lab-api`, which calls the provider.
* Audit: every call logs provider, model, prompt version, input hash, token counts and status (not the key).

### 40.9 API, UI and tests

* Admin → **AI providers** page: enabled providers and chains, health status, today's usage vs budget, workspace classification, test button (sends the 64 × 64 probe).
* Each insight/decision card footer shows provider, model, prompt version, cached yes/no and time (IST).
* Tests: mocked provider (respx) for 429 → back-off → success; 404 → next model; 413 → shrink; circuit breaker; budget exhaustion → numbers-only; image encoder keeps every rendered golden artefact under 170,000 base64 bytes; key never appears in logs or responses (grep test); live smoke test (manual, needs `NVIDIA_API_KEY`) that runs one insight on DS1 and validates the JSON.

---

---

## 41. Classification Evaluation Suite (binary, multiclass, multilabel)

> Round-3 addition (15 Nov 2026). This section is the **single source of truth for classification evaluation**. It extends and supersedes the short lists in §15.2, §16 (Classification row) and §36. Flow: `docs/FLOWCHART.md` §19 (`docs/diagrams/19_classification_eval.png`).2; those sections now point here. Artefact IDs: metrics `CLE.M.*`, tables `CLE.T.*`, plots `CLE.P.*`. Old IDs stay as aliases (`CLF.T.REPORT` → `CLE.T.REPORT`, `CLF.T.CONFUSION` → `CLE.T.CM`, `CLF.T.THRESHOLD` → `CLE.T.THRESHOLD_SWEEP`, `CLF.T.CALIBRATION` → `CLE.T.CALIBRATION`, `CLF.T.GAINS` → `CLE.T.GAINS`, `CLF.T.LEADERBOARD` → `CLE.T.COMPARE`, `CLF.T.MISCLASSIFIED` → `CLE.T.MOST_CONFIDENT_WRONG`, `CLF.T.WOE_IV` → `CLE.T.WOE_IV`). Every metric, table and plot is computed by an established library (§44); lab code only arranges library outputs into artefacts (rule `.cursor/rules/70-use-established-libraries.mdc`).

### 41.1 Settings, notation and prediction sources

| Setting | y shape | Prediction outputs used | Notes |
|---|---|---|---|
| Binary | y ∈ {0,1}; positive label chosen in Intake (default: minority class) | `predict_proba[:,1]` (or `decision_function` when no probabilities), hard label at threshold t | t defaults to 0.5; a tuned t (§41.6) is shown side by side, never replaces the default silently |
| Multiclass (K ≥ 3) | y ∈ {1…K} | probability matrix P (n × K), argmax label | optional class-weighted argmax for cost settings |
| Multilabel (L labels) | Y ∈ {0,1}^{n×L} | per-label probabilities, per-label thresholds (default 0.5) | models via `MultiOutputClassifier`, `ClassifierChain` or native multilabel (§43.2) |
| Ordinal (option on multiclass) | ordered classes | as multiclass | enables weighted kappa (linear/quadratic) and ordinal-distance confusion |

Notation: TP, FP, TN, FN per class (one-vs-rest for multiclass/multilabel); P = TP + FN (actual positives), N = TN + FP; n = total; N_ij = count of true class i predicted as j; t_k = Σ_j N_kj (true count of class k), p_k = Σ_i N_ik (predicted count of class k); p̂ = predicted probability; π = prevalence P/n; C_ij = cost of predicting j when truth is i.

**Prediction sources (every artefact carries a `split` tag and the UI shows it as a pill):**

1. **CV out-of-fold (OOF)** — the default view. For each fold f and repeat r the lab stores `oof_predictions` (run_id, model_id, repeat, fold, row_id, y_true, y_pred@0.5, y_pred@t*, proba_1…proba_K, sample_weight) as Parquet in Supabase Storage.
   * *Per-fold* artefacts: computed on fold f only.
   * *CV-aggregated* artefacts: (a) **mean ± std across folds** (metrics, normalised confusion matrices), (b) **pooled OOF** (all folds concatenated, one value), both shown; repeated CV averages over repeats first.
2. **Hold-out test** — computed once on the final refit; 95% CI by stratified bootstrap (B = 1,000 Balanced, 200 Quick, 2,000 Thorough; seed 42) via `scipy.stats.bootstrap` (paired, BCa where defined, percentile otherwise).
3. **Train (in-sample)** — only to show the train − CV gap (overfitting). Never used for selection.

Selection, threshold tuning and calibrator fitting use **OOF predictions of the training data only**; the test split is read-only (rule 20-ml-integrity).

### 41.2 Confusion-matrix suite

| ID | Variant | Definition | Library call |
|---|---|---|---|
| CLE.T.CM | Raw counts | N_ij | `sklearn.metrics.confusion_matrix(y, ŷ, labels=…)` |
| CLE.T.CM_NORM_TRUE | Row-normalised ("by true class", recall view) | N_ij / t_i — diagonal = per-class recall | `confusion_matrix(..., normalize='true')` |
| CLE.T.CM_NORM_PRED | Column-normalised ("by predicted class", precision view) | N_ij / p_j — diagonal = per-class precision | `confusion_matrix(..., normalize='pred')` |
| CLE.T.CM_NORM_ALL | All-normalised | N_ij / n — cells sum to 1 | `confusion_matrix(..., normalize='all')` |
| CLE.T.CM_FOLDS | Per fold (and per repeat) | one N^(f) per fold, long format: repeat, fold, true, pred, count, row %, col % | sklearn per fold |
| CLE.T.CM_CV | CV-aggregated | pooled Σ_f N^(f) **and** mean ± std of each normalised cell across folds | sklearn + `numpy` mean/std |
| CLE.T.CM_COST | Cost-weighted | C ⊙ N, cell cost and total expected cost; cost matrix edited in UI (default 0 on diagonal, 1 off) | numpy on sklearn output |
| CLE.T.CM_WEIGHTED | Sample-weighted | Σ w over rows in each cell | `confusion_matrix(..., sample_weight=w)` |
| CLE.T.CM_MULTILABEL | Per-label 2 × 2 (multilabel) and one-vs-rest 2 × 2 per class (multiclass) | [[TN, FP],[FN, TP]] per label/class | `sklearn.metrics.multilabel_confusion_matrix` |
| CLE.T.CM_THRESHOLD | Matrix at default 0.5 vs tuned t* (binary/multilabel) | two matrices + difference | sklearn |
| CLE.T.CM_DELTA | Model A − model B (same rows) | N^A − N^B, used in comparisons | numpy on sklearn |
| CLE.T.CM_DERIVED | TP/FP/TN/FN derived table | see columns below | `multilabel_confusion_matrix`, `precision_recall_fscore_support`, `class_likelihood_ratios` |

**CLE.T.CM_DERIVED columns (one row per class/label, plus micro/macro rows):** class, support P, actual negatives N, predicted positives (TP + FP), TP, FP, FN, TN, prevalence P/n, detection prevalence (TP+FP)/n, TPR (recall), TNR (specificity), PPV (precision), NPV, FPR, FNR, FDR = FP/(TP+FP), FOR = FN/(FN+TN), F1, threat score (CSI) TP/(TP+FP+FN), informedness (TPR + TNR − 1), markedness (PPV + NPV − 1), LR+ = TPR/FPR, LR− = FNR/TNR, DOR = LR+/LR−, MCC (one-vs-rest).

Display rules: cells show count and the active percentage; class order follows label order (or ordinal order); diagonal outlined; colour scale linear for normalised, log for raw counts when max/min > 100; more than 30 classes → "top-20 most-confused classes + Other" view with a full CSV download; undefined ratios (0/0) shown as "—" with a tooltip "not computed (zero division)", never as 0 (sklearn `zero_division=np.nan`).

### 41.3 Classification report

**CLE.T.REPORT** (one row per class/label; computed with `precision_recall_fscore_support`, `multilabel_confusion_matrix`, `roc_auc_score`, `average_precision_score`, `brier_score_loss`; cross-checked against `classification_report(output_dict=True)` in tests):

| Column | Formula |
|---|---|
| class | label (string) |
| support | t_k (count) and support % = t_k/n |
| predicted count | p_k |
| precision | TP/(TP + FP) |
| recall | TP/(TP + FN) |
| F1 | 2PR/(P + R) |
| F-β (β = 0.5 and 2 by default; β editable) | (1 + β²)PR/(β²P + R) |
| specificity | TN/(TN + FP) |
| NPV | TN/(TN + FN) |
| FPR | FP/(FP + TN) |
| FNR | FN/(FN + TP) |
| balanced accuracy (OvR) | (TPR + TNR)/2 |
| MCC (OvR) | binary MCC on the class-vs-rest 2 × 2 |
| ROC-AUC (OvR) | `roc_auc_score` on class vs rest (needs scores) |
| average precision (OvR) | `average_precision_score` on class vs rest |
| Brier (OvR) | (1/n)Σ(p̂_ik − y_ik)² |

**Footer rows:**

| Row | Definition |
|---|---|
| macro avg | unweighted mean over classes: (1/K)Σ_k m_k |
| weighted avg | support-weighted mean: Σ_k (t_k/n) m_k |
| micro avg | metric from pooled TP/FP/FN over classes (single-label multiclass: micro P = micro R = micro F1 = accuracy — shown with that note) |
| samples avg (multilabel only) | metric per sample over its label set, then averaged over samples |
| accuracy | Σ_k N_kk / n (multilabel: subset accuracy) |
| balanced accuracy | (1/K)Σ_k recall_k (`balanced_accuracy_score`), plus adjusted (BA − 1/K)/(1 − 1/K) |

Variants: **CLE.T.REPORT_CV** (every cell as mean ± std across folds, plus pooled OOF), **CLE.T.REPORT_FOLDS** (long format: repeat, fold, class, metric, value), **CLE.T.REPORT_TRAIN_TEST** (train / CV / test side by side with gap column), **CLE.T.REPORT_IMB** (imbalanced-learn `classification_report_imbalanced`: pre, rec, spe, f1, geo, iba, sup per class).

### 41.4 Scalar metrics (formulas, applicability, library)

B = binary, M = multiclass, L = multilabel, O = ordinal. "proba" = needs probabilities or scores.

| ID | Metric | Formula | Range / best | Applies | Library |
|---|---|---|---|---|---|
| CLE.M.01 | Accuracy | (1/n)Σ 1[ŷᵢ = yᵢ] | 0…1 ↑ | B M | `accuracy_score` |
| CLE.M.02 | Error rate | 1 − accuracy | ↓ | B M | sklearn |
| CLE.M.03 | Balanced accuracy | (1/K)Σ_k TPR_k; adjusted: (BA − 1/K)/(1 − 1/K) | ↑ | B M | `balanced_accuracy_score(adjusted=…)` |
| CLE.M.04 | Precision (PPV) — macro/micro/weighted/samples | TP/(TP + FP) | ↑ | B M L | `precision_score(average=…)` |
| CLE.M.05 | Recall (TPR, sensitivity) | TP/(TP + FN) | ↑ | B M L | `recall_score` |
| CLE.M.06 | Specificity (TNR) | TN/(TN + FP) | ↑ | B M L | `imblearn.metrics.specificity_score` |
| CLE.M.07 | NPV | TN/(TN + FN) | ↑ | B M L | from `multilabel_confusion_matrix` |
| CLE.M.08 | FPR / FNR | FP/(FP + TN); FN/(FN + TP) | ↓ | B M L | from `multilabel_confusion_matrix` |
| CLE.M.09 | FDR / FOR | FP/(TP + FP); FN/(FN + TN) | ↓ | B M L | from `multilabel_confusion_matrix` |
| CLE.M.10 | F1 | 2PR/(P + R) | ↑ | B M L | `f1_score(average=…)` |
| CLE.M.11 | F-β | (1 + β²)PR/(β²P + R) | ↑ | B M L | `fbeta_score(beta=…)` |
| CLE.M.12 | G-mean | binary √(TPR·TNR); multiclass (Π_k TPR_k)^{1/K} | ↑ | B M | `imblearn.metrics.geometric_mean_score` |
| CLE.M.13 | Index of balanced accuracy (IBA_α) | (1 + α(TPR − TNR))·TPR·TNR, α = 0.1 | ↑ | B M | `imblearn.metrics.make_index_balanced_accuracy` |
| CLE.M.14 | MCC | binary (TP·TN − FP·FN)/√((TP+FP)(TP+FN)(TN+FP)(TN+FN)); multiclass (c·s − Σ_k p_k t_k)/√((s² − Σ p_k²)(s² − Σ t_k²)), c = Σ N_kk, s = n | −1…1 ↑ | B M | `matthews_corrcoef` |
| CLE.M.15 | Cohen's κ | (p_o − p_e)/(1 − p_e); p_o = Σ N_kk/n, p_e = Σ_k t_k p_k / n² | −1…1 ↑ | B M | `cohen_kappa_score` |
| CLE.M.16 | Linear weighted κ | 1 − Σ w_ij O_ij / Σ w_ij E_ij; E_ij = t_i p_j / n; w_ij = \|i − j\|/(K − 1) | ↑ | O | `cohen_kappa_score(weights='linear')` |
| CLE.M.17 | Quadratic weighted κ (QWK) | as above with w_ij = (i − j)²/(K − 1)² | ↑ | O | `cohen_kappa_score(weights='quadratic')` |
| CLE.M.18 | Youden's J (informedness) | TPR + TNR − 1 (multiclass: macro over OvR) | −1…1 ↑ | B M | from `confusion_matrix` |
| CLE.M.19 | Markedness | PPV + NPV − 1 | −1…1 ↑ | B M | from `confusion_matrix` |
| CLE.M.20 | Positive / negative likelihood ratio | LR+ = TPR/FPR; LR− = FNR/TNR | LR+ ↑, LR− ↓ | B | `class_likelihood_ratios` |
| CLE.M.21 | Diagnostic odds ratio | LR+/LR− = (TP·TN)/(FP·FN) | ↑ | B | from `class_likelihood_ratios` |
| CLE.M.22 | Threat score / Jaccard (binary) | TP/(TP + FP + FN) | ↑ | B | `jaccard_score` |
| CLE.M.23 | Prevalence / detection prevalence | P/n; (TP + FP)/n | — | B M L | numpy |
| CLE.M.24 | Log loss (cross-entropy) | −(1/n)Σᵢ Σ_k y_ik ln p̂_ik (clipped) | ↓ | B M L (proba) | `log_loss` |
| CLE.M.25 | D² log-loss | 1 − LL(model)/LL(prior-only model) | ↑ | B M (proba) | `d2_log_loss_score` |
| CLE.M.26 | Brier score (binary) | (1/n)Σ(p̂ᵢ − yᵢ)² | 0…1 ↓ | B (proba) | `brier_score_loss` |
| CLE.M.27 | Multiclass Brier | (1/n)Σᵢ Σ_k (p̂_ik − y_ik)² | 0…2 ↓ | M (proba) | `brier_score_loss` (multiclass support in recent sklearn; else `model_diagnostics.scoring.SquaredError`) |
| CLE.M.28 | Brier decomposition (Murphy) | BS = REL − RES + UNC; REL = (1/n)Σ_b n_b(f̄_b − ō_b)², RES = (1/n)Σ_b n_b(ō_b − ō)², UNC = ō(1 − ō) (exact for binned forecasts; the within-bin term is reported) and the isotonic (CORP) decomposition miscalibration − discrimination + uncertainty | — | B (proba) | `model_diagnostics.scoring.decompose` (CORP); binned form from `sklearn.calibration.calibration_curve` |
| CLE.M.29 | Brier skill score | 1 − BS/BS_ref, BS_ref = π(1 − π) | ↑ | B (proba) | from CLE.M.26 |
| CLE.M.30 | ROC-AUC (binary) | ∫TPR d(FPR) = P(s⁺ > s⁻) | 0.5 chance, 1 best | B (scores) | `roc_auc_score` |
| CLE.M.31 | ROC-AUC OvR macro / weighted / micro | per class vs rest, then macro mean, support-weighted mean, or pooled (micro) | ↑ | M L (proba) | `roc_auc_score(multi_class='ovr', average=…)` |
| CLE.M.32 | ROC-AUC OvO macro / weighted (Hand & Till) | (2/(K(K−1)))Σ_{j<k} ½[A(j\|k) + A(k\|j)] | ↑ | M (proba) | `roc_auc_score(multi_class='ovo', average=…)` |
| CLE.M.33 | Partial AUC (FPR ≤ max_fpr, McClish-standardised) | ½[1 + (pAUC − min)/(max − min)], min = max_fpr²/2, max = max_fpr | ↑ | B | `roc_auc_score(max_fpr=…)` |
| CLE.M.34 | Average precision (PR-AUC, step) — macro/micro/weighted | AP = Σ_n (R_n − R_{n−1}) P_n | baseline π, ↑ | B M L | `average_precision_score` |
| CLE.M.35 | PR-AUC (trapezoid, for reference only) | trapezoid area under PR curve (optimistic; not the default) | ↑ | B | `auc(recall, precision)` |
| CLE.M.36 | KS statistic | max_t \|TPR(t) − FPR(t)\| = max_t \|F₁(t) − F₀(t)\| | 0…1 ↑ | B (scores) | `scipy.stats.ks_2samp` on class-wise scores |
| CLE.M.37 | Gini (Somers' D) | 2·AUC − 1 | ↑ | B | from `roc_auc_score` |
| CLE.M.38 | Top-k accuracy (k = 2, 3, 5) | (1/n)Σ 1[yᵢ ∈ top-k(p̂ᵢ)] | ↑ | M (proba) | `top_k_accuracy_score` |
| CLE.M.39 | Hamming loss | (1/(nL))Σᵢ Σ_l 1[ŷ_il ≠ y_il] | ↓ | L (and B M) | `hamming_loss` |
| CLE.M.40 | Jaccard — samples/macro/micro | \|Y ∩ Ŷ\| / \|Y ∪ Ŷ\| | ↑ | L M | `jaccard_score(average=…)` |
| CLE.M.41 | Subset (exact-match) accuracy | (1/n)Σ 1[Ŷᵢ = Yᵢ] | ↑ | L | `accuracy_score` |
| CLE.M.42 | Coverage error | (1/n)Σᵢ max_{l ∈ Yᵢ} rank_il | ↓ | L (scores) | `coverage_error` |
| CLE.M.43 | Label ranking average precision | (1/n)Σᵢ (1/\|Yᵢ\|)Σ_{l∈Yᵢ} \|{l' ∈ Yᵢ: r_il' ≤ r_il}\| / r_il | ↑ | L (scores) | `label_ranking_average_precision_score` |
| CLE.M.44 | Ranking loss | share of mis-ordered (relevant, irrelevant) label pairs | ↓ | L (scores) | `label_ranking_loss` |
| CLE.M.45 | NDCG@k | DCG@k / IDCG@k | ↑ | L (scores) | `ndcg_score` |
| CLE.M.46 | Expected calibration error (top-label; 15 equal-width bins; equal-mass variant) | Σ_b (\|B_b\|/n)\|acc(B_b) − conf(B_b)\| | ↓ | B M (proba) | `netcal.metrics.ECE`; cross-check `torchmetrics` `CalibrationError` |
| CLE.M.47 | Maximum calibration error | max_b \|acc(B_b) − conf(B_b)\| | ↓ | B M (proba) | `netcal.metrics.MCE` |
| CLE.M.48 | Classwise ECE | (1/K)Σ_k Σ_b (\|B_bk\|/n)\|freq_bk − conf_bk\| | ↓ | M (proba) | `netcal.metrics.ECE` per class (OvR) |
| CLE.M.49 | Calibration slope / intercept (calibration-in-the-large) | fit logit P(y=1) = a + b·logit(p̂); ideal a = 0, b = 1 | — | B (proba) | `statsmodels` `Logit` on logit(p̂) |
| CLE.M.50 | Hosmer–Lemeshow / Spiegelhalter z | HL = Σ_g (O_g − E_g)²/(E_g(1 − E_g/n_g)), df = g − 2 (g = 10); Spiegelhalter z on Σ(y − p̂)(1 − 2p̂) | p > 0.05 = no evidence of miscalibration | B (proba) | thin wrapper: decile bins (`pandas.qcut`) + `scipy.stats.chi2` / `norm` |
| CLE.M.51 | Expected cost (cost-sensitive) | EC = (1/n)Σ_i Σ_j C_ij N_ij; normalised EC = EC / EC(best constant classifier) | ↓ | B M | numpy on `confusion_matrix` |
| CLE.M.52 | Lift@k% / Gain@k% | Lift = precision in top k% / π; Gain = TP in top k% / P | ↑ | B (scores) | `scikitplot` (scikit-plots) cumulative gain/lift helpers; values from sklearn ranks |
| CLE.M.53 | Precision@k% / Recall@k% (alert budget) | precision / recall among the top-k% scored rows | ↑ | B | sklearn on ranked scores |
| CLE.M.54 | Precision at recall ≥ r; recall at precision ≥ p | max precision s.t. recall ≥ r (and mirror) from the PR curve | ↑ | B | `precision_recall_curve` |
| CLE.M.55 | Equal error rate | FPR = FNR point on the DET curve | ↓ | B | `det_curve` |

Every metric gets an ExplainCard (formula in LaTeX, plain-language meaning, when it misleads). Metrics that need probabilities show "not computed — model has no probabilities" for models without `predict_proba`; ROC/PR then use `decision_function` scores and calibration metrics are hidden.

### 41.5 Plot catalogue

All plots are Plotly figures rendered from library outputs (curves from `sklearn.metrics`, `sklearn.calibration`, `netcal`, `scikitplot`; matplotlib-only libraries are used for numbers, not images). Each plot is an artefact with a numbers payload for AI Insights.

| ID | Plot | Shows / axes | When | Compute library |
|---|---|---|---|---|
| CLE.P.CM_COUNTS | Confusion-matrix heatmap — counts | true (y) × predicted (x), count + % | always | sklearn `confusion_matrix` |
| CLE.P.CM_NORM | Confusion-matrix heatmap — normalisation toggle **Counts / Row (true) / Column (pred) / All** | same, cells = rate | always | sklearn `normalize=` |
| CLE.P.CM_FOLDS | Per-fold confusion matrices (small multiples) | one heatmap per fold (row-normalised) | CV | sklearn |
| CLE.P.CM_CV | CV-aggregated matrix | cell = mean ± std of row-normalised rate across folds; pooled counts on hover | CV | sklearn + numpy |
| CLE.P.CM_COST | Cost-weighted heatmap | cell = C_ij·N_ij, total cost in title | cost matrix set | numpy on sklearn |
| CLE.P.CM_DELTA | Difference matrix model A − B | diverging colour | compare | numpy on sklearn |
| CLE.P.CM_MULTILABEL | Per-label 2 × 2 grid | one 2 × 2 per label (TN, FP, FN, TP) | multilabel | `multilabel_confusion_matrix` |
| CLE.P.TOP_CONFUSIONS | Top confused pairs | bar of the N largest off-diagonal N_ij (true → pred) | M | sklearn |
| CLE.P.CLASS_PRED_ERROR | Class prediction error | stacked bar per true class split by predicted class | M | sklearn (Yellowbrick `ClassPredictionError` design) |
| CLE.P.REPORT_HEATMAP | Classification-report heatmap | class × {precision, recall, F1, specificity, support} | always | sklearn |
| CLE.P.PER_CLASS_BARS | Per-class P / R / F1 grouped bars with CV error bars (± std) | class on x | always | sklearn |
| CLE.P.SUPPORT_BARS | Class support per split/fold | train / val / test / after resampling | always | numpy |
| CLE.P.ROC | ROC (binary) with AUC, bootstrap 95% band, default and tuned operating points, chance diagonal | x FPR, y TPR | B | `roc_curve`, `RocCurveDisplay` data |
| CLE.P.ROC_MULTI | Per-class OvR ROC + micro + macro average curves | one line per class | M L | `roc_curve` per class |
| CLE.P.ROC_CV | Fold ROC curves + mean ROC ± 1 std (interpolated on a common FPR grid) | | CV | `roc_curve` + `numpy.interp` |
| CLE.P.PR | Precision-recall with **iso-F1 contours** (F1 = 0.2…0.8), prevalence baseline, AP label | x recall, y precision | B | `precision_recall_curve` |
| CLE.P.PR_MULTI | Per-class PR + micro average | | M L | `precision_recall_curve` |
| CLE.P.PR_CV | Fold PR curves + mean | | CV | sklearn |
| CLE.P.RELIABILITY | Reliability diagram with **probability histogram** below, equal-width and quantile bins, Wilson 95% bars, ECE/MCE/Brier in legend | x mean predicted p, y observed frequency | proba | `sklearn.calibration.calibration_curve`, `netcal` |
| CLE.P.RELIABILITY_MULTI | Top-label and class-wise reliability (small multiples) | | M proba | `netcal` |
| CLE.P.CALIB_COMPARE | Reliability before vs after calibrators (sigmoid, isotonic, temperature, Venn-Abers, beta) | | calibration on | sklearn `CalibratedClassifierCV`, `venn-abers`, `netcal` |
| CLE.P.PROBA_DIST | Class-probability distribution | histogram/KDE (or violin) of p̂ by true class, threshold line | B | numpy / `scipy.stats.gaussian_kde` |
| CLE.P.PROBA_GRID | Multiclass probability grid | violin of p̂(class k) for each true class (K × K) | M | numpy |
| CLE.P.CUM_GAIN | Cumulative gains | x % population targeted, y % positives captured, baseline + perfect | B | `scikitplot` cumulative gain helper |
| CLE.P.LIFT | Lift chart (cumulative and per-decile) | x % population, y lift | B | `scikitplot` |
| CLE.P.KS | KS plot | CDFs of scores for positives and negatives, max gap marked | B | `scipy.stats.ks_2samp` + `numpy` ECDF |
| CLE.P.THRESHOLD_METRICS | Threshold vs metric curves | precision, recall, F1, F-β, MCC, balanced accuracy, specificity vs t; default and chosen t marked | B L | `precision_recall_curve`, `TunedThresholdClassifierCV.cv_results_` |
| CLE.P.DISCRIMINATION | Discrimination threshold plot | precision, recall, F1, queue rate vs t with bands over 50 shuffled splits (Yellowbrick design) | B | sklearn (`StratifiedShuffleSplit`) |
| CLE.P.COST_CURVE | Expected cost vs threshold, and Drummond–Holte cost curve (normalised expected cost vs probability cost) | | cost matrix set | numpy on `roc_curve` |
| CLE.P.DET | DET curve (normal deviate scale) with EER point | x FPR, y FNR | B | `det_curve`, `DetCurveDisplay` data |
| CLE.P.PRECISION_AT_K | Precision@k% and capture rate vs k% | | B | sklearn ranks |
| CLE.P.THRESHOLD_STABILITY | Per-fold optimal thresholds (strip + mean ± std) | | tuning on | `TunedThresholdClassifierCV` per fold |
| CLE.P.METRIC_FOLDS | Box/strip of each metric across folds | metric on x | CV | numpy |
| CLE.P.CONFIDENCE_ERRORS | Histogram of p(pred) for correct vs wrong predictions | | proba | numpy |
| CLE.P.ERROR_OVERLAP | UpSet plot of misclassified rows shared by models | | compare | `upsetplot` data → Plotly |
| CLE.P.COMPARE_BARS | Model comparison bars with 95% CI for a chosen metric | | compare | numpy |
| CLE.P.CD | Critical-difference diagram (Friedman + Nemenyi) | | ≥ 3 models | `scikit-posthocs` `critical_difference_diagram` |
| CLE.P.PVALUE_HEATMAP | Pairwise test p-value heatmap (Holm-adjusted) | | compare | `scikit-posthocs`, `statsmodels` |
| CLE.P.CLASS_BALANCE | Class balance before / after resampling | | imbalance on | imbalanced-learn |
| CLE.P.DECISION_BOUNDARY | Decision regions on a 2D PCA/UMAP projection | | ≤ 10 classes | sklearn `DecisionBoundaryDisplay` data |
| CLE.P.MULTILABEL_BARS | Per-label F1 bars + label cardinality histogram | | L | sklearn |
| CLE.P.CONFORMAL | Conformal set-size histogram and coverage per class | | conformal on | MAPIE |
| CLE.P.SLICES | Metric by segment (feature bins, groups) with overall line | | always | `fairlearn.metrics.MetricFrame` |
| CLE.P.LEARNING / CLE.P.VALIDATION | Learning and validation curves | as §36.1 | always | `learning_curve`, `validation_curve` |

### 41.6 Threshold optimisation (binary and per label)

| Method key | Objective | Rule | Library |
|---|---|---|---|
| thr.default | — | t = 0.5 | — |
| thr.youden | max J(t) = TPR − FPR | argmax over ROC thresholds | `roc_curve` |
| thr.closest_topleft | min √((1 − TPR)² + FPR²) | | `roc_curve` |
| thr.fbeta_max | max F-β (β from UI; default 1) | | `TunedThresholdClassifierCV(scoring=make_scorer(fbeta_score, beta=β))` |
| thr.mcc_max | max MCC | | `TunedThresholdClassifierCV(scoring='matthews_corrcoef')` |
| thr.cost_min | min expected cost Σ C·N | empirical on OOF; for calibrated p̂ the Bayes rule t* = C_FP/(C_FP + C_FN) is shown as a reference | `TunedThresholdClassifierCV(scoring=cost scorer)` |
| thr.precision_at_recall | max precision s.t. recall ≥ r (default r = 0.80) | constrained search on the PR curve | `precision_recall_curve` |
| thr.recall_at_precision | max recall s.t. precision ≥ p (default 0.90) | | `precision_recall_curve` |
| thr.fpr_budget (Neyman–Pearson) | max TPR s.t. FPR ≤ α (default 0.05) | | `roc_curve` |
| thr.capacity | flag the top k% / top N rows (alert budget) | quantile of scores | numpy |
| thr.eer | FPR = FNR | | `det_curve` |
| thr.ks | t at KS maximum | | `roc_curve` |
| thr.prevalence_match | predicted positive rate = training prevalence | | numpy quantile |

Protocol: thresholds are tuned on **training OOF predictions only** (`TunedThresholdClassifierCV` with the same CV splitter, `refit=True`), then applied unchanged to the test split. Reported: **CLE.T.THRESHOLD_SWEEP** (threshold step 0.01 or unique scores ≤ 1,000: t, TP, FP, TN, FN, precision, recall, specificity, F1, F-β, MCC, balanced accuracy, queue rate, expected cost, chosen ✓), **CLE.T.THRESHOLD_CHOICE** (method, objective value at t*, t*, per-fold t* mean ± std, bootstrap 95% CI of t*, test metrics at 0.5 vs at t*). Multiclass: optional class-weight vector w on argmax(p̂ ⊙ w) tuned by Optuna on OOF (cost settings only). Multilabel: one t per label, same methods. The VLM decision agent VD11 (§38) proposes a method using CLE.P.THRESHOLD_METRICS, CLE.P.COST_CURVE and CLE.P.RELIABILITY; guard: the test split is never used.

### 41.7 Imbalance-specific reporting

Triggered when minority share < 20% or imbalance ratio IR = n_max/n_min > 4 (binary) or any class < 5% (multiclass):

* **CLE.T.CLASS_DIST** — class, count and % in full data, train, each fold (val), test, after resampling (inside folds); IR per split.
* **CLE.T.BASELINES** — dummy strategies (`DummyClassifier`: most_frequent, stratified, prior, uniform) with every headline metric, so "beats majority by x" is explicit.
* Headline metrics switch to **PR-AUC (with prevalence baseline), MCC, balanced accuracy, G-mean, IBA, recall of the minority class**; accuracy carries a warning chip "misleading under imbalance".
* `classification_report_imbalanced` (CLE.T.REPORT_IMB) and minority-class confusion row highlighted.
* Minimum positives per validation fold check: < 10 → warning, < 3 → fold metrics marked unreliable and CI widened (bootstrap); suggests RepeatedStratifiedKFold.
* Resampling effect: metrics with vs without resampling (same folds) and CLE.P.CLASS_BALANCE.
* Calibration after resampling: SMOTE/undersampling distorts probabilities; the lab recalibrates on non-resampled OOF data or applies the prior correction p' = p·(π/π_s) / [p·(π/π_s) + (1 − p)·((1 − π)/(1 − π_s))] (π true prevalence, π_s resampled prevalence) — shown in CLE.P.CALIB_COMPARE.
* Threshold tuning recommended automatically (rule engine) with thr.fbeta_max or thr.cost_min.

### 41.8 CV mean ± std tables (every metric)

**CLE.T.CV_METRICS** — one row per scalar metric in §41.4 that applies to the task: metric, averaging (binary/macro/micro/weighted/samples), fold_1 … fold_k (× repeat), mean, std, SEM, min, median, max, 95% CI (t-interval; Nadeau–Bengio corrected variance when "corrected" is on), pooled-OOF value, train mean, train − CV gap, test value, test 95% bootstrap CI, better direction (↑/↓). Computed with `sklearn.model_selection.cross_validate(scoring={…all scorers…}, return_train_score=True, return_indices=True)`; extra metrics computed from stored OOF predictions with the same library functions.

Companion tables: **CLE.T.CV_REPORT** (class × metric mean ± std), **CLE.T.FOLD_CLASS_DIST** (class counts per fold), **CLE.T.CV_CM_STD** (std of each row-normalised cell).

### 41.9 Model-comparison tables

| ID | Columns |
|---|---|
| CLE.T.COMPARE | rank, model, recipe, primary metric mean ± std, every headline metric mean ± std (ROC-AUC, PR-AUC, F1 macro, MCC, balanced accuracy, log loss, Brier, ECE), rank per metric, average rank, CD group, Δ vs best, p vs best (Holm-adjusted), fit time, predict latency (ms/row), model size |
| CLE.T.COMPARE_PER_CLASS | class × model F1 (and recall) with best per class marked |
| CLE.T.COMPARE_CALIBRATION | model × {ECE, MCE, Brier, BSS, slope, intercept, HL p} before/after calibration |
| CLE.T.PAIRWISE_TESTS | model A, model B, test, statistic, p, Holm-adjusted p, effect size (Δ metric, 95% CI), verdict (A better / B better / not distinguishable) |
| CLE.T.MCNEMAR | 2 × 2 table of correct/incorrect for A vs B (n00, n01, n10, n11), χ² or exact p |

### 41.10 Statistical tests

| Test | Use | Formula / note | Library |
|---|---|---|---|
| McNemar (exact when n01 + n10 < 25) | two classifiers, same test rows | χ² = (\|n01 − n10\| − 1)²/(n01 + n10) | `statsmodels.stats.contingency_tables.mcnemar` |
| Cochran's Q | ≥ 3 classifiers, same rows | generalises McNemar | `statsmodels.stats.contingency_tables.cochrans_q` |
| DeLong test (correlated ROC-AUCs) and DeLong AUC CI | AUC of A vs B on the same rows | z = (A₁ − A₂)/√Var(A₁ − A₂) with structural components (fast DeLong) | `MLstatkit.Delong_test` (DeLong z, p-value and AUC CI); cross-checked by paired bootstrap (`scipy.stats.bootstrap`) in tests |
| 5 × 2 cv paired t-test (Dietterich) | A vs B, independent of fold reuse | t = p₁⁽¹⁾ / √((1/5)Σᵢ sᵢ²), df = 5 | `mlxtend.evaluate.paired_ttest_5x2cv` |
| 5 × 2 cv combined F-test (Alpaydin) | more robust variant | F = ΣΣ p²/(2Σ s²) ~ F(10, 5) | `mlxtend.evaluate.combined_ftest_5x2cv` |
| Corrected resampled t-test (Nadeau–Bengio) | k-fold × r repeats scores | t = d̄ / √((1/(kr) + n_test/n_train)·σ̂²) | `scipy.stats.t` (thin wrapper over fold scores from `cross_validate`) |
| Wilcoxon signed-rank | paired fold scores | | `scipy.stats.wilcoxon` |
| Friedman + Nemenyi (CD diagram) | ≥ 3 models across folds/datasets | | `scipy.stats.friedmanchisquare`, `scikit-posthocs` |
| Bootstrap CI of any metric and of Δ metric | test split | stratified, paired | `scipy.stats.bootstrap` |
| Holm–Bonferroni correction | multiple pairs | | `statsmodels.stats.multitest.multipletests` |
| Hosmer–Lemeshow, Spiegelhalter z | calibration | CLE.M.50 | thin wrapper over `pandas.qcut` + `scipy.stats` |

5 × 2 cv tests need their own 5 repetitions of 2-fold CV, so they run on demand ("Run significance tests" button, queued on `q.train`).

### 41.11 Error-analysis tables

| ID | Columns |
|---|---|
| CLE.T.MOST_CONFIDENT_WRONG | rank, row id, fold/split, true, predicted, p(pred), p(true), margin p(pred) − p(true), entropy, top-3 SHAP reasons, 5 key feature values (default 50 rows, sortable) |
| CLE.T.BORDERLINE | rows closest to the threshold (\|p̂ − t\| smallest) with the same columns |
| CLE.T.LEAST_CONFIDENT_RIGHT | correct predictions with the lowest p(true) |
| CLE.T.TOP_CONFUSIONS | true, predicted, count, % of true class, % of all errors, example row ids |
| CLE.T.SLICES | segment (feature bin / group), n, prevalence, accuracy, precision, recall, F1, ROC-AUC, Δ vs overall, flag if Δ F1 < −0.05 (`fairlearn.metrics.MetricFrame`) |
| CLE.T.LABEL_ISSUES | row id, given label, suggested label, self-confidence, label-quality score (possible label noise from OOF probabilities; `cleanlab.filter.find_label_issues`, Apache-2.0) |
| CLE.T.MULTILABEL_STATS | label, support, label cardinality, label density, co-occurrence top pairs, per-label F1 |
| CLE.T.CALIBRATION | bin, lower, upper, n, mean predicted p, observed frequency, gap, Wilson 95% CI |
| CLE.T.CALIBRATION_TESTS | ECE, MCE, classwise ECE, Brier, REL, RES, UNC, BSS, slope, intercept, HL statistic and p, Spiegelhalter z and p |
| CLE.T.GAINS | decile, n, positives, cumulative positives %, gain, lift, cumulative lift, KS at decile, response rate |
| CLE.T.METRICS | metric, train, CV mean ± std, pooled OOF, test, test 95% CI (headline view; full list in CLE.T.CV_METRICS) |
| CLE.T.WOE_IV | as §36.2 (`optbinning`) |

### 41.12 Applicability matrix

| Group | Binary | Multiclass | Multilabel | Needs probabilities |
|---|---|---|---|---|
| Confusion matrices (counts, 3 normalisations, folds, CV, cost) | ✓ | ✓ | per-label 2 × 2 | no |
| Classification report + averages | ✓ | ✓ (micro = accuracy note) | ✓ incl. samples avg | no (AUC/AP/Brier columns yes) |
| ROC / PR / AUC / AP | ✓ | OvR / OvO | per label + micro | scores |
| Calibration (reliability, ECE, Brier, decomposition) | ✓ | top-label + classwise | per label | yes |
| Gains, lift, KS, DET, cost curve, threshold sweep | ✓ | — | per label | scores |
| Top-k, OvO AUC, multiclass MCC, QWK (ordinal) | — | ✓ | — | top-k: yes |
| Hamming, Jaccard samples, subset accuracy, ranking metrics, NDCG | — | — | ✓ | ranking: scores |

### 41.13 Implementation, API and UI

* Package `labcore/eval/classification/`: `confusion.py`, `report.py`, `metrics.py` (scorer registry mapping every CLE.M.* to its library callable and averaging), `thresholds.py`, `calibration.py`, `curves.py`, `stats_tests.py`, `error_analysis.py`, `imbalance.py`, `artefacts.py` (turns library outputs into artefact envelopes §6). No metric formula is re-implemented when a library function exists; derived ratios (NPV, FDR, FOR, markedness) are arithmetic on `multilabel_confusion_matrix` output.
* Curves are down-sampled to ≤ 1,000 points for the browser (full arrays kept in Storage). Bootstraps run on `q.train` workers; per-fold artefacts are computed in the training job; comparison tests are on demand.
* API: `GET /runs/{run_id}/eval/classification?split=oof|test|train&fold=all|mean|<k>&normalize=none|true|pred|all&threshold=<t>|tuned`; `POST /runs/{run_id}/eval/threshold` {method, constraint, cost_matrix} → creates a VD11 decision proposal; `POST /compare/tests` {model_ids, tests[]} → job; `GET /runs/{run_id}/eval/errors?type=most_confident_wrong&limit=50`.
* UI — Modelling → model → **Evaluation** tab with sub-tabs *Overview · Confusion · Report · Curves · Calibration · Threshold · Errors · Imbalance · Compare*. Controls: split pills (Train / CV-OOF / Test), fold selector (Pooled / Mean ± std / Fold k), normalisation segmented control (**Counts / Row / Column / All**), threshold slider (live recompute in the browser from stored OOF arrays up to 200k rows, server otherwise), class filter, cost-matrix editor, β input. Every panel has an ExplainCard and an AI-insight chip.

### 41.14 AI Insights prompts for classification evaluation

Rule-engine findings run first (no LLM): accuracy − majority-baseline accuracy < 0.02 → "barely beats the majority class"; minority recall < 0.5; ECE > 0.05 or HL p < 0.05 → "calibrate"; train − CV ROC-AUC gap > 0.05 → overfitting; fold std of macro-F1 > 0.05 → unstable; one off-diagonal pair > 20% of all errors → "systematic confusion"; PR-AUC < 2 × prevalence → weak; std of per-fold t* > 0.1 → unstable threshold; McNemar/DeLong p > 0.05 between top-2 → "not distinguishable, prefer simpler"; > 1% CLE.T.LABEL_ISSUES → possible label noise.

| Template (versioned in `labcore/insights/prompts/eval_classification_*.md`) | Images | FACTS keys | Required content |
|---|---|---|---|
| `cm` (per model) | CLE.P.CM_NORM (row and column), CLE.P.TOP_CONFUSIONS | CLE.T.CM, CLE.T.CM_DERIVED, CLE.T.TOP_CONFUSIONS | which classes are confused and in which direction, recall vs precision per class, whether errors are symmetric, data/feature hypotheses for the main confusions |
| `report` | CLE.P.REPORT_HEATMAP, CLE.P.PER_CLASS_BARS | CLE.T.REPORT, CLE.T.REPORT_CV, CLE.T.CLASS_DIST | weakest classes, effect of support, macro vs weighted gap explained, stability across folds |
| `curves` | CLE.P.ROC(_MULTI), CLE.P.PR, CLE.P.DET | AUC/AP with CIs, prevalence | ranking quality, whether ROC looks good only because of imbalance, operating region |
| `calibration` | CLE.P.RELIABILITY, CLE.P.CALIB_COMPARE | CLE.T.CALIBRATION_TESTS | over/under-confidence region, which calibrator to use and why |
| `threshold` | CLE.P.THRESHOLD_METRICS, CLE.P.COST_CURVE, CLE.P.THRESHOLD_STABILITY | CLE.T.THRESHOLD_CHOICE, cost matrix | recommended method + t* with trade-off in plain words (e.g. "at t = 0.31 recall rises from 0.62 to 0.80 and precision falls from 0.71 to 0.58") using only FACTS numbers; `apply_patch` = threshold proposal → VD11 |
| `errors` | CLE.P.CONFIDENCE_ERRORS | CLE.T.MOST_CONFIDENT_WRONG (aggregated, no raw PII), CLE.T.SLICES, CLE.T.LABEL_ISSUES | patterns in confident errors, weak segments, label-noise suspicion |
| `imbalance` | CLE.P.CLASS_BALANCE, CLE.P.PR | CLE.T.BASELINES, CLE.T.REPORT_IMB | whether the model beats baselines on the metrics that matter, resampling effect |
| `compare` | CLE.P.COMPARE_BARS, CLE.P.CD, CLE.P.PVALUE_HEATMAP | CLE.T.COMPARE, CLE.T.PAIRWISE_TESTS | champion/challenger with statistical support; flags ties |

Output uses the §23.4 schema with categories extended by `class_confusion`, `threshold` and `error_analysis`. Numbers are validated against FACTS (§23.3 step 5); row-level tables are sent only as aggregates (§40.8).

### 41.15 Tests and acceptance

* Golden tests (seed 42) on DS4 (binary), DS10 (multiclass) and a multilabel fixture (`sklearn.datasets.make_multilabel_classification(random_state=42)`): every CLE.M.* equals the library reference (`classification_report(output_dict=True)`, `roc_auc_score`, etc.) to 1e-9.
* Σ per-fold confusion matrices == pooled OOF matrix; row-normalised rows sum to 1, column-normalised columns sum to 1, all-normalised sums to 1.
* Single-label micro-F1 == accuracy; multiclass MCC equals `matthews_corrcoef`; QWK equals `cohen_kappa_score(weights='quadratic')`.
* DeLong p-value and CI agree with the paired-bootstrap result within tolerance on a fixed example; McNemar equals `statsmodels`; 5 × 2 cv equals `mlxtend`.
* A spy proves threshold tuning and calibrators never read test rows.
* Zero-division cases render "—", never 0.
* Visual snapshot tests for every CLE.P.* on DS4 and DS10.

### 41.16 Counts (classification evaluation)

55 scalar metrics (CLE.M.01–55, many with several averaging modes), 42 tables (CLE.T.*), 45 plots (CLE.P.*, counting LEARNING and VALIDATION separately), 13 threshold methods, 11 statistical tests, 8 AI-insight templates.

---

## 42. Regression Evaluation Suite (audit and completion)

> Round-3 addition. Audit of regression evaluation against §15.1, §16 and §36.1, with every gap filled. This section is the single source of truth for regression evaluation; §15.1, §16 (Regression row) and §36.1 point here. IDs: `REE.M.*`, `REE.T.*`, `REE.P.*`; old `REG.T.*` IDs stay as aliases (`REG.T.METRICS` → `REE.T.CV_METRICS` headline view, `REG.T.FOLDS` → `REE.T.FOLDS`, `REG.T.LEADERBOARD` → `REE.T.COMPARE`, `REG.T.COEF` → `REE.T.COEF`, `REG.T.RESID_STATS` → `REE.T.RESID_STATS`, `REG.T.ERR_SEGMENT` → `REE.T.ERR_SEGMENT`, `REG.T.WORST` → `REE.T.WORST`, `REG.T.INTERVALS` → `REE.T.INTERVALS`).

### 42.1 Audit result

| Area | Before (§15.1 / §36.1) | Gap found | Fixed in |
|---|---|---|---|
| Prediction sources | implied | no explicit OOF / per-fold / pooled / test-bootstrap protocol | §42.2 |
| Metrics | 22 | missing MSLE, MdAPE, MPE, NRMSE variants, RSE, RAE, Huber loss, log-cosh, D² variants by name, tolerance hit-rate, Mincer–Zarnowitz calibration, normalised interval width; no library per metric | §42.3 (40 metrics) |
| Residual tables | 1 summary table | no row-level residual table, no residual test table with verdicts, no influence table, no calibration-by-bin table, no target-transform table | §42.4 |
| Residual tests | partly in a summary row | no Breusch–Pagan/White/Goldfeld–Quandt verdicts, no RESET/Harvey–Collier, no runs test, no Anderson–Darling | §42.4 REE.T.RESID_TESTS |
| Plots | 16 | missing Cook's distance stem, studentised-residual index plot, partial-residual (CCPR) plots, Bland–Altman, REC curve, calibration-in-bins, absolute-error vs ŷ, percentage-error distribution, interval-width vs ŷ, fold pred-vs-actual small multiples, target vs prediction density overlay, error heatmap over two features | §42.5 |
| CV aggregation | mean ± std on metrics table | not every metric; no SEM/CI/pooled column | §42.6 |
| Model comparison | leaderboard only | no pairwise tests table, no Δ-metric CIs | §42.7 |
| AI prompts | generic "Modelling" template | no regression-specific templates or rule triggers | §42.8 |

### 42.2 Prediction sources

Same as §41.1: CV out-of-fold predictions stored per fold/repeat (`oof_predictions`: row_id, fold, repeat, y_true, y_pred, lower, upper, quantiles, weight); per-fold artefacts, CV-aggregated (mean ± std across folds and pooled OOF), test with stratified-by-ŷ-decile bootstrap 95% CIs (`scipy.stats.bootstrap`), train for gap only. With a target transform (`TransformedTargetRegressor`), metrics are computed on the **original scale** (and optionally on the transformed scale, REE.T.TARGET_TRANSFORM).

### 42.3 Scalar metrics

| ID | Metric | Formula | Best | Library |
|---|---|---|---|---|
| REE.M.01 | MAE | (1/n)Σ\|e\|, e = y − ŷ | ↓ | `mean_absolute_error` |
| REE.M.02 | MSE | (1/n)Σe² | ↓ | `mean_squared_error` |
| REE.M.03 | RMSE | √MSE | ↓ | `root_mean_squared_error` |
| REE.M.04 | MSLE | (1/n)Σ(ln(1+y) − ln(1+ŷ))² (y, ŷ > −1) | ↓ | `mean_squared_log_error` |
| REE.M.05 | RMSLE | √MSLE | ↓ | `root_mean_squared_log_error` |
| REE.M.06 | MedAE | median\|e\| | ↓ | `median_absolute_error` |
| REE.M.07 | Max error | max\|e\| | ↓ | `max_error` |
| REE.M.08 | MAPE | (1/n)Σ\|e/y\| (rows with y = 0 masked and counted) | ↓ | `mean_absolute_percentage_error` |
| REE.M.09 | MdAPE | median\|e/y\| | ↓ | `numpy.median` on sklearn-style APE (thin) |
| REE.M.10 | sMAPE | (1/n)Σ 2\|e\|/(\|y\| + \|ŷ\|) | ↓ | `sktime.performance_metrics.forecasting.mean_absolute_percentage_error(symmetric=True)` |
| REE.M.11 | WAPE | Σ\|e\| / Σ\|y\| | ↓ | `sktime` / `utilsforecast.losses` |
| REE.M.12 | Mean error (bias) | (1/n)Σ(ŷ − y) | 0 | numpy |
| REE.M.13 | Mean percentage error | (1/n)Σ(ŷ − y)/y | 0 | numpy |
| REE.M.14 | NRMSE (range / mean / std / IQR) | RMSE / {max−min, ȳ, σ_y, IQR_y} | ↓ | numpy on sklearn RMSE |
| REE.M.15 | Relative squared error (RSE) | Σe² / Σ(y − ȳ)² = 1 − R² | ↓ | from sklearn |
| REE.M.16 | Relative absolute error (RAE) | Σ\|e\| / Σ\|y − ȳ\| | ↓ | numpy |
| REE.M.17 | R² | 1 − SS_res/SS_tot | ↑ | `r2_score` |
| REE.M.18 | Adjusted R² | 1 − (1 − R²)(n − 1)/(n − p − 1) | ↑ | from `r2_score` (p = features after recipe) |
| REE.M.19 | Explained variance | 1 − Var(e)/Var(y) | ↑ | `explained_variance_score` |
| REE.M.20 | Pearson r | cov(y, ŷ)/(σ_y σ_ŷ) | ↑ | `scipy.stats.pearsonr` |
| REE.M.21 | Spearman ρ | Pearson on ranks | ↑ | `scipy.stats.spearmanr` |
| REE.M.22 | Kendall τ-b | concordant − discordant pairs (tie-corrected) | ↑ | `scipy.stats.kendalltau` |
| REE.M.23 | Lin's CCC | 2ρσ_yσ_ŷ / (σ_y² + σ_ŷ² + (μ_y − μ_ŷ)²) | ↑ | numpy on scipy statistics (thin) |
| REE.M.24 | Huber loss (δ) | mean of ½e² if \|e\| ≤ δ else δ(\|e\| − ½δ) | ↓ | numpy (thin, formula on library residuals) |
| REE.M.25 | Log-cosh loss | (1/n)Σ ln cosh(e) | ↓ | numpy (thin) |
| REE.M.26 | Pinball loss (τ) | (1/n)Σ max(τe, (τ − 1)e) | ↓ | `mean_pinball_loss` |
| REE.M.27 | Poisson deviance | 2Σ[y ln(y/ŷ) − (y − ŷ)] / n | ↓ | `mean_poisson_deviance` |
| REE.M.28 | Gamma deviance | 2Σ[−ln(y/ŷ) + (y − ŷ)/ŷ] / n | ↓ | `mean_gamma_deviance` |
| REE.M.29 | Tweedie deviance (power p) | Tweedie unit deviance averaged | ↓ | `mean_tweedie_deviance` |
| REE.M.30 | D² (Tweedie / absolute error / pinball) | 1 − D(model)/D(null) | ↑ | `d2_tweedie_score`, `d2_absolute_error_score`, `d2_pinball_score` |
| REE.M.31 | Mincer–Zarnowitz calibration (slope b, intercept a, joint F-test) | regress y = a + bŷ; ideal a = 0, b = 1 | — | `statsmodels.OLS` + `f_test` |
| REE.M.32 | Tolerance hit rate | share with \|e\| ≤ τ (absolute) or \|e/y\| ≤ τ% | ↑ | numpy |
| REE.M.33 | PICP (coverage) | (1/n)Σ 1[l ≤ y ≤ u] | = nominal | MAPIE `regression_coverage_score` |
| REE.M.34 | MPIW / normalised MPIW | mean(u − l); / range(y) | ↓ (at coverage) | MAPIE `regression_mean_width_score` |
| REE.M.35 | Interval (Winkler) score | (u − l) + (2/α)(l − y)1[y < l] + (2/α)(y − u)1[y > u] | ↓ | `scoringrules.interval_score` |
| REE.M.36 | CRPS | ∫(F(z) − 1[z ≥ y])² dz | ↓ | `properscoring.crps_ensemble` / `scoringrules.crps_*` |
| REE.M.37 | Conditional coverage gap | max over ŷ-deciles of \|coverage_bin − nominal\| | ↓ | MAPIE + numpy |
| REE.M.38 | AIC / BIC / AICc (linear, GLM) | 2k − 2lnL; k ln n − 2lnL; AIC + 2k(k+1)/(n−k−1) | ↓ | `statsmodels` results |
| REE.M.39 | Directional accuracy (sequential) | (1/n)Σ 1[sign(Δŷ) = sign(Δy)] | ↑ | numpy (TradingLab metric for S) |
| REE.M.40 | MASE (sequential / ordered data) | MAE / MAE(naive in-sample) | ↓ | `sktime.performance_metrics.forecasting.mean_absolute_scaled_error` |

### 42.4 Residual and evaluation tables

| ID | Columns | Library |
|---|---|---|
| REE.T.RESIDUALS (row level, paginated, download) | row id, split, fold, y, ŷ, residual e, \|e\|, % error, standardised residual, studentised (internally / externally), leverage hᵢᵢ, Cook's D, DFFITS, interval lower/upper, covered ✓, top-3 SHAP reasons | sklearn; `statsmodels` `OLSInfluence` for linear models (influence on a linear surrogate for non-linear models, labelled as such) |
| REE.T.RESID_STATS | n, mean, std, skew, excess kurtosis, min, p5, Q1, median, Q3, p95, max, % \|std resid\| > 2, % > 3 | `scipy.stats.describe` |
| REE.T.RESID_TESTS | test, statistic, p, verdict (pass/warn/fail at α = 0.05), plain-language meaning — rows: Shapiro–Wilk (n ≤ 5,000), D'Agostino K², Jarque–Bera, Anderson–Darling (normality); Breusch–Pagan, White, Goldfeld–Quandt (heteroscedasticity); Durbin–Watson, Ljung–Box (lags 10/20), Breusch–Godfrey (autocorrelation, ordered data); Ramsey RESET, Harvey–Collier (functional form, linear models); Wald–Wolfowitz runs test (randomness of residual signs) | `scipy.stats`, `statsmodels.stats.diagnostic` (`het_breuschpagan`, `het_white`, `het_goldfeldquandt`, `acorr_ljungbox`, `acorr_breusch_godfrey`, `linear_reset`, `linear_harvey_collier`), `statsmodels.stats.stattools.durbin_watson`, `statsmodels.sandbox.stats.runs.runstest_1samp` |
| REE.T.INFLUENCE | top-N rows by Cook's D: row id, leverage, studentised residual, Cook's D, DFFITS, DFBETAS (largest), threshold flags (h > 2p/n, D > 4/n) | `statsmodels` `OLSInfluence` |
| REE.T.CV_METRICS | metric, fold_1 … fold_k, mean, std, SEM, min, median, max, 95% CI (optionally Nadeau–Bengio corrected), pooled OOF, train mean, train − CV gap, test, test 95% bootstrap CI, direction | `cross_validate(scoring={…}, return_train_score=True)` |
| REE.T.FOLDS | repeat, fold, n_train, n_val, target mean/std in val, every metric, fit time | sklearn |
| REE.T.ERR_SEGMENT | segment (decile of ŷ, decile of y, category), n, MAE, RMSE, bias, MAPE, coverage | numpy / `fairlearn.metrics.MetricFrame` |
| REE.T.ERR_BY_FEATURE_BIN | feature, bin, n, MAE, bias, Δ vs overall | `fairlearn.metrics.MetricFrame` |
| REE.T.CALIBRATION_BINS | decile of ŷ, n, mean ŷ, mean y, gap, 95% CI of mean y | numpy; `model_diagnostics.calibration` |
| REE.T.WORST | rank, row id, y, ŷ, residual, \|std resid\|, leverage, Cook's D, top-3 SHAP | sklearn + `shap` |
| REE.T.INTERVALS | method, nominal coverage, empirical coverage, mean width, normalised width, interval score, conditional coverage gap | MAPIE |
| REE.T.COVERAGE_BY_BIN | ŷ decile, n, coverage, mean width | MAPIE + numpy |
| REE.T.COEF (linear) | feature, coefficient, std error (HC3 robust option), t, p, 95% CI, standardised coefficient, VIF | `statsmodels` (`get_robustcov_results`, `variance_inflation_factor`) |
| REE.T.BASELINES | `DummyRegressor` (mean, median, quantile) and a plain `LinearRegression`, with every headline metric | sklearn |
| REE.T.TARGET_TRANSFORM | metric on transformed scale, metric on original scale, back-transform method (inverse, smearing) | sklearn `TransformedTargetRegressor` |
| REE.T.COMPARE | rank, model, primary metric mean ± std, all headline metrics mean ± std, rank per metric, average rank, CD group, Δ vs best, p vs best (Holm), fit time, latency, size | sklearn + `scikit-posthocs` |
| REE.T.PAIRWISE_TESTS | model A, model B, test, statistic, p, Holm p, Δ RMSE with 95% CI, verdict | `scipy.stats`, `mlxtend`, `statsmodels` |

### 42.5 Plots

| ID | Plot | Shows / axes | When | Compute library |
|---|---|---|---|---|
| REE.P.PRED_ACTUAL | Predicted vs actual with y = x, R²/RMSE label; hexbin for n > 5,000; fold colouring | x y, y ŷ | always | sklearn `PredictionErrorDisplay` data |
| REE.P.PRED_ACTUAL_FOLDS | Per-fold predicted vs actual (small multiples) | | CV | sklearn |
| REE.P.RESID_FITTED | Residuals vs fitted with LOWESS | x ŷ, y e | always | `statsmodels.nonparametric.lowess` |
| REE.P.RESID_HIST | Residual histogram + KDE + normal overlay | | always | `scipy.stats` |
| REE.P.QQ | Residual Q-Q with 95% envelope | | always | `statsmodels.api.ProbPlot` |
| REE.P.SCALE_LOCATION | √\|standardised residual\| vs ŷ with LOWESS | | always | `statsmodels` |
| REE.P.LEVERAGE | Studentised residual vs leverage with Cook's D contours (0.5, 1) | | linear | `statsmodels` `OLSInfluence` |
| REE.P.COOKS | Cook's distance stem plot with 4/n line | x row index | linear | `statsmodels` |
| REE.P.STUDENTISED_INDEX | Externally studentised residual vs row index (± 3 band) | | always | `statsmodels` |
| REE.P.RESID_FEATURE | Residuals vs each feature (small multiples, LOWESS) | | on demand | `statsmodels` lowess |
| REE.P.PARTIAL_RESID | Component-plus-residual (CCPR) plots per feature | | linear | `statsmodels.graphics.regressionplots.plot_ccpr` data |
| REE.P.RESID_TIME / REE.P.RESID_ACF | Residuals over time; ACF/PACF of residuals with bands | | ordered data | `statsmodels.tsa.stattools.acf/pacf` |
| REE.P.ERR_SEGMENT | MAE / bias by ŷ-decile or category | bars | always | `fairlearn` MetricFrame |
| REE.P.ERR_FEATURE_BIN | MAE by feature bin | bars | on demand | `fairlearn` |
| REE.P.ERR_HEATMAP | Mean \|e\| over a 2-feature grid | heatmap | on demand | `scipy.stats.binned_statistic_2d` |
| REE.P.CALIBRATION_BINS | Mean y vs mean ŷ by decile with y = x (regression calibration) and Mincer–Zarnowitz line | | always | `model_diagnostics.calibration.plot_bias` data |
| REE.P.BLAND_ALTMAN | Mean of (y, ŷ) vs difference with bias and ±1.96 s limits of agreement | | always | `statsmodels.graphics.agreement.mean_diff_plot` data |
| REE.P.REC | Regression error characteristic: share of rows with \|e\| ≤ ε vs ε, area over curve | | always | numpy (ECDF via `scipy.stats.ecdf`) |
| REE.P.CUM_ERROR | Cumulative share of total absolute error vs share of rows (sorted by \|e\|) | | always | numpy |
| REE.P.ABS_ERR_FITTED | \|e\| vs ŷ (heteroscedasticity view) | | always | numpy |
| REE.P.PCT_ERR_DIST | Distribution of percentage errors (clipped at ± 100%) | | y > 0 | numpy |
| REE.P.TARGET_PRED_DENSITY | KDE of y vs KDE of ŷ (shrinkage check) | | always | `scipy.stats.gaussian_kde` |
| REE.P.PI_BAND | Prediction intervals sorted by ŷ with actuals | | uncertainty on | MAPIE |
| REE.P.COVERAGE_BIN | Coverage by ŷ-decile vs nominal | | uncertainty on | MAPIE |
| REE.P.PIT | PIT histogram (quantile calibration) | | quantiles on | `scipy.stats` |
| REE.P.WIDTH_FITTED | Interval width vs ŷ | | uncertainty on | MAPIE |
| REE.P.COEF_FOREST | Coefficients with 95% CI | | linear | `statsmodels` |
| REE.P.REG_PATH | Coefficient paths vs log α | | Lasso/Ridge/ENet | `sklearn.linear_model.lasso_path`, `enet_path` |
| REE.P.ALPHA_CV | CV score vs α | | regularised | `LassoCV`, `RidgeCV` |
| REE.P.METRIC_FOLDS | Box/strip of each metric across folds | | CV | numpy |
| REE.P.COMPARE_BARS | Model comparison bars with 95% CI | | compare | numpy |
| REE.P.CD | Critical-difference diagram | | ≥ 3 models | `scikit-posthocs` |
| REE.P.PVALUE_HEATMAP | Pairwise p-values (Holm) | | compare | `scikit-posthocs` |
| REE.P.LEARNING / REE.P.VALIDATION | Learning and validation curves | | always / tuning | sklearn |

### 42.6 CV aggregation

REE.T.CV_METRICS covers **every** applicable REE.M.* metric with fold values, mean ± std, SEM, CI, pooled OOF, train gap and test CI (same protocol as §41.8). The headline view (old REG.T.METRICS) shows RMSE, MAE, R², MAPE (when valid), MedAE and bias.

### 42.7 Statistical comparison

Corrected resampled t-test (Nadeau–Bengio) on fold scores, Wilcoxon signed-rank on paired fold scores and on paired per-row squared errors (test split), 5 × 2 cv paired t-test and combined F-test (`mlxtend`), Friedman + Nemenyi (`scikit-posthocs`), Diebold–Mariano with HLN correction for ordered data (`sktime`/`statsmodels`-based helper; §35.10), paired bootstrap CI of Δ RMSE / Δ MAE (`scipy.stats.bootstrap`), Holm correction (`statsmodels`).

### 42.8 AI Insights prompts for regression evaluation

Rule triggers: R²(CV) < R²(baseline linear) + 0.02 → "no gain over linear"; |bias| > 0.1·σ_y; Breusch–Pagan p < 0.05 and a fan shape → heteroscedasticity (suggest log/Box-Cox target or quantile/conformal intervals); Ljung–Box p < 0.05 on ordered data → autocorrelated errors; Mincer–Zarnowitz slope < 0.9 → shrinkage / over-dispersion; > 1% rows with Cook's D > 4/n → influential points; coverage gap > 5 points → intervals miscalibrated; train − CV RMSE gap > 20% → overfitting; one decile MAE > 2 × overall → weak region.

| Template (`labcore/insights/prompts/eval_regression_*.md`) | Images | FACTS | Required content |
|---|---|---|---|
| `fit` | REE.P.PRED_ACTUAL, REE.P.CALIBRATION_BINS, REE.P.TARGET_PRED_DENSITY | REE.T.CV_METRICS, REE.T.BASELINES | fit quality vs baselines, bias, shrinkage at the tails |
| `residuals` | REE.P.RESID_FITTED, REE.P.QQ, REE.P.SCALE_LOCATION, REE.P.RESID_ACF | REE.T.RESID_STATS, REE.T.RESID_TESTS | assumption checks with plain-language verdicts, suggested remedies (`apply_patch`: target transform, interactions, robust loss) |
| `influence` | REE.P.LEVERAGE, REE.P.COOKS | REE.T.INFLUENCE | influential rows (aggregated), whether conclusions depend on them |
| `segments` | REE.P.ERR_SEGMENT, REE.P.ERR_FEATURE_BIN | REE.T.ERR_SEGMENT | where the model fails and hypotheses |
| `intervals` | REE.P.PI_BAND, REE.P.COVERAGE_BIN, REE.P.PIT | REE.T.INTERVALS, REE.T.COVERAGE_BY_BIN | interval reliability and width trade-off |
| `compare` | REE.P.COMPARE_BARS, REE.P.CD | REE.T.COMPARE, REE.T.PAIRWISE_TESTS | champion with statistical support |

### 42.9 Tests and acceptance

Every REE.M.* equals its library reference on DS3/DS12 (seed 42) to 1e-9; Σ fold residual counts = n; studentised residuals and Cook's D equal `statsmodels` `OLSInfluence` for OLS; residual test p-values equal `statsmodels`; Bland–Altman limits equal `mean_diff_plot` values; snapshot tests for every REE.P.*.

### 42.10 Counts (regression evaluation)

40 metrics (REE.M.01–40), 17 tables (REE.T.*), 36 plots (REE.P.*, counting paired IDs separately), 7 comparison methods, 6 AI-insight templates.

---

## 43. Library gap audit — additions and replacements (round 3)

> Round-3 addition (15 Nov 2026). The catalogues in §10–§42 were compared with what scikit-learn, XGBoost, LightGBM, CatBoost, statsmodels, sktime, darts, statsforecast / neuralforecast / mlforecast, pmdarima, Prophet, arch, pytorch-tabular, pytorch-forecasting, umap-learn, hdbscan, PyOD, imbalanced-learn, category_encoders, feature-engine, ydata-profiling, sweetviz, Yellowbrick, SHAP, LIME, alibi, DiCE, MAPIE, Optuna, PyCaret, H2O and AutoGluon offer. **Rule (now binding, `.cursor/rules/70-use-established-libraries.mdc`): every algorithm, encoder, transformer, metric, statistical test and plot computation must come from a popular, maintained library listed in the Library Matrix (§44). Lab code may only be a thin wrapper (argument mapping, arranging outputs, arithmetic on library outputs, plotting library outputs). WFO and PBO drivers are thin wrappers over ml-for-trading (TradingLab) and scikit-learn functions.** The full change log is in `docs/GAP_AUDIT.md`. Versions are in `backend/requirements/*.txt` (resolved together with `uv pip compile` for Python 3.12).

### 43.1 How the "Library" column is used

Every catalogue table in §10–§42 now has a **Library** column (or an existing *Implementation* / *Library call* column that names the library). Values name the package and, where helpful, the class or function (e.g. `sklearn.metrics.matthews_corrcoef`). "thin" marks lab arithmetic on library outputs (for example NPV from `multilabel_confusion_matrix`). "TradingLab" is the user's ml-for-trading package. Plots name the **compute** library; all plots are rendered with Plotly.

### 43.2 Supervised algorithms added (IDs continue §12)

| ID | Algorithm (key) | Task | Library | Default → Balanced search space | Why added |
|---|---|---|---|---|---|
| R52 | Isotonic regression `reg.isotonic` | regression (one monotone feature or as a calibrator) | `sklearn.isotonic.IsotonicRegression` | increasing='auto'; out_of_bounds='clip' | sklearn has it; monotone relations |
| R53 | PLS regression `reg.pls` | regression, collinear / p > n | `sklearn.cross_decomposition.PLSRegression` | n_components=2 → int(1, min(20, p)) | sklearn, PyCaret-style chemometrics |
| R54 | Multi-task Lasso / ElasticNet `reg.multitask` | multi-output regression | `sklearn.linear_model.MultiTaskLassoCV` / `MultiTaskElasticNetCV` | alphas auto; l1_ratio [0.1…0.9] | multi-output support |
| R55 | Multi-output wrappers `reg.multioutput` | multi-output regression | `sklearn.multioutput.MultiOutputRegressor`, `RegressorChain` | base model from §12.1; chain order random(seed) | multi-output support |
| R56 | Quantile regression forest `reg.qrf` | regression with quantiles | `quantile_forest.RandomForestQuantileRegressor` | n_estimators=300; quantiles [0.05, 0.5, 0.95] | distribution-free intervals |
| R57 | GLM (glum) `reg.glum` | Poisson/Gamma/Tweedie GLM, large n | `glum.GeneralizedLinearRegressorCV` | family from target; l1_ratio [0, 1] | fast elastic-net GLMs |
| R58 | Symbolic regression `reg.symbolic` (optional, Thorough) | interpretable formulas | `gplearn.genetic.SymbolicRegressor` | population 1000, generations 20, parsimony 0.001 | interpretability |
| R59 | FIGS / hierarchical-shrinkage trees `reg.figs` | interpretable trees | `imodels` (`FIGSRegressor`, `HSTreeRegressorCV`) | max_rules=12 → int(4, 30) | interpretable models (imodels) |
| R60 | GPBoost (boosting + random effects) `reg.gpboost` (optional) | grouped / panel data | `gpboost` | group column required; learning_rate 0.05 | mixed-effects data |
| C36 | Logistic / Ridge classifier with built-in CV `clf.logreg_cv` | classification | `sklearn.linear_model.LogisticRegressionCV`, `RidgeClassifierCV` | Cs=10; cv from §13 | sklearn CV estimators |
| C37 | Multilabel wrappers `clf.multilabel` | multilabel | `sklearn.multioutput.MultiOutputClassifier`, `ClassifierChain` | base model from §12.2 | multilabel support (§41) |
| C38 | Native multilabel estimators `clf.multilabel_native` | multilabel | sklearn `RandomForestClassifier`, `ExtraTreesClassifier`, `KNeighborsClassifier`, `MLPClassifier` on Y ∈ {0,1}^{n×L} | as §12.2 | multilabel support |
| C39 | Threshold wrappers `clf.threshold` | binary / multilabel | `sklearn.model_selection.TunedThresholdClassifierCV`, `FixedThresholdClassifier` | §41.6 methods | threshold optimisation |
| C40 | Semi-supervised `clf.semi` (optional) | partially labelled data | `sklearn.semi_supervised.SelfTrainingClassifier`, `LabelSpreading` | threshold 0.75; kernel knn | unlabelled rows in uploads |
| C41 | Interpretable rule models `clf.rules` | classification | `imodels` (`RuleFitClassifier`, `FIGSClassifier`, `GreedyRuleListClassifier`) | max_rules 12 → int(4, 30) | interpretability |
| C42 | RIPPER rule learner `clf.ripper` (optional) | binary | `wittgenstein.RIPPER` | k=2, prune_size 0.33 | rule lists |
| C43 | Calibrated prediction sets `clf.venn_abers` | binary/multiclass probabilities | `venn_abers.VennAbersCalibrator` | inductive, cal_size 0.2 | calibration (§21, §41) |
| R61 / C44 | AutoML preset `automl.autogluon` (optional image) | regression / classification | `autogluon.tabular.TabularPredictor` | presets='medium_quality', time_limit 900 s | AutoGluon parity |
| R62 / C45 | AutoML preset `automl.h2o` (optional image, Java 17) | regression / classification | `h2o.automl.H2OAutoML` | max_models 20, seed 42 | H2O parity |

PyCaret 3.3.2 (last release April 2024) pins older scikit-learn and is **not installed**; it was used only as a feature checklist (its `compare_models`, `plot_model` and `tune_model` options are all covered by §12–§14, §41, §42).

### 43.3 Sequence (time-ordered window) models: library backing

| ID | Model | Library (replaces "PyTorch / lab") |
|---|---|---|
| Q1–Q4, Q6, Q8, Q9 | RNN, LSTM, GRU, Bi-RNN, 1D-CNN, CNN-LSTM, Transformer encoder | built-in `torch.nn` modules (`nn.RNN`, `nn.LSTM`, `nn.GRU`, `nn.Conv1d`, `nn.TransformerEncoder`) composed and trained with `lightning`; no custom layers |
| Q5 | Stacked LSTM + attention | `torch.nn.LSTM` + `torch.nn.MultiheadAttention` |
| Q7 | TCN | `pytorch-tcn` (`TCN`) |
| Q10 | PatchTST-style encoder | `neuralforecast.models.PatchTST` (forecast windows) |
| Q11 | TFT | `pytorch_forecasting.TemporalFusionTransformer` (classification via `CrossEntropy` loss) / `neuralforecast.models.TFT` |
| Q12 | xLSTM / Mamba (optional, GPU only) | `xlstm`, `mamba-ssm` (optional GPU image) |
| Q13 | Sequentially bootstrapped DL bagging | TradingLab `SequentiallyBootstrappedBagging*` (thin wrapper around a Lightning model) |
| Q14 | ROCKET / MiniRocket / MultiRocket + ridge (new) | `aeon.classification.convolution_based` / `aeon.regression.convolution_based` |
| Q15 | Catch22 / TSFresh features + GBM (new) | `aeon.transformations.collection.feature_based.Catch22`, `tsfresh.extract_relevant_features` + LightGBM |
| Q16 | Interval forests DrCIF / TSF (new) | `aeon.classification.interval_based` |
| Q17 | k-NN with DTW (new) | `aeon.classification.distance_based.KNeighborsTimeSeriesClassifier` |
| Q18 | HIVE-COTE 2 (new, Thorough only, slow) | `aeon.classification.hybrid.HIVECOTEV2` |

`tsai` was evaluated and excluded: version 1.0.1 requires scikit-learn < 1.8 (conflicts with the pinned 1.9.1).

### 43.4 Tabular deep learning: library backing and flags

| ID | Model | Library | Status |
|---|---|---|---|
| T1, T3, T4, T5, T7, T8, T10, T11, T12, T14, T15, T16 | MLP, TabNet, FT-Transformer, TabTransformer, NODE, AutoInt, GANDALF, GATE, DANet, MDN, stacking, SSL pre-training | `pytorch-tabular` 1.2.0 | default |
| T2 | ResNet-MLP | no maintained library compatible with numpy 2 / scikit-learn 1.9 (`rtdl` last released 2022; `pytorch-widedeep` 1.7.0 requires numpy < 2) | **optional, off by default** (experimental) |
| T6 | SAINT | same as T2 | **optional, off by default** |
| T9 | DCN-v2 | no maintained tabular library | **optional, off by default** |
| T13 | TabPFN | `tabpfn` (model-weights licence) | off by default (licence) |

`pytorch-tabnet` (last release 2023) is replaced by pytorch-tabular's `TabNetModelConfig`.

### 43.5 Unsupervised additions

| ID | Algorithm | Library | Notes |
|---|---|---|---|
| D23 | PLS / CCA (supervised DR) | `sklearn.cross_decomposition` | |
| D24 | Neighbourhood components analysis | `sklearn.neighbors.NeighborhoodComponentsAnalysis` | supervised DR |
| D25 | Factor analysis with varimax / quartimax rotation | `sklearn.decomposition.FactorAnalysis(rotation=…)` | promax/oblimin need factor_analyzer (GPL-2.0) → licence review |
| D26 | densMAP | `umap.UMAP(densmap=True)` | density-preserving |
| D27 | Mini-batch NMF | `sklearn.decomposition.MiniBatchNMF` | large data |
| D28 | Feature agglomeration (variable clustering) | `sklearn.cluster.FeatureAgglomeration` | |
| K20 | Time-series k-means (Euclidean / DTW / soft-DTW) | `tslearn.clustering.TimeSeriesKMeans` | panels of series |
| K21 | k-Shape | `tslearn.clustering.KShape` | shape-based series clustering |
| K22 | Kernel k-means | `tslearn.clustering.KernelKMeans` | |
| K23 | Spectral bi-/co-clustering (optional) | `sklearn.cluster.SpectralBiclustering`, `SpectralCoclustering` | |
| A15 | INNE | `pyod.models.inne` | |
| A16 | KDE / GMM / MCD / SOD / ROD / LMDD detectors | `pyod.models.*` | |
| A17 | Deep Isolation Forest | `pyod.models.dif` | |
| A18 | LUNAR, ALAD, AnoGAN, SO-GAAL / MO-GAAL (optional, GPU) | `pyod.models.*` | |
| A19 | XGBOD (semi-supervised, uses known anomalies) | `pyod.models.xgbod` | |
| A20 | LSCP ensemble | `pyod.models.lscp` | |
| A21 | Matrix-profile discords (time series) | `stumpy.stump` | |
| A22 | Change points (PELT, BinSeg, BottomUp, Window, KernelCPD) | `ruptures` | |
| A23 | Darts anomaly scorers (k-means, norm, Wasserstein) | `darts.ad` | |
| — | Contamination-free thresholding (IQR, MAD, Karcher, OCSVM, … 30+ methods) | `pythresh` | replaces a fixed contamination guess |

Replaced "lab" items: PCA reconstruction error → `pyod.models.pca.PCA`; Mahalanobis / robust z → `sklearn.covariance.MinCovDet.mahalanobis`, `pyod.models.mad.MAD`; S-H-ESD → **optional thin wrapper** (`statsmodels` STL residuals + `scipy.stats.t` critical values; no maintained Python library — `adtk` last released 2020), default replaced by STL residual + `pyod` MAD + `ruptures`; Deep Embedded Clustering (DEC) → **optional, off by default** (no maintained library); dense / variational / denoising autoencoders for DR → **optional, off by default** (thin Lightning modules over `torch.nn`), anomaly autoencoders use `pyod.models.auto_encoder` / `vae`. K-Medoids: `scikit-learn-extra` (last release 2023) and `kmedoids` (GPL-3.0) both flagged → **optional**. PHATE (GPL-2.0) → licence review.

### 43.6 Forecasting additions (IDs continue §19.2 / §35.2)

| ID | Model | Library | Notes |
|---|---|---|---|
| F55 | AutoReg AR(p) | `statsmodels.tsa.ar_model.AutoReg` | lags by AIC |
| F56 | ARDL / UECM | `statsmodels.tsa.ardl` | distributed lags of exogenous series |
| F57 | Markov-switching regression / AR (regimes) | `statsmodels.tsa.regime_switching` | k_regimes 2–3; financial regimes |
| F58 | Dynamic factor model (incl. mixed frequency) | `statsmodels.tsa.statespace.DynamicFactor`, `DynamicFactorMQ` | many related series |
| F59 | ThetaModel, STLForecast (alternative backends) | `statsmodels.tsa.forecasting` | |
| F60 | pmdarima auto_arima | `pmdarima.auto_arima` (OCSB / Canova–Hansen seasonal tests, stepwise) | second Auto-ARIMA, cross-check of F12 |
| F61 | GARCH family: EGARCH, GJR-GARCH, FIGARCH, HARCH, APARCH; Normal / t / skew-t errors; HAR-RV (HARX mean) | `arch.arch_model` | extends F23 |
| F62 | Darts models: KalmanForecaster, FFT, NaiveDrift / NaiveMovingAverage, LinearRegressionModel, LightGBMModel / XGBModel / CatBoostModel (probabilistic), BlockRNNModel, TSMixerModel, TiDEModel | `darts.models` | alternative backend with likelihoods |
| F63 | pytorch-forecasting TFT / N-HiTS / DeepAR | `pytorch_forecasting` | alternative backend with interpretation plots |
| F64 | skforecast ForecasterRecursive / ForecasterDirect / ForecasterRecursiveMultiSeries | `skforecast` | explicit (was "alternative") |
| F65 | AutoGluon TimeSeriesPredictor (optional image) | `autogluon.timeseries` | AutoML parity |
| F66 | Forecast ensembles (replaces "lab") | `sktime.forecasting.compose.EnsembleForecaster` / `AutoEnsembleForecaster`, `darts.models.RegressionEnsembleModel`, `NaiveEnsembleModel` | |
| F67 | Foundation models (optional image): Chronos, TimesFM | `chronos-forecasting`, `timesfm` | Moirai (`uni2ts`) excluded: requires torch < 2.5 |

Fourier terms (was "lab") → `utilsforecast.feature_engineering.fourier` / `sktime.transformations.series.fourier.FourierFeatures`. Kalman filter (was `pykalman`, now conflicting with sktime 1.3) → `statsmodels` state-space models (`UnobservedComponents`, `SARIMAX`) and `darts.models.KalmanForecaster`. NeuralProphet not added (last release June 2024).

### 43.7 Encoders added (IDs continue §11.2)

| ID | Encoder | Library | Notes |
|---|---|---|---|
| E23 | Decision-tree encoder | `feature_engine.encoding.DecisionTreeEncoder` | target-aware, fold-internal |
| E24 | String-similarity encoder | `feature_engine.encoding.StringSimilarityEncoder` | dirty categories |
| E25 | Min-hash encoder | `skrub.MinHashEncoder` | high-cardinality strings |
| E26 | Gap encoder | `skrub.GapEncoder` | interpretable latent categories |
| E27 | Table vectoriser (auto column typing + encoders) | `skrub.TableVectorizer` | baseline assembler, cross-check of Intake |
| E28 | Multiclass target-encoding wrapper | `category_encoders.wrapper.PolynomialWrapper` | target encoding for K > 2 |
| E29 | Infrequent-category grouping | `sklearn.preprocessing.OneHotEncoder(min_frequency, max_categories)`, `feature_engine.encoding.RareLabelEncoder` | |
| E30 | Target-ordered ordinal encoder | `feature_engine.encoding.OrdinalEncoder(encoding_method='ordered')` | |
| E31 | Mean encoder with smoothing | `feature_engine.encoding.MeanEncoder` | alternative to sklearn `TargetEncoder` |
| E32 | Datetime encoder | `skrub.DatetimeEncoder`, `feature_engine.datetime.DatetimeFeatures` | |

### 43.8 Preprocessing, feature engineering and selection added

| Group | Added transformers | Library |
|---|---|---|
| Imputation | ArbitraryNumberImputer, EndTailImputer, RandomSampleImputer, CategoricalImputer, AddMissingIndicator, DropMissingData; MissForest-style = `IterativeImputer(estimator=ExtraTreesRegressor)` | `feature_engine.imputation`, sklearn |
| Outliers | Winsorizer (Gaussian / IQR / MAD / quantiles), ArbitraryOutlierCapper, OutlierTrimmer | `feature_engine.outliers` |
| Discretisation | EqualFrequency-, EqualWidth-, DecisionTree-, GeometricWidth-Discretiser; optimal binning | `feature_engine.discretisation`, `optbinning` |
| Transforms | LogCpTransformer, ArcsinTransformer, ReciprocalTransformer, BoxCox / YeoJohnson; FunctionTransformer | `feature_engine.transformation`, sklearn |
| Feature creation | MathFeatures, RelativeFeatures, CyclicalFeatures, DecisionTreeFeatures, GeoDistanceFeatures; PolynomialFeatures, SplineTransformer, Nystroem, RBFSampler | `feature_engine.creation`, sklearn |
| Datetime | DatetimeFeatures, DatetimeSubtraction, DatetimeOrdinal | `feature_engine.datetime` |
| Time-series features | LagFeatures, WindowFeatures, ExpandingWindowFeatures; mlforecast lag transforms; tsfresh (with relevance filter), tsfel, Catch22 | `feature_engine.timeseries.forecasting`, `mlforecast.lag_transforms`, `tsfresh`, `tsfel`, `aeon` |
| Selection | DropConstantFeatures, DropDuplicateFeatures, DropCorrelatedFeatures, SmartCorrelatedSelection, DropHighPSIFeatures, SelectByShuffling, SelectBySingleFeaturePerformance, RecursiveFeatureElimination / Addition, SelectByTargetMeanPerformance, ProbeFeatureSelection, SelectByInformationValue, **MRMR** (was unlabelled); SelectFdr / SelectFpr / SelectFwe, GenericUnivariateSelect; ExhaustiveFeatureSelector, floating SFS; ShapRFECV | `feature_engine.selection`, sklearn, `mlxtend.feature_selection`, `probatus` |
| Data contracts | schema and value checks on ingestion | `pandera` |

### 43.9 Cross-validation schemes added or re-backed

| Key | Scheme | Library |
|---|---|---|
| cv.predefined | User-supplied fold column | `sklearn.model_selection.PredefinedSplit` |
| cv.multilabel_strat | (Repeated) multilabel stratified K-fold | `iterstrat.ml_stratifiers.MultilabelStratifiedKFold` |
| cv.group_ts | Group time-series split (groups ordered in time) | `mlxtend.evaluate.GroupTimeSeriesSplit` |
| cv.bootstrap | Bootstrap .632 / .632+ (was "lab") | `mlxtend.evaluate.bootstrap_point632_score` |
| cv.walk_forward | Walk-forward (was "lab") | `sktime.split.ExpandingWindowSplitter`, `SlidingWindowSplitter`, `ExpandingGreedySplitter` |
| cv.ts_cutoffs | Single window / explicit cut-offs | `sktime.split.SingleWindowSplitter`, `CutoffSplitter` |
| cv.ts_fold | skforecast backtesting folds | `skforecast.model_selection.TimeSeriesFold`, `OneStepAheadFold` |
| cv.nixtla_cv | Rolling-origin CV for Nixtla models | `StatsForecast.cross_validation`, `MLForecast.cross_validation`, `NeuralForecast.cross_validation` |
| cv.darts_backtest | Historical forecasts / backtest | `darts` `historical_forecasts`, `backtest` |
| cv.blocked | Blocked K-fold (was "lab") | `sklearn.model_selection.KFold(shuffle=False)` + thin gap wrapper |
| cv.hv_block | hv-block | **optional thin wrapper** over `KFold(shuffle=False)` (no maintained library) |
| cv.purged, cv.cpcv | Purged K-fold, CPCV | TradingLab (unchanged) |

### 43.10 EDA additions

| ID | Table / plot | Library |
|---|---|---|
| EDA.T.ALERTS | profile alerts: constant, high cardinality, high correlation, imbalance, missing, skewed, uniform, unique, zeros, duplicates (rules reproduce ydata-profiling alert types, computed with pandas/scipy so the core stack does not depend on ydata-profiling) | pandas, scipy |
| EDA.T.PHIK | φK correlation matrix + significance (mixed types) | `phik` |
| EDA.T.ASSOC | Cramér's V, Tschuprow's T, Theil's U for categorical pairs; correlation ratio η | `scipy.stats.contingency.association`, `dython.nominal` |
| EDA.T.SPLIT_COMPARE | train vs test per feature: KS / χ² p, PSI, Wasserstein, Jensen–Shannon + adversarial-validation ROC-AUC | `scipy.stats`, `scipy.spatial.distance`, sklearn |
| EDA.T.DIST_CORR | distance correlation | `dcor` |
| EDA.T.HURST | Hurst exponent, DFA, sample entropy (sequential) | `nolds` |
| EDA.T.CONTRACT | data-contract check results | `pandera` |
| EDA.P.NULLITY_DENDRO | nullity dendrogram | `missingno` (numbers) / `scipy.cluster.hierarchy` |
| EDA.P.RANK1D / EDA.P.RANK2D | Shapiro rank per feature; pairwise Pearson / covariance rank | scipy (Yellowbrick design) |
| EDA.P.RADVIZ / EDA.P.PARALLEL | RadViz and parallel coordinates by class | `pandas.plotting` numbers → Plotly |
| EDA.P.FEATURE_TARGET | feature correlation / MI to target bars | `sklearn.feature_selection.mutual_info_*`, scipy |
| EDA.P.PHIK | φK heatmap | `phik` |
| — | Optional one-click full HTML profile and train/test comparison report | `ydata-profiling` (separate image), `sweetviz` |

MIC (`minepy`, GPL, unmaintained) removed from EDA.T.CORR.* — replaced by φK, distance correlation and mutual information.

### 43.11 Explainability, uncertainty and tuning additions

| Area | Added | Library |
|---|---|---|
| Interactions | SHAP interaction values (replaces lab Friedman H as default; H stays as optional thin wrapper over sklearn PDP) | `shap.TreeExplainer.shap_interaction_values` |
| Interactions (optional) | Shapley interaction indices | `shapiq` |
| ALE | ALE 1D/2D (replaces alibi ALE) | `PyALE` |
| Anchors | anchor rules | `alibi` **flagged: Business Source License 1.1** → optional, off until licensed |
| DL attributions | Integrated Gradients, DeepLift, saliency, feature ablation | `captum` |
| Glass-box | EBM global/local, Morris sensitivity | `interpret` |
| Trees | tree diagrams | `dtreeviz`, `sklearn.tree.plot_tree` / `export_text` |
| Slices / fairness | metric by group | `fairlearn.metrics.MetricFrame` |
| Label quality | label-issue detection from OOF probabilities | `cleanlab` (Apache-2.0) |
| Calibration | beta calibration, histogram binning, BBQ, ECE family | `netcal` |
| Conformal | conformal predictive systems, Mondrian | `crepes` (with MAPIE as default) |
| Venn–Abers | IVAP / CVAP | `venn-abers` |
| Proper scores | CRPS, energy score, interval score | `scoringrules`, `properscoring` |
| Tuning | samplers QMC, BruteForce, NSGA-III, GP; pruners Median, Patient, Wilcoxon, Threshold; all `optuna.visualization` plots (history, importances, parallel coordinate, contour, slice, EDF, intermediate values, rank, timeline, Pareto front, hypervolume history); RDB storage on Supabase Postgres | `optuna`, `optuna-integration` |
| Model comparison | critical-difference diagram, post-hoc tests | `scikit-posthocs` |

### 43.12 Isolated or excluded libraries (dependency conflicts checked on 15 Nov 2026)

| Library | Reason | Decision |
|---|---|---|
| ydata-profiling 4.18.4 | requires numpy < 2.4, scipy < 1.17, matplotlib ≤ 3.10 | separate optional image `lab-worker-reports` |
| evidently 0.7.23 | requires plotly < 6 | separate optional monitoring image; drift metrics from scipy |
| tsai 1.0.1 | requires scikit-learn < 1.8 | excluded (see §43.3) |
| pytorch-widedeep 1.7.0 | requires numpy < 2 | excluded (see §43.4) |
| ngboost 0.6.0 | caps scikit-learn < 1.7 on Python < 3.14 | pinned 0.5.11 (supports scikit-learn < 2) |
| pykalman 0.11.2 | requires scikit-base < 0.14 (sktime 1.3 needs ≥ 1.0) | removed; statsmodels / darts Kalman |
| confidenceinterval 1.0.5 | pins setuptools ~= 68.2 | replaced by `MLstatkit` for DeLong |
| uni2ts 2.0.0 (Moirai) | requires torch < 2.5 | excluded from the foundation image |
| PyCaret 3.3.2 | last release April 2024, old scikit-learn pins | not installed; checklist only |
| alibi, alibi-detect | Business Source License 1.1 | licence review |
| factor_analyzer, PHATE, kmedoids, pycatch22, minepy, pingouin | GPL family | not imported by labcore (factor_analyzer used only as a dev-time test oracle) |
| deepchecks | AGPL-3.0 | not used |
| sdv / deepecho | Business Source License | not used |
| scikit-survival | GPL-3.0 (survival analysis is out of scope) | not used |

### 43.13 Counts after the audit

| Catalogue | Before round 3 | Added | After |
|---|---|---|---|
| Regression algorithms | 51 | 11 (R52–R62) | 62 |
| Classification algorithms | 35 | 10 (C36–C45) | 45 |
| Sequential window models | 13 (Q1–Q13) | 5 (Q14–Q18) | 18 |
| Dimensionality reduction | 22 | 6 (D23–D28) | 28 |
| Clustering | 19 | 4 (K20–K23) | 23 |
| Anomaly detection | 14 | 9 (A15–A23) + thresholding | 23 |
| Forecasting | 54 | 13 (F55–F67) | 67 |
| Encoders | 22 | 10 (E23–E32) | 32 |
| CV schemes | 20 (+ purged/CPCV) | 9 new keys, 3 re-backed | 29 |
| Classification evaluation (§41) | 25 metrics / 9 tables / 13 plots | — | 55 / 42 / 45 |
| Regression evaluation (§42) | 22 metrics / 8 tables / 16 plots | — | 40 / 17 / 36 |
| EDA | 19 tables / 9 plot groups | 7 tables, 6 plots | 26 tables |

Optional / off-by-default items (with reasons): T2, T6, T9, T13, DEC, DR autoencoders, K-Medoids, fuzzy c-means (scikit-fuzzy, low release cadence), k-modes / k-prototypes (`kmodes`, last release 2022 — the only maintained option, kept optional), PHATE, Anchors, S-H-ESD, hv-block, Friedman H, R58, R60, C40, C42, AutoML and foundation images.

---

## 44. Appendix — Library Matrix (single source of truth)

> Round-3 addition, updated in v2.2 (150 libraries; round 4 added openpyxl, python-calamine, defusedxml, skops, charset-normalizer, nbformat, WeasyPrint, python-pptx, python-docx, slowapi, OpenTelemetry and the dev tools jsonschema and pgserver). Every library the lab imports, with the pinned version (latest PyPI release checked on 15 Nov 2026, IST, adjusted where the joint resolution required it — see §43.12), licence, purpose and requirements file under `backend/requirements/`. The worker images were resolved together with `uv pip compile --python-version 3.12`; lock files `api.lock.txt`, `worker-light.lock.txt` and `worker-train.lock.txt` (generated with `--python-platform x86_64-manylinux_2_28` and the PyTorch CPU index) are in the kit. TradingLab (`ml-for-trading`, private Git dependency) is not on PyPI and is installed from a tagged commit. A library that is not in this table may not be imported (rule 70).

Licence policy: permissive licences (MIT, BSD, Apache-2.0, NCSA, MPL-2.0 for test tooling) are allowed. LGPL (psycopg) is allowed for normal dynamic use. GPL/AGPL/BSL libraries are not imported by `labcore`; they appear only in `optional-licence-review.txt` (not installed) or as a dev-time test oracle (factor_analyzer).

| Library | Version pin | Licence | Used for | Requirements file | PyPI |
|---|---|---|---|---|---|
| aeon | 1.6.0 | BSD-3-Clause | sequence classifiers/regressors (ROCKET family, DrCIF, DTW-kNN, HIVE-COTE 2), Catch22 | `ts` | https://pypi.org/project/aeon/ |
| alibi | 0.9.6 | BSL-1.1 | licence review: Anchors | `optional-licence-review` | https://pypi.org/project/alibi/ |
| arch | 9.0.0 | NCSA | GARCH family, unit-root tests (DF-GLS, Phillips-Perron, Zivot-Andrews), bootstrap | `ts` | https://pypi.org/project/arch/ |
| autogluon | 1.6.3 | Apache-2.0 | optional AutoML image (tabular, time series) | `optional-automl` | https://pypi.org/project/autogluon/ |
| boruta | 0.4.3 | BSD-3-Clause | Boruta feature selection | `ml-core` | https://pypi.org/project/boruta/ |
| captum | 0.9.0 | BSD-3-Clause | DL attributions (IG, DeepLift, saliency) | `dl-cpu` | https://pypi.org/project/captum/ |
| catboost | 1.2.10 | Apache-2.0 | gradient boosting with native categoricals (R35, C23) | `ml-core` | https://pypi.org/project/catboost/ |
| category-encoders | 2.11.2 | BSD-3-Clause | encoders E5–E20, PolynomialWrapper (E28) | `ml-core` | https://pypi.org/project/category-encoders/ |
| celery | 5.7.0 | BSD-3-Clause | job queue | `api` | https://pypi.org/project/celery/ |
| charset-normalizer | 3.5.2 | MIT | encoding detection on CSV upload (§9, §45.3) | `ml-core` | https://pypi.org/project/charset-normalizer/ |
| chronos-forecasting | 2.3.2 | Apache-2.0 | optional foundation forecasting | `optional-foundation` | https://pypi.org/project/chronos-forecasting/ |
| cleanlab | 2.9.0 | Apache-2.0 | label-issue detection | `xai-uq` | https://pypi.org/project/cleanlab/ |
| coreforecast | 0.0.20 | Apache-2.0 | fast lag/rolling transforms used by mlforecast | `ts` | https://pypi.org/project/coreforecast/ |
| crepes | 0.9.1 | BSD-3-Clause | conformal predictive systems, Mondrian conformal | `xai-uq` | https://pypi.org/project/crepes/ |
| darts | 0.48.1 | Apache-2.0 | alternative forecasting backend, backtests, anomaly scorers | `ts` | https://pypi.org/project/darts/ |
| dcor | 0.7 | MIT | distance correlation | `eda` | https://pypi.org/project/dcor/ |
| defusedxml | 0.7.1 | PSF-2.0 | XML-bomb-safe parsing for any XML input (§46.3) | `ml-core` | https://pypi.org/project/defusedxml/ |
| dice-ml | 0.12 | MIT | counterfactual explanations | `xai-uq` | https://pypi.org/project/dice-ml/ |
| dtreeviz | 2.3.2 | MIT | decision-tree visualisation | `xai-uq` | https://pypi.org/project/dtreeviz/ |
| duckdb | 2.0.0 | MIT | SQL over Parquet for large previews | `ml-core` | https://pypi.org/project/duckdb/ |
| dython | 0.7.12 | MIT | Theil's U and correlation ratio | `eda` | https://pypi.org/project/dython/ |
| evidently | 0.7.23 | Apache-2.0 | optional monitoring reports (isolated image) | `optional-monitoring` | https://pypi.org/project/evidently/ |
| exchange-calendars | 4.11.1 | Apache-2.0 | trading-day frequency labels (XNSE/XBOM/XNYS) for intake D2 (§33.4) | `eda` | https://pypi.org/project/exchange-calendars/ |
| factor-analyzer | 0.5.1 | GPL-2.0 | dev-only test oracle for KMO/Bartlett | `dev` | https://pypi.org/project/factor-analyzer/ |
| fairlearn | 0.15.0 | MIT | metric-by-segment tables (MetricFrame) | `xai-uq` | https://pypi.org/project/fairlearn/ |
| fastapi | 0.163.0 | MIT | REST API | `api` | https://pypi.org/project/fastapi/ |
| feature-engine | 1.9.4 | BSD-3-Clause | imputers, outlier cappers, discretisers, transformers, feature creation, datetime/lag/window features, selectors (§43.8), encoders E23/E24/E29–E31 | `ml-core` | https://pypi.org/project/feature-engine/ |
| glum | 3.4.1 | BSD-3-Clause | fast elastic-net GLMs (R57) | `ml-core` | https://pypi.org/project/glum/ |
| gpboost | 1.8.0 | Apache-2.0 | boosting with random effects (R60, optional) | `ml-core` | https://pypi.org/project/gpboost/ |
| gplearn | 0.4.3 | BSD-3-Clause | symbolic regression (R58, optional) | `ml-core` | https://pypi.org/project/gplearn/ |
| h2o | 3.46.0.12 | Apache-2.0 | optional AutoML image (Java 17) | `optional-automl` | https://pypi.org/project/h2o/ |
| hdbscan | 0.8.44 | BSD-3-Clause | HDBSCAN with soft membership and condensed tree | `unsupervised` | https://pypi.org/project/hdbscan/ |
| hierarchicalforecast | 1.5.3 | Apache-2.0 | hierarchical reconciliation (BottomUp, TopDown, MiddleOut, MinTrace, ERM) | `ts` | https://pypi.org/project/hierarchicalforecast/ |
| httpx | 0.28.1 | BSD-3-Clause | HTTP client | `api` | https://pypi.org/project/httpx/ |
| hypothesis | 6.170.15 | MPL-2.0 | property tests | `dev` | https://pypi.org/project/hypothesis/ |
| imbalanced-learn | 0.14.2 | MIT | resampling, balanced ensembles, imbalance metrics (G-mean, IBA, specificity, classification_report_imbalanced) | `ml-core` | https://pypi.org/project/imbalanced-learn/ |
| imodels | 3.0.4 | MIT | RuleFit, FIGS, HS-trees, rule lists | `xai-uq` | https://pypi.org/project/imodels/ |
| interpret | 0.7.8 | MIT | EBM (R37, C25), Morris sensitivity | `xai-uq` | https://pypi.org/project/interpret/ |
| iterative-stratification | 0.1.9 | BSD-3-Clause | multilabel stratified K-fold | `ml-core` | https://pypi.org/project/iterative-stratification/ |
| jinja2 | 3.1.6 | BSD-3-Clause | report templates | `api` | https://pypi.org/project/jinja2/ |
| jsonschema | 4.26.0 | MIT | feature-contract validation in tests (§45.2) | `dev` | https://pypi.org/project/jsonschema/ |
| kaleido | 1.5.1 | MIT | static PNG export of Plotly figures (AI insights, reports) | `ml-core` | https://pypi.org/project/kaleido/ |
| kmedoids | 0.5.5 | GPL-3.0 | licence review: k-medoids | `optional-licence-review` | https://pypi.org/project/kmedoids/ |
| kmodes | 0.12.2 | MIT | k-modes / k-prototypes (optional; last release 2022) | `unsupervised` | https://pypi.org/project/kmodes/ |
| kneed | 0.9.0 | BSD-3-Clause | knee/elbow detection (k-scan, scree) | `ml-core` | https://pypi.org/project/kneed/ |
| lightgbm | 4.7.0 | MIT | gradient boosting (R34, C22), quantile objectives | `ml-core` | https://pypi.org/project/lightgbm/ |
| lightning | 2.6.6 | Apache-2.0 | training loops for DL models | `dl-cpu` | https://pypi.org/project/lightning/ |
| lime | 0.2.0.1 | BSD-2-Clause | LIME tabular explanations (low release cadence; widely used) | `xai-uq` | https://pypi.org/project/lime/ |
| locust | 2.47.0 | MIT | load tests | `dev` | https://pypi.org/project/locust/ |
| mamba-ssm | 2.3.2.post1 | Apache-2.0 | optional GPU: Mamba | `optional-gpu` | https://pypi.org/project/mamba-ssm/ |
| mapie | 1.6.0 | BSD-3-Clause | conformal prediction (regression, classification, time series), coverage/width metrics | `xai-uq` | https://pypi.org/project/mapie/ |
| minisom | 2.3.6 | MIT | self-organising maps | `unsupervised` | https://pypi.org/project/minisom/ |
| missingno | 0.5.2 | MIT | nullity matrix and dendrogram values | `eda` | https://pypi.org/project/missingno/ |
| mlflow | 3.18.0 | Apache-2.0 | experiment tracking and model registry | `ml-core` | https://pypi.org/project/mlflow/ |
| mlforecast | 1.1.0 | Apache-2.0 | ML forecasting with lag features (F26), lag transforms | `ts` | https://pypi.org/project/mlforecast/ |
| mlstatkit | 0.1.91 | MIT | DeLong test and CI for ROC-AUC | `ml-core` | https://pypi.org/project/mlstatkit/ |
| mlxtend | 0.25.0 | BSD-3-Clause | 5×2cv t- and F-tests, bootstrap .632/.632+, GroupTimeSeriesSplit, exhaustive/floating feature selection | `ml-core` | https://pypi.org/project/mlxtend/ |
| model-diagnostics | 1.5.1 | MIT | CORP Brier/score decomposition, bias and reliability diagnostics | `ml-core` | https://pypi.org/project/model-diagnostics/ |
| mypy | 2.4.1 | MIT | types | `dev` | https://pypi.org/project/mypy/ |
| nbformat | 5.11.1 | BSD-3-Clause | Jupyter notebook pipeline export (§46.4) | `ml-core` | https://pypi.org/project/nbformat/ |
| netcal | 1.4.0 | Apache-2.0 | ECE/MCE, beta calibration, histogram binning, reliability data | `xai-uq` | https://pypi.org/project/netcal/ |
| neuralforecast | 3.3.1 | Apache-2.0 | neural forecasting (F28–F53), Auto* tuning | `ts` | https://pypi.org/project/neuralforecast/ |
| ngboost | 0.5.11 | Apache-2.0 | natural-gradient probabilistic boosting (R36, C24) | `ml-core` | https://pypi.org/project/ngboost/ |
| nolds | 0.6.3 | MIT | Hurst exponent, DFA, sample entropy | `eda` | https://pypi.org/project/nolds/ |
| numpy | 2.4.6 | BSD-3-Clause | arrays; thin arithmetic on library outputs | `ml-core` | https://pypi.org/project/numpy/ |
| openai | 3.51.0 | Apache-2.0 | OpenAI-compatible client for NVIDIA API catalog | `api` | https://pypi.org/project/openai/ |
| openpyxl | 3.1.5 | MIT | XLSX template/output writing (§45) | `ml-core` | https://pypi.org/project/openpyxl/ |
| opentelemetry-instrumentation-celery | 0.66b2 | Apache-2.0 | Celery task tracing (§46.2) | `api` | https://pypi.org/project/opentelemetry-instrumentation-celery/ |
| opentelemetry-instrumentation-fastapi | 0.66b2 | Apache-2.0 | FastAPI tracing (§46.2) | `api` | https://pypi.org/project/opentelemetry-instrumentation-fastapi/ |
| opentelemetry-sdk | 1.45.2 | Apache-2.0 | tracing SDK (§46.2) | `api` | https://pypi.org/project/opentelemetry-sdk/ |
| opentsne | 1.0.4 | BSD-3-Clause | FFT-accelerated t-SNE | `unsupervised` | https://pypi.org/project/opentsne/ |
| optbinning | 1.0.0 | Apache-2.0 | optimal binning, WOE/IV tables | `ml-core` | https://pypi.org/project/optbinning/ |
| optuna | 5.0.0 | MIT | hyperparameter search, pruning, visualisation | `ml-core` | https://pypi.org/project/optuna/ |
| optuna-integration | 5.0.0 | MIT | integration callbacks (LightGBM, XGBoost, CatBoost, MLflow) | `ml-core` | https://pypi.org/project/optuna-integration/ |
| pacmap | 0.9.1 | Apache-2.0 | PaCMAP | `unsupervised` | https://pypi.org/project/pacmap/ |
| pandas | 2.3.3 | BSD-3-Clause | data frames (2.x; pandas 3 blocked by pytorch-tabular) | `ml-core` | https://pypi.org/project/pandas/ |
| pandas-stubs | 3.1.0.261029 | BSD-3-Clause | types | `dev` | https://pypi.org/project/pandas-stubs/ |
| pandera | 0.36.0 | MIT | data contracts on ingestion | `eda` | https://pypi.org/project/pandera/ |
| pgserver | 0.1.4 | Apache-2.0 | throw-away Postgres for the local DB test harness (dev only) | `dev` | https://pypi.org/project/pgserver/ |
| phate | 2.0.0 | GPL-2.0 | licence review: PHATE | `optional-licence-review` | https://pypi.org/project/phate/ |
| phik | 0.12.5 | MIT | φK correlation and significance | `eda` | https://pypi.org/project/phik/ |
| pillow | 13.0.0 | MIT-CMU | image resizing/encoding for VLM calls | `api` | https://pypi.org/project/pillow/ |
| plotly | 7.1.0 | MIT | all interactive plots | `ml-core` | https://pypi.org/project/plotly/ |
| pmdarima | 2.1.1 | MIT | auto_arima with seasonal tests (F60) | `ts` | https://pypi.org/project/pmdarima/ |
| polars | 2.1.0 | MIT | fast ingestion and profiling | `ml-core` | https://pypi.org/project/polars/ |
| prince | 0.23.1 | MIT | MCA, FAMD, CA | `unsupervised` | https://pypi.org/project/prince/ |
| probatus | 3.2.1 | MIT | ShapRFECV feature elimination | `ml-core` | https://pypi.org/project/probatus/ |
| properscoring | 0.1 | Apache-2.0 | CRPS for ensembles | `xai-uq` | https://pypi.org/project/properscoring/ |
| prophet | 1.5.0 | MIT | Prophet (F21) | `ts` | https://pypi.org/project/prophet/ |
| psycopg | 3.3.9 | LGPL-3.0 | Postgres driver (dynamically linked; standard use) | `api` | https://pypi.org/project/psycopg/ |
| pyale | 1.2.0 | MIT | ALE 1D/2D | `xai-uq` | https://pypi.org/project/pyale/ |
| rapidfuzz | 3.14.1 | MIT | Jaro–Winkler rename detection for intake schema diff D7 (§33.11) | `eda` | https://pypi.org/project/rapidfuzz/ |
| pyarrow | 26.0.1 | Apache-2.0 | Parquet artefacts and OOF predictions | `ml-core` | https://pypi.org/project/pyarrow/ |
| pydantic | 2.14.3 | MIT | schemas | `api` | https://pypi.org/project/pydantic/ |
| pydantic-settings | 2.16.3 | MIT | settings | `api` | https://pypi.org/project/pydantic-settings/ |
| pyod | 3.6.8 | BSD-2-Clause | anomaly detectors A2–A23 | `unsupervised` | https://pypi.org/project/pyod/ |
| pytest | 9.2.0 | MIT | tests | `dev` | https://pypi.org/project/pytest/ |
| pytest-cov | 7.1.0 | MIT | coverage | `dev` | https://pypi.org/project/pytest-cov/ |
| python-calamine | 0.9.1 | MIT | fast, read-only XLSX/XLS reading (no macros) for uploads (§45.3) | `ml-core` | https://pypi.org/project/python-calamine/ |
| python-docx | 1.2.0 | MIT | DOCX report export (§25) | `ml-core` | https://pypi.org/project/python-docx/ |
| python-multipart | 0.0.33 | Apache-2.0 | form parsing | `api` | https://pypi.org/project/python-multipart/ |
| python-pptx | 1.0.2 | MIT | PPTX report export (§25) | `ml-core` | https://pypi.org/project/python-pptx/ |
| pythresh | 1.1.1 | BSD-2-Clause | contamination-free outlier thresholds | `unsupervised` | https://pypi.org/project/pythresh/ |
| pytorch-forecasting | 1.8.0 | MIT | TFT, N-HiTS, DeepAR (Q11, F63) | `dl-cpu` | https://pypi.org/project/pytorch-forecasting/ |
| pytorch-tabular | 1.2.0 | MIT | tabular DL T1, T3–T5, T7, T8, T10–T12, T14–T16 | `dl-cpu` | https://pypi.org/project/pytorch-tabular/ |
| pytorch-tcn | 1.2.3 | MIT | temporal convolutional network (Q7) | `dl-cpu` | https://pypi.org/project/pytorch-tcn/ |
| pywavelets | 1.10.0 | MIT | wavelet transforms for TS EDA/denoising features (§43.10) | `ts` | https://pypi.org/project/pywavelets/ |
| quantile-forest | 1.5.0 | Apache-2.0 | quantile regression forest (R56) | `ml-core` | https://pypi.org/project/quantile-forest/ |
| redis | 8.1.0 | MIT | Key Value client | `api` | https://pypi.org/project/redis/ |
| respx | 0.23.1 | BSD-3-Clause | HTTP mocks | `dev` | https://pypi.org/project/respx/ |
| ruff | 0.17.5 | MIT | lint | `dev` | https://pypi.org/project/ruff/ |
| ruptures | 1.1.10 | BSD-2-Clause | change-point detection | `ts` | https://pypi.org/project/ruptures/ |
| scikit-fuzzy | 0.5.0 | BSD-3-Clause | fuzzy c-means (optional) | `unsupervised` | https://pypi.org/project/scikit-fuzzy/ |
| scikit-learn | 1.9.1 | BSD-3-Clause | core estimators (R/C/D/K), pipelines, CV splitters, metrics, calibration, threshold tuning, inspection (PDP, permutation) | `ml-core` | https://pypi.org/project/scikit-learn/ |
| scikit-plots | 0.4.0.post11 | BSD-3-Clause | cumulative gain, lift and KS helper values | `ml-core` | https://pypi.org/project/scikit-plots/ |
| scikit-posthocs | 0.18.0 | MIT | Nemenyi and other post-hoc tests, critical-difference diagrams | `ml-core` | https://pypi.org/project/scikit-posthocs/ |
| scipy | 1.17.1 | BSD-3-Clause | statistical tests (normality, KS, χ², Wilcoxon, Friedman), bootstrap CIs, distributions, KDE, association measures | `ml-core` | https://pypi.org/project/scipy/ |
| scoringrules | 0.12.0 | Apache-2.0 | CRPS, energy and interval scores | `xai-uq` | https://pypi.org/project/scoringrules/ |
| sentry-sdk | 2.75.0 | MIT | error tracking | `api` | https://pypi.org/project/sentry-sdk/ |
| shap | 0.54.1 | MIT | SHAP values, interaction values, plots data | `xai-uq` | https://pypi.org/project/shap/ |
| shapiq | 1.8.0 | MIT | Shapley interaction indices (optional) | `xai-uq` | https://pypi.org/project/shapiq/ |
| skforecast | 0.27.0 | BSD-3-Clause | recursive/direct forecasters, backtesting folds | `ts` | https://pypi.org/project/skforecast/ |
| skops | 0.16.0 | MIT | safe persistence of sklearn pipelines with a type allow-list (§45.8) | `ml-core` | https://pypi.org/project/skops/ |
| skrub | 0.11.0 | BSD-3-Clause | MinHash/Gap/Datetime encoders, TableVectorizer (E25–E27, E32) | `ml-core` | https://pypi.org/project/skrub/ |
| sktime | 1.3.0 | BSD-3-Clause | splitters (walk-forward), forecasting metrics, reduction, ensembles, Fourier features | `ts` | https://pypi.org/project/sktime/ |
| slowapi | 0.1.10 | MIT | per-user/IP rate limiting on lab-api (§46.3) | `api` | https://pypi.org/project/slowapi/ |
| sqlalchemy | 2.1.8 | MIT | database access | `api` | https://pypi.org/project/sqlalchemy/ |
| statsforecast | 2.1.1 | Apache-2.0 | statistical forecasting (F1–F25), conformal intervals, cross-validation | `ts` | https://pypi.org/project/statsforecast/ |
| statsmodels | 0.15.0 | BSD-3-Clause | OLS/GLM inference, residual and influence diagnostics, ARIMA/ETS/UCM/VAR/VECM/AutoReg/ARDL/Markov-switching/dynamic factor, stationarity and autocorrelation tests, McNemar, Cochran Q, multiple-testing correction, LOWESS, Bland–Altman | `ml-core` | https://pypi.org/project/statsmodels/ |
| structlog | 26.1.0 | MIT / Apache-2.0 | logging | `api` | https://pypi.org/project/structlog/ |
| stumpy | 1.14.1 | BSD-3-Clause | matrix profile, discords, motifs | `ts` | https://pypi.org/project/stumpy/ |
| supabase | 2.34.1 | MIT | Supabase client (Auth, Storage) | `api` | https://pypi.org/project/supabase/ |
| sweetviz | 2.3.3 | MIT | optional HTML EDA / train-vs-test comparison report | `eda` | https://pypi.org/project/sweetviz/ |
| tabpfn | 10.0.0 | Apache-2.0 code; weights own licence | licence review: TabPFN | `optional-licence-review` | https://pypi.org/project/tabpfn/ |
| tenacity | 9.2.1 | Apache-2.0 | retries/back-off | `api` | https://pypi.org/project/tenacity/ |
| timesfm | 3.0.2 | Apache-2.0 | optional foundation forecasting | `optional-foundation` | https://pypi.org/project/timesfm/ |
| torch | 2.15.0 | BSD-3-Clause | deep-learning runtime (CPU wheels on Render) | `dl-cpu` | https://pypi.org/project/torch/ |
| torchmetrics | 1.8.2 | Apache-2.0 | metric tracking inside DL training, calibration-error cross-check | `dl-cpu` | https://pypi.org/project/torchmetrics/ |
| trimap | 1.2.0 | Apache-2.0 | TriMap | `unsupervised` | https://pypi.org/project/trimap/ |
| tsfel | 0.3.0 | BSD-3-Clause | time-series feature extraction | `ts` | https://pypi.org/project/tsfel/ |
| tsfresh | 0.21.2 | MIT | window feature extraction with relevance filtering | `ts` | https://pypi.org/project/tsfresh/ |
| tslearn | 0.10.0 | BSD-2-Clause | time-series k-means, k-Shape, kernel k-means, DTW | `ts` | https://pypi.org/project/tslearn/ |
| umap-learn | 0.6.0 | BSD-3-Clause | UMAP, densMAP | `unsupervised` | https://pypi.org/project/umap-learn/ |
| upsetplot | 0.9.0 | BSD-3-Clause | error-overlap (UpSet) data | `ml-core` | https://pypi.org/project/upsetplot/ |
| utilsforecast | 0.2.17 | Apache-2.0 | forecast losses, Fourier features, plotting helpers | `ts` | https://pypi.org/project/utilsforecast/ |
| uvicorn | 0.54.0 | BSD-3-Clause | ASGI server | `api` | https://pypi.org/project/uvicorn/ |
| venn-abers | 1.5.4 | MIT | Venn–Abers calibration | `xai-uq` | https://pypi.org/project/venn-abers/ |
| weasyprint | 70.0 | BSD-3-Clause | PDF run reports (§25, §46.4); needs Pango | `ml-core` | https://pypi.org/project/weasyprint/ |
| wittgenstein | 0.3.5 | MIT | RIPPER rule learner (C42, optional) | `xai-uq` | https://pypi.org/project/wittgenstein/ |
| xgboost | 3.4.1 | Apache-2.0 | gradient boosting (R33, C21) | `ml-core` | https://pypi.org/project/xgboost/ |
| xlstm | 2.0.6 | Apache-2.0 | optional GPU: xLSTM | `optional-gpu` | https://pypi.org/project/xlstm/ |
| ydata-profiling | 4.18.4 | MIT | optional full HTML profile (isolated image) | `optional-reports` | https://pypi.org/project/ydata-profiling/ |

---

## 45. Prediction Studio — batch upload and custom input form

> Round-4 addition (15 Nov 2026). Supersedes the Single and Batch rows of §22 in detail (the What-if, Forecast, Monitoring and API rows of §22 stay as they are and reuse the components below). The **Predict** module (§5.2, module 8) opens on a two-option chooser: **(A) Batch upload** and **(B) Custom input**. Both modes are driven by the **feature contract** saved with every model, run the **saved preprocessing pipeline** (never a refit), and return the same uncertainty fields. Flow: `docs/FLOWCHART.md` §20 (`docs/diagrams/20_prediction_studio.png`). Database: migration `20261115000000_prediction_studio.sql`.

### 45.1 What the user gets

| | (A) Batch upload | (B) Custom input form |
|---|---|---|
| Input | CSV, XLSX or Parquet of prediction features (a template can be downloaded) | Form generated from the contract: sliders + number boxes, dropdowns, toggles, date pickers, lookback editor |
| Execution | Celery job on `q.predict.batch` (Render `lab-worker-light` for sklearn/boosting models; routed to `q.predict.heavy` on `lab-worker-train` for TS, clustering/DR/anomaly and DL models, whose libraries are only in the train image), progress bar over SSE, cancellable | Synchronous `POST /predict/single` (p95 target < 500 ms for tree/linear models; DL and SHAP may take longer and show a spinner) |
| Output | Results grid (paginated) + download as CSV or XLSX + summary plots | Result card with point value, interval or probabilities, gauge, local SHAP waterfall, what-if sliders, AI explanation |
| Stored in | `prediction_jobs`, `prediction_results` (first 1 000 rows) and Storage `predictions/{workspace}/{prediction_job}/output.*` | `prediction_jobs` (mode `single`/`what_if`) and one `prediction_results` row |

### 45.2 Feature contract (model signature)

Written by the training job **from the training split only** (never from validation or test rows) and stored in three places: table `model_signatures.feature_contract` (JSONB), Storage `models/{workspace}/{model}/feature_contract.json`, and — when MLflow is enabled — as the MLflow model signature + input example. JSON Schema: `docs/contracts/feature_contract.schema.json`; worked examples for every sample dataset: `data/samples/predict/contracts/*.feature_contract.json`.

| Field | Content |
|---|---|
| `features[]` | `name`, `kind` (numeric / categorical / boolean / datetime / identifier_like), `dtype`, `nullable`, numeric `min`/`max`/`median`/`p01`/`p99`/`integer`, categorical `categories` (≤ 200 stored, `categories_truncated`), `n_categories`, `mode`, `role` |
| `identifier_like` | columns with > 50 distinct values and > 50 % unique (names, tickets, free text): **values are never stored** (PII); excluded from the model by default; shown as optional passthrough |
| `id_columns` | passthrough identifiers copied to the output (`row_key`), never used as features |
| `time_column`, `frequency`, `series_column`, `horizon_max` | sequential / TS metadata; `horizon_max` is the HorizonGuard h_max at training time (§20) |
| `derived_features` | engineered columns produced by the pipeline (lags, rolling stats, date parts, ratios, encodings); computed automatically, never asked from the user |
| `reference` | per-feature reference histograms/quantiles (10 bins) for drift (PSI/KS) and the fitted OOD detector id |
| `preprocessing_hash`, `library_versions`, `contract_hash` | the prediction cache key includes `contract_hash`; a library-version mismatch on load raises a clear error instead of predicting |

### 45.3 Validation (both modes; batch shows a report before scoring)

| ID | Check | Result |
|---|---|---|
| PV01 | File type by magic bytes + extension (CSV/TSV, XLSX, Parquet); XLSX parsed with `python-calamine` (read-only, no macros), XML hardened by `defusedxml`; zip-bomb guard (uncompressed/compressed ratio > 100 or > 500 MB → reject) | block |
| PV02 | Size and row caps: 50 MB upload and 1 000 000 rows by default (admin-configurable per plan, §45.8) | block |
| PV03 | Encoding (UTF-8 / UTF-8-BOM / cp1252 detection), delimiter sniffing, header row present, duplicate column names | block on duplicates |
| PV04 | Missing required feature columns (name match is exact, then case/whitespace-insensitive with a rename proposal) | block, with "download template" link |
| PV05 | Extra columns: ignored and listed; the **target column** if present is dropped with a warning (it would otherwise suggest leakage) | warn |
| PV06 | Dtype coercion per contract (numeric, boolean `true/false/1/0/yes/no`, datetime with the contract's format); rows that fail coercion are listed | warn; block if > 5 % of rows fail |
| PV07 | Unseen categories: handled by the saved encoder policy (`handle_unknown='infrequent_if_exist'` / target-encoder prior); flagged per row | warn |
| PV08 | Numeric out of training range: outside [p01, p99] → `range_warning`; outside [min, max] → `out_of_range` flag (no clipping unless the user ticks "clip to training range") | warn |
| PV09 | Missing values in non-nullable features: imputed by the saved imputer and flagged | warn |
| PV10 | Row-level OOD: score from the OOD detector fitted at training (`sklearn.ensemble.IsolationForest` on the preprocessed training matrix, so it runs on the light worker; Mahalanobis via `sklearn.covariance.MinCovDet` for ≤ 50 numeric features); flag if above the training 99th percentile | flag per row |
| PV11 | Batch drift vs training: PSI and KS per feature (`scipy.stats.ks_2samp`), PSI > 0.2 highlighted; shown in the validation report and the AI insight | info |
| PV12 | Sequential (non-TS) data: time column parses, rows are sorted (auto-sort offered), no duplicate timestamps per series, lookback history available for lag features (else the first rows are marked `insufficient_history`) | block if history missing for all rows |
| PV13 | Time series: requested timestamps start at last training timestamp + 1 step, are contiguous at the contract frequency, length ≤ `horizon_max` (HTTP 422 with HorizonGuard reasons otherwise), known-future exogenous columns present for every step, series ids known | block |
| PV14 | Constant or all-NaN columns in the upload | warn |
| PV15 | CSV/formula injection: cells beginning with `=`, `+`, `-`, `@`, tab or CR are treated as text on input and **prefixed with `'` on export** (OWASP) | sanitise |
| PV16 | Identifier columns that look like personal data (email, phone, PAN/Aadhaar patterns) are masked in the UI and excluded from AI prompts | sanitise |

A batch with only warnings goes to `needs_review`; the user confirms ("Score anyway") or fixes the file. Blocks stop before any model code runs.

### 45.4 Output columns by task

| Task | Columns (prefix `pred_`) | Library |
|---|---|---|
| Regression | `pred_value`; `pred_lower_{level}`, `pred_upper_{level}` for each chosen level (default 90 %, options 80/90/95/99); `pred_interval_method` | MAPIE (`SplitConformalRegressor` / `CrossConformalRegressor`, CQR with quantile GBMs), `quantile-forest`, NGBoost `pred_dist`; method chosen at training (§21) |
| Binary / multiclass | `pred_class`; `pred_proba_{class}` (calibrated, §41.6 calibrator); `pred_confidence` (max probability); `pred_margin` (top-1 − top-2); `pred_entropy` (normalised, 0–1); `pred_threshold` (binary; method from §41.6); `pred_set` (conformal prediction set at the chosen level, LAC/APS/RAPS) | sklearn `CalibratedClassifierCV` / saved calibrator, `scipy.stats.entropy`, MAPIE `SplitConformalClassifier` |
| Multilabel | per label `pred_{label}`, `pred_proba_{label}`, per-label threshold | sklearn + MAPIE (per label) |
| Time series | `unique_id`, `ds`, `pred_value`, `pred_lower_{level}`, `pred_upper_{level}`, `pred_step` (1…h) | statsforecast / mlforecast / neuralforecast native intervals or conformal intervals (`ConformalIntervals`) |
| Clustering | `pred_cluster`; `pred_distance` (to assigned centroid) or `pred_membership_{k}` (GMM/fuzzy soft membership); `pred_outlier` (HDBSCAN noise); `pred_strength` (HDBSCAN `approximate_predict` probability) | sklearn `KMeans.transform`, `GaussianMixture.predict_proba`, `hdbscan.approximate_predict` / `membership_vector` |
| Dimensionality reduction | `pred_dim_1`…`pred_dim_k` (embedding coordinates); `pred_recon_error` for linear methods | sklearn `transform`, `umap.UMAP.transform`, `openTSNE` `transform` (plain sklearn t-SNE has no out-of-sample transform → mode disabled with a reason) |
| Anomaly detection | `pred_score`, `pred_is_anomaly` (threshold from training / pythresh) | `pyod` `decision_function`, `pythresh` |
| All tasks | `row_index`, id columns, `flag_ood`, `ood_score`, `flag_out_of_range` (list), `flag_unseen_categories` (list), `flag_imputed` (list), optional `shap_top{1..k}_feature` / `_value` / `_contribution` (k = 3 default, up to 10) | `shap` (Tree/Linear explainer; Kernel/Permutation sampled for others, capped at 2 000 rows per batch unless the user raises it) |

Probabilities are calibrated only if the model was calibrated at training; otherwise the column header says "uncalibrated". All intervals carry their nominal level and method; conformal coverage holds marginally on exchangeable data and is labelled as not guaranteed for time series without the adaptive method.

### 45.5 (A) Batch upload — flow

1. **Choose model** (registered alias or any finished model the user can read) → page shows the contract summary and a **Download template** button (`GET /models/{id}/template?format=csv|xlsx`): exact columns in order, a dtype row in XLSX (data-validation lists for categoricals, number formats, date formats), one example row filled with medians/modes (marked "example — delete before upload" in a comment column that the validator ignores).
2. **Upload** to Supabase Storage via a signed URL (`predictions/{workspace}/{prediction_job}/input.*`, ≤ 50 MB) → `POST /predict/batch {model_id, input_path, options}` creates a `prediction_jobs` row (idempotency key = sha256(model_id, input sha256, options)) and returns `202 {prediction_job_id}`.
3. **Validate** (PV01–PV16) in the worker; status `validating` → `needs_review` (warnings) or `failed` (blocks). The UI shows the validation report with per-column issues and a "fix and re-upload" path.
4. **Score** in chunks of 50 000 rows (memory guard: estimated bytes = rows × features × 8 × 4; above 60 % of the worker's RAM the job is re-queued on `q.predict.heavy`), streaming progress (`progress` 0–1) over SSE; `request_job_cancel()` stops between chunks.
5. **Write output** as CSV (always) and XLSX (if ≤ 1 048 576 rows), sanitised against formula injection, plus a `summary.json` (counts, distribution of predictions, share flagged OOD, drift table). First 1 000 rows go to `prediction_results` for the grid; the rest are read from the file with pagination (DuckDB over the CSV/Parquet).
6. **Show** a results grid (virtualised), summary plots (`PRD.P.DIST` prediction distribution, `PRD.P.CONFIDENCE` confidence/entropy histogram, `PRD.P.INTERVAL_WIDTH`, `PRD.P.DRIFT` PSI bars, `PRD.P.OOD` OOD score histogram), and an AI insight for the batch (§45.12).

### 45.6 (B) Custom input form

| Contract kind | Widget | Default | Bounds / options |
|---|---|---|---|
| numeric (continuous) | slider + number box (synchronised; slider uses p01–p99, the box accepts min–max and shows an out-of-range warning beyond) | training median | step from data resolution; integer features snap to integers |
| numeric with ≤ 10 distinct integer values | segmented control | mode | the seen values |
| categorical (≤ 30 categories) | dropdown / combobox with search | mode | seen categories only; "other (unseen)" option maps to the encoder's unknown handling and is flagged |
| categorical (> 30) | searchable combobox (virtualised) | mode | seen categories |
| boolean | toggle | mode | — |
| datetime | date(-time) picker | last training date (sequential) or median | within training range + horizon; timezone from the contract |
| identifier_like | hidden by default ("show passthrough fields") | empty | free text, not used by the model |
| derived / engineered | not shown; computed by the pipeline; visible read-only under "Computed features" | — | — |
| sequential (lags) | **lookback window editor**: an editable table of the last L rows (L = max lag or the DL lookback), pre-filled from the end of the training data; or **pick a date from history** (pre-fills the window ending at that date and shows the actual value for comparison) | last training window | — |
| time series | horizon slider (≤ `horizon_max`), levels (80/95), future exogenous grid | h_default | HorizonGuard |

Buttons: **Fill from a random training row** (`GET /models/{id}/sample-row?seed=` — a row from the training split, identifiers masked), **Reset to defaults**, **Copy as JSON**, **Add to batch** (appends the row to a scratch table that can be submitted as a batch). Every change re-predicts after a 300 ms debounce (`POST /predict/single`), cancelling the previous request.

Result card: point value with interval band, or class probability bars with the threshold line; a **gauge** (probability of the positive class or position of the prediction within the training target range); confidence badges (margin, entropy, conformal set size); OOD and range flags with the offending features; **local SHAP waterfall** (`shap` explainer chosen per model family, background = 100 training rows from the contract's stored sample); **what-if sliders** for the top-5 SHAP features with an ICE line for the active feature and a sensitivity tornado (§22 What-if); "Explain this prediction" → AI insight (§45.12).

### 45.7 API (prefix `/api/v1`)

| Method & path | Purpose |
|---|---|
| `GET /models/{id}/schema` | feature contract (identifier values never included) + task + available uncertainty methods + limits |
| `GET /models/{id}/template?format=csv\|xlsx` | blank template with exact columns, dtype hints and one example row |
| `GET /models/{id}/sample-row?seed=42` | one random training-split row (for "Fill from a random training row"; masked identifiers) |
| `POST /predict/single` `{model_id, row, options:{level, threshold?, shap:bool, horizon?}}` | synchronous single-row prediction with validation flags, interval/probabilities, gauge value, SHAP values |
| `POST /predict/batch` `{model_id, input_path, options:{levels, shap_top_k, clip_to_range, output_formats}}` | create a batch prediction job → `202 {prediction_job_id, job_id}` |
| `GET /predict/jobs/{id}` ; `GET /predict/jobs/{id}/events` (SSE) | status, progress, validation report, summary |
| `POST /predict/jobs/{id}/confirm` | continue a job in `needs_review` |
| `POST /predict/jobs/{id}/cancel` | calls `request_job_cancel()` |
| `GET /predict/jobs/{id}/results?offset&limit` | paginated rows |
| `GET /predict/jobs/{id}/download?format=csv\|xlsx` | signed URL (10 min) to the output file |
| `POST /predict/explain` `{prediction_job_id, row_index}` | AI insight for one row or the whole batch (§45.12) |

These replace the earlier `POST /predict/{model_id}` and `POST /predict/{model_id}/batch` paths in §6.2 (kept as aliases for one release). Errors use RFC 9457 problem+json with the PV code (e.g. `PV13`).

### 45.8 Limits, security and performance

* Upload ≤ 50 MB / ≤ 1 000 000 rows (Render `lab-worker-light` 2c-4g); larger files are routed to `lab-worker-train` or rejected with guidance (split the file or use the API).
* Models are loaded from the lab's own artefact store only, verified by sha256; sklearn pipelines are persisted with **`skops`** (type allow-list, no arbitrary pickle) where all steps are supported, otherwise joblib + signed hash; DL models as Lightning checkpoints with `torch.load(weights_only=True)`. User-uploaded models are not accepted in v1.
* Model cache in the worker (LRU, 4 models, keyed by `model_id + contract_hash`); `POST /predict/single` is served by `lab-api` only for models < 50 MB without heavy dependencies, otherwise enqueued on `q.predict.heavy` (`lab-worker-train`) and awaited for up to 30 s (then the UI switches to a job with progress).
* Rate limits: 60 single predictions/min/user, 10 batch jobs/hour/user (admin-configurable); AI explanations count against the AI budget (§40).
* Retention: inputs and outputs expire after 30 days (`prediction_jobs.expires_at`, daily cleanup); results tables keep only the first 1 000 rows.
* RLS: members read; analysts and above create jobs; only workers (service role) write results and status (migration `20261115000100_hardening.sql`); storage bucket `predictions` is private with a 50 MB cap and tabular MIME types.
* Audit: every batch and every downloaded output is logged in `audit_log` (who, model, rows, file hash).

### 45.9 Sample prediction files (generated, seed 42)

`scripts/make_predict_samples.py` builds one file per dataset (three for DS17) into `data/samples/predict/` with the target removed, plus an illustrative feature contract per file and `predict_manifest.json`. Non-sequential data: random 80/20 split with `numpy.random.default_rng(42)`, 30 rows drawn from the hold-out. Sequential/TS data: chronological; forecast requests contain the next h timestamps (and known-future exogenous columns) with h = the HorizonGuard cap. Every preset in `data/samples/presets/` references its file(s) (`predict_sample` / `predict_samples` and `feature_contract`). Test: `tests/unit/test_predict_samples.py`.

| ID | File | Rows | Source |
|---|---|---|---|
| DS1 | `iris_predict.csv` | 30 | bundled |
| DS2 | `breast_cancer_wdbc_predict.csv` | 30 | bundled |
| DS3 | `titanic_predict.csv` | 30 | bundled |
| DS4 | `adult_predict.csv` | 30 | downloaded (UCI adult.test) |
| DS5 | `german_credit_predict.csv` | 30 | downloaded (OpenML 31) |
| DS6 | `credit_card_fraud_predict.csv` | 30 | downloaded (OpenML 1597 parquet) |
| DS7 | `bank_marketing_predict.csv` | 30 | downloaded (UCI 222) |
| DS8 | `credit_default_taiwan_predict.csv` | 30 | downloaded (UCI 350) |
| DS9 | `heart_disease_cleveland_predict.csv` | 30 | bundled |
| DS10 | `penguins_predict.csv` | 30 | bundled |
| DS11 | `wine_quality_red_predict.csv` | 30 | bundled |
| DS12 | `california_housing_predict.csv` | 30 | downloaded (OpenML 537) |
| DS13 | `ames_house_prices_predict.csv` | 30 | downloaded (OpenML 42165) |
| DS14 | `auto_mpg_predict.csv` | 30 | bundled |
| DS15 | `concrete_strength_predict.csv` | 30 | bundled |
| DS16 | `bike_sharing_day_predict.csv` | 30 | bundled |
| DS17 | `sklearn_diabetes_predict.csv` | 30 | bundled with scikit-learn |
| DS17 | `sklearn_digits_predict.csv` | 30 | bundled with scikit-learn |
| DS17 | `sklearn_wine_predict.csv` | 30 | bundled with scikit-learn |
| DS18 | `mall_customers_predict.csv` | 30 | bundled |
| DS19 | `wholesale_customers_predict.csv` | 30 | bundled |
| DS20 | `online_retail_rfm_predict.csv` | 30 | downloaded (UCI 502), RFM derived |
| DS21 | `credit_card_fraud_unlabelled_predict.csv` | 30 | downloaded (OpenML 1597 parquet) |
| DS22 | `airline_passengers_predict.csv` | 24 | bundled |
| DS23 | `shampoo_sales_predict.csv` | 9 | bundled |
| DS24 | `daily_min_temperatures_predict.csv` | 30 | bundled |
| DS25 | `monthly_sunspots_predict.csv` | 24 | bundled |
| DS26 | `co2_mauna_loa_predict.csv` | 24 | bundled |
| DS27 | `us_macrodata_predict.csv` | 16 | bundled |
| DS28 | `etth1_predict.csv` | 48 | bundled |
| DS29 | `electricity_load_predict.csv` | 48 | schema-derived (no download) |
| DS30 | `nifty50_daily_predict.csv` | 30 | bundled |
| DS31 | `multi_asset_prices_predict.csv` | 30 | downloaded (Yahoo chart API, 3 months) |
| DS32 | `tradinglab_dollar_bars_predict.csv` | 30 | synthetic (schema-correct) |
| DS33 | `synthetic_classification_predict.csv` | 30 | synthetic generator (by design) |

### 45.10 Data model and storage

`model_signatures` (1 row per model: contract JSONB, hashes, MLflow URI), `prediction_jobs` (mode, status, options, validation report, input/output paths, progress, idempotency key, expiry), `prediction_results` (row-level prediction, interval, confidence, flags, explanation; unique `(prediction_job_id, row_index)`; workspace consistency trigger). The older `predictions` table (§7) stays as a per-job summary for monitoring. Bucket `predictions` (private, 50 MB, CSV/XLSX/Parquet). RLS tests: `supabase/tests/prediction_rls_test.sql`.

### 45.11 Frontend components (`frontend/src/components/predict/`)

`PredictModeChooser` (two large cards: Batch upload / Custom input), `ModelPicker`, `ContractSummary`, `TemplateDownloadButton`, `BatchUploadDropzone` (react-dropzone-style, type/size pre-check), `ValidationReport` (issues grouped by PV code with row/column drill-down), `JobProgress` (SSE, cancel), `PredictionResultsGrid` (TanStack Table + Virtual, column groups: inputs / prediction / uncertainty / flags / SHAP), `PredictionSummaryPlots`, `DownloadMenu` (CSV/XLSX), `DynamicFeatureForm` (react-hook-form + zod schema generated from the contract), `NumericSliderInput`, `CategoryCombobox`, `BooleanToggle`, `DateInput`, `LookbackWindowEditor`, `HistoryDatePicker`, `PredictionCard`, `ProbabilityBars`, `IntervalBand`, `ConfidenceGauge`, `ShapWaterfall`, `WhatIfPanel`, `PredictionInsight`. Empty states ("no trained model yet → go to Supervised"), errors (problem+json mapped to messages), keyboard access for every slider (arrow keys, PageUp/PageDown), ARIA labels from feature names, and a mobile layout where the form stacks above the result card.

### 45.12 AI insight for predictions (NVIDIA VLM, §40)

Template `prompts/prediction.md` (extended): inputs are the FACTS for the row or batch (prediction, interval or probabilities, calibration status, conformal set size, margin/entropy, OOD score and flags, top SHAP contributions, drift table for batches) plus the PNGs of the SHAP waterfall, gauge and (batch) summary plots. Output fields as §23.4 plus `confidence_explanation` and `caveats` (e.g. "out of training range for Age", "uncalibrated probabilities"). Numbers are checked against FACTS; identifier and personal-data columns are never sent; numbers-only mode produces the same explanation from rules.

### 45.13 Tests

* `tests/unit/test_predict_samples.py` (exists): every DS1–DS33 has a sample, each matches its contract (columns, row counts, horizon caps), targets removed, no identifier values stored.
* Validator unit tests per PV code with crafted files (missing column, extra target column, bad dtypes, unseen category, out-of-range, NaN, wrong timestamps, horizon > h_max, CSV-injection cells, zip bomb XLSX, duplicate headers).
* Parity: `POST /predict/single` and the batch path give identical outputs for the same rows (1e-9); outputs equal `pipeline.predict`/`predict_proba` of the saved model on the golden datasets.
* Coverage: 90 % regression intervals reach 88–92 % empirical coverage on the DS12 hold-out and APS sets ≥ 89 % on DS10 (computed by the tests at build time; no value is asserted by this document).
* RLS: `supabase/tests/prediction_rls_test.sql` (10 assertions; passes on the local harness `tests/db_harness/run_db_tests.py`).
* E2E (Playwright): upload `titanic_predict.csv` → validation report → download XLSX; custom form for DS3 → change Age slider → prediction updates < 1 s → SHAP waterfall renders; template download round-trips through validation with zero blocks.

---

## 46. Hardening — ML integrity, scale/ops, security, UX and feature parity (stress test, v2.2)

> Round-4 red-team audit (15 Nov 2026). Every finding, its severity and where it was fixed is listed in `docs/STRESS_TEST.md` (IDs `ST-*`). This section is the normative result: where it is stricter than an earlier section, **§46 wins**. CURSOR_PROMPT Phase 8.2 and the phase ACs reference the IDs below.

### 46.1 ML integrity guarantees

| ID | Risk | Guarantee (implementation) | Test |
|---|---|---|---|
| MI-01 | Preprocessing fit on all rows | every fitted step lives in one `sklearn.pipeline.Pipeline` / `imblearn.pipeline.Pipeline` passed whole to `cross_validate`/Optuna; the lab never calls `fit_transform` on the full frame before splitting | spy transformer records the row indices it was fit on; must equal the fold's train indices |
| MI-02 | Target encoding leakage | `sklearn.preprocessing.TargetEncoder` (internal cross-fitting, `cv=5`, `shuffle=False` for sequential) or category_encoders inside the pipeline; never pre-computed | OOF score with a pure-noise high-cardinality column ≈ chance (|AUC − 0.5| < 0.03 on 5 000 synthetic rows) |
| MI-03 | Optimistic score after tuning | model selection on CV; **nested CV** (outer 5 / inner 3) available and **on by default when n < 2 000** and in Thorough mode; the reported estimate for a tuned model is the outer score | nested vs non-nested gap shown on the leaderboard |
| MI-04 | Financial/sequential leakage | `PurgedKFold`/CPCV with `t1` label end times and embargo (§13, §32); sequential splits never shuffle; scalers/FFD d* fit per training window; lag/rolling features computed **after** the split boundary with `shift ≥ 1` | purging test: no train label interval overlaps a test interval; feature at t uses data ≤ t−1 |
| MI-05 | TS scaling leakage | target transforms (Box-Cox λ, scaling, differencing order from tests) fitted on each backtest window's history only (statsforecast/mlforecast `target_transforms`, per-window) | λ differs across windows; equals full-history λ only on the last window |
| MI-06 | Seed drift | `LAB_DEFAULT_SEED=42` → numpy `default_rng`, `random`, torch (`manual_seed`, `use_deterministic_algorithms(True, warn_only=True)`), estimator `random_state`, Optuna `TPESampler(seed=42)`, CV `random_state`; seed + library versions + data hash on every run | rerunning a Quick run reproduces metrics to 1e-12 (CPU) |
| MI-07 | Class imbalance | stratified splits; imbalance detection (minority < 20 % or ratio > 4) switches headline metrics (rule 20) and proposes `class_weight` / resampling inside folds; stratified group K-fold when groups exist; extreme rarity (< 30 minority rows) → warning + repeated stratified CV | resampler never sees validation rows |
| MI-08 | Very small data (n < 200) | repeated K-fold (5×5) or LOO for n < 50; algorithms with `min_rows` above n are disabled with a reason; DL disabled below 1 000 rows unless forced; HorizonGuard caps h ≤ ⌊n/4⌋ for n < 50 | registry test: no algorithm offered below its `min_rows` |
| MI-09 | Very large data | estimator `max_rows_hint` + memory estimator (`rows × cols × 8 B × model factor`) before enqueue; above the worker limit → stratified subsample for tuning, full refit only if it fits, or refusal with the numbers; plots on 50 000-row samples (labelled) | refusal message test at 1.2× limit |
| MI-10 | High-cardinality categoricals | > 50 levels → target / hashing / count encoder proposals; one-hot capped at 30 levels with "infrequent" bucket (`min_frequency`); identifier-like columns (> 50 % unique) excluded by default (§45.2) | encoder choice test on DS13/DS3 |
| MI-11 | All-NaN / constant / duplicate columns | dropped in the recipe with an Intake warning (`VarianceThreshold(0)`, all-NaN check, duplicate-column hash); near-constant (> 99 % one value) flagged | recipe preview lists dropped columns |
| MI-12 | Date parsing ambiguity | ISO 8601 first; ambiguous day/month formats resolved by testing both and picking the one with zero parse errors and monotonic order; if both valid → user must choose (Intake card); timezone stored; mixed formats → rows reported | DS-style fixtures `01/02/2024` ambiguous → prompt |
| MI-13 | Multi-target | multi-output regression via native multioutput estimators or `MultiOutputRegressor`/`RegressorChain`; multilabel classification via `MultiOutputClassifier`/`ClassifierChain`; metrics per target + averaged; Prediction Studio emits one column group per target | DS-synthetic multi-target golden test |
| MI-14 | Multicollinearity | VIF table (statsmodels) and correlation clusters in EDA; linear models flagged when VIF > 10; permutation importance grouped by correlated clusters to avoid diluted importances | VIF golden values |
| MI-15 | Target leakage via features | Intake leakage suspects (near-perfect single-feature AUC/R², post-outcome timestamps, IDs correlated with target) must be confirmed or dropped before training (§33) | DS7 `duration` flagged |
| MI-16 | Test-set reuse | the hold-out is locked after first evaluation; re-evaluations are logged and the UI shows "test set used n times" | audit row per test evaluation |
| MI-17 | Forecast horizon | HorizonGuard (§20) enforced in API, worker and form; batch requests longer than h_max are rejected (PV13) | horizon tests |
| MI-18 | Duplicate rows across splits | exact-duplicate rows grouped so they cannot be split across train/test (`GroupKFold` on the duplicate hash) when duplicates > 1 % | duplicate leak test |

### 46.2 Scale, reliability and operations

| ID | Area | Decision |
|---|---|---|
| OPS-01 | Upload limits | datasets ≤ 500 MB and ≤ `LAB_MAX_ROWS` (5 M) rows; prediction files ≤ 50 MB / 1 M rows; bucket-level limits in migrations and `supabase/config.toml`; **hosted Supabase must be on Pro with the global file size limit raised to 2 GB** (Free plan caps every upload at 50 MB); resumable (TUS) upload for files > 6 MB |
| OPS-02 | Memory | per-task memory estimate before enqueue; `--max-tasks-per-child 20` recycling; Celery `worker_max_memory_per_child` (light 3.2 GB, train 14 GB); Polars/DuckDB for profiling; float32 downcast for wide frames; chunked prediction (50 000 rows) |
| OPS-03 | Long jobs | per-queue soft/hard time limits as in §39.3 (q.eda 15/20 min, q.train.cpu 90/120, q.tune 4/5 h, q.explain 30/40, q.forecast 60/90, q.insights 5/6, q.report 10/15) plus q.ingest 10/15, q.predict.batch 30/45 and q.predict.heavy 60/90 (v2.2); soft limit → best-so-far result saved; heartbeat every 30 s into `jobs.heartbeat_at`; a reaper marks jobs without heartbeat for 10 min as failed |
| OPS-04 | Retries and idempotency | `acks_late=True`, `task_reject_on_worker_lost=True`, broker `visibility_timeout` > hard limit, autoretry only for transient errors (network, 5xx, 429) with exponential backoff + jitter (max 3); every create endpoint accepts `Idempotency-Key` (unique index on `jobs` / `prediction_jobs`); results written with upserts keyed by `(job, fold, algo)` |
| OPS-05 | Cancellation | `request_job_cancel()` RPC sets `cancel_requested`; workers check between folds/trials/chunks and at Optuna callbacks; `revoke(terminate=False)` for queued tasks; partial artefacts kept and labelled "cancelled" |
| OPS-06 | Artefact storage | layout `{bucket}/{workspace}/{entity}/{id}/…`; content-addressed plots (sha256); lifecycle: plots/artefacts of deleted experiments purged after 7 days, prediction files after 30 days, datasets kept until deleted; storage usage per workspace on the Admin page |
| OPS-07 | NVIDIA API limits | Redis token bucket per model (`AI_RPM_LIMIT=35`), daily caps per workspace and user, `Retry-After`-aware backoff on 429, circuit breaker (5 failures/60 s → numbers-only for 5 min), request de-duplication by FACTS hash, response cache 7 days (§40) |
| OPS-08 | Cost guards | admin-set caps: concurrent jobs per user (2) and workspace (6), CPU-hours per month, storage GB, AI requests/day; fallback paid providers need an explicit spend cap |
| OPS-09 | Concurrency | `--prefetch-multiplier 1`; light worker concurrency 2, train 1 (n_jobs = cores); Optuna parallelism through RDB storage, not threads; one heavy job per user at a time by default |
| OPS-10 | Cold starts | paid Render instances do not spin down; the free plan (spins down when idle) is not used for `lab-api`; model LRU cache warmed on deploy for `@champion` models |
| OPS-11 | Deploy ordering | `render.yaml` sets `autoDeployTrigger: "off"`; `deploy.yml` runs `supabase db push` first, then Render deploy hooks, then smoke tests; migrations follow **expand → migrate → contract** so the running app and Vercel previews keep working during a deploy |
| OPS-12 | Observability | structured JSON logs with `job_id`/`run_id`/`workspace_id`; OpenTelemetry traces API → Celery; Sentry (backend DSN on Render, browser DSN on Vercel) with `send_default_pii=False` and a `before_send` scrubber; Flower behind admin auth; alerts on queue depth, job failure rate, 429 rate, storage growth |
| OPS-13 | Backups and DR | Supabase Pro daily backups + **PITR add-on** for production; weekly `pg_dump` of the schema + metadata to a separate bucket; Storage objects are not covered by DB backups → nightly copy of `models/` and `datasets/` to an external bucket (rclone) — documented in `docs/DEPLOY.md`; restore drill each quarter |
| OPS-14 | Network | workers egress allow-list: Supabase, NVIDIA API, PyPI mirror at build only, and the dataset hosts in `data/samples/urls.txt` (sample downloads); everything else blocked where the platform allows |

### 46.3 Security

| ID | Threat | Control |
|---|---|---|
| SEC-01 | Users forging metrics, audit or AI-usage rows | INSERT/UPDATE on computed tables only via the service role (workers); users create only their own inputs (migration `20261115000100_hardening.sql`) |
| SEC-02 | Malformed storage paths causing errors / policy bypass | `try_uuid()` in every storage policy |
| SEC-03 | Job tampering | users cannot update `jobs`/`prediction_jobs`; cancellation via `request_job_cancel()` (security definer, role-checked) |
| SEC-04 | CSV / formula injection | cells starting with `= + - @ \t \r` prefixed with `'` in every CSV/XLSX export (predictions, leaderboards, reports) |
| SEC-05 | Zip / XML bombs | XLSX read with calamine; ratio and absolute size guards (§45.3 PV01); `defusedxml` for any XML; Parquet row-group and column-count limits |
| SEC-06 | Unsafe deserialisation | models only from the lab's own store with sha256 verification; `skops` for sklearn pipelines where supported; `torch.load(weights_only=True)`; no user-uploaded pickles in v1 |
| SEC-07 | CORS / CSRF | `CORS_ALLOWED_ORIGINS` = production domain + the project's preview domain pattern; credentials only via `Authorization: Bearer` (no cookies to `lab-api`), so CSRF does not apply to the API |
| SEC-08 | Prompt injection via data | cell values never in the instruction part of prompts; column names sanitised; outputs validated against FACTS (§23.7) |
| SEC-09 | PII | PII detector (column names + regex for email, phone, PAN, Aadhaar) at intake; masked in previews, prompts, logs and Sentry; identifier-like values never stored in contracts |
| SEC-10 | Secrets | service role and provider keys only on Render; CI grep for secrets in client bundles (existing); secret scanning enabled on the GitHub repo |
| SEC-11 | Abuse | rate limits per user/IP on `lab-api` (slowapi + Redis); upload count limits; admin audit export |

### 46.4 UX guarantees

* **Empty states** for every module (no datasets / no runs / no models / no predictions) with one primary action and a "Load sample" link.
* **Errors** as RFC 9457 problem+json with a stable code (`PVxx`, `HGxx`, `JOBxx`); the UI maps codes to plain-language messages with a fix suggestion; never a raw stack trace.
* **Progress** for every job (percentage, step, ETA, cancel); optimistic UI only for cheap actions.
* **Mobile**: read-only dashboards, leaderboards and the Prediction Studio custom form work at ≥ 360 px; training setup is desktop-first with a notice.
* **Accessibility**: WCAG 2.2 AA (contrast in both themes, focus order, keyboard sliders, `aria-live` for job status, alt text from artefact titles, colour-blind-safe palettes with shape/dash redundancy); axe-core checks in Playwright.
* **Reproducibility exports** (per run): run report (HTML interactive + PDF), **pipeline code export** (`.py` script and Jupyter notebook that rebuild the recipe, estimator, CV and seed with the pinned library versions; `requirements.txt` from the lock), the feature contract, and a zip "reproduction bundle" (data hash, config JSON, code, environment). Leaderboard export as CSV/XLSX.

### 46.5 Comparison with established AutoML / ML workbench tools (researched Nov 2026)

| Tool | Notable capabilities | Adopted in the lab |
|---|---|---|
| PyCaret (3.x frozen; 4.0 alpha line with a FastAPI + React control plane, FSL licence) | compare_models leaderboard, `plot_model`, prediction logs, scheduled drift monitor + retraining, experiment templates | leaderboard (§12), experiment templates (`presets`), **prediction logs** (`prediction_jobs`, §45), scheduled drift checks (v2.5) |
| AutoGluon 1.5+ (Apache-2.0; 1.6.3 pinned in the optional image) | multi-layer stack ensembling, fixed model portfolio, tabular foundation models (TabDPT, RealTabPFN-2.5 non-commercial), Chronos-2 for TS, `predictor.refit_full` | ensembles (R41/C*), optional AutoGluon image (`optional-automl.txt`, §43), **refit-on-full-data** before deployment (§25), foundation TS opt-in (F53) |
| H2O-3 / Driverless AI | AutoML leaderboard export, MOJO scoring artefacts, reason codes per prediction, automatic model documentation | leaderboard export (§46.4), ONNX/joblib export (§25), per-row SHAP reason codes (§45.4), auto model card (§25) |
| DataRobot | humility rules (uncertain prediction / outlying input triggers), prediction explanations in batch outputs, prediction outlier warnings, batch prediction jobs with chunking and schedules, "prepare for deployment" retrain | **humility rules** → `flag_ood`, `flag_out_of_range`, interval-width warnings with configurable actions (warn / abstain / route to human) in §45; SHAP top-k in batch; chunked jobs; schedules (v2.5) |
| Dataiku | visual flow, data quality rules, model documentation generator, scenarios (schedules/triggers) | dataset lineage view (§33), data quality checks in Intake, report generator (§25); visual flow editor not adopted (scope) |
| Vertex AI AutoML / Model Monitoring | batch prediction to tables, feature attributions, skew/drift monitoring | batch to CSV/XLSX/Parquet, SHAP, drift PSI/KS (§22 Monitoring, §45 PV11) |
| MLJAR | automatic Markdown/HTML reports per model, "Explain/Perform/Compete" modes | run report per model (§46.4), Quick/Balanced/Thorough presets (§14) |
| Orange / KNIME / Weka | visual workflows, widget-based teaching, many classic algorithms | education layer (§24) and the pipeline graph view of each run (read-only DAG) instead of a full visual editor; Weka-only algorithms not adopted unless a maintained Python library exists (rule 70) |

**New features added in v2.2** (all scoped in CURSOR_PROMPT): humility rules and abstain option (Phase 3A), leaderboard export (Phase 2), refit-on-full-data before registration (Phase 3), reproduction bundle + notebook export (Phase 3), pipeline graph view (Phase 2), prediction logs and retention (Phase 3A), scheduled batch scoring and drift checks (Phase 7, optional).

### 46.6 Consistency fixes applied in v2.2 (summary)

SSE is served directly by `lab-api` (not fanned out through Vercel) in §3, §5, §8 and §29; queue `q.predict.heavy` added (§8, `render.yaml`); prediction endpoints unified (§6.2 ↔ §45.7); generic job endpoints `GET /jobs/{id}/events` and `POST /jobs/{id}/cancel` (§6.2 ↔ CURSOR_PROMPT §4.3); bucket limits aligned between `supabase/config.toml` and migrations; env matrix (§39.10) ↔ `.env.example` ↔ `render.yaml`; embedded `render.yaml` in §39.7 re-synced; the self-hosted VLM leftovers in §8 removed; table list in CURSOR_PROMPT Phase 0 completed. Full list: `docs/STRESS_TEST.md`.
