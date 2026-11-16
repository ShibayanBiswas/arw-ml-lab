"""Expanded TS forecasters (statsforecast HistoricAverage / Theta / AutoETS)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast

ROOT = Path(__file__).resolve().parents[2]


def _airline_y() -> np.ndarray:
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    return pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)


def test_catalogue_has_five():
    ids = {m["id"] for m in TS_MODEL_CATALOGUE}
    assert ids >= {
        "seasonal_naive",
        "sarima_airline",
        "historic_average",
        "theta",
        "auto_ets",
    }


def test_historic_average_and_theta():
    y = _airline_y()
    h = 12
    ha = forecast("historic_average", y[:-h], h)
    th = forecast("theta", y[:-h], h, m=12)
    assert len(ha["y_pred"]) == h
    assert len(th["y_pred"]) == h
    assert np.isfinite(ha["y_pred"]).all()
    assert np.isfinite(th["y_pred"]).all()
