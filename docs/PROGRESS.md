# Build progress (keep current — CURSOR_PROMPT.md §000 "Resume")

| Field | Value |
|---|---|
| Current phase | One-shot finish (Chunk A → B → C) — in progress |
| Last completed step | Chunk A deploy.yml honesty + checkout@v5; remote migrations verified via MCP |
| Last green commit | *(pending)* |
| Open failures | See **Blocked — needs Shibayan** |
| Next action | Chunk B deepen 2/2A/3/3A/4 → Chunk C 4A…8.2 → FINAL_REPORT |

## Blocked — needs Shibayan

| Item | Why | Exact action |
|---|---|---|
| `SUPABASE_ACCESS_TOKEN` | Not in local `.env` / CLI login; GitHub `production` env empty | Create at https://supabase.com/dashboard/account/tokens then: `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab` |
| `SUPABASE_DB_PASSWORD` | Not in local env | `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab` |
| Render Blueprint `need_payment_info` | Blueprint `exs-dbsnkbpsrm7s73drvi90` unpaid | Approve payment in Render, then set `vars.RENDER_ENABLED=true`, `vars.LAB_API_URL`, deploy-hook secrets, Vercel `NEXT_PUBLIC_LAB_API_URL` |
| `NVIDIA_API_KEY` on Render | Only after lab-api exists | Put key in Render `lab-shared` only — never Vercel |
| GitHub Pro branch protection | Optional | Enable required checks on `main` if on Pro |
| Supabase Storage 2 GB limit | Pro project setting | Dashboard → Storage → raise global file size |

**Note:** `SUPABASE_PROJECT_ID` can be set to `ushtfpelbpjfkjoppklz` (already attempted via agent). Remote DB already has 8 migrations applied (MCP `list_migrations`). Deploy `render`/`smoke` now skip honestly unless `RENDER_ENABLED=true`.

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
| 4A–8.2 | not started | — | — |
