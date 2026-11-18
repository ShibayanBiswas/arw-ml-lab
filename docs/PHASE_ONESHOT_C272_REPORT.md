# Phase oneshot-c272 — SoftTimeLimit mid-run best-so-far

## Built
- `labcore/ops/soft_time_limit.py`: `PartialHolder`, `sanitize_leaderboard_rows`.
- `run_supervised_cv(..., on_partial=)` checkpoints after each finished algorithm.
- `run_optuna_tune(..., on_partial=)` Optuna trial callback with best-so-far.
- Train/tune Celery tasks wire `PartialHolder` so a soft kill mid-loop keeps completed models/trials (not empty `partial`).
- Contract OPS.SOFT.TIME_LIMIT now has 6 checks (mid-run hooks).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_ops_soft_time_limit.py -q --tb=short
....                                                                     [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing; Actions billing still kills CI in ~2s.
