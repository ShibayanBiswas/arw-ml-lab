"""F60 — pmdarima auto_arima (skipped when pmdarima not installed; CI unit job omits ts.txt)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("pmdarima")

from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast, forecast_pmdarima_auto_arima

ROOT = Path(__file__).resolve().parents[2]


def _airline_train() -> tuple[np.ndarray, int]:
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    y = pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)
    h = 12
    return y[:-h], h


def test_catalogue_includes_pmdarima_auto_arima_f60():
    ids = {m["id"] for m in TS_MODEL_CATALOGUE}
    assert "pmdarima_auto_arima" in ids
    row = next(m for m in TS_MODEL_CATALOGUE if m["id"] == "pmdarima_auto_arima")
    assert row["library"] == "pmdarima"


def test_pmdarima_auto_arima_finite_airline():
    train, h = _airline_train()
    yhat, resid = forecast_pmdarima_auto_arima(train, h, m=12, seed=42)
    assert len(yhat) == h
    assert np.isfinite(yhat).all()
    assert len(resid) == len(train)
    assert np.isfinite(resid).all()


def test_forecast_dispatch_pmdarima_auto_arima():
    train, h = _airline_train()
    out = forecast("pmdarima_auto_arima", train, h, m=12)
    assert out["key"] == "pmdarima_auto_arima"
    assert len(out["y_pred"]) == h
    assert np.isfinite(out["y_pred"]).all()
    assert out["resid"] is not None
    assert len(out["resid"]) == len(train)