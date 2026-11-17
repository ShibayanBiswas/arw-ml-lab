# Phase oneshot-c211 — OPS.SSE.PROGRESS

## Built
- `labcore/ops/sse_progress.py` — jobs SSE route + FE `jobEventsUrl` + Caddy proxy kit check.
- Unit test.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_sse_progress.py -v --tb=short
============================== 1 passed in 1.20s ==============================
```

## Deviations
Hosted SSE prove still blocked (Contabo).
