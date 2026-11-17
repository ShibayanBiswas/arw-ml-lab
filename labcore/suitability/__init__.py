"""Financial labelling suitability — FS1–FS20 (ARCHITECTURE §37)."""

from labcore.suitability.fs_checks import run_suitability
from labcore.suitability.plots import plot_label_balance

__all__ = ["plot_label_balance", "run_suitability"]
