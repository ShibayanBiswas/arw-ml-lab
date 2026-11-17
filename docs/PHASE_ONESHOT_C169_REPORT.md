# Phase oneshot-c169 — MI.SEED.DRIFT

## Built
- `labcore/integrity/seed_drift_policy.py` — **MI-06** `LAB_DEFAULT_SEED=42`, `apply_lab_seed`, metric equality atol **1e-12**.
- `labcore/integrity/seed_drift_contract.py` — offline artefact **`MI.SEED.DRIFT`** for ST-ML-02 (Quick `run_supervised_cv` reproduce + seed-change drift negative).
- `tests/unit/test_mi_seed_drift_contract.py` — duplicate-run equality, seed-43 drift, manifest.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.SEED.DRIFT** MI-06.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_seed_drift_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 6 passed in 49.47s ==============================
```

## Notes
- Distinct from oneshot-c168 **MI.PURGED.SPLIT** (MI-04); c169 is reproducibility only offline.
- Reuses `run_supervised_cv` path proven in `test_mi06_quick_reproducible`; full run-metadata hash ledger remains Phase 8.2.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Duplicate Quick logistic runs: `cv_mean` equal within 1e-12.
- [x] Seed 43 subsample changes `cv_mean` on fixture (drift negative).
- [x] Import allowlist green.
- [x] Rule 70: sklearn train path only; torch seed via existing `deep.engine.set_seed`.

**Ship commit:** `1ee6d42`