# Phase oneshot-c266 — decision-agent offline eval harness

## Built
- `labcore/decisions/eval_harness.py`: five deterministic guard cases (shuffled CV, horizon, TabPFN, secrets, allow-list).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_decision_eval_harness.py -q --tb=short
.                                                                        [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
