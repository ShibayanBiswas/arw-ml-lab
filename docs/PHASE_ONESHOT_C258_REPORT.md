# Phase oneshot-c258 — detect CalibratedClassifierCV for calibration_status

## Built
- `calibration_status_label` inspects pipeline / named_steps for `CalibratedClassifier*` or `calibrated_`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_predict_calibration_status.py -q --tb=line
...                                                                      [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
