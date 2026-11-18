# ONE-SHOT: finish ARW ML Lab end-to-end (paste into Cursor Agent, Agent mode, strongest thinking model, Max mode)

You are the sole engineer on github.com/ShibayanBiswas/arw-ml-lab (branch main, head 6be4659). Work AUTONOMOUSLY in Agent mode until everything below is done. Do NOT switch to Plan mode, do NOT stop after a phase to wait for "continue", do NOT ask me to confirm chunks. This message overrides every "STOP and wait for continue" line in CURSOR_PROMPT.md §000 and the phase reports. Only stop if blocked by a missing secret, a paid plan, or account access I must give. If that happens, log it in PROGRESS.md under "Blocked — needs Shibayan", skip that item and keep working on everything else.

## 0. Read first (whole files, then keep re-reading the relevant section before each chunk)
AGENTS.md, .cursor/rules/*.mdc, CURSOR_PROMPT.md (§000 18-phase table + DoD), docs/ARCHITECTURE.md v2.2 (incl. §45 Prediction Studio, §46 Hardening), docs/STRESS_TEST.md (50 findings), docs/PROGRESS.md, docs/DECISIONS.md, docs/GAP_AUDIT.md, every docs/PHASE_*_REPORT.md, docs/DEPLOY.md, render.yaml, .github/workflows/*.yml.

## 1. Current truth (verified 15 Nov 2026, 11:30 PM IST; don't redo, just build on it)
- Done (thin): 0, 1, 8.1 (partial), 1A, 2 (+cont, cont-2, cont-3), 2A, 2B, 3, 3A, 4. CI (frontend/backend/supabase/kit-checks) is green. Vercel `arw-ml-lab` is READY at https://arw-ml-lab.vercel.app (200 → /login).
- Not started: 4A, 5B, 5, 5A, 6, 6A, 6B, 7, 8.2.
- DEPLOY ROOT CAUSE (runs 43743009644, 43742293101, 43738372117): job `migrate` fails at step "Require Supabase secrets". It prints `SUPABASE_ACCESS_TOKEN missing` because the GitHub `production` environment/repo secrets SUPABASE_ACCESS_TOKEN, SUPABASE_PROJECT_ID (=ushtfpelbpjfkjoppklz) and SUPABASE_DB_PASSWORD were never set. `render` and `smoke` are then skipped. Even with those set, they would fail next: RENDER_DEPLOY_HOOK_API/_WORKER_LIGHT/_WORKER_TRAIN and vars.LAB_API_URL don't exist, because the Render Blueprint (exs-dbsnkbpsrm7s73drvi90) failed with `need_payment_info`. No lab-api is live, and Vercel NEXT_PUBLIC_LAB_API_URL is still a placeholder.

## 2. Chunk A: make Deploy green honestly (do this first)
1. If `gh auth status` works and the values exist in my local .env / Supabase CLI login, run `gh secret set SUPABASE_ACCESS_TOKEN|SUPABASE_PROJECT_ID|SUPABASE_DB_PASSWORD --env production`. Never print values, never commit them. Otherwise list the exact commands for me under Blocked.
2. Edit deploy.yml so `render` and `smoke` run only when `vars.RENDER_ENABLED == 'true'`. Otherwise print a clear "Render not provisioned (need_payment_info), skipped" notice (no fake success, no silent pass). Keep `migrate` strict. Add a `workflow_dispatch` dry-run (`supabase db push --dry-run`). Bump actions off Node 20 (checkout@v5 etc.).
3. Verify with `supabase migration list --linked` that all 8 migrations are applied remotely. Run pgTAP via tests/db_harness.
4. Backend hosting (v2.3): Contabo VPS per `docs/DEPLOY_CONTABO.md` (not Render). If Contabo host + secrets + Actions billing exist, bootstrap → Deploy → smoke. If not, log Blocked in `docs/PROGRESS.md` and continue offline.
5. Push, then confirm CI green, Deploy green (or honestly "skipped: Render blocked"), and Vercel READY via the Vercel status on the commit.

## 3. Chunk B: deepen every thin phase to FULL spec (in plan order 2 → 2A → 3 → 3A → 4)
- 2: all R1–R51 / C1–C35 AlgorithmSpecs (now 47). Full CLE.P (45) and REE.P (36) plot catalogues. Halving / Hyperband / NSGA-II tuning. Purged K-fold + CPCV in labcore/cv. MLflow nested runs. CD-diagram goldens. KNN/rare encoders. Pipeline-graph UI.
- 2A: full T1–T16 / Q1–Q13. Full DL.P.* Plotly set. MC-dropout, deep ensembles, conformal DL heads. Leakage-safe scalers inside purged folds (thin version z-scores the full series; fix this). AMP/GPU worker path. A Deep Learning UI page (it's ModulePlaceholder now).
- 3: full SHAP plot matrix, DiCE / Anchors / EBM, ONNX export + parity test, MLflow model registry (§17/§21/§22/§25). Explain UI page.
- 3A (§45): PV01–PV16 all real (PV02/03/10–16 are `severity=deferred` stubs today). Zip/XLSX-bomb guards. Celery chunked batch up to 1M rows with cancel + Idempotency-Key (sync cap is 5 000 today). DS12/22/18/33 suites. Conformal columns in the batch UI. Sequential lookback. AI prediction narrative. Playwright + axe. pgTAP prediction_rls_test green.
- 4: full F* model set and DS24/DS28 goldens. Backtest at the structural h_max. Golden forecasts.
- 8.1: hosted smoke. backend/worker/maintenance.py retention/reaper are no-op stubs; implement them in 8.2. Also wire the empty test dirs (tests/e2e, tests/load, tests/contract_tradinglab).

## 4. Chunk C: build the remaining phases to full spec (strict order, each with its DoD)
4A (§35 TS full catalogue) → 5B (§37 FS1–FS20 suitability) → 5 (§13 purged K-fold/CPCV, PBO, §15, TradingLab contract tests) → 5A (§32 walk-forward + golden WFO) → 6 (§18/§23/§40 unsupervised: clustering, DR, anomaly + AI Insights through the NVIDIA provider layer with mocked-provider tests and the insights validator) → 6A (§38 VLM decision agent: guards + eval harness, server-side key only) → 6B (§36 per-family catalogue) → 7 (§25/§26/§46.4 reports, monitoring/drift, enterprise; Playwright e2e, Locust load, ZAP) → 8.2 (§39 + §46 hardening; close every open STRESS_TEST item; §39.13 AC). Every module page currently rendering ModulePlaceholder must become a real workbench backed by real endpoints.

## 5. Loop for EVERY chunk (no exceptions)
Implement → `make test` (all earlier tests too) + ruff + mypy + `pnpm exec tsc --noEmit` + `pnpm test --run` + `pnpm build` + db_harness pgTAP + the phase's own ACs. Paste real commands and outputs into docs/PHASE_<n>_REPORT.md (or PHASE_<n>_CONT_REPORT.md).
Then update docs/PROGRESS.md (current phase, last green commit, open failures, next action), add an ADR in DECISIONS.md if needed, and commit `phase <n>: <summary>`.
Then `git push`, wait for the CI and Deploy runs to finish (`gh run watch`), and fix any red run before moving on. Confirm Vercel READY for that commit and that https://arw-ml-lab.vercel.app returns 200.
Rules: seed 42, never fabricate or hard-code metrics, libraries only from §44 / backend/requirements (rule 70), RLS on every new table and bucket, ExplainCard for every new registry key, no secrets in diffs or logs, NVIDIA_API_KEY never on the client.

## 6. Finish
Write docs/FINAL_REPORT.md. Include:
- a per-phase status table (all 18 plus cont slices) with AC evidence links;
- the CI, Deploy and Vercel run URLs;
- live URLs and smoke results;
- STRESS_TEST closure matrix;
- what remains Blocked and the exact action I must take (e.g. Render payment, GitHub Pro for branch protection, Supabase 2 GB file limit, Auth redirect URLs).
Then commit and push, and verify green one last time.
