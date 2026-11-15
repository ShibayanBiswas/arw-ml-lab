# Phase 2B — Workstation UI (home / modules / logos)

Approved plan: `phase_2b_workstation_ui_2c917bbd` (UI-first; Phase 3 Explain+Predict waits; full §34 2A-cont deferred).

## Locked decisions

1. **UI before engines:** Port SP / Marketing Workstation shell polish into ML Lab only — BrandLogo, sidebar rails, Home Terminal, ModuleHub. No Phase 3 Explain/Predict/UQ.
2. **Patterns only:** Copy visual patterns from Desktop SP/Marketing and gitignored `refs/sp-workstation`; never commit their source.
3. **No markets widgets:** Lab status strip (seed 42, module count, no fabricated metrics) instead of tape/charts.
4. **Registry-driven:** Home tiles and module hubs read `MODULES` / `mod.nav`; no hand-coded form per algorithm.
5. **Deploy sync (ADR-0006):** after green commit, push `origin/main` and confirm Vercel READY.

## Workstreams

0. Plan + ADR-0010 + PROGRESS  
1. Theme-aware BrandLogo + Sidebar / DashboardShell ARWL wiring  
2. Home Terminal (Greeting / TerminalHeader / ModuleGallery) + ModuleHub  
3. Vitest + tsc, report, commit `phase 2b: workstation ui shell`, push, Vercel READY, STOP

## Acceptance

- [ ] Sidebar: ARWL logo expanded + gold ML monogram collapsed; dark invert works  
- [ ] Home: Greeting + TerminalHeader + icon module tiles + luxe footer  
- [ ] Sidebar module rails use SP active/hover classes  
- [ ] Each module home lists submodule cards from registry  
- [ ] Vitest + `tsc --noEmit` green  
- [ ] Commit + push + Vercel READY  
