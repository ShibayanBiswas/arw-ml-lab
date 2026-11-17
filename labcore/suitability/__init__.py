"""Financial labelling suitability — FS1–FS20 (ARCHITECTURE §37)."""

from labcore.suitability.fs_checks import compute_suitability_parameter_grid, run_suitability
from labcore.suitability.plots import (
    plot_daily_volatility,
    plot_label_balance,
    plot_sample_barriers,
    plot_suitability_grid,
)

__all__ = [
    "compute_suitability_parameter_grid",
    "plot_daily_volatility",
    "plot_label_balance",
    "plot_sample_barriers",
    "plot_suitability_grid",
    "run_suitability",
]
