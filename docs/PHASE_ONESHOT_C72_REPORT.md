# Phase oneshot-c72 — REE.P.VALIDATION

## Built
- `plot_regression_validation_curve` in `labcore/eval/regression/plots.py` — `sklearn.model_selection.validation_curve` with `KFold(shuffle=True, random_state=seed)` and default scoring `neg_mean_squared_error`; Plotly train/CV traces with ±1 std error bars; artefact id `REE.P.VALIDATION`. (Plot body landed in `2d8f811` alongside c71 LEARNING; this slice adds the oracle test + phase report.)

## Tests
```
uv run pytest tests/unit/test_ree_validation.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_validation.py .                                      [100%]

============================= 1 passed in 20.35s ==============================
```

## Notes
- Seed 42 on `make_regression` and `Ridge(random_state=42)`; test oracles against raw `validation_curve` and `ValidationCurveDisplay.from_estimator` means (1e-9 rtol).
- `REE.P.LEARNING` from c71 unchanged; VALIDATION inserted above it in `plots.py`.
- Next gap: remaining §42 REE plots / suite wiring as per FINAL_REPORT.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; library-only `validation_curve` / `ValidationCurveDisplay`.
- [x] Thin wrapper; no from-scratch CV scoring.
- [x] Imports limited to pinned stack (sklearn, plotly, numpy).