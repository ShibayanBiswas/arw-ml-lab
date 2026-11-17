# Phase oneshot-c167 — MI.TS.TARGET_TRANSFORM

## Built
- `labcore/integrity/ts_target_transform_policy.py` — **MI-05** expanding backtest train slices, Box-Cox λ via sklearn `PowerTransformer`, skew-shift fixture; seed **42**.
- `labcore/integrity/ts_target_transform_contract.py` — offline artefact **`MI.TS.TARGET_TRANSFORM`** for ST-ML-02 (TS target transforms fitted per backtest window; ARCHITECTURE §46.1 MI-05).
- `tests/unit/test_mi_ts_target_transform_contract.py` — λ differs across windows, last window = full pre-holdout λ, full-series fit leak negative.
- `docs/STRESS_TEST.md` — **ST-ML-02** offline row notes **MI.TS.TARGET_TRANSFORM** MI-05.

## Tests
```
.\.venv\Scripts\python.exe -m pytest tests\unit\test_mi_ts_target_transform_contract.py tests\unit\test_import_allowlist.py -v --tb=short
============================= 9 passed in 16.38s ==============================
```

## Notes
- Oneshot prompt cited MI-04; §46.1 maps **TS target transforms per backtest window** to **MI-05** (MI-04 is purged sequential/financial splits). This lane wires MI-05 only offline.
- Distinct from oneshot-c165 **MI.PREPROCESS.FIT** (MI-01) and c164 **MI.DUPLICATE.GROUP** (MI-18).
- mlforecast/statsforecast per-window `target_transforms` in the train runner remain Phase 4/5 prove.
- Seed **42**; no Contabo.

## Self-check (CURSOR_PROMPT §000)
- [x] Window λ inequality and last-window = pre-holdout equality on real sklearn Box-Cox.
- [x] Full-series λ ≠ pre-holdout λ on fixture (leak heuristic).
- [x] Import allowlist green.
- [x] Rule 70: sklearn `PowerTransformer` + scipy Box-Cox only.

**Ship commit:** `5ee2b20`