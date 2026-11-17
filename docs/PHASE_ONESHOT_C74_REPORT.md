# Phase oneshot-c74 — REE.P.QQ

## Built
- `plot_qq` in `labcore/eval/regression/plots.py` — normal Q-Q from `statsmodels.graphics.gofplots.ProbPlot` (`theoretical_quantiles` vs `sample_quantiles`); 95% order-statistic envelope via `scipy.stats.beta` on ranks; statsmodels-style reference line (`theoretical × σ + μ`); artefact id `REE.P.QQ`; `numbers` carries quantiles, envelope and reference for FACTS/oracle checks.

## Tests
```
uv run pytest tests/unit/test_ree_qq.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_qq.py .                                              [100%]

============================= 1 passed in 22.38s ==============================
```

## Notes
- Seed 42 on synthetic residual fixture; oracle replays `ProbPlot` and direct `beta.ppf` / `norm.ppf` envelope (1e-10–1e-12 atol).
- Replaces prior `scipy.stats.probplot`-only Q-Q helper in the same function.
- `plot_qq` body landed in `b170baa` alongside c75 `SCALE_LOCATION`; this slice adds the oracle test + phase report.
- Next gap: `REE.P.RESID_HIST` (KDE + normal overlay) or `REE.P.COOKS` (stem + 4/n) per ARCHITECTURE §42 residuals group.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; ProbPlot + scipy beta envelope only (no hand-rolled quantiles).
- [x] Thin wrapper; Plotly layout on library coordinates.
- [x] Imports within pinned stack (statsmodels, scipy, plotly, numpy).