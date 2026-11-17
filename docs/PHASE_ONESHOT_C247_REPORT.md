# Phase oneshot-c247 — batch conformal interval columns

## Built
- `labcore/predict/score.py`: `try_predict_intervals` + `predict_batch` emits `pred_lower_{level}` / `pred_upper_{level}` / `pred_interval_method` when the saved pipeline has MAPIE `predict_interval` or `conformal_qhat_`.
- `backend/app/routers/predict.py` `_score_validated`: merges interval columns into the results CSV and JSON.
- `BatchPredictPanel` + `api.ts`: surfaces conformal column names (`PRED.BATCH.CONFORMAL`).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_predict_batch_intervals.py -q --tb=short
...                                                                      [100%]
EXIT:0
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
