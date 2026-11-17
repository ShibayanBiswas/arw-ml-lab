# Phase oneshot-c205 — OPS.CONTABO.CONCURRENCY

## Built
- `labcore/ops/contabo_concurrency.py` — assert worker-train `--concurrency 1` + GPU false.
- Unit test.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_contabo_concurrency.py -v --tb=short
============================== 1 passed in 0.19s ==============================
```

## CI note
GitHub Actions still fails in ~2–4s (billing). Local contracts green.

## Deviations
None.
