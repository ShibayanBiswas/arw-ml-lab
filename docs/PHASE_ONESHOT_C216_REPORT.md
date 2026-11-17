# Phase oneshot-c216 — OPS.MAX_ROWS

## Built
- `Settings.lab_max_rows` (default 2_000_000).
- `labcore/ops/max_rows_guard.py` + train/tune 422 before enqueue.
- Unit tests.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_max_rows_guard.py -q --tb=line
..                                                                       [100%]
```
