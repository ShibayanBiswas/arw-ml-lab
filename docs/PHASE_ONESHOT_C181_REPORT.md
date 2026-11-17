# Phase oneshot-c181 — TRAIN.REFIT.FULL

## Built
- `labcore/train/refit_full.py` — ST-FEAT-02 prepare-for-deployment refit (default ON); scopes `train_only` / `train_plus_oof_pool`; `include_test` forbidden.
- `labcore/train/refit_full_contract.py` — offline artefact **`TRAIN.REFIT.FULL`**.
- `labcore/train/__init__.py` — exports policy helpers.
- `tests/unit/test_train_refit_full.py` — manifest + test-exclusion + policy guard.
- `docs/STRESS_TEST.md` — **ST-FEAT-02** → `fixed + tested` (offline; registry UI toggle Phase 3/8.2).

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_train_refit_full.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 4 passed in 7.70s ==============================
```

## Notes
- Seed **42**. Hold-out test never enters the refit index set.
- Contabo / Actions billing still blocked.

## Self-check (CURSOR_PROMPT §000)
- [x] Default-on toggle policy.
- [x] Test hold-out locked out of refit indices.
- [x] Import allowlist green; sklearn `clone` + fit only (rule 70).
- [x] Real pytest output only.
