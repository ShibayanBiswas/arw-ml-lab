# Phase oneshot-c245 — PV13 HorizonGuard on predict validate

## Built
- `validate_predict_frame` accepts `h_request=` and reads `contract.timeseries` (`n`, `freq`); blocks when HorizonGuard rejects.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_pv13_horizon.py -q --tb=short
..                                                                       [100%]
EXIT:0
```
