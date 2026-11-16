"""F19 UnobservedComponents local level."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast

ROOT = Path(__file__).resolve().parents[2]


def test_ucm_local_level_forecast():
    assert any(m["id"] == "ucm_local_level" for m in TS_MODEL_CATALOGUE)
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    y = pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)
    h = 12
    out = forecast("ucm_local_level", y[:-h], h)
    assert len(out["y_pred"]) == h
    assert np.isfinite(out["y_pred"]).all()
    assert out["resid"] is not None


def test_optimized_theta_and_seasonal_ses():
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    y = pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)
    h = 12
    train = y[:-h]
    for key in ("optimized_theta", "seasonal_ses_optimized"):
        out = forecast(key, train, h, m=12)  # type: ignore[arg-type]
        assert len(out["y_pred"]) == h
        assert np.isfinite(out["y_pred"]).all(), key
