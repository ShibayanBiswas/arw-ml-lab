# Phase oneshot-c201 — VD.NUMBERS.ONLY

## Built
- `labcore/decisions/baseline.py` — numbers-only decision baseline + guard contract.
- `POST /api/v1/decisions/propose` (default `numbers_only=true`).
- `tests/unit/test_vd_numbers_only.py`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_vd_numbers_only.py -v --tb=line
============================== 2 passed in 1.28s ==============================
```

## Deviations
None. Contabo/NVIDIA still blocked.

## TODOs
Wire FE decision cards to `/decisions/propose` on each VD point.
