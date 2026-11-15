"""D2 — Frequency inference — ARCHITECTURE §33.4."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

try:
    import exchange_calendars as xcals
except ImportError:  # pragma: no cover
    xcals = None  # type: ignore[assignment]


def _resolve_time_series(df: pd.DataFrame, d1: dict[str, Any]) -> pd.Series | None:
    acc = d1.get("accepted")
    if not acc:
        return None
    if acc.get("composite_of"):
        ycol, qcol = acc["composite_of"][:2]
        y = pd.to_numeric(df[ycol], errors="coerce")
        q = pd.to_numeric(df[qcol], errors="coerce")
        try:
            composed = pd.PeriodIndex.from_fields(
                year=y.astype("Int64"), quarter=q.astype("Int64")
            ).to_timestamp()
        except Exception:
            composed = pd.to_datetime(
                {
                    "year": y,
                    "month": (q.fillna(1).astype(int) - 1) * 3 + 1,
                    "day": 1,
                },
                errors="coerce",
            )
        return pd.Series(composed, index=df.index, name="__composite_time__")
    col = acc.get("column")
    if col and col in df.columns:
        fmt = acc.get("format")
        s = df[col]
        if pd.api.types.is_datetime64_any_dtype(s):
            return pd.to_datetime(s)
        # Prefer ISO / explicit format; never force dayfirst on YYYY-MM-DD
        text = s.astype(str)
        if text.str.match(r"^\d{4}-\d{2}-\d{2}").mean() >= 0.8:
            return pd.to_datetime(text, errors="coerce")
        if fmt and "%" in str(fmt):
            return pd.to_datetime(text, format=fmt, errors="coerce")
        if fmt == "epoch_s":
            return pd.to_datetime(s, unit="s", errors="coerce")
        if fmt == "excel_serial":
            return pd.to_datetime(s, unit="D", origin="1899-12-30", errors="coerce")
        # Period-like YYYY-MM
        if text.str.match(r"^\d{4}-\d{2}$").mean() >= 0.8:
            return pd.to_datetime(text, format="%Y-%m", errors="coerce")
        return pd.to_datetime(text, errors="coerce", dayfirst=True)
    return None


def _trading_calendar_label(times: pd.Series) -> str | None:
    if xcals is None or times.dropna().empty:
        return None
    t = times.dropna().sort_values().drop_duplicates()
    if len(t) < 10:
        return None
    # daily-ish deltas
    deltas = t.diff().dropna().dt.days
    if deltas.empty:
        return None
    mode = float(deltas.mode().iloc[0]) if not deltas.mode().empty else float(deltas.median())
    if mode not in (1.0, 3.0) and not (0.9 <= mode <= 3.1):
        return None
    weekend_share = float(t.dt.dayofweek.isin([5, 6]).mean())
    if weekend_share > 0.05:
        return None
    start, end = t.iloc[0].normalize(), t.iloc[-1].normalize()
    best_name = None
    best_hit = -1.0
    # Prefer India exchanges when ties are close (NIFTY / lab default locale)
    scores: dict[str, float] = {}
    for cal_name in ("XNSE", "XBOM", "XNYS"):
        try:
            cal = xcals.get_calendar(cal_name)
            sessions = cal.sessions_in_range(start, end)
            sess = pd.DatetimeIndex(sessions).tz_localize(None)
            if len(sess) == 0:
                continue
            observed = pd.DatetimeIndex(t.dt.normalize().unique())
            hit = float(len(observed.intersection(sess)) / max(len(observed), 1))
            scores[cal_name] = hit
            if hit > best_hit:
                best_hit = hit
                best_name = cal_name
        except Exception:
            continue
    if scores:
        # Lab default locale Asia/Kolkata — prefer XNSE when within 5pp of best
        india_name = "XNSE" if scores.get("XNSE", 0) >= scores.get("XBOM", 0) else "XBOM"
        india = scores.get(india_name, 0.0)
        if india >= 0.80 and (best_hit - india) <= 0.05:
            best_name = india_name
            best_hit = india
    if best_name and best_hit >= 0.85:
        return f"trading days ({best_name})"
    return "B"


def _seasonality_candidates(series: pd.Series, freq_alias: str | None) -> list[float]:
    from statsmodels.tsa.stattools import acf

    out: list[float] = []
    table = {
        "H": [24.0, 168.0],
        "h": [24.0, 168.0],
        "D": [7.0, 365.25],
        "B": [5.0, 21.0, 252.0],
        "trading": [5.0, 21.0, 252.0],
        "W": [52.18],
        "M": [12.0],
        "MS": [12.0],
        "ME": [12.0],
        "Q": [4.0],
        "QS": [4.0],
        "QE": [4.0],
    }
    raw = freq_alias or "D"
    if "trading" in str(raw).lower():
        key = "trading"
    elif str(raw).upper().startswith("QS") or str(raw).upper().startswith("QE") or str(raw).upper().startswith("Q"):
        key = "QS" if "S" in str(raw).upper() else ("QE" if "E" in str(raw).upper() else "Q")
        if key not in table:
            key = "Q"
    elif str(raw).upper().startswith("MS") or str(raw).upper() in {"M", "ME"}:
        key = "MS" if str(raw).upper().startswith("MS") else ("ME" if str(raw).upper() == "ME" else "M")
    elif str(raw).upper().startswith("H"):
        key = "H"
    else:
        key = str(raw)
    if key in table:
        base = table[key]
    elif key and key[0] in table:
        base = table.get(key[0], [])
    else:
        base = table.get(key, [7.0, 365.25])
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 24:
        return list(base)[:2]
    try:
        nlags = min(len(s) // 2 - 1, 400)
        ac = acf(s, nlags=nlags, fft=True)
        for m in base:
            mi = int(round(m))
            if 1 <= mi < len(ac) and ac[mi] > 0.1 and len(s) >= 2 * m:
                out.append(float(m))
        if not out:
            out = [float(x) for x in base if len(s) >= 2 * x][:3]
    except Exception:
        out = list(base)[:2]
    return out


def infer_frequency(df: pd.DataFrame, d1: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    times = _resolve_time_series(df, d1)
    if times is None or times.notna().sum() < 3:
        return {
            "alias": None,
            "regularity": 0.0,
            "calendar": None,
            "seasonal_periods": [],
            "confidence": 0.0,
            "reasons": ["no_time_index"],
        }

    t = times.dropna().sort_values()
    entity = (d1.get("entity") or {}).get("column")
    if entity and entity in df.columns:
        # use first entity group for freq
        g = df.loc[times.notna()].groupby(entity, sort=False)
        first = next(iter(g.groups))
        idx = g.groups[first]
        t = times.loc[idx].dropna().sort_values()

    uniq = t.drop_duplicates()
    sample = uniq.iloc[:10_000]
    freq = None
    try:
        freq = pd.infer_freq(sample)
    except Exception:
        freq = None

    deltas = sample.diff().dropna()
    if deltas.empty:
        regularity = 0.0
        mode_delta = None
    else:
        # mode of timedelta
        secs = deltas.dt.total_seconds()
        mode_delta = float(secs.mode().iloc[0]) if not secs.mode().empty else float(secs.median())
        tol = max(abs(mode_delta) * 0.01, 1.0)
        regularity = float((np.abs(secs - mode_delta) <= tol).mean())

    calendar = None
    alias = freq
    if mode_delta is not None:
        day = 86400.0
        if alias is None:
            if abs(mode_delta - 3600) < 120 or (60 <= mode_delta <= 3600 and mode_delta % 60 == 0 and mode_delta < day):
                if abs(mode_delta - 3600) < 120:
                    alias = "H"
                else:
                    alias = "H" if mode_delta >= 1800 else "T"
            elif abs(mode_delta - day) < 3600 or abs(mode_delta - 3 * day) < 3600:
                alias = "D"
            elif abs(mode_delta - 7 * day) < day:
                alias = "W"
            elif 25 * day <= mode_delta <= 35 * day:
                alias = "MS"
            elif 85 * day <= mode_delta <= 100 * day:
                alias = "QS"
        # hourly override when infer_freq failed but deltas are ~1h
        if alias is None and 3000 <= mode_delta <= 4200:
            alias = "H"
        if (alias is None or str(alias).upper() in {"D", "H"}) and 3000 <= mode_delta <= 4200:
            alias = "H"
        # Normalise pandas lowercase aliases
        if isinstance(alias, str) and alias in {"h", "H"}:
            alias = "H"
        if isinstance(alias, str) and alias.upper().startswith("Q"):
            # QS-OCT etc. → QS for seasonality / horizon
            if "Q" in alias.upper():
                pass

    trading = _trading_calendar_label(uniq)
    if trading:
        alias = trading
        calendar = trading

    if regularity < 0.6:
        reasons = ["irregular_suggest_resample"]
    else:
        reasons = [f"regularity={regularity:.2f}"]

    # target-like numeric for seasonality (ids/continuous/discrete all OK)
    target_like = None
    for name, meta in profile["columns"].items():
        if meta.get("semantic_type") in {"continuous", "numeric_discrete", "id"}:
            if name == (d1.get("accepted") or {}).get("column"):
                continue
            if pd.api.types.is_numeric_dtype(df[name]):
                target_like = name
                break
    if target_like is None:
        for name in df.columns:
            if pd.api.types.is_numeric_dtype(df[name]):
                target_like = name
                break
    seasonal = (
        _seasonality_candidates(df[target_like], alias) if target_like else []
    )
    # Always include catalogue defaults for the alias when empty
    if not seasonal and alias:
        seasonal = _seasonality_candidates(
            pd.Series(dtype=float), alias
        ) or []

    if isinstance(alias, str):
        if alias.lower() == "h":
            alias = "H"
        elif alias.lower() == "t" or alias.lower() == "min":
            alias = "T"

    conf = min(1.0, 0.5 + 0.5 * regularity) if alias else 0.2
    return {
        "alias": alias,
        "regularity": float(regularity),
        "calendar": calendar,
        "seasonal_periods": seasonal,
        "n_missing_timestamps": None,
        "first": str(uniq.iloc[0]) if len(uniq) else None,
        "last": str(uniq.iloc[-1]) if len(uniq) else None,
        "confidence": conf,
        "reasons": reasons,
    }
