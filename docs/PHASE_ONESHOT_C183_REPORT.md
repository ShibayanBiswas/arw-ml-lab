# Phase oneshot-c183 — REP.T.LEADERBOARD FE wiring

## Built
- `frontend/src/lib/api.ts` — `downloadExperimentLeaderboard` + CSV/XLSX path helpers (ST-UX-02).
- `frontend/src/components/train/TrainWorkbench.tsx` — Download CSV / XLSX buttons (`data-artefact="REP.T.LEADERBOARD"`).
- `tests/unit/test_fe_leaderboard_export_wb.py` — source wiring contract.
- `docs/STRESS_TEST.md` — **ST-UX-02** → `fixed + tested` (Playwright E2E remains Phase 8.2).

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_fe_leaderboard_export_wb.py -v --tb=short
============================== 2 passed in 0.26s ==============================
```

## Notes
- Server-side SEC-04 escape already in leaderboard export helpers; Contabo still blocked.

## Self-check (CURSOR_PROMPT §000)
- [x] FE calls existing `/leaderboard.csv` and `/leaderboard.xlsx`.
- [x] No new third-party deps.
