# Build progress (keep current — CURSOR_PROMPT.md §000 "Resume")

| Field | Value |
|---|---|
| Current phase | One-shot Chunk C — continue catalogues / FS / Playwright |
| Last completed step | oneshot-c29 CLE.P + ONNX/skops export |
| Last green commit | (pending c29 push) |
| Open failures | Deploy migrate (Supabase secrets); Render unpaid |
| Next action | Shibayan: secrets + Render. Agent: more CLE.P / Playwright / F* |

## Blocked — needs Shibayan

| Item | Exact action |
|---|---|
| `SUPABASE_ACCESS_TOKEN` | `gh secret set SUPABASE_ACCESS_TOKEN --env production --repo ShibayanBiswas/arw-ml-lab` |
| `SUPABASE_DB_PASSWORD` | `gh secret set SUPABASE_DB_PASSWORD --env production --repo ShibayanBiswas/arw-ml-lab` |
| Render payment | Approve Blueprint; `vars.RENDER_ENABLED=true`, `vars.LAB_API_URL`, deploy hooks; Vercel `NEXT_PUBLIC_LAB_API_URL` |
| `NVIDIA_API_KEY` | Render `lab-shared` only |
| TradingLab submodule | `vendor/tradinglab` for FS6–19 + AFML parity |

## One-shot commits (16 Nov 2026)
A deploy gate → B.1–B.3 → C.1–C.12 (incl. CD diagram, LIME/DiCE)

See docs/FINAL_REPORT.md for the full table.
