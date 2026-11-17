"""Financial labelling suitability — FS1–FS20 (ARCHITECTURE §37)."""

from labcore.suitability.fs_checks import run_suitability
from labcore.suitability.fs_checks import compute_suitability_parameter_grid
from labcore.suitability.plots import plot_label_balance, plot_suitability_grid

__all__ = [
    "compute_suitability_parameter_grid",
    "plot_label_balance",
    "plot_suitability_grid",
    "run_suitability",
]
