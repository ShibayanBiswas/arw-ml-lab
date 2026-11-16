# Phase oneshot-c34 — DR trustworthiness / Shepard + Prophet catalogue

## Built
- `fit_dr` returns sklearn `trustworthiness` when n≥10.
- `DR.P.SHEPARD` Plotly + Spearman ρ (`labcore/unsupervised/dr_plots.py`).
- API `POST /api/v1/unsupervised/dr/shepard`.
- F20 Prophet wrapper in TS catalogue (lazy import; unit test skips if prophet absent — CI unit job does not install prophet).

## Tests
```
pytest tests/unit/test_dr_trust_shepard.py tests/unit/test_prophet_forecast.py -q
→ 1 passed, 1 skipped (prophet)
```
