"""F16 AutoTBATS catalogue wrapper."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast

ROOT = Path(__file__).resolve().parents[2]


def test_catalogue_has_auto_tbats():
    assert any(m["id"] == "auto_tbats" for m in TS_MODEL_CATALOGUE)


def test_auto_tbats_forecast():
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    y = pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)
    h = 12
    train = y[:-h]
    out = forecast("auto_tbats", train, h, m=12)  # type: ignore[arg-type]
    assert out["key"] == "auto_tbats"
    assert len(out["y_pred"]) == h
    assert np.isfinite(out["y_pred"]).all()