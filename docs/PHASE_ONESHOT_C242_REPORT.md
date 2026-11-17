# Phase oneshot-c242 — PV11 batch drift (optional reference)

## Built
- `validate_predict_frame(..., reference_df=)` runs KS + PSI via `labcore.monitoring.drift` on overlapping numeric features.
- Without `reference_df`, PV11 stays deferred (unchanged default).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_pv11_batch_drift.py -q --tb=short
..                                                                       [100%]
EXIT:0
```
