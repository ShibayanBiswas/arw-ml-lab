"""Thin TS forecasters — statsforecast SeasonalNaive + statsmodels SARIMAX."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd

from labcore.timeseries.horizon_guard import seasonal_allowed

ModelKey = Literal[
    "seasonal_naive",
    "sarima_airline",
    "historic_average",
    "theta",
    "auto_ets",
    "auto_arima",
    "naive",
    "seasonal_window_average",
]


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


def forecast_historic_average(y_train: np.ndarray, h: int) -> np.ndarray:
    """Global mean forecaster via statsforecast HistoricAverage."""
    from statsforecast import StatsForecast
    from statsforecast.models import HistoricAverage

    df = to_nixtla_df(y_train)
    sf = StatsForecast(models=[HistoricAverage()], freq=1, n_jobs=1)
    fc = sf.forecast(df=df, h=h)
    col = [c for c in fc.columns if c not in ("unique_id", "ds")][0]
    return np.asarray(fc[col], dtype=float)


def forecast_theta(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """Theta method via statsforecast (season_length=m)."""
    from statsforecast import StatsForecast
    from statsforecast.models import Theta

    df = to_nixtla_df(y_train)
    sf = StatsForecast(models=[Theta(season_length=m)], freq=1, n_jobs=1)
    fc = sf.forecast(df=df, h=h)
    col = [c for c in fc.columns if c not in ("unique_id", "ds")][0]
    return np.asarray(fc[col], dtype=float)


def forecast_auto_ets(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """AutoETS via statsforecast."""
    from statsforecast import StatsForecast
    from statsforecast.models import AutoETS

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    season_length = m if ok else 1
    _ = reason
    df = to_nixtla_df(y_train)
    sf = StatsForecast(models=[AutoETS(season_length=season_length)], freq=1, n_jobs=1)
    fc = sf.forecast(df=df, h=h)
    col = [c for c in fc.columns if c not in ("unique_id", "ds")][0]
    return np.asarray(fc[col], dtype=float)


def forecast_auto_arima(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """AutoARIMA via statsforecast (seasonal when HorizonGuard allows)."""
    from statsforecast import StatsForecast
    from statsforecast.models import AutoARIMA

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    season_length = m if ok else 1
    _ = reason
    df = to_nixtla_df(y_train)
    sf = StatsForecast(
        models=[AutoARIMA(season_length=season_length)],
        freq=1,
        n_jobs=1,
    )
    fc = sf.forecast(df=df, h=h)
    col = [c for c in fc.columns if c not in ("unique_id", "ds")][0]
    return np.asarray(fc[col], dtype=float)


def forecast_naive(y_train: np.ndarray, h: int) -> np.ndarray:
    """Last-value naive via statsforecast Naive."""
    from statsforecast import StatsForecast
    from statsforecast.models import Naive

    df = to_nixtla_df(y_train)
    sf = StatsForecast(models=[Naive()], freq=1, n_jobs=1)
    fc = sf.forecast(df=df, h=h)
    col = [c for c in fc.columns if c not in ("unique_id", "ds")][0]
    return np.asarray(fc[col], dtype=float)


def forecast_seasonal_window_average(
    y_train: np.ndarray,
    h: int,
    *,
    m: int = 12,
    window_size: int = 2,
) -> np.ndarray:
    """SeasonalWindowAverage via statsforecast."""
    from statsforecast import StatsForecast
    from statsforecast.models import SeasonalWindowAverage

    if len(y_train) < m * window_size:
        raise ValueError(
            f"seasonal_window_average needs n≥m·window ({len(y_train)}<{m * window_size})"
        )
    df = to_nixtla_df(y_train)
    sf = StatsForecast(
        models=[SeasonalWindowAverage(season_length=m, window_size=window_size)],
        freq=1,
        n_jobs=1,
    )
    fc = sf.forecast(df=df, h=h)
    col = [c for c in fc.columns if c not in ("unique_id", "ds")][0]
    return np.asarray(fc[col], dtype=float)


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
    if key == "historic_average":
        yhat = forecast_historic_average(y_train, h)
        return {"key": key, "y_pred": yhat, "resid": None}
    if key == "theta":
        yhat = forecast_theta(y_train, h, m=m)
        return {"key": key, "y_pred": yhat, "resid": None}
    if key == "auto_ets":
        yhat = forecast_auto_ets(y_train, h, m=m)
        return {"key": key, "y_pred": yhat, "resid": None}
    if key == "auto_arima":
        yhat = forecast_auto_arima(y_train, h, m=m)
        return {"key": key, "y_pred": yhat, "resid": None}
    if key == "naive":
        yhat = forecast_naive(y_train, h)
        return {"key": key, "y_pred": yhat, "resid": None}
    if key == "seasonal_window_average":
        yhat = forecast_seasonal_window_average(y_train, h, m=m)
        return {"key": key, "y_pred": yhat, "resid": None}
    raise ValueError(f"unknown model key: {key}")


TS_MODEL_CATALOGUE: list[dict[str, str]] = [
    {"id": "seasonal_naive", "library": "statsforecast", "name": "Seasonal Naive"},
    {"id": "sarima_airline", "library": "statsmodels", "name": "SARIMA airline"},
    {"id": "historic_average", "library": "statsforecast", "name": "Historic Average"},
    {"id": "theta", "library": "statsforecast", "name": "Theta"},
    {"id": "auto_ets", "library": "statsforecast", "name": "AutoETS"},
    {"id": "auto_arima", "library": "statsforecast", "name": "AutoARIMA"},
    {"id": "naive", "library": "statsforecast", "name": "Naive"},
    {"id": "seasonal_window_average", "library": "statsforecast", "name": "SeasonalWindowAverage"},
]
