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
    "garch11",
    "random_walk_drift",
    "holt",
    "holt_winters",
    "auto_ces",
    "croston_classic",
    "window_average",
    "auto_theta",
    "prophet",
    "croston_optimized",
    "imapa",
    "ses_optimized",
]


def _sf_point_forecast(y_train: np.ndarray, h: int, model: Any) -> np.ndarray:
    from statsforecast import StatsForecast

    df = to_nixtla_df(y_train)
    sf = StatsForecast(models=[model], freq=1, n_jobs=1)
    fc = sf.forecast(df=df, h=h)
    col = [c for c in fc.columns if c not in ("unique_id", "ds")][0]
    return np.asarray(fc[col], dtype=float)


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


def forecast_random_walk_drift(y_train: np.ndarray, h: int) -> np.ndarray:
    """F3 — RandomWalkWithDrift via statsforecast."""
    from statsforecast.models import RandomWalkWithDrift

    return _sf_point_forecast(y_train, h, RandomWalkWithDrift())


def forecast_holt(y_train: np.ndarray, h: int) -> np.ndarray:
    """F6 — Holt linear trend via statsforecast."""
    from statsforecast.models import Holt

    return _sf_point_forecast(y_train, h, Holt())


def forecast_holt_winters(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F7 — HoltWinters; requires seasonal gate n ≥ 2m+h."""
    from statsforecast.models import HoltWinters

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    if not ok:
        raise ValueError(f"holt_winters seasonal gate: {reason}")
    return _sf_point_forecast(y_train, h, HoltWinters(season_length=m))


def forecast_auto_ces(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F15 — AutoCES via statsforecast."""
    from statsforecast.models import AutoCES

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    season_length = m if ok else 1
    _ = reason
    return _sf_point_forecast(y_train, h, AutoCES(season_length=season_length))


def forecast_croston_classic(y_train: np.ndarray, h: int) -> np.ndarray:
    """F25 — CrostonClassic (intermittent demand)."""
    from statsforecast.models import CrostonClassic

    return _sf_point_forecast(y_train, h, CrostonClassic())


def forecast_window_average(y_train: np.ndarray, h: int, *, window_size: int = 12) -> np.ndarray:
    """F4 — WindowAverage via statsforecast."""
    from statsforecast.models import WindowAverage

    if len(y_train) < window_size:
        raise ValueError(f"window_average needs n≥window ({len(y_train)}<{window_size})")
    return _sf_point_forecast(y_train, h, WindowAverage(window_size=window_size))


def forecast_auto_theta(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F14 — AutoTheta via statsforecast."""
    from statsforecast.models import AutoTheta

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    season_length = m if ok else 1
    _ = reason
    return _sf_point_forecast(y_train, h, AutoTheta(season_length=season_length))


def forecast_croston_optimized(y_train: np.ndarray, h: int) -> np.ndarray:
    """F25 — CrostonOptimized via statsforecast."""
    from statsforecast.models import CrostonOptimized

    return _sf_point_forecast(y_train, h, CrostonOptimized())


def forecast_imapa(y_train: np.ndarray, h: int) -> np.ndarray:
    """F25 — IMAPA intermittent demand via statsforecast."""
    from statsforecast.models import IMAPA

    return _sf_point_forecast(y_train, h, IMAPA())


def forecast_ses_optimized(y_train: np.ndarray, h: int) -> np.ndarray:
    """F5 — SimpleExponentialSmoothingOptimized."""
    from statsforecast.models import SimpleExponentialSmoothingOptimized

    return _sf_point_forecast(y_train, h, SimpleExponentialSmoothingOptimized())


def forecast_prophet(y_train: np.ndarray, h: int, *, freq: str = "D") -> np.ndarray:
    """F20 — Prophet (requires daily-like synthetic calendar index)."""
    from prophet import Prophet

    y = np.asarray(y_train, dtype=float)
    ds = pd.date_range("2000-01-01", periods=len(y), freq=freq)
    df = pd.DataFrame({"ds": ds, "y": y})
    m = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
    )
    m.fit(df)
    future = m.make_future_dataframe(periods=h, freq=freq)
    fc = m.predict(future)
    return np.asarray(fc["yhat"].iloc[-h:], dtype=float)


def forecast_garch11(y_train: np.ndarray, h: int) -> dict[str, Any]:
    """GARCH(1,1) variance forecast via ``arch`` (returns + conditional σ)."""
    from arch import arch_model

    y = np.asarray(y_train, dtype=float)
    # Prefer returns if levels look like prices
    if np.nanmin(y) > 0 and np.nanmax(y) / max(np.nanmin(y), 1e-12) > 2:
        r = 100.0 * np.diff(np.log(y))
    else:
        r = y.copy()
    if len(r) < 50:
        raise ValueError(f"garch11 needs ≥50 returns (got {len(r)})")
    am = arch_model(r, vol="Garch", p=1, q=1, mean="Constant", rescale=False)
    fitted = am.fit(disp="off")
    fc = fitted.forecast(horizon=h)
    var = np.asarray(fc.variance.values[-1], dtype=float)
    sigma = np.sqrt(np.maximum(var, 0.0))
    mu = float(fitted.params.get("mu", 0.0))
    # Point path: mean + 0 (variance path is the primary artefact)
    yhat = np.full(h, mu, dtype=float)
    return {
        "y_pred": yhat,
        "sigma": sigma,
        "variance": var.tolist(),
        "params": {k: float(v) for k, v in fitted.params.items()},
        "resid": np.asarray(fitted.resid, dtype=float),
    }


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
    if key == "garch11":
        out = forecast_garch11(y_train, h)
        return {"key": key, "y_pred": out["y_pred"], "resid": out["resid"], "extra": out}
    if key == "random_walk_drift":
        return {"key": key, "y_pred": forecast_random_walk_drift(y_train, h), "resid": None}
    if key == "holt":
        return {"key": key, "y_pred": forecast_holt(y_train, h), "resid": None}
    if key == "holt_winters":
        return {"key": key, "y_pred": forecast_holt_winters(y_train, h, m=m), "resid": None}
    if key == "auto_ces":
        return {"key": key, "y_pred": forecast_auto_ces(y_train, h, m=m), "resid": None}
    if key == "croston_classic":
        return {"key": key, "y_pred": forecast_croston_classic(y_train, h), "resid": None}
    if key == "window_average":
        return {"key": key, "y_pred": forecast_window_average(y_train, h), "resid": None}
    if key == "auto_theta":
        return {"key": key, "y_pred": forecast_auto_theta(y_train, h, m=m), "resid": None}
    if key == "prophet":
        return {"key": key, "y_pred": forecast_prophet(y_train, h), "resid": None}
    if key == "croston_optimized":
        return {"key": key, "y_pred": forecast_croston_optimized(y_train, h), "resid": None}
    if key == "imapa":
        return {"key": key, "y_pred": forecast_imapa(y_train, h), "resid": None}
    if key == "ses_optimized":
        return {"key": key, "y_pred": forecast_ses_optimized(y_train, h), "resid": None}
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
    {"id": "garch11", "library": "arch", "name": "GARCH(1,1)"},
    {"id": "random_walk_drift", "library": "statsforecast", "name": "RandomWalkWithDrift"},
    {"id": "holt", "library": "statsforecast", "name": "Holt"},
    {"id": "holt_winters", "library": "statsforecast", "name": "HoltWinters"},
    {"id": "auto_ces", "library": "statsforecast", "name": "AutoCES"},
    {"id": "croston_classic", "library": "statsforecast", "name": "CrostonClassic"},
    {"id": "window_average", "library": "statsforecast", "name": "WindowAverage"},
    {"id": "auto_theta", "library": "statsforecast", "name": "AutoTheta"},
    {"id": "prophet", "library": "prophet", "name": "Prophet"},
    {"id": "croston_optimized", "library": "statsforecast", "name": "CrostonOptimized"},
    {"id": "imapa", "library": "statsforecast", "name": "IMAPA"},
    {"id": "ses_optimized", "library": "statsforecast", "name": "SESOptimized"},
]
