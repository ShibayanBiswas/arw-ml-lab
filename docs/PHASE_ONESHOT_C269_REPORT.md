# Phase oneshot-c269 — conformal DL residual wrapper

## Built
- `labcore/uncertainty/conformal_dl.py`: qhat from calib residuals + interval predict; never refits the network.

## Tests (real)
`
.\.venv\Scripts\python.exe -m pytest tests/unit/test_conformal_dl.py -q --tb=short
.                                                                        [100%]
`

## Contabo
Still blocked — `CONTABO_HOST` missing.
