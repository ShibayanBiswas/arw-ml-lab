# Phase oneshot-c180 — PRED.HUMILITY

## Built
- `labcore/predict/humility.py` — ST-FEAT-01 humility policy (`warn` / `abstain` / `review`) for OOD, out-of-range, and wide intervals; escalate precedence abstain > review > warn.
- `labcore/predict/humility_contract.py` — offline artefact **`PRED.HUMILITY`**.
- `labcore/predict/score.py` — optional `humility=` on `predict_single` (suppresses prediction when abstain); never refits.
- `tests/unit/test_pred_humility.py` — manifest + abstain/clean/review cases.
- `docs/STRESS_TEST.md` — **ST-FEAT-01** → `fixed + tested` (offline; hosted Prediction Studio wiring Phase 3A/8.2).

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_pred_humility.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 5 passed in 25.67s ==============================
```

## Notes
- Seed **42**. Contabo / Actions billing still blocked (see PROGRESS).
- Does not yet wire humility flags into the Prediction Studio UI (Phase 3A/8.2).

## Self-check (CURSOR_PROMPT §000)
- [x] Configurable warn / abstain / review actions.
- [x] Clean rows pass through; abstain suppresses prediction value.
- [x] Import allowlist green; no new third-party deps (rule 70).
- [x] Numbers from real pytest run only.
