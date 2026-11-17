# Phase oneshot-c191 — Optuna storage wiring

## Built
- `backend/app/settings.py` — `OPTUNA_STORAGE_URL`.
- `backend/worker/tasks/tune.py` — passes storage + `study_name=exp-{id}` into `run_optuna_tune`.
- `.env.example` — documents the variable.
- `tests/unit/test_tune_optuna_storage_wiring.py`.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_tune_optuna_storage_wiring.py -v --tb=short
============================== 2 passed in 0.24s ==============================
```

## Notes
- Complements oneshot-c189 resume contract. Contabo still blocked.
