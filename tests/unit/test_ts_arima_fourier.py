"""F13 ARIMA with Fourier exogenous terms."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast

ROOT = Path(__file__).resolve().parents[2]


def test_arima_fourier_forecast():
    assert any(m["id"] == "arima_fourier" for m in TS_MODEL_CATALOGUE)
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    y = pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)
    h = 12
    out = forecast("arima_fourier", y[:-h], h, m=12)
    assert len(out["y_pred"]) == h
    assert np.isfinite(out["y_pred"]).all()
