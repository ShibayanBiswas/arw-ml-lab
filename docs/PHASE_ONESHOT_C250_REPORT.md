# Phase oneshot-c250 — predict batch Idempotency-Key contract

## Built
- `labcore/predict/idempotency_contract.py`: offline wiring + runtime checks that `Idempotency-Key` is accepted on batch predict and `JobStore` reuses keys.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_predict_batch_idempotency.py -q --tb=short
..                                                                       [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
