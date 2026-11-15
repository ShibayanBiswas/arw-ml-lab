"""Thin HorizonGuard re-export — ARCHITECTURE §20 (canonical: labcore.timeseries)."""

from __future__ import annotations

from labcore.timeseries.horizon_guard import compute_horizon_guard, horizon_guard, norm_freq

__all__ = ["horizon_guard", "compute_horizon_guard", "norm_freq"]
