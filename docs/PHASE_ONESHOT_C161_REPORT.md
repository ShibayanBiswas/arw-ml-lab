# Phase oneshot-c161 — MI.DATA.QUALITY

## Built
- `labcore/integrity/data_quality_contract.py` — **ST-ML-03** offline contract: **MI-11** (`drop_constant_columns` / `RecipeSpec.drop_constant`) and **MI-12** (ambiguous `dd/mm` Intake questions via `detect_datetime_index`); artefact **`MI.DATA.QUALITY`**, seed **42**.
- `tests/unit/test_mi_data_quality_contract.py` — contract checks + negative MI-11 path.
- `docs/STRESS_TEST.md` — **ST-ML-03** → `fixed + tested`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_data_quality_contract.py tests\unit\test_import_allowlist.py -v --tb=short
======================= 7 passed, 3 warnings in 37.92s ========================
```

## Notes
- Next STRESS row after c160 **OPS.GPU.WORKER** (**ST-OPS-11**); closes **ST-ML-03** offline (distinct from c159 **ST-ML-02** slice).
- Intake banner / user format choice remains Phase 1A UI prove.
- Seed **42**; no Contabo / NVIDIA / TradingLab.

## Self-check (CURSOR_PROMPT §000)
- [x] MI-11/MI-12 assertions from real `drop_constant_columns` and `detect_datetime_index` runs.
- [x] Import allowlist green.
- [x] Rule 70: existing recipe + intake helpers only.

**Ship commit:** `70df6a3`