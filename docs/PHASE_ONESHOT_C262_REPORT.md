# Phase oneshot-c262 — MC-dropout smoke API

## Built
- `POST /api/v1/deep/mc-dropout/smoke` on `backend/app/routers/deep.py`.

## Tests (real)
`
.\.venv\Scripts\python.exe -m pytest tests/unit/test_mc_dropout_api.py -q --tb=short
.                                                                        [100%]
`

## Contabo
Still blocked — `CONTABO_HOST` missing.
