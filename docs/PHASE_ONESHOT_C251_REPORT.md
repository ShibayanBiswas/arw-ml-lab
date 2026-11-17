# Phase oneshot-c251 — FE predictBatchJson Idempotency-Key

## Built
- `frontend/src/lib/api.ts` `predictBatchJson` always sends `Idempotency-Key` (caller override or `crypto.randomUUID()`).
- `labcore/predict/fe_idempotency_contract.py` + unit test.

## Tests (real)
```
.\.venv\Scripts\python.exe -c "from labcore.predict.fe_idempotency_contract import assert_fe_predict_batch_idempotency_header; print(assert_fe_predict_batch_idempotency_header())"
{'id': 'FE.PRED.IDEMPOTENCY', 'seed': 42, 'ok': True}
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
