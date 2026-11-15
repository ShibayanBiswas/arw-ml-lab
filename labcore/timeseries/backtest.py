"""Rolling-origin expanding-window backtest (Phase 4 thin)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from labcore.timeseries.horizon_guard import compute_horizon_guard
from labcore.timeseries.metrics import ljung_box_residuals, point_metrics
from labcore.timeseries.models import ModelKey, forecast


def rolling_origin_backtest(
    y: pd.Series | np.ndarray,
    *,
    h: int,
    w: int = 4,
    m: int = 12,
    freq: str = "MS",
    models: list[ModelKey] | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Expanding-window rolling origin: W test blocks of length h.

    Train sizes grow; origins place the last W non-overlapping (or stepping by h)
    holdouts before the series end. Seed recorded for provenance (deterministic).
    """
    _ = seed
    y_arr = np.asarray(pd.Series(y).astype(float).to_numpy(), dtype=float)
    n = len(y_arr)
    guard = compute_horizon_guard(n, freq, m=float(m), w=w, h_request=h)
    if h > guard["h_max"]:
        return {
            "ok": False,
            "error": "h_exceeds_h_max",
            "horizon": guard,
            "reject_reasons": guard.get("reject_reasons") or [f"h={h} > h_max={guard['h_max']}"],
        }

    models = models or ["seasonal_naive", "sarima_airline"]
    # Origins: end indices of each test window (exclusive). Last window ends at n.
    # train = y[:origin], test = y[origin:origin+h]
    origins: list[int] = []
    for i in range(w):
        # Place windows ending at n, n-h, ... (expanding train)
        origin = n - (w - i) * h
        if origin < max(int(2 * m), 24):
            continue
        origins.append(origin)
    if not origins:
        return {"ok": False, "error": "no_valid_origins", "horizon": guard}

    per_model: dict[str, Any] = {}
    for key in models:
        fold_metrics: list[dict[str, float]] = []
        all_true: list[float] = []
        all_pred: list[float] = []
        last_resid: np.ndarray | None = None
        errors: list[str] = []
        for origin in origins:
            y_tr = y_arr[:origin]
            y_te = y_arr[origin : origin + h]
            if len(y_te) < h:
                continue
            try:
                out = forecast(key, y_tr, h, m=m)
            except Exception as exc:  # noqa: BLE001 — collect per-fold
                errors.append(f"origin={origin}: {exc}")
                continue
            yhat = np.asarray(out["y_pred"], dtype=float)[:h]
            fold_metrics.append(point_metrics(y_te, yhat, y_tr, m=m))
            all_true.extend(y_te.tolist())
            all_pred.extend(yhat.tolist())
            if out.get("resid") is not None:
                last_resid = np.asarray(out["resid"], dtype=float)

        if not fold_metrics:
            per_model[key] = {"ok": False, "errors": errors, "folds": []}
            continue
        keys0 = fold_metrics[0]
        mean = {k: float(np.nanmean([fm[k] for fm in fold_metrics])) for k in keys0}
        std = {
            k: float(np.nanstd([fm[k] for fm in fold_metrics], ddof=1))
            if len(fold_metrics) > 1
            else 0.0
            for k in keys0
        }
        entry: dict[str, Any] = {
            "ok": True,
            "n_folds": len(fold_metrics),
            "folds": fold_metrics,
            "cv_mean": mean,
            "cv_std": std,
            "errors": errors,
            "origins": origins,
        }
        if last_resid is not None:
            entry["ljung_box"] = ljung_box_residuals(last_resid, season_m=m)
        per_model[key] = entry

    # Soft Step 3: empirical h* from pooled SARIMA abs errors vs seasonal naive scale
    h_star = _empirical_h_star(y_arr, per_model, m=m, h=h)

    return {
        "ok": True,
        "n": n,
        "h": h,
        "w": w,
        "m": m,
        "seed": seed,
        "horizon": guard,
        "origins": origins,
        "models": per_model,
        "h_star": h_star,
    }


def _empirical_h_star(
    y: np.ndarray,
    per_model: dict[str, Any],
    *,
    m: int,
    h: int,
) -> int | None:
    """Largest j with MASE_j < 1 if per-horizon MASE available; else None."""
    # Thin: use overall MASE — if SARIMA mean MASE < 1, h*=h else reduce
    sar = per_model.get("sarima_airline") or {}
    if not sar.get("ok"):
        return None
    mase = (sar.get("cv_mean") or {}).get("mase")
    if mase is None or not np.isfinite(mase):
        return None
    if mase < 1.0:
        return h
    return max(1, h // 2)
