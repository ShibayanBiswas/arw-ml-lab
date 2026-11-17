# Phase oneshot-c172 — MI.HIGH.CARD

## Built
- `labcore/integrity/high_cardinality_policy.py` — **MI-10** level thresholds (50 / 30), encoder proposals, `OneHotEncoder` cap + infrequent bucket, identifier uniqueness gate.
- `labcore/integrity/high_cardinality_contract.py` — offline artefact **`MI.HIGH.CARD`** for ST-ML-02 (proposals, one-hot cap, identifier exclusion, target-encoder recipe wiring).
- `tests/unit/test_mi_high_cardinality_contract.py` — proposals, cap, manifest, negative monkeypatch.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.HIGH.CARD** MI-10.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_high_cardinality_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 6 passed in 36.66s ==============================
```

## Notes
- Distinct from oneshot-c171 **MI.HORIZON.GUARD** (MI-17); c172 is categorical encoding / identifier exclusion only offline.
- Reuses `build_feature_contract` / `looks_identifier` (§45.2) and sklearn `OneHotEncoder` + `TargetEncoder` via `compile_recipe`.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] n>50 proposes target, hashing, count encoders.
- [x] n>30 one-hot output within cap (max_categories=30, infrequent_if_exist).
- [x] Identifier-like column excluded; contract stores no banned values.
- [x] High-cardinality fixture compiles target-encoder recipe pipeline.
- [x] Import allowlist green.
- [x] Rule 70: sklearn wrappers only for encoding.

**Ship commit:** (filled after commit)