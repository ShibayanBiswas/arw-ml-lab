# Phase oneshot-c195 — PRED.HUMILITY API wire

## Built
- `PredictSingleBody.humility` (`dict | false | null`); null/omit → default policy; `false` disables.
- `_humility_opts_for_row` merges validate PV10 / out_of_range into humility opts.
- `predictSingle` FE sends `humility` (null = defaults on).
- `tests/unit/test_predict_humility_api.py`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_predict_humility_api.py -v --tb=line
======================= 3 passed, 4 warnings in 22.96s ========================
```

## Deviations
None. Contabo/Actions still blocked.

## TODOs
Browser DS1 Prediction Studio humility badge on live Contabo.
