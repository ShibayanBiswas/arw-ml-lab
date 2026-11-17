# Phase oneshot-c243 — PV16 identifier_like / PII flag

## Built
- Predict validation emits PV16 warn when `identifier_like` features appear in the batch (never send cell values to VLM); info when none.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_pv16_pii_flag.py tests\unit\test_pv11_batch_drift.py -q --tb=short
....                                                                     [100%]
EXIT:0
```
