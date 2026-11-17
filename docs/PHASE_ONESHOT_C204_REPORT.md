# Phase oneshot-c204 — Admin VLM numbers-only FE + 8.1 Contabo status

## Built
- `runInsights` / `proposeDecision` in `frontend/src/lib/api.ts`.
- Admin · VLM probe button (`AI.NUMBERS.ONLY` / `VD.NUMBERS.ONLY` artefacts).
- `docs/PHASE_8_1_REPORT.md` Contabo hosted-smoke table (honest blocked status).

## Tests
FE TypeScript only (no new pytest). Offline AI/VD contracts already green in c200/c201.

## Deviations
Hosted probe needs live Contabo `lab-api`.

## TODOs
Browser-click Admin → VLM probe once Deploy is green.
