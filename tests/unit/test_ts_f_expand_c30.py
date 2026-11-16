"""oneshot-c30 — additional F* statsforecast wrappers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast

ROOT = Path(__file__).resolve().parents[2]


def _airline_y() -> np.ndarray:
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    return pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)


def test_catalogue_includes_f3_f6_f15_f25():
    ids = {m["id"] for m in TS_MODEL_CATALOGUE}
    assert ids >= {
        "random_walk_drift",
        "holt",
        "auto_ces",
        "croston_classic",
        "window_average",
        "auto_theta",
        "croston_optimized",
        "imapa",
        "ses_optimized",
    }


def test_rwd_holt_window_shapes():
    y = _airline_y()
    h = 12
    train = y[:-h]
    for key in (
        "random_walk_drift",
        "holt",
        "window_average",
        "auto_theta",
        "croston_classic",
        "croston_optimized",
        "imapa",
        "ses_optimized",
    ):
        out = forecast(key, train, h, m=12)  # type: ignore[arg-type]
        assert len(out["y_pred"]) == h
        assert np.isfinite(out["y_pred"]).all(), key
