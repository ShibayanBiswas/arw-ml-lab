"""Financial labelling suitability — FS1–FS20 (ARCHITECTURE §37)."""

from labcore.suitability.fs_checks import compute_suitability_parameter_grid, run_suitability
from labcore.suitability.plots import (
    plot_daily_volatility,
    plot_holding_period_distribution,
    plot_label_balance,
    plot_min_ffd,
    plot_price_cusum,
    plot_sadf,
    plot_sample_barriers,
    plot_suitability_grid,
    plot_trendscan,
    plot_uniqueness_concurrency,
)

__all__ = [
    "compute_suitability_parameter_grid",
    "plot_daily_volatility",
    "plot_holding_period_distribution",
    "plot_label_balance",
    "plot_min_ffd",
    "plot_price_cusum",
    "plot_sadf",
    "plot_sample_barriers",
    "plot_trendscan",
    "plot_suitability_grid",
    "plot_uniqueness_concurrency",
    "run_suitability",
]
