# Phase oneshot-c254 — PV12 insufficient_history row flag on batch CSV

## Built
- `ValidationReport.insufficient_history_rows` set by PV12 lookback warn path.
- `_score_validated` writes `insufficient_history` boolean column into the results CSV when those rows exist.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_pv12_sequential.py -q --tb=line
.......                                                                  [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
