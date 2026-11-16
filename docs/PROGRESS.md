# Build progress (keep current — CURSOR_PROMPT.md §000 "Resume")

| Field | Value |
|---|---|
| Current phase | One-shot interim — docs/FINAL_REPORT.md; continue remaining 4A/5/5A/6B/7/8.2 ACs |
| Last completed step | oneshot-c8 Admin UI; CI green through 3109058 |
| Last green commit | 3109058 |
| Open failures | Deploy migrate (Supabase secrets); Render unpaid |
| Next action | Shibayan: secrets + Render. Agent: full catalogues / WFO retune / Playwright |

## Blocked — needs Shibayan

| Item | Exact action |
|---|---|
| `SUPABASE_ACCESS_TOKEN` | `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab` |
| `SUPABASE_DB_PASSWORD` | `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab` |
| Render payment | Approve Blueprint; `vars.RENDER_ENABLED=true`, `vars.LAB_API_URL`, deploy hooks; Vercel `NEXT_PUBLIC_LAB_API_URL` |
| `NVIDIA_API_KEY` | Render `lab-shared` only |
| TradingLab submodule | `vendor/tradinglab` for FS6–19 + AFML parity |

## One-shot commits (16 Nov 2026)
A deploy gate → B.1–B.3 PV/purged/Celery/TS → C.1–C.8 PBO/WFO/AI/guards/reports/drift/experiments/admin

See docs/FINAL_REPORT.md for the full table.
