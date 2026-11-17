# Phase oneshot-c189 — OPS.OPTUNA.RESUME

## Built
- `labcore/train/tune.py` — optional `storage` / `OPTUNA_STORAGE_URL`, `load_if_exists`, remaining-trial budget, resume metadata on artefact.
- `labcore/ops/optuna_resume_contract.py` — offline artefact **`OPS.OPTUNA.RESUME`** (SQLite resume 2→4 trials).
- `tests/unit/test_ops_optuna_resume.py`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_optuna_resume.py -v --tb=short
============================= 1 passed in 14.15s ==============================
```

## Notes
- Seed **42**. Contabo / Actions billing still blocked. Production should set `OPTUNA_STORAGE_URL` to Postgres session URL.

## Self-check
- [x] Second call resumes from 2 trials and completes 4.
- [x] In-memory path unchanged when storage unset.
