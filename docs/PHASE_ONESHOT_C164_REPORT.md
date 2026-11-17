# Phase oneshot-c164 — MI.DUPLICATE.GROUP

## Built
- `labcore/integrity/duplicate_split_policy.py` — **MI-18** duplicate-row share gate (> 1 %), stable row-hash groups, split leak assertion; seed **42**.
- `labcore/integrity/duplicate_split_contract.py` — offline artefact **`MI.DUPLICATE.GROUP`** for ST-ML-02 remainder (distinct from c163 **MI.SAMPLE.SIZE** / ST-ML-05).
- `tests/unit/test_mi_duplicate_split_contract.py` — threshold gate, GroupKFold non-leak vs naive KFold leak, negative fixture.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.DUPLICATE.GROUP** MI-18.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_duplicate_split_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 6 passed in 12.11s ==============================
```

## Notes
- Distinct from oneshot-c163 **MI.SAMPLE.SIZE** (ST-ML-05 MI-07/08/09); wires GroupKFold recommendation only offline.
- Train runner auto-select of `group_kfold` when dup share > 1 % remains Phase 2 prove.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Duplicate share and GroupKFold checks from real sklearn splits on synthetic frames.
- [x] Import allowlist green.
- [x] Rule 70: sklearn GroupKFold + pandas only (no custom splitter).

**Ship commit:** (see git log `phase oneshot-c164`)