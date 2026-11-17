# Phase 2 report — Auth/brand + thin supervised slice

**Date:** 2026-11-15 (IST)  
**Status:** green for **recommended thin scope** (ADR-0005); full CURSOR_PROMPT Phase 2 §41/§42 / full R*/C* → **Phase 2-cont**

## Built

### Workstream 0 — Auth / brand / free deploy
- SP-style BFF auth: password → on-screen OTP → session (`jose` HS256 + `bcryptjs`); roster `frontend/src/data/team.ts`
- Routes `/login`, `/otp`; API `frontend/src/app/api/auth/*`; cookies `ml_session` / `ml_pending`
- Migration `20261115180000_lab_bff_auth.sql` (`lab_app_users`, `lab_otps` + RLS); pgTAP `lab_bff_auth_test.sql`
- FastAPI `AUTH_MODE=bff` + shared `JWT_SECRET`; `lab-session.ts` Bearer from session (bypass for pytest only)
- Branding: **Machine Learning Lab**, ARWL logos under `frontend/public/brand/`, AuthShell / Sidebar
- Docs: ADR-0005, `docs/DEPLOY.md` free-path notes, `docs/DEPLOY.md` updated
- **Vercel MCP:** team SSO consent still required for repair/rename (link issued in-session; expires ~10 min). Render Blueprint still `need_payment_info` → local/`docker compose` API until payment OK

### Workstream 1 — Thin supervised
- `labcore/preprocess/recipe.py`: impute / one-hot|ordinal / standard|robust|minmax / optional SMOTE via `imblearn.Pipeline`
- `labcore/registry/algorithms.py`: **14** R*/C* (Ridge/Lasso/ElasticNet, RF, HistGBM, XGB, LGBM, CatBoost × reg+clf, Logistic)
- `labcore/train/run.py`: 20% hold-out + StratifiedKFold/KFold (seed 42), OOF-style fold metrics + test; fold-fit spy hook
- `labcore/train/presets.py`: Optuna Quick/Balanced/Thorough/Exhaustive trial budgets (catalog hook)
- `labcore/train/export.py`: formula-safe leaderboard CSV (SEC-04)
- API: `POST /api/v1/experiments/train`, GET experiment/leaderboard + `.csv`; Celery `lab.train.run` on `q.train.cpu`
- FE: `TrainWorkbench` recipe + leaderboard UI

## Acceptance criteria (thin subset — real runs)

| AC (plan subset) | Result |
|---|---|
| Catalog ≥10 algorithms | **PASS** (14) |
| All thin specs instantiate | **PASS** |
| MI-11 drop constant/all-NaN | **PASS** |
| Shuffled target → near chance | **PASS** |
| Fold-fit spy (per-fold fit) | **PASS** |
| SMOTE not applied to validation length | **PASS** |
| DS3 Quick train (logistic/RF/LGBM) | **PASS** |
| DS12 Quick train (ridge/RF/LGBM) | **PASS** (sklearn `fetch_california_housing` fallback when OpenML lazy file missing) |
| Leaderboard CSV formula escape | **PASS** |
| Tuning presets Quick=20 / Balanced=60 | **PASS** |
| Full §41/§42, all R1–R51/C1–C35, 20 CV schemes, Halving/NSGA-II, CD diagram | **DEFERRED** → Phase 2-cont |

### Commands / output

```
.\.venv\Scripts\pytest.exe tests/unit --tb=no -q --disable-warnings
.......s..s............................................................. [ 98%]
.                                                                        [100%]
EXIT:0

.\.venv\Scripts\pytest.exe tests/unit/test_phase2_train.py -q
..........                                                               [100%]
EXIT:0

.\.venv\Scripts\python.exe tests/db_harness/run_db_tests.py
ok   20261115180000_lab_bff_auth.sql
== lab_bff_auth_test.sql
 ok - lab_app_users exists / lab_otps exists / RLS ok
(+ prior RLS suites ok)
EXIT:0

.\.venv\Scripts\python.exe -m ruff check labcore backend
(exit 0 after Phase 2 path fixes)

cd frontend && pnpm exec tsc --noEmit
(exit 0)

cd frontend && pnpm test --run
Test Files  3 passed (3) / Tests  6 passed (6)
```

## Deviations / TODOs (Phase 2-cont)

- Full classification/regression evaluation suites (§41 / §42) and plots
- Remaining AlgorithmSpec matrix R*/C* + parametrised preset draws
- Full CV catalogue (20 schemes), Optuna trial loop (presets hooked only), Halving/NSGA-II
- McNemar/DeLong/CD diagram golden tests; MLflow nested runs when tracking URI set
- TargetEncoder / rare encoder / KNN impute expansions; pipeline graph view UI
- Hosted: apply BFF migration on Supabase project if not yet; Vercel env `JWT_SECRET` + seed map; re-auth MCP and fix any Hobby deploy failures
- Render workers remain payment-blocked

## Self-verification checklist (§000)

- [x] unit tests green (2 skipped pre-existing soft-skips); phase2 train 10/10; frontend vitest + tsc green
- [x] db_harness pgTAP green incl. `lab_bff_auth`
- [x] no new stubs in train/preprocess/auth shipped paths
- [x] train/experiment endpoints added; auth tables migrated + RLS
- [x] no secrets in commit
- [x] seed 42 on CV / SMOTE / estimators
- [ ] Playwright axe-core: not expanded this phase (auth/train screens have loading/error text)

## Next

**Phase 2-cont** (finish full Phase 2 AC) **or Phase 2A** per user **continue**.
