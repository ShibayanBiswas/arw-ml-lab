"""F14 DynamicOptimizedTheta + F17 MSTL."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast

ROOT = Path(__file__).resolve().parents[2]


def _airline_y() -> np.ndarray:
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    return pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)


def test_catalogue_has_mstl_and_dotheta():
    ids = {m["id"] for m in TS_MODEL_CATALOGUE}
    assert "mstl" in ids
    assert "dynamic_optimized_theta" in ids


def test_dynamic_optimized_theta_and_mstl():
    y = _airline_y()
    h = 12
    train = y[:-h]
    # airline has enough length for seasonal gate at m=12, h=12
    out_t = forecast("dynamic_optimized_theta", train, h, m=12)
    assert len(out_t["y_pred"]) == h
    assert np.isfinite(out_t["y_pred"]).all()
    out_m = forecast("mstl", train, h, m=12)
    assert len(out_m["y_pred"]) == h
    assert np.isfinite(out_m["y_pred"]).all()
