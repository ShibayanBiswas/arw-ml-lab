# Phase oneshot-c76 — REE.P.RESID_HIST

## Built
- `plot_residual_hist` in `labcore/eval/regression/plots.py` — density histogram (`numpy.histogram`), `scipy.stats.gaussian_kde` curve, and normal PDF overlay (`scipy.stats.norm.pdf` at sample μ, σ); artefact id `REE.P.RESID_HIST`; `numbers` carries bin centres, densities, KDE and normal coordinates for FACTS/oracle checks.

## Tests
```
uv run pytest tests/unit/test_ree_resid_hist.py -v --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.2.0, pluggy-1.7.0
Fugue tests will be initialized with options:
rootdir: C:\Users\shiba\OneDrive\Desktop\Machine Learning Lab
configfile: pyproject.toml
plugins: anyio-4.16.0, dash-4.5.0, fugue-0.9.9, hypothesis-6.170.15, platformdirs-4.14.5, cov-7.1.0, respx-0.23.1
collected 1 item

tests\unit\test_ree_resid_hist.py .                                      [100%]

============================= 1 passed in 12.63s ==============================
```

## Notes
- Seed 42 on synthetic residual fixture; oracle replays `histogram`, `gaussian_kde`, and `norm.pdf` (1e-10–1e-12 atol).
- Next gap: `REE.P.COOKS` (stem + 4/n) or `REE.P.LEVERAGE` (`OLSInfluence` contours) per ARCHITECTURE §42 influence group.

## Self-check (CURSOR_PROMPT §000)
- [x] No fabricated metrics; pytest output pasted verbatim.
- [x] Seed 42; scipy KDE/normal only (no hand-rolled density).
- [x] Thin wrapper; Plotly layout on library coordinates.
- [x] Imports within pinned stack (scipy, plotly, numpy).