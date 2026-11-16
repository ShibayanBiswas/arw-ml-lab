"""F20 Prophet — skipped when prophet not installed (CI unit job omits prophet)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("prophet")

from labcore.timeseries.models import forecast

ROOT = Path(__file__).resolve().parents[2]


def test_prophet_forecast_shape():
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    y = pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)
    h = 12
    out = forecast("prophet", y[:-h], h)
    assert len(out["y_pred"]) == h
    assert np.isfinite(out["y_pred"]).all()
