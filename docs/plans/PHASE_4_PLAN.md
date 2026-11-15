# Phase 4 — Time Series thin + deploy sync

Approved plan: `phase_4_ts_thin_f3fcda0f`.

## Locked decisions

1. Thin ACs: HorizonGuard ≥20 cases; DS22 h_max=24 + SARIMA MASE &lt; SeasonalNaive + Ljung-Box p&gt;0.05; DS23 h_max≤9 + seasonal disabled; h&gt;h_max → 422.
2. Libraries: statsforecast SeasonalNaive, statsmodels SARIMAX/STL/Ljung-Box.
3. Canonical HorizonGuard in `labcore/timeseries/`; intake wraps it.
4. Deploy: sole `arw-ml-lab`; push + READY + STOP.

## Out of scope → 4-cont / 4A

Full F1–F54, DS24 coverage, DS28 GPU, §35 catalogues.
