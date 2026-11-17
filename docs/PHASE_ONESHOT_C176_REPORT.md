# Phase oneshot-c176 — MI.STML02.OFFLINE

## Built
- `labcore/integrity/st_ml_02_contract.py` — **ST-ML-02** offline rollup artefact **`MI.STML02.OFFLINE`**: registry for MI-01…MI-18 contract modules + **DEEP.GPU.GUARD**; validates `docs/STRESS_TEST.md` row.
- `tests/unit/test_st_ml_02_offline_contract.py` — rollup positives + negative monkeypatch.
- `docs/STRESS_TEST.md` — **ST-ML-02** → `fixed + tested` (offline rollup; worker/UI prove Phase 2/4/5).
- `docs/PROGRESS.md` — last step c176; next action ST-UX-02 / Chunk C / Phase 7.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_st_ml_02_offline_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 4 passed in 34.59s ==============================
```

## Notes
- Distinct from oneshot-c175 **MI.MULTICOLLINEARITY** (MI-14); c176 closes the ST-ML-02 offline slice after c159…c175 per-rule kits.
- MI-08/09 / MI-11/12 / MI-16 point at ST-ML-05 / ST-ML-03 / ST-ML-04 modules but are included in the MI-01…MI-18 coverage table.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Every MI-01…MI-18 rule maps to a contract `ARTEFACT_ID` in-repo.
- [x] ST-ML-02 STRESS row cites rollup + contract modules.
- [x] Import allowlist green.
- [x] Rule 70: stdlib `importlib` only; no new third-party deps.

**Ship commit:** `8e1cc1b`