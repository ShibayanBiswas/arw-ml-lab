"""Thin TS forecasters — statsforecast SeasonalNaive + statsmodels SARIMAX."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd

from labcore.timeseries.horizon_guard import seasonal_allowed

ModelKey = Literal["seasonal_naive", "sarima_airline"]


def to_nixtla_df(
    y: pd.Series | np.ndarray,
    *,
    ds: pd.DatetimeIndex | pd.Index | None = None,
    unique_id: str = "series",
) -> pd.DataFrame:
    y = pd.Series(y).astype(float).reset_index(drop=True)
    if ds is None:
        ds_vals: Any = np.arange(len(y))
    else:
        ds_vals = pd.Index(ds)
        if len(ds_vals) != len(y):
            raise ValueError("ds length must match y")
    return pd.DataFrame({"unique_id": unique_id, "ds": ds_vals, "y": y.to_numpy()})


def forecast_seasonal_naive(
    y_train: np.ndarray,
    h: int,
    *,
    m: int = 12,
) -> np.ndarray:
    """Seasonal naive via statsforecast (needs n ≥ m; ETS 2m+h gate not applied)."""
    from statsforecast import StatsForecast
    from statsforecast.models import SeasonalNaive

    if len(y_train) < m:
        raise ValueError(f"seasonal_naive needs n≥m ({len(y_train)}<{m})")
    df = to_nixtla_df(y_train)
    sf = StatsForecast(models=[SeasonalNaive(season_length=m)], freq=1, n_jobs=1)
    fc = sf.forecast(df=df, h=h)
    col = [c for c in fc.columns if c not in ("unique_id", "ds")][0]
    return np.asarray(fc[col], dtype=float)


def forecast_sarima_airline(
    y_train: np.ndarray,
    h: int,
    *,
    m: int = 12,
) -> tuple[np.ndarray, np.ndarray]:
    """SARIMA(0,1,1)(0,1,1)m — classic airline model (statsmodels SARIMAX).

    Returns (point forecast, in-sample residuals after fit).
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    if not ok:
        raise ValueError(f"sarima seasonal gate: {reason}")
    y = np.asarray(y_train, dtype=float)
    model = SARIMAX(
        y,
        order=(0, 1, 1),
        seasonal_order=(0, 1, 1, m),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    fitted = model.fit(disp=False)
    pred = np.asarray(fitted.forecast(h), dtype=float)
    resid = np.asarray(fitted.resid, dtype=float)
    return pred, resid


def forecast(
    key: ModelKey,
    y_train: np.ndarray,
    h: int,
    *,
    m: int = 12,
) -> dict[str, Any]:
    if key == "seasonal_naive":
        yhat = forecast_seasonal_naive(y_train, h, m=m)
        return {"key": key, "y_pred": yhat, "resid": None}
    if key == "sarima_airline":
        yhat, resid = forecast_sarima_airline(y_train, h, m=m)
        return {"key": key, "y_pred": yhat, "resid": resid}
    raise ValueError(f"unknown model key: {key}")
