"""F10 — generic SARIMA via statsmodels SARIMAX."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from labcore.timeseries.models import (
    TS_MODEL_CATALOGUE,
    forecast,
    forecast_sarima,
    forecast_sarima_airline,
)

ROOT = Path(__file__).resolve().parents[2]


def _airline_train() -> np.ndarray:
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    y = pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)
    h = 12
    return y[:-h], h


def test_catalogue_includes_sarima_f10():
    ids = {m["id"] for m in TS_MODEL_CATALOGUE}
    assert "sarima" in ids


def test_sarima_default_matches_airline_preset():
    train, h = _airline_train()
    m = 12
    yhat_f10, resid_f10 = forecast_sarima(train, h, m=m)
    yhat_preset, resid_preset = forecast_sarima_airline(train, h, m=m)
    np.testing.assert_allclose(yhat_f10, yhat_preset, rtol=1e-9, atol=1e-9)
    np.testing.assert_allclose(resid_f10, resid_preset, rtol=1e-9, atol=1e-9)


def test_forecast_dispatch_sarima():
    train, h = _airline_train()
    out = forecast("sarima", train, h, m=12)
    assert out["key"] == "sarima"
    assert len(out["y_pred"]) == h
    assert np.isfinite(out["y_pred"]).all()
    assert out["resid"] is not None
    assert len(out["resid"]) == len(train)


def test_sarima_gate_rejects_short_series():
    with pytest.raises(ValueError, match="sarima gate"):
        forecast_sarima(np.arange(20.0), h=12, m=12)