# Phase oneshot-c166 — MI.TARGET.ENCODING

## Built
- `labcore/integrity/target_encoding_policy.py` — **MI-02** chance-AUC guard, recipe `TargetEncoder` extractor, sequential `shuffle=False` policy; seed **42**.
- `labcore/integrity/target_encoding_contract.py` — offline artefact **`MI.TARGET.ENCODING`** for ST-ML-02 remainder (distinct from c165 **MI.PREPROCESS.FIT** MI-01).
- `tests/unit/test_mi_target_encoding_contract.py` — recipe wiring, 5 000-row noise AUC, prefit vs in-pipeline negative, manifest, monkeypatch failure.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.TARGET.ENCODING** MI-02.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_target_encoding_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 7 passed in 11.56s ==============================
```

## Notes
- Distinct from oneshot-c165 **MI.PREPROCESS.FIT** (MI-01); wires `compile_recipe` → sklearn `TargetEncoder(cv=…)` only offline.
- Phase 2 train runner already uses recipe pipelines; sequential `shuffle=False` on inner CV stays a train-path prove.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Noise column OOF `|AUC − 0.5| < 0.03` on 5 000 synthetic rows.
- [x] Import allowlist green.
- [x] Rule 70: sklearn `TargetEncoder` / `compile_recipe` only.

**Ship commit:** `4621bf5`