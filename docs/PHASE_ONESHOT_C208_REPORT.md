# Phase oneshot-c208 — OPS.CONTABO.DL_DEFAULTS

## Built
- `labcore/ops/contabo_dl_defaults.py` — TORCH threads, §12 doc needles, TabPFN off.
- `.env.example` `LAB_MAX_ROWS=2000000` (Contabo §12).
- Unit test.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ops_contabo_dl_defaults.py -v --tb=short
============================== 1 passed in 1.82s ==============================
```

## Deviations
None.
