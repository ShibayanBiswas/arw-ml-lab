# Architecture decision records

## ADR-0015 — One-shot B.1 deepen: in-lab purged/CPCV + PV matrix (2026-11-16)

- **Purged K-fold / CPCV** implemented in `labcore/cv/purged.py` citing AFML ch. 7/12 because `vendor/tradinglab` is not present. When the submodule is added, swap adapters to TradingLab primitives and keep the same public API (`PurgedKFold`, `CombinatorialPurgedKFold`, `ml_get_train_times`).
- **PV02/03/10/14/15** promoted from deferred stubs to real checks; PV10 uses contract median/p01/p99 z-scores (no IsolationForest refit at predict — training-time IF detector still Phase 3A-cont).
- **FS1–FS5** live in `labcore/suitability`; FS6–FS20 stay DEFERRED until TradingLab label adapters (Phase 5 / 5B).
- DL sequential z-score now fits on **purged train windows only** (`scaler_fit_on=train_windows_only`).

## ADR-0014 — Phase 4 Time Series thin (2026-11-15)

- Thin smoke of §19/§20 only: canonical `labcore/timeseries/horizon_guard.py` (Steps 1–2–4; Step 3 soft h* after backtest); SeasonalNaive (statsforecast) + airline SARIMA (statsmodels); rolling-origin W=4; MASE/MAE/RMSE/sMAPE + Ljung-Box; STL/classical/ACF analysis; sync API + minimal `TsWorkbench`.
- Intake `labcore/intake/horizon.py` re-exports the canonical guard (DS22 golden h_max=24 preserved).
- Seasonal gate: n ≥ 2m+h with strict boundary (n ≤ 2m+h → disabled) so DS23 at h=12 is refused.
- Full F1–F54, DS24 coverage ±5 pp, DS28 GPU N-HiTS/PatchTST, §35 → **4-cont / 4A**.
- CI unit job installs `statsforecast` pin (not full `ts.txt`) for SeasonalNaive.

## ADR-0013 — Phase 3A Prediction Studio thin (2026-11-15)

- Thin smoke of §45 only: PV core (PV01 extension + PV04–PV09; other codes deferred stubs), CSV/XLSX templates, sync batch validate+score (≤5k rows), contract-driven custom form UI, DS3 sample path.
- Train drops identifier-like columns before fit and persists `feature_contract` + champion pipeline into in-memory `MODEL_STORE` (`model_id` on experiment result). Never refit at predict; formula-safe CSV export (SEC-04).
- Full PV01–PV16 matrix, Celery `q.predict.batch` / 1M chunking, Playwright, conformal batch columns, sequential lookback, AI `prompts/prediction.md` → **3A-cont**.
- Deploy sync unchanged: sole Vercel `arw-ml-lab` (ADR-0011).

## ADR-0012 — Phase 3 Explain / Predict / UQ thin (2026-11-15)

- Thin smoke only: TreeSHAP (`shap.TreeExplainer`), PDP/ICE (`sklearn.inspection`), MAPIE `SplitConformalRegressor` / `SplitConformalClassifier(aps)`, `CalibratedClassifierCV` + `FrozenEstimator` (sklearn ≥1.6 removed `cv='prefit'`), feature contracts + `predict_single`/`predict_batch` (never refit).
- Full §17 explainers, §25 registry/ONNX/export, §45 Prediction Studio UI → **3-cont / 3A**.
- In-memory `MODEL_STORE` for thin API routes; durable registry stays Phase 3A/7.

## ADR-0011 — Sole Vercel project `arw-ml-lab` (2026-11-15)

- This repo deploys to **one** Vercel project: **`arw-ml-lab`** (`prj_gohylY9RNNIcBZHqG6GqaKtaTmrY`), Root Directory **`frontend`**, production alias `https://arw-ml-lab.vercel.app`.
- A stray project named **`frontend`** (Root Directory `.`) was created by linking from `frontend/` and failed every build with `NEXT_NO_VERSION`. It was deleted; local `frontend/.vercel` must not be recreated.
- Agents/devs: run Vercel CLI from the **repo root** (link to `arw-ml-lab`) or rely on Git integration. Never create a second Git-connected project for this repo.
- CI must pin `pnpm/action-setup` to `frontend/package.json` because job `defaults.working-directory` does not apply to `uses:` steps.

## ADR-0010 — Phase 2B Workstation UI shell (2026-11-15)

