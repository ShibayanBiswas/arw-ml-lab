# Phase oneshot-c71 — REE.P.LEARNING

## Built
- `plot_regression_learning_curve` in `labcore/eval/regression/plots.py` — thin wrapper over `sklearn.model_selection.learning_curve` (default `scoring="r2"`, five train sizes 30%–100%, seed 42) → Plotly train/CV traces with ±1σ bands; artefact id `REE.P.LEARNING`.

## Tests
```
uv run pytest tests/unit/test_ree_learning.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_learning.py .                                        [100%]

============================= 1 passed in 12.39s ==============================
```

## Notes
- CLE already had `CLE.P.LEARNING`; this mirrors that pattern for regression with explicit R² scoring.
- Next gap: `REE.P.VALIDATION` (sklearn `validation_curve`).

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; oracle asserts means match direct `learning_curve` call.
- [x] Thin wrapper; no from-scratch curve logic.
- [x] sklearn + plotly only (pinned stack).