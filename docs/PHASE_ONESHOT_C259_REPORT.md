# Phase oneshot-c259 — batch conformal prediction sets (pred_set)

## Built
- `try_predict_sets` + `predict_batch` emit `pred_set` when the saved pipeline exposes MAPIE-style `predict_set`.
- `_score_validated` writes `pred_set` into CSV (stringified) and JSON.

## Tests (real)
```
.\.venv\Scripts\python.exe -c "… importlib load test_predict_batch_pred_set …"
OK
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