- Insert **Phase 2B** before Phase 3: UI-first parity with SP / Marketing Workstation for home, modules, and logos. Phase 3 Explain+Predict and full §34 2A-cont wait for next continue.
- Port **patterns only** (BrandLogo theme invert, `.sidebar-module-rail`, Greeting / TerminalHeader / module tiles, ModuleHub). Never commit `refs/sp-workstation` or Desktop SP/Marketing source.
- Sidebar expanded = ARWL wordmark; collapsed = gold **ML** monogram. Mobile top bar uses BrandLogo. Dark theme uses `brightness-0 invert` on the PNG.
- Home Terminal replaces sparse tile dump; footer `ANAND RATHI WEALTH · MACHINE LEARNING LAB`. Lab status strip (seed 42, module count) instead of markets tape.
- `[module]/page.tsx` is a registry-driven submodule launcher (`ModuleHub` from `mod.nav`), not a blank placeholder.
- Vitest `testTimeout` raised to 30s so bcrypt roster seed under parallel load does not flake.

## ADR-0009 — Phase 2A Deep Learning thin smoke (2026-11-15)

- Full §34 (all T*/Q*, DL.P catalogue, MC-dropout/ensembles) deferred to **2A-cont**; this stop is a thin smoke like Phase 2.
- Engine: Lightning + pytorch-tabular (`CategoryEmbedding` / `TabNet` / `FTTransformer`) + `torch.nn.LSTM` + `pytorch-tcn`; AdamW defaults, early stopping, LR finder.
- Specs: T1/T3/T4, Q2/Q7, T13 TabPFN (hidden unless `TABPFN_ENABLED=true`), Q12 xLSTM GPU stub (HTTP 422 without `LAB_GPU_WORKER=true`).
- Soft dep: `pytorch-tabnet==4.1.0` added to `dl-cpu.txt` (TabNet `create_group_matrix`); `requests` pinned for pytorch-tabular import.
- `AlgorithmSpec.resources` / `enabled_env` added; catalog filters licence-gated models; train/tune routes refuse GPU-only / disabled TabPFN with 422.

## ADR-0008 — Phase 2-cont-3 password-only SP auth UI + durable seed (2026-11-15)

- Product request: **no OTP screen** — login is email+password → `ml_session` immediately (ADR-0005 OTP step removed).
- Change password uses **current + new** (no on-screen OTP); SP layout/styles retained with ML Lab branding.
- Hosted passwords: `SEED_DEFAULT_PASSWORD_MAP` on Vercel + upsert into `lab_app_users`. BFF may use **`SUPABASE_SERVICE_ROLE_KEY` server-only** in Next.js route handlers for this table (never `NEXT_PUBLIC_*`, never client bundle). In-memory Map remains local/dev fallback.
- UI must match SP Workstation auth shell (aurora, auth-card-large, disclaimer modal, ThemeToggle, light/dark).

## ADR-0007 — Phase 2-cont-2 Tune / CV / nested default (2026-11-15)

- Nested CV **on by default when n_train &lt; 2000** (MI-03); outer folds use the selected scheme, inner = 3-fold stratified/kfold for tune only.
- Optuna artefacts: study best params + trial history dict; MLflow logging only when `MLFLOW_TRACKING_URI` is set (no fabricated tracking).
- TargetEncoder is an optional recipe encoder (`target`) fitted inside the pipeline / CV folds only (MI-02).
- Full plot catalogues and Halving/NSGA-II remain deferred to 2-cont-3.

## ADR-0006 — Phase 2-cont Eval Core + deploy sync (2026-11-15)

- Phase 2 thin deferred full §41/§42; this stop implements **Eval Core** only: CM suite, classification report, CLE.M for binary/multiclass, CLE.T.CV_METRICS, threshold OOF-only spy, McNemar/5×2/DeLong; REE residuals / resid tests / influence / core REE.M; minimum Plotly set for Overview/Confusion/Report/Curves/Residuals.
- Deferred to next 2-cont slice: full CLE.P.* / REE.P.* catalogues, remaining CV schemes, Optuna trial loop / Halving / NSGA-II, leftover R*/C*, MLflow nested runs, CD-diagram goldens.
- Eval artefact payload lives on the experiment result under `eval.classification` / `eval.regression` (JSON numbers + plotly); OOF arrays cached under `.cache/eval` in tests.
- **Standing ops:** after every phase green commit, push `origin/main` and confirm Vercel Hobby production is READY (Machine Learning Lab / Root Directory `frontend`).

## ADR-0005 — BFF auth primary (Phase 2, 2026-11-15)

