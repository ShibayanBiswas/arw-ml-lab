# Phase oneshot-c168 — MI.PURGED.SPLIT

## Built
- `labcore/integrity/purged_split_policy.py` — **MI-04** label-interval overlap guard, contiguous sequential test folds, embargo tail check, horizon fixture; seed **42**.
- `labcore/integrity/purged_split_contract.py` — offline artefact **`MI.PURGED.SPLIT`** for ST-ML-02 (PurgedKFold + CPCV purge; ARCHITECTURE §46.1 MI-04).
- `tests/unit/test_mi_purged_split_contract.py` — per-fold no overlap, CPCV, naive non-purge leak negative.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.PURGED.SPLIT** MI-04.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_purged_split_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 9 passed in 24.72s ==============================
```

## Notes
- Distinct from oneshot-c167 **MI.TS.TARGET_TRANSFORM** (MI-05); this lane is purged sequential/financial splits only offline.
- Wires existing `labcore.cv.purged` (`PurgedKFold`, `CombinatorialPurgedKFold`, `ml_get_train_times`) — no TradingLab submodule required.
- WFO inner purged CV in train runner remains Phase 5A prove.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Every PurgedKFold fold on horizon fixture: zero train/test label-interval overlap.
- [x] Test folds contiguous (no shuffle); embargo tail absent from train.
- [x] Naive non-purged train set fails overlap check on same fixture.
- [x] Import allowlist green.
- [x] Rule 70: purge logic in `labcore/cv/purged.py` only; contract is orchestration + asserts.

**Ship commit:** `3e8ab80`