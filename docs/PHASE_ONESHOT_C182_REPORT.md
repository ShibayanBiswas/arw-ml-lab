# Phase oneshot-c182 — UX.MOBILE.PREDICT

## Built
- `frontend/src/components/predict/CustomPredictForm.tsx` — `min-w-[360px]`; form pane above result pane (`flex-col`, `lg:grid-cols-2`).
- `frontend/src/components/train/TrainWorkbench.tsx` — desktop-first notice on narrow viewports.
- `labcore/ux/mobile_predict_contract.py` — offline artefact **`UX.MOBILE.PREDICT`** (ST-UX-04).
- `tests/unit/test_ux_mobile_predict.py` — source-marker contract.
- `docs/STRESS_TEST.md` — **ST-UX-04** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ux_mobile_predict.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 3 passed in 1.98s ==============================
```

## Notes
- Seed **42**. Contabo / Actions billing still blocked.

## Self-check (CURSOR_PROMPT §000)
- [x] Form stacks above result at ≥ 360 px markers.
- [x] Training desktop-first notice present.
- [x] Import allowlist green.
