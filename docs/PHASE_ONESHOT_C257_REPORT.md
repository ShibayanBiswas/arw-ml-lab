# Phase oneshot-c257 — persist OOF pred_threshold on feature contract

## Built
- `labcore/train/run.py`: after classification eval, write `feature_contract["pred_threshold"]` from OOF-tuned `t_star` (Youden/F1) and default `calibration_status=uncalibrated`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_train_persists_pred_threshold.py -q --tb=line
.                                                                        [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
