# Phase oneshot-c246 — PV12 sequential predict validation

## Built
- `labcore/predict/validate.py`: PV12 when `contract.time_column` is set — parse time, warn unsorted (auto-sort offered), warn duplicate timestamps per series, lookback / lag history (`insufficient_history`; block if all rows lack history). Deferred when no time column.
- `labcore/ux/pv_messages.py` + `frontend/src/lib/pv-messages.ts`: PV11–PV13, PV16 UI copy; `IMPLEMENTED_PV_CODES` now PV01–PV16.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_pv12_sequential.py -q --tb=line
......                                                                   [100%]
EXIT:0
```

```
.\.venv\Scripts\python.exe -c "from labcore.ux.global_states_contract import assert_pv_messages_sync; print(assert_pv_messages_sync())"
{'n_codes': 16, 'frontend': 'frontend/src/lib/pv-messages.ts'}
```

## Contabo
Still blocked — `CONTABO_HOST` missing from local `.env`.
