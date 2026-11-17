# Phase oneshot-c232 — OPS.COMPOSE.GRACE

## Built
- Contract that `docker-compose.prod.yml` sets `stop_grace_period: 300s` on both workers (§39.3 maxShutdownDelaySeconds).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_compose_grace.py -q --tb=line
.                                                                        [100%]
EXIT:0
```
