# Phase oneshot-c265 — Contabo DL small-epoch smoke contract

## Built
- `assert_deep_router_small_epochs` in `labcore/ops/contabo_dl_defaults.py` (max_epochs default 1, cap 5).

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_ops_contabo_dl_defaults.py -q --tb=short
.                                                                        [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
