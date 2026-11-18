# Phase oneshot-c260 — MC-dropout thin wrapper

## Built
- `labcore/uncertainty/mc_dropout.py`: stochastic forwards with Dropout layers force-enabled; returns mean/std; never refits.
- Exported from `labcore.uncertainty`.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_mc_dropout.py -q --tb=short
.                                                                        [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
