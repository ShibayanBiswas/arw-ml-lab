# Phase oneshot-c274 — REP.T.BUNDLE runnable reproduce.py

## Built
- Replaced `_reproduce_py_stub` with `_reproduce_py`: seed 42, load `config/run.json`, check `environment/core-pins.txt`, assert dataset/algorithm, no stub print.
- Contract executes `reproduce.py` from a temp extract of the zip.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_rep_t_bundle_export.py -q --tb=short
...                                                                      [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing; Actions billing still kills CI in ~2s.