- ARCHITECTURE §39.5 lists Supabase Auth as primary; SP `jose`+OTP as fallback. **User request:** same login as SP Workstation, **no Supabase email/magic OTP**, same Rathi roster.
- **Primary for this lab until Phase 7 SSO:** Next.js BFF (`jose` HS256 + `bcryptjs` + on-screen OTP), cookies `ml_session` / `ml_pending`, roster from `frontend/src/data/team.ts`.
- Persist users/OTP in **Supabase Postgres** (`lab_app_users`, `lab_otps`) — not MongoDB — so the data platform stays one Postgres.
- FastAPI accepts BFF JWTs when `AUTH_MODE=bff` (shared `JWT_SECRET`); `AUTH_TEST_BYPASS` remains for pytest only.
- Supabase Auth magic-link UI is removed from the primary login path; Storage/RLS unchanged.
- Thin Phase 2 ML slice: recipe + ≥10 algorithms + CV + leaderboard; full §41/§42 deferred to Phase 2-cont.

## ADR-0004 — Phase 1A intake rule-based only (2026-11-15)

- LLM adjudicator (§33.9) deferred to Phase 6; Phase 1A ships detectors D1–D8 + validator behind the same proposal schema.
- Financial targets are JSON builders only (`triple_barrier`, `fwd_log_return`, …); TradingLab remains Phase 5 (extends ADR-0002).
- `lab.intake.run` must not overwrite the Phase-1 `TaskSpec` on `DATASET_STORE`; confirmed `task_spec` attaches to the experiment via confirm.
- Large-frame intake uses a ≤20k stride sample for detectors; full `n_rows` is preserved on the profile.
- New pins: `exchange-calendars==4.11.1`, `rapidfuzz==3.14.1` (`eda.txt` / §44); `worker-light.lock.txt` recompiled for 3.12.

## ADR-0003 — Phase 8.1 hosted skeleton scope (2026-11-15)

- Live path: private GitHub `arw-ml-lab`, Supabase Pro, Render Blueprint (`render.yaml`), Vercel Root Directory `frontend`.
- TradingLab git submodule **not** added in 8.1 (remains Phase 5; CI `submodules: recursive` is a no-op without `.gitmodules`).
- §39.13 sample flow “EDA → Quick train → leaderboard → explain → predict” is **deferred** until those stages exist (Phase 2+). Phase 8.1 smoke is `GET /healthz` plus optional DS1 EDA via `scripts/smoke_hosted.sh` when workers and secrets are ready.
- `lab-beat` runs `python -m backend.worker.maintenance --all` with Phase 8.1 no-op stubs; real reaper/retention in Phase 8.2.
- Default branch renamed to `main` to match CI/deploy triggers.
- Secrets only in Render / Vercel / GitHub Environment `production` dashboards — never in the repo or chat.
- **Branch protection:** GitHub Free on a **private** repo returns HTTP 403 for classic protection and rulesets (“Upgrade to GitHub Pro”). Documented in DEPLOY; enable after Pro or org-owned repo.
- **Render Blueprint:** created (`exs-dbsnkbpsrm7s73drvi90`) with `autoSync=false`; first plan fails with `need_payment_info` until a payment method is on the Render workspace. Approve Blueprint only after payment + cost OK.
- **Supabase:** project `ushtfpelbpjfkjoppklz` (`ap-south-1`); migrations applied via MCP (not CLI `db push`). Hosted global file-size 2 GB still requires Pro plan + dashboard toggle.
- **Vercel:** project `arw-ml-lab`, Root Directory `frontend`, production `https://arw-ml-lab.vercel.app`.

## ADR-0002 — Phase 1 EDA without TradingLab (2026-11-15)

- TradingLab remains Phase 5. EDA.T.BREAKS TL methods (Chow/CUSUM/SADF), TL volatility estimators, and ONC feature clustering return `not computed` with reason `tradinglab_phase_5`.
- Breaks still include `ruptures` PELT; financial stats use scipy/pandas returns metrics until Phase 5.
- `arch` and `ruptures` added to `eda.txt` so sequential EDA runs on `lab-worker-light`.
- Local `StoragePort` filesystem adapter under `.cache/uploads/` for tests without hosted Supabase.

## ADR-0001 — Phase 0 foundations (2026-11-15)

- **SP design source:** Cloned `ShibayanBiswas/sp-workstation` into `refs/sp-workstation` (git-ignored) and ported tokens/shell patterns into `frontend/`.
- **PyJWT:** Declared explicitly in `backend/requirements/api.txt` (was already a transitive of `supabase`) for JWKS verification in FastAPI.
- **Local Docker image:** Phase 0 compose builds from `api.lock.txt` for fast smoke; Render `lab-worker-train` still uses `worker-train.lock.txt` per `render.yaml`.
- **Supabase CLI:** Pinned to `3.1.0` in CI/deploy (ST-OPS-10).
- **TradingLab:** Not vendored in Phase 0 (owned by Phase 5).
