# Phase oneshot-c248 — prediction narrative (§45.12)

## Built
- `labcore/predict/narrative.py`: FACTS-only prediction explanation (interval, humility, OOD, PV codes); never invents metrics.
- `POST /api/v1/insights/run` with `stage=prediction` uses the narrative builder under numbers-only / prefer_mock.
- `CustomPredictForm`: "Explain this prediction" → `PRED.NARRATIVE`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_prediction_narrative.py -q --tb=short
..                                                                       [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
