# Phase oneshot-c255 — calibration_status on batch predictions

## Built
- `labcore/predict/calibration_label.py`: resolve calibrated vs uncalibrated from feature contract / pipeline flag.
- `_score_validated` adds `calibration_status` column when probabilities are present (§45.4).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_predict_calibration_status.py -q --tb=line
..                                                                       [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
