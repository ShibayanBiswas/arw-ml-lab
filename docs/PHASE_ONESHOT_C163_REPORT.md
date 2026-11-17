# Phase oneshot-c163 — MI.SAMPLE.SIZE

## Built
- `labcore/integrity/sample_size_policy.py` — **ST-ML-05** / MI-07 (imbalance flags), MI-08 (CV ladder, `min_rows` + DL 1k gate, HorizonGuard n/4), MI-09 (memory estimate + 1.2× refusal message); artefact **`MI.SAMPLE.SIZE`**, seed **42**.
- `labcore/integrity/small_large_data_contract.py` — offline contract manifest for STRESS row **ST-ML-05**.
- `labcore/train/run.py` — default CV scheme from `cv_scheme_for_n`; filter algorithms with `eligible_algorithms`.
- `labcore/registry/__init__.py` — lazy `get_catalog` export to break registry↔train import cycle.
- `tests/unit/test_mi_small_large_data_contract.py` — positives + MI-09 negative fixture.
- `docs/STRESS_TEST.md` — **ST-ML-05** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_small_large_data_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 8 passed in 12.11s ==============================
```

## Notes
- Distinct from oneshot-c162 **OPS.STORAGE.BACKUP**, c161 **MI.DATA.QUALITY**, c159 **MI.NESTED.CV** slice of ST-ML-02.
- Pre-enqueue memory guard + 50k plot subsample labels remain Phase 2 API prove.
- Seed **42**; no Contabo / NVIDIA / TradingLab.

## Self-check (CURSOR_PROMPT §000)
- [x] MI-07/08/09 numbers from real policy runs (no fabricated metrics).
- [x] Import allowlist green.
- [x] Rule 70: stdlib + numpy + existing cv/horizon helpers only in policy module.

**Ship commit:** (see git log `phase oneshot-c163`)