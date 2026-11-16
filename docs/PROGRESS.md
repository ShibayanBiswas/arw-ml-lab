# Build progress (keep current — CURSOR_PROMPT.md §000 "Resume")

| Field | Value |
|---|---|
| Current phase | One-shot finish — Chunk B.1 landed; continuing B deepen + C |
| Last completed step | B.1: PV deepen, purged/CPCV, explain/unsup/FS1–5 UI, DL scaler fix, registry expand |
| Last green commit | *(pending push of B.1)* |
| Open failures | See **Blocked — needs Shibayan** |
| Next action | Keep deepening B (plots/tuning/Celery predict) → Chunk C 4A…8.2 → FINAL_REPORT |

## Blocked — needs Shibayan

| Item | Why | Exact action |
|---|---|---|
| `SUPABASE_ACCESS_TOKEN` | Not in local `.env` / CLI login; GitHub `production` env empty | Create at https://supabase.com/dashboard/account/tokens then: `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab` |
| `SUPABASE_DB_PASSWORD` | Not in local env | `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab` |
| Render Blueprint `need_payment_info` | Blueprint `exs-dbsnkbpsrm7s73drvi90` unpaid | Approve payment in Render, then set `vars.RENDER_ENABLED=true`, `vars.LAB_API_URL`, deploy-hook secrets, Vercel `NEXT_PUBLIC_LAB_API_URL` |
| `NVIDIA_API_KEY` on Render | Only after lab-api exists | Put key in Render `lab-shared` only — never Vercel |
| GitHub Pro branch protection | Optional | Enable required checks on `main` if on Pro |
| Supabase Storage 2 GB limit | Pro project setting | Dashboard → Storage → raise global file size |
| TradingLab submodule | `vendor/tradinglab` absent | Needed for FS6–FS20 + AFML parity; purged/CPCV currently in-lab (ADR pending) |

**Note:** `SUPABASE_PROJECT_ID` = `ushtfpelbpjfkjoppklz`. Remote DB has 8 migrations. Deploy `render`/`smoke` skip unless `RENDER_ENABLED=true`.

## Phase log
| Phase | Status | Report | Commit |
|---|---|---|---|
| 0 | done | docs/PHASE_0_REPORT.md | phase 0: foundations |
| 1 | done | docs/PHASE_1_REPORT.md | phase 1: data + EDA + education |
| 8.1 | done (partial hosted smoke) | docs/PHASE_8_1_REPORT.md | phase 8.1: hosted skeleton |
| 1A | done | docs/PHASE_1A_REPORT.md | phase 1A: dataset intake |
| 2 | done (thin) → deepening | docs/PHASE_2_REPORT.md | phase 2: auth brand thin supervised |
| 2A | done (thin) → deepening | docs/PHASE_2A_REPORT.md | phase 2a: dl thin smoke |
| 2B | done | docs/PHASE_2B_REPORT.md | phase 2b: workstation ui shell |
| 3 | done (thin) → deepening | docs/PHASE_3_REPORT.md | phase 3: explain predict uq thin |
| 3A | done (thin) → deepening | docs/PHASE_3A_REPORT.md | phase 3a: prediction studio thin |
| 4 | done (thin) → deepening | docs/PHASE_4_REPORT.md | phase 4: timeseries thin |
| One-shot A | done | deploy.yml honesty | deploy: gate render/smoke |
| One-shot B.1 | done | docs/PHASE_ONESHOT_B1_REPORT.md | phase oneshot-b1 |
| 4A–8.2 | not started | — | — |
