# Phase oneshot-c273 — Predict soft-limit + cancel flags

## Built
- `labcore/ops/cancel_flags.py`: memory + Redis cancel stores; `LAB_CANCEL_USE_REDIS` on Contabo compose for api + worker-light.
- `backend/worker/tasks/predict.py`: `PartialHolder` mid-chunk checkpoints; SoftTimeLimit → `save_best_so_far`; cancel via JOB_STORE status **and** cancel-flag key.
- Predict/jobs cancel routes set the flag so Celery workers see cancel across processes.
- OPS.SOFT.TIME_LIMIT contract now includes predict wiring (7 checks).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_ops_cancel_flags.py tests/unit/test_ops_soft_time_limit.py::test_soft_time_limit_manifest_seed_42 -q --tb=short
....                                                                     [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing; Actions billing still kills CI in ~2s.
