# Phase oneshot-c256 — pred_threshold column on batch results

## Built
- `labcore/predict/threshold_label.py`: read training decision threshold from the feature contract.
- `_score_validated` writes `pred_threshold` when probabilities are present and a threshold was saved (§45.4).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_pred_threshold_label.py -q --tb=line
.                                                                        [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
