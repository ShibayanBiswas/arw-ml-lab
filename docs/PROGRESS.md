# Build progress (keep current — CURSOR_PROMPT.md §000 "Resume")

| Field | Value |
|---|---|
| Current phase | One-shot interim — see docs/FINAL_REPORT.md; continue 4A→8.2 |
| Last completed step | oneshot-c3 insights+guards CI green; FS14/FS20 + interim FINAL_REPORT |
| Last green commit | dbcb069 (CI https://github.com/ShibayanBiswas/arw-ml-lab/actions/runs/43806362529) |
| Open failures | Deploy migrate (missing Supabase secrets); Render unpaid |
| Next action | Shibayan: secrets + Render payment. Agent: deepen 4A/5/5A/6B/7/8.2 |

## Blocked — needs Shibayan

| Item | Why | Exact action |
|---|---|---|
| `SUPABASE_ACCESS_TOKEN` | Not in local `.env` / CLI login; GitHub `production` env empty | Create at https://supabase.com/dashboard/account/tokens then: `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab` |
| `SUPABASE_DB_PASSWORD` | Not in local env | `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab` |
| Render Blueprint `need_payment_info` | Blueprint `exs-dbsnkbpsrm7s73drvi90` unpaid | Approve payment in Render, then set `vars.RENDER_ENABLED=true`, `vars.LAB_API_URL`, deploy-hook secrets, Vercel `NEXT_PUBLIC_LAB_API_URL` |
| `NVIDIA_API_KEY` on Render | Only after lab-api exists | Put key in Render `lab-shared` only — never Vercel |
| GitHub Pro branch protection | Optional | Enable required checks on `main` if on Pro |
| Supabase Storage 2 GB limit | Pro project setting | Dashboard → Storage → raise global file size |
| TradingLab submodule | `vendor/tradinglab` absent | Needed for FS6–FS19 + AFML parity |

**Note:** `SUPABASE_PROJECT_ID` = `ushtfpelbpjfkjoppklz`. Remote DB has 8 migrations. Deploy `render`/`smoke` skip unless `RENDER_ENABLED=true` (and migrate secrets set).

## Phase log
| Phase | Status | Report | Commit |
|---|---|---|---|
| 0–4 thin | done | PHASE_*_REPORT.md | prior |
| One-shot A | done | deploy.yml | 6851ce9 |
| One-shot B.1–B.3 | done | PHASE_ONESHOT_B1_REPORT.md | 5e7db5c…8dcd625 |
| One-shot C.1–C.3 | done (partial 5/6/6A/8.2) | FINAL_REPORT.md | 8524aa6…dbcb069 |
| 4A–8.2 full | in progress | FINAL_REPORT.md | — |
