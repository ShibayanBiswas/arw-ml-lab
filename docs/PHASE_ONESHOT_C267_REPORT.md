# Phase oneshot-c267 — decision eval-harness HTTP route

## Built
- `GET /api/v1/decisions/eval-harness` returns the offline guard suite.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_decision_eval_api.py -q --tb=short
.                                                                        [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
