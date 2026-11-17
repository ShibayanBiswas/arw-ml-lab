# Phase oneshot-c165 — MI.PREPROCESS.FIT

## Built
- `labcore/integrity/preprocess_fit_policy.py` — **MI-01** `FitIndexSpy`, fold index equality helper, full-frame prefit heuristic; seed **42**.
- `labcore/integrity/preprocess_fit_contract.py` — offline artefact **`MI.PREPROCESS.FIT`** for ST-ML-02 remainder (distinct from c164 **MI.DUPLICATE.GROUP** MI-18).
- `tests/unit/test_mi_preprocess_fit_contract.py` — cross_validate spy per fold, prefit negative, manifest, monkeypatch failure.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.PREPROCESS.FIT** MI-01.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_preprocess_fit_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================== 8 passed in 8.64s ==============================
```

## Notes
- Distinct from oneshot-c164 **MI.DUPLICATE.GROUP** (MI-18); wires pipeline-level fit scope only offline.
- Enforcing “no pre-split `fit_transform`” on the train runner remains Phase 2 prove (existing fold loop already refits per fold).
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Spy indices verified on real sklearn `cross_validate` folds.
- [x] Import allowlist green.
- [x] Rule 70: sklearn Pipeline / LogisticRegression / StandardScaler only.