# Phase oneshot-c231 — OPS.CONTABO.OPTUNA env docs

## Built
- `DEPLOY_CONTABO.md` §7 lists `OPTUNA_STORAGE_URL` (session Postgres) and `HEALTHCHECK_PING_URL`.
- Contract `OPS.CONTABO.OPTUNA`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_contabo_env_optuna.py -q --tb=line
.                                                                        [100%]
EXIT:0
```
