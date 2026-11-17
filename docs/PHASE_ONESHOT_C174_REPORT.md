# Phase oneshot-c174 — MI.MULTI.TARGET

## Built
- `labcore/integrity/multi_target_policy.py` — **MI-13** sklearn `MultiOutputRegressor` / `RegressorChain` / `MultiOutputClassifier` wrappers; per-target R² and Prediction Studio column groups.
- `labcore/integrity/multi_target_contract.py` — offline artefact **`MI.MULTI.TARGET`** for ST-ML-02 (multi-output regression, regressor chain, multilabel classifier, studio groups).
- `tests/unit/test_mi_multi_target_contract.py` — synthetic fixtures, manifest, negative monkeypatch.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.MULTI.TARGET** MI-13.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_multi_target_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 6 passed in 11.21s ==============================
```

## Notes
- Distinct from oneshot-c173 **MI.TARGET.LEAKAGE** (MI-15); c174 is multi-output / multilabel sklearn wiring only offline.
- Metrics use sklearn `r2_score(..., multioutput='raw_values')` plus macro mean; no from-scratch multi-target metrics.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] `MultiOutputRegressor` predicts `(n, 2)` with per-target R² > 0.5 on synthetic ridge fixture.
- [x] `RegressorChain` uses `random_state=seed` and finite predictions.
- [x] `MultiOutputClassifier` on two labels with per-label accuracy > 0.55.
- [x] Prediction Studio one column group per target name.
- [x] Import allowlist green.
- [x] Rule 70: sklearn multioutput wrappers only.

**Ship commit:** (filled after push)