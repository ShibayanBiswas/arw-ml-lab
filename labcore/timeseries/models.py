"""Thin TS forecasters — statsforecast SeasonalNaive + statsmodels SARIMAX."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd

from labcore.timeseries.horizon_guard import sarima_allowed, seasonal_allowed

ModelKey = Literal[
    "seasonal_naive",
    "sarima_airline",
    "sarima",
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
    "dynamic_optimized_theta",
    "mstl",
    "adida",
    "tsb",
    "croston_sba",
    "ucm_local_level",
    "ucm_local_linear_trend",
    "optimized_theta",
    "seasonal_ses_optimized",
    "mfles",
    "tbats",
    "auto_tbats",
    "arima",
    "arima_fourier",
    "var",
    "vecm",
    "varmax",
    "sarimax",
    "auto_mfles",
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


def forecast_sarima(
    y_train: np.ndarray,
    h: int,
    *,
    m: int = 12,
    order: tuple[int, int, int] = (0, 1, 1),
    seasonal_order: tuple[int, int, int, int] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """F10 — SARIMA (p,d,q)(P,D,Q)m via statsmodels ``SARIMAX``.

    Returns (point forecast, in-sample residuals after fit).
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    if seasonal_order is None:
        seasonal_order = (0, 1, 1, m)
    n = len(y_train)
    ok, reason = sarima_allowed(n, h, m=m, order=order, seasonal_order=seasonal_order)
    if not ok:
        raise ValueError(f"sarima gate: {reason}")
    ok_seas, reason_seas = seasonal_allowed(n, float(seasonal_order[3] or m), h)
    if not ok_seas:
        raise ValueError(f"sarima seasonal gate: {reason_seas}")
    y = np.asarray(y_train, dtype=float)
    model = SARIMAX(
        y,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    fitted = model.fit(disp=False)
    pred = np.asarray(fitted.forecast(h), dtype=float)
    resid = np.asarray(fitted.resid, dtype=float)
    return pred, resid


def forecast_sarima_airline(
    y_train: np.ndarray,
    h: int,
    *,
    m: int = 12,
) -> tuple[np.ndarray, np.ndarray]:
    """SARIMA(0,1,1)(0,1,1)m — classic airline preset (delegates to F10)."""
    return forecast_sarima(
        y_train,
        h,
        m=m,
        order=(0, 1, 1),
        seasonal_order=(0, 1, 1, m),
    )


def forecast_sarimax(
    y_train: np.ndarray,
    h: int,
    *,
    m: int = 12,
    exog: np.ndarray | None = None,
    exog_future: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """F11 — SARIMAX with future-known exog (default: linear time index)."""
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    if not ok:
        raise ValueError(f"sarimax seasonal gate: {reason}")
    y = np.asarray(y_train, dtype=float)
    n = len(y)
    if exog is None:
        exog = np.arange(n, dtype=float).reshape(-1, 1)
    else:
        exog = np.asarray(exog, dtype=float)
        if exog.ndim == 1:
            exog = exog.reshape(-1, 1)
    if exog_future is None:
        exog_future = np.arange(n, n + h, dtype=float).reshape(-1, 1)
    else:
        exog_future = np.asarray(exog_future, dtype=float)
        if exog_future.ndim == 1:
            exog_future = exog_future.reshape(-1, 1)
    model = SARIMAX(
        y,
        exog=exog,
        order=(0, 1, 1),
        seasonal_order=(0, 1, 1, m),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    fitted = model.fit(disp=False)
    pred = np.asarray(fitted.forecast(h, exog=exog_future), dtype=float)
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


def forecast_dynamic_optimized_theta(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F14 — DynamicOptimizedTheta via statsforecast."""
    from statsforecast.models import DynamicOptimizedTheta

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    season_length = m if ok else 1
    _ = reason
    return _sf_point_forecast(y_train, h, DynamicOptimizedTheta(season_length=season_length))


def forecast_adida(y_train: np.ndarray, h: int) -> np.ndarray:
    """F25 — ADIDA via statsforecast."""
    from statsforecast.models import ADIDA

    return _sf_point_forecast(y_train, h, ADIDA())


def forecast_tsb(
    y_train: np.ndarray,
    h: int,
    *,
    alpha_d: float = 0.2,
    alpha_p: float = 0.2,
) -> np.ndarray:
    """F25 — TSB intermittent demand."""
    from statsforecast.models import TSB

    return _sf_point_forecast(y_train, h, TSB(alpha_d=alpha_d, alpha_p=alpha_p))


def forecast_croston_sba(y_train: np.ndarray, h: int) -> np.ndarray:
    """F25 — CrostonSBA."""
    from statsforecast.models import CrostonSBA

    return _sf_point_forecast(y_train, h, CrostonSBA())


def forecast_mstl(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F17 — MSTL with AutoETS trend forecaster."""
    from statsforecast.models import MSTL, AutoETS

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    if not ok:
        raise ValueError(f"mstl seasonal gate: {reason}")
    return _sf_point_forecast(
        y_train,
        h,
        MSTL(season_length=[m], trend_forecaster=AutoETS(model="ZZN")),
    )


def forecast_optimized_theta(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F14 — OptimizedTheta via statsforecast."""
    from statsforecast.models import OptimizedTheta

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    season_length = m if ok else 1
    _ = reason
    return _sf_point_forecast(y_train, h, OptimizedTheta(season_length=season_length))


def forecast_seasonal_ses_optimized(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F5/F7 — SeasonalExponentialSmoothingOptimized."""
    from statsforecast.models import SeasonalExponentialSmoothingOptimized

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    if not ok:
        raise ValueError(f"seasonal_ses_optimized gate: {reason}")
    return _sf_point_forecast(y_train, h, SeasonalExponentialSmoothingOptimized(season_length=m))


def forecast_mfles(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F18 — MFLES via statsforecast (fixed hyperparams for CI speed)."""
    from statsforecast.models import MFLES

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    season_length = m if ok else None
    _ = reason
    return _sf_point_forecast(
        y_train, h, MFLES(season_length=season_length, max_rounds=25, changepoints=False)
    )


def forecast_auto_mfles(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F18 — AutoMFLES via statsforecast (small n_windows for CI)."""
    from statsforecast.models import AutoMFLES

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    season_length = m if ok else None
    _ = reason
    test_size = max(h, m if season_length else h)
    return _sf_point_forecast(
        y_train,
        h,
        AutoMFLES(test_size=test_size, season_length=season_length, n_windows=2),
    )


def forecast_tbats(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F16 — TBATS via statsforecast (constrained flags for CI speed)."""
    from statsforecast.models import TBATS

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    if not ok:
        raise ValueError(f"tbats gate: {reason}")
    return _sf_point_forecast(
        y_train,
        h,
        TBATS(
            season_length=m,
            use_boxcox=False,
            use_trend=True,
            use_damped_trend=False,
            use_arma_errors=False,
        ),
    )


def forecast_auto_tbats(y_train: np.ndarray, h: int, *, m: int = 12) -> np.ndarray:
    """F16 — AutoTBATS via statsforecast (arma errors off for CI speed)."""
    from statsforecast.models import AutoTBATS

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    if not ok:
        raise ValueError(f"auto_tbats gate: {reason}")
    return _sf_point_forecast(
        y_train,
        h,
        AutoTBATS(season_length=m, use_arma_errors=False),
    )


def forecast_arima(
    y_train: np.ndarray,
    h: int,
    *,
    order: tuple[int, int, int] = (1, 1, 1),
) -> np.ndarray:
    """F9 — non-seasonal ARIMA via statsforecast."""
    from statsforecast.models import ARIMA

    return _sf_point_forecast(y_train, h, ARIMA(order=order))


def forecast_arima_fourier(
    y_train: np.ndarray,
    h: int,
    *,
    m: int = 12,
    k: int = 2,
    order: tuple[int, int, int] = (1, 1, 1),
) -> np.ndarray:
    """F13 — ARIMA with Fourier seasonal terms (utilsforecast + statsforecast)."""
    from statsforecast import StatsForecast
    from statsforecast.models import ARIMA
    from utilsforecast.feature_engineering import fourier

    ok, reason = seasonal_allowed(len(y_train), float(m), h)
    if not ok:
        raise ValueError(f"arima_fourier gate: {reason}")
    df = to_nixtla_df(y_train)
    train, x_future = fourier(df, freq=1, season_length=m, k=k, h=h)
    sf = StatsForecast(models=[ARIMA(order=order)], freq=1, n_jobs=1)
    fc = sf.forecast(df=train, h=h, X_df=x_future)
    col = [c for c in fc.columns if c not in ("unique_id", "ds")][0]
    return np.asarray(fc[col], dtype=float)


def forecast_var(
    y_train: np.ndarray,
    h: int,
    *,
    maxlags: int = 5,
) -> dict[str, Any]:
    """F21 — statsmodels VAR (multivariate; y_train shape (n, k), k≥2)."""
    from statsmodels.tsa.api import VAR

    Y = np.asarray(y_train, dtype=float)
    if Y.ndim != 2 or Y.shape[1] < 2:
        raise ValueError("var requires y_train with shape (n, k), k≥2")
    if Y.shape[0] < maxlags + 10:
        raise ValueError(f"var needs n ≥ maxlags+10 (got n={Y.shape[0]}, maxlags={maxlags})")
    model = VAR(Y)
    fitted = model.fit(maxlags=maxlags, ic="aic")
    lag_order = int(fitted.k_ar)
    pred = np.asarray(fitted.forecast(Y[-lag_order:], steps=h), dtype=float)
    return {
        "y_pred": pred,
        "resid": np.asarray(fitted.resid, dtype=float),
        "lag_order": lag_order,
        "aic": float(fitted.aic),
    }


def forecast_vecm(
    y_train: np.ndarray,
    h: int,
    *,
    k_ar_diff: int = 2,
) -> dict[str, Any]:
    """F23 — statsmodels VECM with Johansen trace rank selection."""
    from statsmodels.tsa.vector_ar.vecm import VECM, select_coint_rank

    Y = np.asarray(y_train, dtype=float)
    if Y.ndim != 2 or Y.shape[1] < 2:
        raise ValueError("vecm requires y_train with shape (n, k), k≥2")
    if Y.shape[0] < k_ar_diff + 30:
        raise ValueError(f"vecm needs n ≥ k_ar_diff+30 (got n={Y.shape[0]})")
    rank_res = select_coint_rank(Y, det_order=0, k_ar_diff=k_ar_diff, method="trace", signif=0.05)
    coint_rank = max(int(rank_res.rank), 1)
    model = VECM(Y, k_ar_diff=k_ar_diff, coint_rank=coint_rank, deterministic="ci")
    fitted = model.fit()
    pred = np.asarray(fitted.predict(steps=h), dtype=float)
    return {
        "y_pred": pred,
        "resid": np.asarray(fitted.resid, dtype=float),
        "coint_rank": coint_rank,
        "k_ar_diff": k_ar_diff,
    }


def forecast_varmax(
    y_train: np.ndarray,
    h: int,
    *,
    order: tuple[int, int] = (1, 0),
) -> dict[str, Any]:
    """F22 — statsmodels VARMAX (constrained order for CI speed)."""
    from statsmodels.tsa.statespace.varmax import VARMAX

    Y = np.asarray(y_train, dtype=float)
    if Y.ndim != 2 or Y.shape[1] < 2:
        raise ValueError("varmax requires y_train with shape (n, k), k≥2")
    if Y.shape[0] < 40:
        raise ValueError(f"varmax needs n ≥ 40 (got n={Y.shape[0]})")
    model = VARMAX(Y, order=order, trend="c")
    fitted = model.fit(disp=False, maxiter=50)
    pred = np.asarray(fitted.forecast(steps=h), dtype=float)
    return {
        "y_pred": pred,
        "resid": np.asarray(fitted.resid, dtype=float),
        "order": order,
        "aic": float(fitted.aic),
    }


def forecast_ucm_local_level(y_train: np.ndarray, h: int) -> tuple[np.ndarray, np.ndarray]:
    """F19 — UnobservedComponents local level (statsmodels)."""
    from statsmodels.tsa.statespace.structural import UnobservedComponents

    y = np.asarray(y_train, dtype=float)
    model = UnobservedComponents(y, level="local level")
    fitted = model.fit(disp=False)
    pred = np.asarray(fitted.forecast(h), dtype=float)
    resid = np.asarray(fitted.resid, dtype=float)
    return pred, resid


def forecast_ucm_local_linear_trend(y_train: np.ndarray, h: int) -> tuple[np.ndarray, np.ndarray]:
    """F19/F26 — UnobservedComponents local linear trend (Kalman state-space)."""
    from statsmodels.tsa.statespace.structural import UnobservedComponents

    y = np.asarray(y_train, dtype=float)
    model = UnobservedComponents(y, level="local linear trend")
    fitted = model.fit(disp=False)
    pred = np.asarray(fitted.forecast(h), dtype=float)
    resid = np.asarray(fitted.resid, dtype=float)
    return pred, resid


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
    endog: np.ndarray | None = None,
) -> dict[str, Any]:
    if key == "seasonal_naive":
        yhat = forecast_seasonal_naive(y_train, h, m=m)
        return {"key": key, "y_pred": yhat, "resid": None}
    if key == "sarima_airline":
        yhat, resid = forecast_sarima_airline(y_train, h, m=m)
        return {"key": key, "y_pred": yhat, "resid": resid}
    if key == "sarima":
        yhat, resid = forecast_sarima(y_train, h, m=m)
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
    if key == "dynamic_optimized_theta":
        return {
            "key": key,
            "y_pred": forecast_dynamic_optimized_theta(y_train, h, m=m),
            "resid": None,
        }
    if key == "mstl":
        return {"key": key, "y_pred": forecast_mstl(y_train, h, m=m), "resid": None}
    if key == "adida":
        return {"key": key, "y_pred": forecast_adida(y_train, h), "resid": None}
    if key == "tsb":
        return {"key": key, "y_pred": forecast_tsb(y_train, h), "resid": None}
    if key == "croston_sba":
        return {"key": key, "y_pred": forecast_croston_sba(y_train, h), "resid": None}
    if key == "ucm_local_level":
        yhat, resid = forecast_ucm_local_level(y_train, h)
        return {"key": key, "y_pred": yhat, "resid": resid}
    if key == "ucm_local_linear_trend":
        yhat, resid = forecast_ucm_local_linear_trend(y_train, h)
        return {"key": key, "y_pred": yhat, "resid": resid}
    if key == "optimized_theta":
        return {
            "key": key,
            "y_pred": forecast_optimized_theta(y_train, h, m=m),
            "resid": None,
        }
    if key == "seasonal_ses_optimized":
        return {
            "key": key,
            "y_pred": forecast_seasonal_ses_optimized(y_train, h, m=m),
            "resid": None,
        }
    if key == "mfles":
        return {"key": key, "y_pred": forecast_mfles(y_train, h, m=m), "resid": None}
    if key == "tbats":
        return {"key": key, "y_pred": forecast_tbats(y_train, h, m=m), "resid": None}
    if key == "auto_tbats":
        return {"key": key, "y_pred": forecast_auto_tbats(y_train, h, m=m), "resid": None}
    if key == "arima":
        return {"key": key, "y_pred": forecast_arima(y_train, h), "resid": None}
    if key == "arima_fourier":
        return {
            "key": key,
            "y_pred": forecast_arima_fourier(y_train, h, m=m),
            "resid": None,
        }
    if key == "var":
        Y = endog if endog is not None else y_train
        out = forecast_var(Y, h)
        return {
            "key": key,
            "y_pred": out["y_pred"],
            "resid": out["resid"],
            "extra": {"lag_order": out["lag_order"], "aic": out["aic"]},
        }
    if key == "vecm":
        Y = endog if endog is not None else y_train
        out = forecast_vecm(Y, h)
        return {
            "key": key,
            "y_pred": out["y_pred"],
            "resid": out["resid"],
            "extra": {"coint_rank": out["coint_rank"], "k_ar_diff": out["k_ar_diff"]},
        }
    if key == "varmax":
        Y = endog if endog is not None else y_train
        out = forecast_varmax(Y, h)
        return {
            "key": key,
            "y_pred": out["y_pred"],
            "resid": out["resid"],
            "extra": {"order": out["order"], "aic": out["aic"]},
        }
    if key == "sarimax":
        yhat, resid = forecast_sarimax(y_train, h, m=m)
        return {"key": key, "y_pred": yhat, "resid": resid}
    if key == "auto_mfles":
        return {"key": key, "y_pred": forecast_auto_mfles(y_train, h, m=m), "resid": None}
    raise ValueError(f"unknown model key: {key}")


TS_MODEL_CATALOGUE: list[dict[str, str]] = [
    {"id": "seasonal_naive", "library": "statsforecast", "name": "Seasonal Naive"},
    {"id": "sarima_airline", "library": "statsmodels", "name": "SARIMA airline"},
    {"id": "sarima", "library": "statsmodels", "name": "SARIMA"},
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
    {"id": "dynamic_optimized_theta", "library": "statsforecast", "name": "DynamicOptimizedTheta"},
    {"id": "mstl", "library": "statsforecast", "name": "MSTL"},
    {"id": "adida", "library": "statsforecast", "name": "ADIDA"},
    {"id": "tsb", "library": "statsforecast", "name": "TSB"},
    {"id": "croston_sba", "library": "statsforecast", "name": "CrostonSBA"},
    {"id": "ucm_local_level", "library": "statsmodels", "name": "UCM local level"},
    {
        "id": "ucm_local_linear_trend",
        "library": "statsmodels",
        "name": "UCM local linear trend",
    },
    {"id": "optimized_theta", "library": "statsforecast", "name": "OptimizedTheta"},
    {
        "id": "seasonal_ses_optimized",
        "library": "statsforecast",
        "name": "SeasonalSESOptimized",
    },
    {"id": "mfles", "library": "statsforecast", "name": "MFLES"},
    {"id": "tbats", "library": "statsforecast", "name": "TBATS"},
    {"id": "auto_tbats", "library": "statsforecast", "name": "AutoTBATS"},
    {"id": "arima", "library": "statsforecast", "name": "ARIMA"},
    {
        "id": "arima_fourier",
        "library": "statsforecast+utilsforecast",
        "name": "ARIMA+Fourier",
    },
    {"id": "var", "library": "statsmodels", "name": "VAR"},
    {"id": "vecm", "library": "statsmodels", "name": "VECM"},
    {"id": "varmax", "library": "statsmodels", "name": "VARMAX"},
    {"id": "sarimax", "library": "statsmodels", "name": "SARIMAX"},
    {"id": "auto_mfles", "library": "statsforecast", "name": "AutoMFLES"},
]
