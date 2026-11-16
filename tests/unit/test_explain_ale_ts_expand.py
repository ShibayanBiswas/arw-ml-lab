"""ALE (PyALE) + expanded statsforecast TS models (oneshot-c13)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from labcore.explain.ale import ale_1d
from labcore.timeseries.models import TS_MODEL_CATALOGUE, forecast
from lightgbm import LGBMRegressor
from sklearn.datasets import make_regression


def test_ale_1d_centred_mean_near_zero():
    X, y = make_regression(n_samples=240, n_features=5, noise=0.2, random_state=42)
    cols = [f"f{i}" for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=cols)
    model = LGBMRegressor(n_estimators=30, max_depth=3, random_state=42, verbose=-1)
    model.fit(df, y)
    out = ale_1d(model, df, "f0", grid_size=12, seed=42)
    assert out["id"] == "EXPLAIN.T.ALE"
    assert len(out["grid"]) == len(out["effect"])
    centred = np.asarray(out["effect_centred"], dtype=float)
    assert abs(float(np.mean(centred))) < 1e-9


def test_ts_catalogue_includes_new_keys():
    ids = {m["id"] for m in TS_MODEL_CATALOGUE}
    assert {"auto_arima", "naive", "seasonal_window_average"} <= ids


def test_naive_and_seasonal_window_forecast_shapes():
    rng = np.random.default_rng(42)
    # seasonal pattern
    t = np.arange(60)
    y = np.sin(2 * np.pi * t / 12) + rng.normal(0, 0.05, size=60)
    h = 6
    naive = forecast("naive", y, h)
    assert naive["y_pred"].shape == (h,)
    assert np.allclose(naive["y_pred"], y[-1])
    swa = forecast("seasonal_window_average", y, h, m=12)
    assert swa["y_pred"].shape == (h,)
    assert np.all(np.isfinite(swa["y_pred"]))


def test_auto_arima_forecast_finite():
    rng = np.random.default_rng(42)
    y = np.cumsum(rng.normal(0, 1, size=48)) + 10
    out = forecast("auto_arima", y, h=4, m=12)
    assert out["y_pred"].shape == (4,)
    assert np.all(np.isfinite(out["y_pred"]))


def test_garch11_variance_forecast():
    rng = np.random.default_rng(42)
    # Simulated returns with mild clustering
    e = rng.normal(0, 1, size=400)
    r = np.zeros(400)
    sig = 1.0
    for t in range(1, 400):
        sig = np.sqrt(0.1 + 0.1 * r[t - 1] ** 2 + 0.8 * sig**2)
        r[t] = sig * e[t]
    out = forecast("garch11", r, h=5)
    assert out["y_pred"].shape == (5,)
    assert "extra" in out and "sigma" in out["extra"]
    assert np.all(np.isfinite(out["extra"]["sigma"]))
    assert np.all(out["extra"]["sigma"] > 0)
