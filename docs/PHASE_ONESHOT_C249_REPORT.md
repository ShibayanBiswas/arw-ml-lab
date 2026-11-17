# Phase oneshot-c249 — attach OOF residual conformal qhat at train

## Built
- `labcore/predict/conformal_attach.py`: `oof_absolute_residual_qhat` + `attach_oof_residual_qhat`.
- `labcore/train/run.py`: regression champions get `conformal_qhat_` from OOF absolute residuals (level 0.9); stored on `feature_contract.uncertainty`; re-attached after refit_full.

## Tests (real)
```
.\.venv\Scripts\python.exe -m pytest tests/unit/test_conformal_attach.py --tb=line -q
.                                                                        [100%]
```

## Contabo
Still blocked — `CONTABO_HOST` missing.
