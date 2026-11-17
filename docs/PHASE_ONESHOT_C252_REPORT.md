# Phase oneshot-c252 — batch classification confidence columns

## Built
- `predict_batch`: when `predict_proba` is available, emits `pred_confidence` (max p̂), `pred_margin` (top-1 − top-2), `pred_entropy` (normalised `scipy.stats.entropy`).
- `_score_validated` merges those columns into the results CSV/JSON.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_predict_batch_clf_columns.py -q --tb=line
.                                                                        [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing. CI still dies in ~3s (Actions billing).
