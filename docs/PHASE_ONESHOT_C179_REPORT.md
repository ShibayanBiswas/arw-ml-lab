# Phase oneshot-c179 — UX.GLOBAL.STATES

## Built
- `labcore/ux/pv_messages.py` — PV01–PV10, PV14, PV15 plain-language title/fix map (synced with validate).
- `labcore/ux/global_states_contract.py` — offline artefact **`UX.GLOBAL.STATES`** for **ST-UX-03** (ModulePlaceholder states, CURSOR_PROMPT axe checklist, Py/TS PV map parity).
- `frontend/src/lib/pv-messages.ts` — browser copy for prediction validation codes.
- `tests/unit/test_ux_global_states_contract.py` — manifest + PV message smoke.
- `docs/STRESS_TEST.md` — **ST-UX-03** → `fixed + tested` (offline kit; Playwright axe Phase 8.2).

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ux_global_states_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 3 passed in 3.50s ==============================
```

## Notes
- Distinct from oneshot-c178 **REP.T.BUNDLE** (ST-UX-02 zip); c179 is global UX states + PV UI map only offline.
- Does not wire `pv-messages.ts` into Prediction Studio UI yet (Phase 3A/8.2).
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] ModulePlaceholder exposes empty / loading / error + `data-state`.
- [x] CURSOR_PROMPT §000 cites axe-core and tri-state screens.
- [x] Python `PV_MESSAGES` keys match `frontend/src/lib/pv-messages.ts`.
- [x] Import allowlist green.
- [x] Rule 70: stdlib + in-repo reads only; no new third-party deps.

**Ship commit:** `(pending)`