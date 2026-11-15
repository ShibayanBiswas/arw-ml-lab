# Phase 2B report — Workstation UI shell + deploy sync

**Date:** 2026-11-15 (IST)  
**Status:** green for locked UI scope (ADR-0010)

## Built

### Brand / shell
- `BrandLogo.tsx` — theme-aware ARWL PNG; dark invert (`brightness-0 invert`)
- `Sidebar.tsx` — BrandLogo when expanded; gold **ML** monogram when collapsed; `.sidebar-module-rail` / active rails; MODULES kicker; Home Terminal row
- `DashboardShell.tsx` — mobile top bar BrandLogo (not plain text)

### Home Terminal
- `components/home/TerminalHeader.tsx`, `Greeting.tsx` (IST Asia/Kolkata), `ModuleGallery.tsx`, `HomeTerminal.tsx`
- Lab status strip: seed 42, module count, no fabricated metrics
- Luxe footer: `ANAND RATHI WEALTH · MACHINE LEARNING LAB`
- `(lab)/page.tsx` renders `HomeTerminal` with session name

### Module hubs
- `ModuleHub.tsx` — submodule cards from `mod.nav`
- `[module]/page.tsx` uses ModuleHub (not blank placeholder)
- `lib/module-icons.tsx` — icon map for gallery / hubs

### Tests / config
- `BrandLogo.test.tsx`, `HomeTerminal.test.tsx`, extended `shell-tokens.test.ts`
- `vitest.config.ts` — `testTimeout: 30_000` (bcrypt roster under load)

## AC (real runs)

| AC | Result |
|---|---|
| Sidebar ARWL + ML monogram; dark invert | **PASS** (BrandLogo + shell tests) |
| Home Greeting + TerminalHeader + tiles + footer | **PASS** (`HomeTerminal.test.tsx`) |
| Sidebar rails SP classes present | **PASS** (`shell-tokens.test.ts`) |
| Module hub lists `mod.nav` cards | **PASS** (ModuleHub + page wiring) |
| Vitest + tsc green | **PASS** (below) |

### Commands

```
pnpm test --run
 Test Files  7 passed (7)
      Tests  15 passed (15)
EXIT:0

pnpm exec tsc --noEmit
EXIT:0
```

## Deviations / deferred

- Phase 3 Explain / Predict / UQ engines
- Phase 2A-cont full §34 T*/Q*
- Markets tape / charts (SP/Marketing-specific; intentionally omitted)

## Self-check (§000)

- [x] ACs run with real output (no stubs)
- [x] seed 42 referenced on home status; no fabricated metrics
- [x] patterns only — no refs/ source committed
- [x] report + DECISIONS + PROGRESS
- [x] commit + push + Vercel READY (below)

### Deploy closeout

- GitHub `main`: `f3bf6de` (`phase 2b: workstation ui shell`)
- Vercel production **READY**: `https://arw-ml-cfvej0uee-shibayan-biswas-projects.vercel.app` (alias `https://arw-ml-lab.vercel.app`)

## Next

Stop and wait for user **continue** → Phase 3 (Explain+Predict) or Phase 2A-cont (full §34).
