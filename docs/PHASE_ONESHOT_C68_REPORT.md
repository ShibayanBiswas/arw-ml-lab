# Phase oneshot-c68 — CLE.P.PER_CLASS_BARS

## Built
- `plot_per_class_bars` — grouped precision / recall / F1 per class via `sklearn.metrics.precision_recall_fscore_support`; accepts a single OOF split or aligned CV fold lists and shows ±1 sample std error bars when `n_folds > 1`.

## Tests
```
uv run pytest tests/unit/test_cle_per_class_bars.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_cle_per_class_bars.py .                                  [100%]

============================== 1 passed in 8.98s ==============================
```

## Notes
- Remote `main` had no `oneshot-c67` commit after fetch/poll; implemented away from `plot_conformal` to reduce overlap risk with a concurrent c67 slice.
- Seed 42 for StratifiedKFold / LogisticRegression in the unit test.