# Phase oneshot-c170 — MI.CLASS.RESAMPLE

## Built
- `labcore/integrity/class_imbalance_policy.py` — **MI-07** validation-length and SMOTE train-only helpers.
- `labcore/integrity/class_imbalance_contract.py` — offline artefact **`MI.CLASS.RESAMPLE`** for ST-ML-02 (imbalance gates, fold-internal SMOTE via spy, recipe `resample=smote`).
- `tests/unit/test_mi_class_imbalance_contract.py` — detection, SMOTE fold spy, recipe wiring, manifest.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.CLASS.RESAMPLE** MI-07.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_class_imbalance_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 6 passed in 22.80s ==============================
```

## Notes
- Distinct from oneshot-c169 **MI.SEED.DRIFT** (MI-06) and ST-ML-05 **MI.SAMPLE.SIZE** (MI-07/08/09 flags only); c170 is fold-internal resampling + imbalance gates offline.
- Distinct from oneshot-c171 **MI.HORIZON.GUARD** (MI-17), committed on main after this gap fill.
- Reuses `FitIndexSpy` from MI-01 policy and `classify_class_imbalance` from `sample_size_policy`.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Minority share / ratio / extreme-rarity gates on fixed label vectors.
- [x] SMOTE in `imblearn.Pipeline`: spy indices match fold train; val prediction length unchanged.
- [x] `compile_recipe(resample=smote)` yields `imblearn` pipeline with SMOTE step.
- [x] Import allowlist green.
- [x] Rule 70: sklearn + imbalanced-learn only; no custom resampler.

**Ship commit:** `1045a5e`