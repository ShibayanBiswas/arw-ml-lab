"""F9 ARIMA + CLE/REE metric-fold and density plots."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from labcore.eval.classification.plots import plot_metric_folds
from labcore.eval.regression.plots import (
    plot_metric_folds_ree,
    plot_pct_err_dist,
    plot_target_pred_density,
)
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast

ROOT = Path(__file__).resolve().parents[2]


def test_arima_forecast():
    assert any(m["id"] == "arima" for m in TS_MODEL_CATALOGUE)
    df = pd.read_csv(ROOT / "data" / "samples" / "airline_passengers.csv")
    y = pd.to_numeric(df["Passengers"], errors="coerce").dropna().to_numpy(dtype=float)
    h = 12
    out = forecast("arima", y[:-h], h)
    assert len(out["y_pred"]) == h
    assert np.isfinite(out["y_pred"]).all()


def test_metric_folds_and_ree_density():
    folds = plot_metric_folds({"f1": [0.7, 0.72, 0.68], "mcc": [0.4, 0.45, 0.42]})
    assert folds["id"] == "CLE.P.METRIC_FOLDS"
    ree = plot_metric_folds_ree({"rmse": [1.1, 1.0, 1.2], "mae": [0.8, 0.9, 0.85]})
    assert ree["id"] == "REE.P.METRIC_FOLDS"
    rng = np.random.default_rng(42)
    y = rng.normal(10, 2, 80)
    pred = y + rng.normal(0, 0.5, 80)
    dens = plot_target_pred_density(y, pred)
    assert dens["id"] == "REE.P.TARGET_PRED_DENSITY"
    pct = plot_pct_err_dist(y, pred)
    assert pct["id"] == "REE.P.PCT_ERR_DIST"
    assert pct["numbers"]["n"] == 80
