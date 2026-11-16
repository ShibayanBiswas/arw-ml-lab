"""F16 TBATS + F18 MFLES catalogue wrappers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast

ROOT = Path(__file__).resolve().parents[2]


def test_catalogue_has_mfles_tbats():
    ids = {m["id"] for m in TS_MODEL_CATALOGUE}
    assert "mfles" in ids
    assert "tbats" in ids


def test_mfles_and_tbats_forecast():
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    y = pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)
    h = 12
    train = y[:-h]
    for key in ("mfles", "tbats"):
        out = forecast(key, train, h, m=12)  # type: ignore[arg-type]
        assert len(out["y_pred"]) == h
        assert np.isfinite(out["y_pred"]).all(), key
