# Phase oneshot-c271 — Contabo DL quick/balanced presets

## Built
- `labcore/deep/contabo_presets.py`: CPU-only quick/balanced presets (batch ≤ 256, threads 2).
- Sequential smoke accepts `preset=` and clamps epochs to the preset.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_contabo_dl_presets.py -q --tb=short
.                                                                        [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing. CI still dies in ~2s (Actions billing).
