# Phase oneshot-c280 — Feature-contract schema UQ fields

## Built
- `docs/contracts/feature_contract.schema.json`: `pred_threshold`, `calibration_status`, `uncertainty` (conformal metadata).
- Unit tests round-trip validate train-time UQ fields and reject bad calibration labels.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_feature_contract_schema_uq.py tests/unit/test_predict_samples.py -q --tb=short
.........................................                                [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing; Actions billing still kills CI in ~2s.
