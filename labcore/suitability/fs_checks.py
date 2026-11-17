"""FS financial labelling suitability (ARCHITECTURE §37).

Implemented: FS1–FS20. FS16–FS18 use thin AFML/statsmodels/scipy/ruptures
equivalents (`labcore.finance.sadf`, `trendscan`, MA-cross primary); TradingLab
parity contract tests remain deferred until ``vendor/tradinglab`` lands.
FS7/FS9–FS13 likewise use AFML-equivalent thin formulas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
import pandas as pd

Status = Literal["PASS", "WARN", "FAIL", "INFO", "DEFERRED"]


@dataclass
class FSResult:
    code: str
    status: Status
    message: str
    details: dict[str, Any] = field(default_factory=dict)


def _detect_price_col(df: pd.DataFrame) -> str | None:
    for cand in ("close", "Close", "adj_close", "Adj Close", "price", "Price", "PX_LAST"):
        if cand in df.columns:
            return cand
    # numeric column with name hint
    for c in df.columns:
        cl = str(c).lower()
        if any(k in cl for k in ("close", "price", "px")) and pd.api.types.is_numeric_dtype(df[c]):
            return str(c)
    return None


def _detect_returns_col(df: pd.DataFrame) -> str | None:
    for cand in ("return", "returns", "ret", "logret", "log_return"):
        for c in df.columns:
            if str(c).lower() == cand:
                return str(c)
    return None


def check_fs1_time_index(df: pd.DataFrame, time_col: str | None) -> FSResult:
    """FS1 — sorted, unique, parseable time index."""
    if time_col and time_col in df.columns:
        raw = df[time_col]
    elif isinstance(df.index, pd.DatetimeIndex):
        raw = df.index.to_series()
    else:
        return FSResult(
            "FS1",
            "FAIL",
            "no parseable time index or time column",
            {"time_col": time_col},
        )
    parsed = pd.to_datetime(raw, errors="coerce", utc=False)
    n_bad = int(parsed.isna().sum())
    if n_bad > 0 and n_bad == len(parsed):
        return FSResult("FS1", "FAIL", "time values unparseable", {"n_bad": n_bad})
    if n_bad / max(len(parsed), 1) > 0.005:
        return FSResult(
            "FS1",
            "FAIL",
            f"{n_bad} unparseable timestamps",
            {"n_bad": n_bad},
        )
    clean = parsed.dropna()
    n_dup = int(clean.duplicated().sum())
    dup_pct = n_dup / max(len(clean), 1)
    sorted_ok = bool(clean.is_monotonic_increasing)
    if not sorted_ok:
        return FSResult(
            "FS1",
            "FAIL",
            "time index not sorted ascending",
            {"n_dup": n_dup, "sorted": False},
        )
    if dup_pct > 0.005:
        return FSResult(
            "FS1",
            "FAIL",
            f"duplicate timestamps ({dup_pct:.2%})",
            {"n_dup": n_dup},
        )
    if n_dup > 0:
        return FSResult(
            "FS1",
            "WARN",
            f"{n_dup} duplicate timestamps (<0.5%) — auto-drop recommended",
            {"n_dup": n_dup},
        )
    return FSResult("FS1", "PASS", "time index sorted, unique, parseable")


def check_fs2_price_or_returns(df: pd.DataFrame) -> FSResult:
    price = _detect_price_col(df)
    rets = _detect_returns_col(df)
    if price is not None:
        return FSResult("FS2", "PASS", f"price series found: '{price}'", {"price_col": price})
    if rets is not None:
        return FSResult(
            "FS2",
            "WARN",
            f"only returns found: '{rets}' (index reconstructed)",
            {"returns_col": rets},
        )
    return FSResult("FS2", "FAIL", "neither price nor returns series detected")


def check_fs3_positivity(df: pd.DataFrame, price_col: str | None) -> FSResult:
    if price_col is None or price_col not in df.columns:
        rets = _detect_returns_col(df)
        if rets and rets in df.columns:
            r = pd.to_numeric(df[rets], errors="coerce").dropna()
            extreme = int((r.abs() > 0.5).sum())
            if extreme > 3:
                return FSResult(
                    "FS3",
                    "WARN",
                    f"{extreme} extreme |return| > 50% jumps",
                    {"n_extreme": extreme},
                )
            return FSResult("FS3", "PASS", "returns sanity ok (no price path)")
        return FSResult("FS3", "FAIL", "no price/returns for positivity check")
    px = pd.to_numeric(df[price_col], errors="coerce")
    n_nonpos = int((px.dropna() <= 0).sum())
    if n_nonpos:
        return FSResult(
            "FS3",
            "FAIL",
            f"{n_nonpos} non-positive prices",
            {"n_nonpos": n_nonpos},
        )
    ret_series = px.pct_change(fill_method=None).dropna()
    extreme = int((ret_series.abs() > 0.5).sum())
    if extreme > 3:
        return FSResult(
            "FS3",
            "WARN",
            f"{extreme} extreme daily jumps (>50%) — possible splits",
            {"n_extreme": extreme},
        )
    return FSResult("FS3", "PASS", "prices positive; jump sanity ok")


def check_fs4_ohlcv(df: pd.DataFrame) -> FSResult:
    cols_lower = {str(c).lower(): c for c in df.columns}
    ohlc = ["open", "high", "low", "close"]
    present = [k for k in ohlc if k in cols_lower]
    has_vol = "volume" in cols_lower or "vol" in cols_lower
    if len(present) == 4:
        o = pd.to_numeric(df[cols_lower["open"]], errors="coerce")
        h = pd.to_numeric(df[cols_lower["high"]], errors="coerce")
        low = pd.to_numeric(df[cols_lower["low"]], errors="coerce")
        c = pd.to_numeric(df[cols_lower["close"]], errors="coerce")
        bad = (h < low) | (c > h) | (c < low) | (o > h) | (o < low)
        bad_pct = float(bad.mean()) if len(bad) else 0.0
        if bad_pct > 0.01:
            return FSResult(
                "FS4",
                "FAIL",
                f"inconsistent OHLC in {bad_pct:.1%} of rows",
                {"bad_pct": bad_pct, "volume": has_vol},
            )
        msg = "full OHLCV consistent" if has_vol else "full OHLC consistent (no volume)"
        return FSResult("FS4", "PASS", msg, {"volume": has_vol})
    if "close" in cols_lower:
        return FSResult(
            "FS4",
            "WARN",
            "close only — high/low barriers and Parkinson vol unavailable",
            {"present": present},
        )
    return FSResult("FS4", "FAIL", "no OHLC columns detected", {"present": present})


def check_fs5_frequency(df: pd.DataFrame, time_col: str | None) -> FSResult:
    if time_col and time_col in df.columns:
        ts = pd.to_datetime(df[time_col], errors="coerce").dropna()
    elif isinstance(df.index, pd.DatetimeIndex):
        ts = pd.Series(df.index)
    else:
        return FSResult("FS5", "FAIL", "cannot assess frequency without time index")
    if len(ts) < 3:
        return FSResult("FS5", "FAIL", "too few timestamps for frequency check")
    ts = ts.sort_values()
    freq = pd.infer_freq(ts)
    diffs = ts.diff().dropna()
    if diffs.empty:
        return FSResult("FS5", "FAIL", "irregular — no diffs")
    median_delta = diffs.median()
    # missing share vs regular grid at median delta
    expected = 1 + int((ts.iloc[-1] - ts.iloc[0]) / median_delta) if median_delta else len(ts)
    missing_pct = max(0.0, 1.0 - len(ts) / max(expected, 1))
    if freq is None and missing_pct > 0.10:
        return FSResult(
            "FS5",
            "FAIL",
            f"irregular without calendar; ~{missing_pct:.0%} gaps",
            {"freq": None, "missing_pct": missing_pct},
        )
    if missing_pct > 0.10:
        return FSResult(
            "FS5",
            "FAIL",
            f">{missing_pct:.0%} missing expected bars",
            {"freq": freq, "missing_pct": missing_pct},
        )
    if missing_pct >= 0.02:
        return FSResult(
            "FS5",
            "WARN",
            f"{missing_pct:.1%} missing expected bars",
            {"freq": freq, "missing_pct": missing_pct},
        )
    return FSResult(
        "FS5",
        "PASS",
        f"frequency ok (infer_freq={freq})",
        {"freq": freq, "missing_pct": missing_pct},
    )


def check_fs6_length(df: pd.DataFrame) -> FSResult:
    """FS6 — number of bars n (≥1000 PASS, 500–999 WARN, <500 FAIL)."""
    n = int(len(df))
    if n >= 1000:
        return FSResult("FS6", "PASS", f"n={n} bars", {"n": n})
    if n >= 500:
        return FSResult("FS6", "WARN", f"n={n} bars (500–999)", {"n": n})
    return FSResult("FS6", "FAIL", f"n={n} bars (<500)", {"n": n})


def compute_daily_ewma_vol(
    df: pd.DataFrame,
    price_col: str | None = None,
    *,
    span: int = 100,
) -> dict[str, Any]:
    """Close-to-close EWMA σ (AFML ``get_daily_vol`` equivalent) for FS7 / FS.P.VOL."""
    col = price_col or _detect_price_col(df)
    if col is None or col not in df.columns:
        return {"ok": False, "reason": "no price column for EWMA vol"}
    px = pd.to_numeric(df[col], errors="coerce")
    rets = px.pct_change(fill_method=None)
    min_periods = max(span // 2, 10)
    vol = rets.ewm(span=span, min_periods=min_periods).std()
    warm = vol.iloc[span:] if len(vol) > span else vol.dropna()
    if len(warm) == 0:
        return {
            "ok": False,
            "reason": "insufficient bars for EWMA vol warm-up",
            "price_col": col,
            "span": span,
        }
    non_null = float(warm.notna().mean())
    positive = float((warm.fillna(0) > 0).mean())
    return {
        "ok": True,
        "price_col": col,
        "span": span,
        "min_periods": min_periods,
        "volatility": vol,
        "non_null_share": non_null,
        "positive_share": positive,
        "median_vol": float(warm.median()) if warm.notna().any() else None,
    }


def check_fs7_daily_vol(df: pd.DataFrame, price_col: str | None, *, span: int = 100) -> FSResult:
    """FS7 — EWMA volatility estimable (AFML ``get_daily_vol`` equivalent).

    Uses ``pandas.Series.ewm(span=span).std()`` on close-to-close returns.
    PASS if ≥95% non-null after warm-up and vol > 0; WARN 80–95%; else FAIL.
    """
    comp = compute_daily_ewma_vol(df, price_col, span=span)
    if not comp.get("ok"):
        reason = comp.get("reason", "no price column for EWMA vol")
        return FSResult("FS7", "FAIL", reason, {"span": span})
    non_null = float(comp["non_null_share"])
    positive = float(comp["positive_share"])
    details = {
        "span": span,
        "non_null_share": non_null,
        "positive_share": positive,
        "median_vol": comp.get("median_vol"),
    }
    if non_null >= 0.95 and positive >= 0.95:
        return FSResult("FS7", "PASS", f"EWMA vol ok (non-null={non_null:.1%})", details)
    if non_null >= 0.80 and positive >= 0.80:
        return FSResult("FS7", "WARN", f"EWMA vol thin (non-null={non_null:.1%})", details)
    return FSResult("FS7", "FAIL", f"EWMA vol not estimable (non-null={non_null:.1%})", details)


def compute_cusum_filter_events(
    df: pd.DataFrame,
    price_col: str | None = None,
    *,
    vol_span: int = 100,
    h_mult: float = 1.0,
    h: float | None = None,
) -> dict[str, Any]:
    """Symmetric CUSUM filter (AFML ch. 2) for FS9 / FS.P.PRICE."""
    col = price_col or _detect_price_col(df)
    if col is None or col not in df.columns:
        return {"ok": False, "reason": "no price column for CUSUM events"}
    px = pd.to_numeric(df[col], errors="coerce")
    valid = px.notna()
    n_valid = int(valid.sum())
    if n_valid < 50:
        return {"ok": False, "reason": "too few prices for CUSUM", "n": n_valid, "price_col": col}
    px_vals = px[valid].to_numpy(dtype=float)
    df_ilocs = np.flatnonzero(valid.to_numpy())
    log_r = np.diff(np.log(px_vals))
    if h is None:
        vol = pd.Series(log_r).ewm(span=vol_span, min_periods=50).std()
        vol_mean = float(vol.dropna().mean())
        if not np.isfinite(vol_mean) or vol_mean <= 0:
            return {
                "ok": False,
                "reason": "CUSUM threshold h not positive",
                "h": vol_mean,
                "price_col": col,
            }
        h_eff = vol_mean * h_mult
    else:
        h_eff = float(h)
        if not np.isfinite(h_eff) or h_eff <= 0:
            return {
                "ok": False,
                "reason": "CUSUM threshold h not positive",
                "h": h_eff,
                "price_col": col,
            }
    events: list[dict[str, Any]] = []
    s_pos = 0.0
    s_neg = 0.0
    for j, r in enumerate(log_r):
        if not np.isfinite(r):
            continue
        s_pos = max(0.0, s_pos + float(r))
        s_neg = min(0.0, s_neg + float(r))
        if s_pos > h_eff:
            events.append(
                {
                    "bar": j,
                    "df_iloc": int(df_ilocs[j]),
                    "direction": 1,
                    "price": float(px_vals[j]),
                }
            )
            s_pos = 0.0
        elif s_neg < -h_eff:
            events.append(
                {
                    "bar": j,
                    "df_iloc": int(df_ilocs[j]),
                    "direction": -1,
                    "price": float(px_vals[j]),
                }
            )
            s_neg = 0.0
    return {
        "ok": True,
        "price_col": col,
        "vol_span": vol_span,
        "h_mult": h_mult,
        "h": h_eff,
        "n_returns": int(len(log_r)),
        "n_events": len(events),
        "events": events,
    }


def check_fs9_event_count(df: pd.DataFrame, price_col: str | None) -> FSResult:
    """FS9 — CUSUM event count with h = mean daily EWMA σ (AFML cusum_filter thin).

    PASS ≥300 events, WARN 100–299, FAIL <100.
    """
    if price_col is None or price_col not in df.columns:
        return FSResult("FS9", "FAIL", "no price column for CUSUM events")
    comp = compute_cusum_filter_events(df, price_col)
    if not comp.get("ok"):
        reason = comp.get("reason", "CUSUM computation failed")
        extra = {k: comp[k] for k in ("n", "h") if k in comp}
        return FSResult("FS9", "FAIL", reason, extra)
    events = int(comp["n_events"])
    h = float(comp["h"])
    details = {"events": events, "h": h, "n_returns": int(comp["n_returns"])}
    if events >= 300:
        return FSResult("FS9", "PASS", f"{events} CUSUM events", details)
    if events >= 100:
        return FSResult("FS9", "WARN", f"{events} CUSUM events (100–299)", details)
    return FSResult("FS9", "FAIL", f"{events} CUSUM events (<100)", details)


PT_SL_GRID: tuple[tuple[int, int], ...] = ((1, 1), (1, 2), (2, 1), (2, 2))
VERTICAL_BARRIER_GRID: tuple[int, ...] = (5, 10, 20)
CUSUM_H_GRID: tuple[float, ...] = (0.5, 1.0, 2.0)


def _cusum_event_starts(log_r: np.ndarray, h: float) -> list[int]:
    """Symmetric CUSUM event bar indices (AFML ch. 2 thin)."""
    s_pos = 0.0
    s_neg = 0.0
    starts: list[int] = []
    for i, r in enumerate(log_r):
        if not np.isfinite(r):
            continue
        s_pos = max(0.0, s_pos + float(r))
        s_neg = min(0.0, s_neg + float(r))
        if s_pos > h:
            starts.append(i)
            s_pos = 0.0
        elif s_neg < -h:
            starts.append(i)
            s_neg = 0.0
    return starts


def _mean_uniqueness_from_spans(spans: list[tuple[int, int]]) -> float | None:
    if len(spans) < 2:
        return None
    n_t = max(t1 for _t0, t1 in spans) + 1
    concurrent = np.zeros(n_t, dtype=float)
    for t0, t1 in spans:
        concurrent[t0 : t1 + 1] += 1.0
    uniques: list[float] = []
    for t0, t1 in spans:
        c = np.maximum(concurrent[t0 : t1 + 1], 1.0)
        uniques.append(float(np.mean(1.0 / c)))
    return float(np.mean(uniques))


def enumerate_trial_tb_events(
    df: pd.DataFrame,
    price_col: str,
    *,
    horizon: int = 5,
    vol_span: int = 100,
    pt_mult: float = 1.0,
    sl_mult: float = 1.0,
    cusum_mult: float | None = None,
) -> dict[str, Any]:
    """Triple-barrier trial events with barrier geometry (FS.P.BARRIERS / §37.6)."""
    if price_col not in df.columns:
        return {"ok": False, "reason": "no price column"}
    px = pd.to_numeric(df[price_col], errors="coerce").dropna()
    if len(px) < 60:
        return {"ok": False, "reason": "too few bars", "n": int(len(px))}
    log_p = np.log(px.to_numpy(dtype=float))
    rets = np.diff(log_p)
    vol = pd.Series(rets).ewm(span=vol_span, min_periods=30).std().to_numpy()
    if cusum_mult is None:
        starts = list(range(len(rets) - 1))
        cusum_h: float | None = None
        n_cusum_events = len(starts)
    else:
        vol_mean = float(pd.Series(rets).ewm(span=100, min_periods=50).std().dropna().mean())
        if not np.isfinite(vol_mean) or vol_mean <= 0:
            return {"ok": False, "reason": "CUSUM threshold not positive"}
        cusum_h = cusum_mult * vol_mean
        starts = _cusum_event_starts(rets, cusum_h)
        n_cusum_events = len(starts)
    events: list[dict[str, Any]] = []
    for i in starts:
        if i >= len(rets) - 1:
            continue
        sigma = vol[i]
        if not np.isfinite(sigma) or sigma <= 0:
            continue
        end_px = min(i + 1 + horizon, len(log_p))
        path = log_p[i + 1 : end_px] - log_p[i]
        if len(path) == 0:
            continue
        upper = pt_mult * sigma
        lower = sl_mult * sigma
        t1 = end_px - 1
        label = 0
        if np.any(path >= upper):
            label = 1
            touch = int(np.argmax(path >= upper))
            t1 = i + 1 + touch
        elif np.any(path <= -lower):
            label = -1
            touch = int(np.argmax(path <= -lower))
            t1 = i + 1 + touch
        t1 = min(t1, len(log_p) - 1)
        entry_price = float(np.exp(log_p[i]))
        events.append(
            {
                "t0": int(i),
                "t1": int(t1),
                "vertical_t": int(end_px - 1),
                "label": int(label),
                "sigma": float(sigma),
                "pt_log": float(upper),
                "sl_log": float(lower),
                "pt_mult": float(pt_mult),
                "sl_mult": float(sl_mult),
                "entry_price": entry_price,
                "pt_price": float(entry_price * np.exp(upper)),
                "sl_price": float(entry_price * np.exp(-lower)),
            }
        )
    return {
        "ok": True,
        "method": "triple_barrier",
        "price_col": price_col,
        "horizon": horizon,
        "vol_span": vol_span,
        "pt_mult": pt_mult,
        "sl_mult": sl_mult,
        "cusum_mult": cusum_mult,
        "cusum_h": cusum_h,
        "n_cusum_events": n_cusum_events,
        "n_labels": len(events),
        "events": events,
    }


def sample_trial_tb_events(
    df: pd.DataFrame,
    price_col: str,
    *,
    horizon: int = 5,
    vol_span: int = 100,
    pt_mult: float = 1.0,
    sl_mult: float = 1.0,
    cusum_mult: float | None = None,
    n_samples: int = 3,
    seed: int = 42,
) -> dict[str, Any]:
    """Representative events for FS.P.BARRIERS (one per label class when possible)."""
    base = enumerate_trial_tb_events(
        df,
        price_col,
        horizon=horizon,
        vol_span=vol_span,
        pt_mult=pt_mult,
        sl_mult=sl_mult,
        cusum_mult=cusum_mult,
    )
    if not base.get("ok"):
        return base
    events = base["events"]
    if not events:
        return {"ok": False, "reason": "no trial labels", "n_cusum_events": base["n_cusum_events"]}
    n_samples = max(1, min(int(n_samples), 6, len(events)))
    rng = np.random.default_rng(seed)
    by_label: dict[int, list[dict[str, Any]]] = {-1: [], 0: [], 1: []}
    for ev in events:
        by_label[ev["label"]].append(ev)
    picked: list[dict[str, Any]] = []
    for lab in (-1, 0, 1):
        pool = by_label[lab]
        if pool:
            picked.append(pool[int(rng.integers(len(pool)))])
    if len(picked) < n_samples:
        rest = [e for e in events if e not in picked]
        order = rng.permutation(len(rest))
        for j in order:
            if len(picked) >= n_samples:
                break
            picked.append(rest[int(j)])
    return {
        **base,
        "seed": seed,
        "n_samples": len(picked[:n_samples]),
        "sampled_events": picked[:n_samples],
    }


def compute_trial_tb_cell(
    df: pd.DataFrame,
    price_col: str,
    *,
    horizon: int = 5,
    vol_span: int = 100,
    pt_mult: float = 1.0,
    sl_mult: float = 1.0,
    cusum_mult: float | None = None,
) -> dict[str, Any]:
    """One triple-barrier trial cell for §37.6 grid / FS10 / FS.P.*."""
    base = enumerate_trial_tb_events(
        df,
        price_col,
        horizon=horizon,
        vol_span=vol_span,
        pt_mult=pt_mult,
        sl_mult=sl_mult,
        cusum_mult=cusum_mult,
    )
    if not base.get("ok"):
        return base
    events = base["events"]
    if not events:
        return {"ok": False, "reason": "no trial labels", "n_cusum_events": base["n_cusum_events"]}
    labels = [int(e["label"]) for e in events]
    spans = [(int(e["t0"]), int(e["t1"])) for e in events]
    n_labels = len(labels)
    counts = {
        -1: int(sum(1 for x in labels if x < 0)),
        0: int(sum(1 for x in labels if x == 0)),
        1: int(sum(1 for x in labels if x > 0)),
    }
    shares = {k: float(v) / n_labels for k, v in counts.items()}
    signed_n = counts[-1] + counts[1]
    minority_signed = (
        float(min(counts[-1], counts[1]) / signed_n) if signed_n > 0 else None
    )
    mean_u = _mean_uniqueness_from_spans(spans)
    n_eff = float(n_labels * mean_u) if mean_u is not None else None
    return {
        "ok": True,
        "method": "triple_barrier",
        "horizon": horizon,
        "vol_span": vol_span,
        "pt_mult": pt_mult,
        "sl_mult": sl_mult,
        "cusum_mult": cusum_mult,
        "cusum_h": base["cusum_h"],
        "n_cusum_events": base["n_cusum_events"],
        "n_labels": n_labels,
        "counts": counts,
        "shares": shares,
        "minority_signed_share": minority_signed,
        "vertical_barrier_share": shares[0],
        "avg_uniqueness": mean_u,
        "n_eff": n_eff,
    }


def compute_trial_tb_label_balance(
    df: pd.DataFrame,
    price_col: str,
    *,
    horizon: int = 5,
    vol_span: int = 100,
) -> dict[str, Any]:
    """Trial triple-barrier labels (±1σ, vertical bars) for FS10 / FS.P.LABEL_BALANCE."""
    return compute_trial_tb_cell(
        df,
        price_col,
        horizon=horizon,
        vol_span=vol_span,
        pt_mult=1.0,
        sl_mult=1.0,
        cusum_mult=None,
    )


def compute_suitability_parameter_grid(
    df: pd.DataFrame,
    price_col: str | None = None,
    *,
    seed: int = 42,
) -> dict[str, Any]:
    """§37.6 — 36 trial labelling cells and default pick (max n_eff, minority ≥ 15%)."""
    _ = seed
    col = price_col or _detect_price_col(df)
    if col is None:
        raise ValueError("no price column for suitability grid")
    cells: list[dict[str, Any]] = []
    for pt_sl in PT_SL_GRID:
        for vertical in VERTICAL_BARRIER_GRID:
            for cusum_mult in CUSUM_H_GRID:
                cell = compute_trial_tb_cell(
                    df,
                    col,
                    horizon=vertical,
                    pt_mult=float(pt_sl[0]),
                    sl_mult=float(pt_sl[1]),
                    cusum_mult=cusum_mult,
                )
                row: dict[str, Any] = {
                    "pt_sl": list(pt_sl),
                    "vertical": vertical,
                    "cusum_mult": cusum_mult,
                }
                if cell.get("ok"):
                    row.update(
                        {
                            "minority_share": cell["minority_signed_share"],
                            "vertical_share": cell["vertical_barrier_share"],
                            "avg_uniqueness": cell["avg_uniqueness"],
                            "n_events": int(cell["n_labels"]),
                            "n_cusum_events": int(cell["n_cusum_events"]),
                            "n_eff": cell["n_eff"],
                        }
                    )
                else:
                    row["error"] = cell.get("reason", "failed")
                cells.append(row)
    eligible = [
        c
        for c in cells
        if c.get("minority_share") is not None and float(c["minority_share"]) >= 0.15
    ]
    pool = eligible if eligible else [c for c in cells if c.get("n_eff") is not None]
    default_cell = (
        max(pool, key=lambda c: float(c.get("n_eff") or 0.0)) if pool else None
    )
    return {
        "price_col": col,
        "n_cells": len(cells),
        "cells": cells,
        "default_cell": default_cell,
        "seed": seed,
    }


def compute_fixed_horizon_label_balance(
    df: pd.DataFrame,
    price_col: str,
    *,
    horizon: int = 5,
    tau_sigma_mult: float = 0.5,
) -> dict[str, Any]:
    """Fixed-horizon sign labels with dead-zone τ = ``tau_sigma_mult`` × σ (FS19 trial)."""
    if price_col not in df.columns:
        return {"ok": False, "reason": "no price column"}
    px = pd.to_numeric(df[price_col], errors="coerce").dropna()
    n = len(px)
    if horizon > n / 10:
        return {"ok": False, "reason": "horizon too large", "n": n, "horizon": horizon}
    rets = px.pct_change(horizon, fill_method=None).dropna()
    if len(rets) < 30:
        return {"ok": False, "reason": "too few forward returns", "n_fwd": int(len(rets))}
    sigma = float(rets.std())
    tau = tau_sigma_mult * sigma if sigma > 0 else 0.0
    labeled = np.where(np.abs(rets.to_numpy()) >= tau, np.sign(rets.to_numpy()), 0).astype(int)
    vals, cnts = np.unique(labeled, return_counts=True)
    counts = {-1: 0, 0: 0, 1: 0}
    for v, c in zip(vals, cnts, strict=True):
        counts[int(v)] = int(c)
    n_labels = int(len(labeled))
    shares = {k: float(v) / n_labels for k, v in counts.items()}
    side_shares = [shares[k] for k in (-1, 1) if counts[k] > 0]
    minority_signed = float(min(side_shares)) if side_shares else None
    return {
        "ok": True,
        "method": "fixed_horizon",
        "horizon": horizon,
        "tau": tau,
        "n_labels": n_labels,
        "counts": counts,
        "shares": shares,
        "minority_signed_share": minority_signed,
        "vertical_barrier_share": shares[0],
    }


def check_fs10_class_balance(df: pd.DataFrame, price_col: str | None) -> FSResult:
    """FS10 — class balance after trial fixed-horizon ±1σ labels (AFML thin).

    For each bar i, look ahead min(5, n-i-1) bars; label +1 if cum log-return
    ≥ +σ_i, −1 if ≤ −σ_i, else 0 (vertical barrier). Minority share among
    {−1,+1} (ignoring 0): ≥15% PASS, 5–15% WARN, else FAIL.
    """
    if price_col is None or price_col not in df.columns:
        return FSResult("FS10", "FAIL", "no price column for trial labels")
    bal = compute_trial_tb_label_balance(df, price_col)
    if not bal.get("ok"):
        reason = str(bal.get("reason", "trial labels failed"))
        return FSResult("FS10", "FAIL", reason, {k: v for k, v in bal.items() if k != "ok"})
    counts = bal["counts"]
    n_labels = int(bal["n_labels"])
    n_signed = counts[-1] + counts[1]
    details: dict[str, Any] = {
        "n_labels": n_labels,
        "n_signed": n_signed,
        "pos": counts[1],
        "neg": counts[-1],
        "zero_share": float(bal["shares"][0]),
    }
    if n_signed < 20:
        return FSResult("FS10", "FAIL", "too few signed trial labels", details)
    minority = float(bal["minority_signed_share"])
    details["minority_share"] = minority
    if minority >= 0.15:
        return FSResult("FS10", "PASS", f"minority={minority:.1%} after ±1σ trial", details)
    if minority >= 0.05:
        return FSResult("FS10", "WARN", f"minority={minority:.1%} (5–15%)", details)
    return FSResult("FS10", "FAIL", f"minority={minority:.1%} (<5%)", details)


def check_fs13_effective_sample_size(df: pd.DataFrame, price_col: str | None) -> FSResult:
    """FS13 — effective sample size n_events × mean ū (AFML thin).

    PASS ≥200, WARN 50–199, FAIL <50.
    """
    u = check_fs12_average_uniqueness(df, price_col)
    if "mean_uniqueness" not in u.details:
        return FSResult("FS13", "FAIL", u.message, u.details)
    n_spans = int(u.details.get("n_spans", 0))
    mean_u = float(u.details["mean_uniqueness"])
    n_eff = float(n_spans * mean_u)
    details = {**u.details, "n_eff": n_eff}
    if n_eff >= 200:
        return FSResult("FS13", "PASS", f"n_eff={n_eff:.1f}", details)
    if n_eff >= 50:
        return FSResult("FS13", "WARN", f"n_eff={n_eff:.1f} (50–199)", details)
    return FSResult("FS13", "FAIL", f"n_eff={n_eff:.1f} (<50)", details)


def compute_trial_uniqueness_profile(
    df: pd.DataFrame,
    price_col: str,
    *,
    horizon: int = 5,
    vol_span: int = 100,
) -> dict[str, Any]:
    """Trial ±1σ label spans: per-event ū_i and concurrency c_t (FS12 / FS.P.UNIQUENESS)."""
    if price_col not in df.columns:
        return {"ok": False, "reason": "no price column"}
    px = pd.to_numeric(df[price_col], errors="coerce").dropna()
    if len(px) < 60:
        return {"ok": False, "reason": "too few bars", "n": int(len(px))}
    log_p = np.log(px.to_numpy(dtype=float))
    rets = np.diff(log_p)
    vol = pd.Series(rets).ewm(span=vol_span, min_periods=30).std().to_numpy()
    spans: list[tuple[int, int]] = []
    for i in range(len(rets) - 1):
        sigma = vol[i]
        if not np.isfinite(sigma) or sigma <= 0:
            continue
        end = min(i + 1 + horizon, len(log_p) - 1)
        t1 = end
        path = log_p[i + 1 : end + 1] - log_p[i]
        for j, r in enumerate(path):
            if r >= sigma or r <= -sigma:
                t1 = i + 1 + j
                break
        spans.append((i, t1))
    if len(spans) < 20:
        return {"ok": False, "reason": "too few spans", "n_spans": len(spans)}
    n_t = max(t1 for _t0, t1 in spans) + 1
    concurrent = np.zeros(n_t, dtype=float)
    for t0, t1 in spans:
        concurrent[t0 : t1 + 1] += 1.0
    per_event: list[float] = []
    for t0, t1 in spans:
        c = np.maximum(concurrent[t0 : t1 + 1], 1.0)
        per_event.append(float(np.mean(1.0 / c)))
    mean_u = float(np.mean(per_event))
    return {
        "ok": True,
        "price_col": price_col,
        "horizon": horizon,
        "vol_span": vol_span,
        "n_spans": len(spans),
        "mean_uniqueness": mean_u,
        "per_event_uniqueness": per_event,
        "concurrency": concurrent.tolist(),
        "max_concurrency": float(np.max(concurrent)),
        "median_concurrency": (
            float(np.median(concurrent[concurrent > 0])) if np.any(concurrent > 0) else 0.0
        ),
    }


def check_fs12_average_uniqueness(df: pd.DataFrame, price_col: str | None) -> FSResult:
    """FS12 — average uniqueness of trial label spans (AFML ch. 4 thin).

    Build concurrent count c_t over trial ±1σ / 5-bar events; ū_i = mean(1/c_t)
    over each event span; report mean ū. PASS ≥0.3, WARN 0.1–0.3, FAIL <0.1.
    """
    if price_col is None or price_col not in df.columns:
        return FSResult("FS12", "FAIL", "no price column for uniqueness")
    prof = compute_trial_uniqueness_profile(df, price_col)
    if not prof.get("ok"):
        reason = prof.get("reason", "uniqueness failed")
        return FSResult("FS12", "FAIL", reason, {k: v for k, v in prof.items() if k != "ok"})
    mean_u = float(prof["mean_uniqueness"])
    details = {"mean_uniqueness": mean_u, "n_spans": int(prof["n_spans"])}
    if mean_u >= 0.3:
        return FSResult("FS12", "PASS", f"mean ū={mean_u:.3f}", details)
    if mean_u >= 0.1:
        return FSResult("FS12", "WARN", f"mean ū={mean_u:.3f} (0.1–0.3)", details)
    return FSResult("FS12", "FAIL", f"mean ū={mean_u:.3f} (<0.1)", details)


def compute_trial_holding_profile(
    df: pd.DataFrame,
    price_col: str,
    *,
    horizon: int = 5,
    vol_span: int = 100,
    pt_mult: float = 1.0,
    sl_mult: float = 1.0,
    cusum_mult: float | None = None,
) -> dict[str, Any]:
    """Trial triple-barrier holding periods in bars (FS.P.HOLDING / §37.8)."""
    base = enumerate_trial_tb_events(
        df,
        price_col,
        horizon=horizon,
        vol_span=vol_span,
        pt_mult=pt_mult,
        sl_mult=sl_mult,
        cusum_mult=cusum_mult,
    )
    if not base.get("ok"):
        return {k: v for k, v in base.items()}
    events = base["events"]
    if len(events) < 20:
        return {"ok": False, "reason": "too few events", "n_events": len(events)}
    holdings: list[int] = []
    by_label: dict[int, list[int]] = {-1: [], 0: [], 1: []}
    for ev in events:
        h = int(ev["t1"]) - int(ev["t0"])
        holdings.append(h)
        by_label[int(ev["label"])].append(h)
    arr = np.array(holdings, dtype=float)
    return {
        "ok": True,
        "price_col": price_col,
        "horizon": horizon,
        "vol_span": vol_span,
        "pt_mult": pt_mult,
        "sl_mult": sl_mult,
        "cusum_mult": cusum_mult,
        "n_events": len(holdings),
        "holding_bars": holdings,
        "by_label": {str(k): v for k, v in by_label.items()},
        "mean_holding": float(np.mean(arr)),
        "median_holding": float(np.median(arr)),
        "min_holding": int(np.min(arr)),
        "max_holding": int(np.max(arr)),
    }


def check_fs11_vertical_barrier_share(df: pd.DataFrame, price_col: str | None) -> FSResult:
    """FS11 — share of trial labels ended by vertical barrier (label 0).

    Reuses FS10 trial labelling; PASS <60%, WARN 60–85%, FAIL >85%.
    """
    base = check_fs10_class_balance(df, price_col)
    if base.status == "FAIL" and "minority" not in base.message:
        return FSResult("FS11", "FAIL", base.message, base.details)
    zero_share = float(base.details.get("zero_share", 1.0))
    details = {**base.details, "vertical_barrier_share": zero_share}
    if zero_share < 0.60:
        return FSResult("FS11", "PASS", f"vertical-barrier share={zero_share:.1%}", details)
    if zero_share <= 0.85:
        return FSResult("FS11", "WARN", f"vertical-barrier share={zero_share:.1%}", details)
    return FSResult("FS11", "FAIL", f"vertical-barrier share={zero_share:.1%} (>85%)", details)


def check_fs8_stale_prices(df: pd.DataFrame, price_col: str | None) -> FSResult:
    """FS8 — share of zero returns (<5% PASS, 5–20% WARN, >20% FAIL)."""
    if price_col and price_col in df.columns:
        px = pd.to_numeric(df[price_col], errors="coerce")
        r = px.pct_change(fill_method=None).dropna()
    else:
        rets_col = _detect_returns_col(df)
        if not rets_col:
            return FSResult("FS8", "FAIL", "no price/returns for stale check")
        r = pd.to_numeric(df[rets_col], errors="coerce").dropna()
    if len(r) == 0:
        return FSResult("FS8", "FAIL", "empty returns")
    zero_share = float((r == 0).mean())
    if zero_share > 0.20:
        return FSResult(
            "FS8",
            "FAIL",
            f"{zero_share:.1%} zero returns (stale)",
            {"zero_share": zero_share},
        )
    if zero_share >= 0.05:
        return FSResult(
            "FS8",
            "WARN",
            f"{zero_share:.1%} zero returns",
            {"zero_share": zero_share},
        )
    return FSResult(
        "FS8",
        "PASS",
        f"{zero_share:.1%} zero returns",
        {"zero_share": zero_share},
    )


def check_fs15_stationarity(df: pd.DataFrame, price_col: str | None) -> FSResult:
    """FS15 — ADF on log-price (expect unit root) and on returns (expect stationary)."""
    from statsmodels.tsa.stattools import adfuller

    if price_col is None or price_col not in df.columns:
        return FSResult("FS15", "INFO", "no price series for ADF / FFD gate")
    px = pd.to_numeric(df[price_col], errors="coerce").dropna()
    if len(px) < 50:
        return FSResult("FS15", "WARN", "too few prices for ADF", {"n": len(px)})
    log_px = np.log(px.clip(lower=1e-12))
    rets = log_px.diff().dropna()
    adf_price = adfuller(log_px, maxlag=10, autolag="AIC", result_object=True)
    adf_ret = adfuller(rets, maxlag=10, autolag="AIC", result_object=True)
    p_price = float(adf_price.pvalue)
    p_ret = float(adf_ret.pvalue)
    from labcore.finance.ffd import scan_min_ffd

    try:
        ffd = scan_min_ffd(log_px.to_numpy(dtype=float), d_step=0.05)
        d_star = ffd["d_star"]
    except ValueError:
        d_star = None
    details = {
        "adf_log_price_pvalue": p_price,
        "adf_returns_pvalue": p_ret,
        "ffd_d_star": d_star,
    }
    if p_ret >= 0.05:
        return FSResult(
            "FS15",
            "WARN",
            f"returns may be non-stationary (ADF p={p_ret:.4g})",
            details,
        )
    return FSResult(
        "FS15",
        "PASS",
        f"log-price ADF p={p_price:.4g}; returns ADF p={p_ret:.4g}",
        details,
    )


def check_fs19_fixed_horizon(
    df: pd.DataFrame,
    price_col: str | None,
    *,
    horizon: int = 5,
) -> FSResult:
    """FS19 — fixed-horizon feasibility (pandas; no TradingLab).

    h ≤ n/10 and threshold τ = 0.5σ gives minority class ≥ 15% → PASS.
    """
    if price_col is None or price_col not in df.columns:
        return FSResult("FS19", "FAIL", "no price series for fixed-horizon trial")
    bal = compute_fixed_horizon_label_balance(df, price_col, horizon=horizon)
    if not bal.get("ok"):
        reason = str(bal.get("reason", "fixed-horizon trial failed"))
        return FSResult("FS19", "FAIL", reason, {k: v for k, v in bal.items() if k != "ok"})
    minority = float(bal["minority_signed_share"] or 0.0)
    details = {
        "horizon": horizon,
        "tau": bal["tau"],
        "shares": bal["shares"],
        "minority": minority,
    }
    if minority >= 0.15:
        return FSResult("FS19", "PASS", f"minority={minority:.1%} at h={horizon}", details)
    if minority >= 0.05:
        return FSResult("FS19", "WARN", f"minority={minority:.1%} at h={horizon}", details)
    return FSResult("FS19", "FAIL", f"minority={minority:.1%} at h={horizon}", details)


def check_fs14_return_acf(df: pd.DataFrame, price_col: str | None) -> FSResult:
    """FS14 — Ljung-Box on returns (informational, never FAIL)."""
    from statsmodels.stats.diagnostic import acorr_ljungbox

    if price_col and price_col in df.columns:
        px = pd.to_numeric(df[price_col], errors="coerce")
        r = px.pct_change(fill_method=None).dropna()
    else:
        rets_col = _detect_returns_col(df)
        if not rets_col:
            return FSResult("FS14", "INFO", "no returns series for ACF")
        r = pd.to_numeric(df[rets_col], errors="coerce").dropna()
    if len(r) < 30:
        return FSResult("FS14", "INFO", "too few returns for Ljung-Box", {"n": len(r)})
    lb = acorr_ljungbox(r, lags=[10], return_df=True)
    pval = float(lb["lb_pvalue"].iloc[0])
    return FSResult(
        "FS14",
        "INFO",
        f"Ljung-Box lag10 p={pval:.4g}",
        {"pvalue": pval, "lags": 10},
    )


def check_fs20_leakage(df: pd.DataFrame) -> FSResult:
    """FS20 — flag suspicious future-dated / leaky column names."""
    suspicious = []
    for c in df.columns:
        cl = str(c).lower()
        if any(
            tok in cl
            for tok in (
                "future_",
                "fwd_",
                "forward_",
                "next_",
                "t+1",
                "lead_",
                "target_leak",
            )
        ):
            suspicious.append(str(c))
    if suspicious:
        return FSResult(
            "FS20",
            "FAIL",
            f"confirmed future-looking columns: {suspicious}",
            {"columns": suspicious},
        )
    return FSResult("FS20", "PASS", "no obvious future-dated feature names")


def _method_verdict(
    checks: list[FSResult],
    *,
    required: set[str],
    caution: set[str] | None = None,
) -> dict[str, Any]:
    by = {c.code: c for c in checks}
    failed = [c for c in required if by.get(c) and by[c].status == "FAIL"]
    warned = [
        c
        for c in (caution or set()) | required
        if by.get(c) and by[c].status == "WARN"
    ]
    if failed:
        status = "NOT_SUITABLE"
    elif warned:
        status = "SUITABLE_WITH_CAUTIONS"
    else:
        status = "SUITABLE"
    return {"status": status, "failed": failed, "warned": warned}


def check_fs16_structural_breaks(
    df: pd.DataFrame,
    price_col: str | None = None,
) -> FSResult:
    """FS16 — SADF peak + optional ruptures change-points (informational)."""
    from labcore.finance.sadf import compute_sadf_series

    col = price_col or _detect_price_col(df)
    if col is None:
        return FSResult("FS16", "INFO", "no price column for structural-break scan")
    raw = pd.to_numeric(df[col], errors="coerce").dropna()
    if len(raw) < 40:
        return FSResult("FS16", "INFO", "series too short for SADF", {"n": int(len(raw))})
    log_px = np.log(raw.clip(lower=1e-12).to_numpy(dtype=float))
    # Suitability is interactive: SADF on a trailing window; ruptures on a subsample.
    tail = log_px[-min(len(log_px), 250) :]
    try:
        sadf = compute_sadf_series(
            tail,
            min_window=30,
            max_lookback=min(40, len(tail) - 5),
            end_step=max(1, len(tail) // 25),
        )
        peak = float(sadf["peak_sadf"])
        peak_end = sadf["peak_end"]
    except Exception as exc:  # noqa: BLE001 — informational lane
        return FSResult("FS16", "INFO", f"SADF unavailable: {exc}")
    n_breaks = 0
    try:
        import ruptures as rpt

        sample = log_px[:: max(1, len(log_px) // 400)]
        if len(sample) >= 20:
            algo = rpt.Pelt(model="rbf").fit(sample.reshape(-1, 1))
            bkps = algo.predict(pen=5)
            n_breaks = max(0, len(bkps) - 1)
        else:
            n_breaks = 0
    except Exception:
        n_breaks = -1
    return FSResult(
        "FS16",
        "INFO",
        f"SADF peak={peak:.2f}; ruptures breaks={n_breaks}",
        {
            "peak_sadf": peak,
            "peak_end": peak_end,
            "n_breaks": n_breaks,
            "sadf_window": int(len(tail)),
            "library": "statsmodels+ruptures",
        },
    )


def check_fs17_trend_scanning(
    df: pd.DataFrame,
    price_col: str | None = None,
) -> FSResult:
    """FS17 — share of trend-scan |t| > 2 over L ∈ [5, 20]."""
    from labcore.finance.trendscan import compute_trendscan_series

    col = price_col or _detect_price_col(df)
    if col is None:
        return FSResult("FS17", "FAIL", "no price column for trend-scanning")
    raw = pd.to_numeric(df[col], errors="coerce").dropna()
    if len(raw) < 30:
        return FSResult("FS17", "FAIL", "need ≥30 prices for trend-scan", {"n": int(len(raw))})
    # Trailing window keeps FS17 interactive on multi-year samples.
    window = raw.iloc[-min(len(raw), 400) :]
    log_px = np.log(window.clip(lower=1e-12).to_numpy(dtype=float))
    try:
        scan = compute_trendscan_series(log_px, l_min=5, l_max=20, step=2)
    except Exception as exc:  # noqa: BLE001
        return FSResult("FS17", "FAIL", f"trend-scan failed: {exc}")
    share = float(scan["share_abs_t_gt_2"])
    details = {
        "share_abs_t_gt_2": share,
        "peak_t_value": scan["peak_t_value"],
        "n_origins": len(scan["origins"]),
    }
    if share >= 0.20:
        return FSResult("FS17", "PASS", f"share |t|>2 = {share:.1%} (≥20%)", details)
    if share >= 0.05:
        return FSResult("FS17", "WARN", f"share |t|>2 = {share:.1%} (5–20%)", details)
    return FSResult("FS17", "FAIL", f"share |t|>2 = {share:.1%} (<5%)", details)


def check_fs18_meta_labelling(
    df: pd.DataFrame,
    price_col: str | None = None,
    *,
    fast: int = 10,
    slow: int = 30,
) -> FSResult:
    """FS18 — primary rule (MA cross) yields ≥100 signals (thin stand-in)."""
    col = price_col or _detect_price_col(df)
    if col is None:
        return FSResult("FS18", "FAIL", "no price column for meta-labelling primary")
    px = pd.to_numeric(df[col], errors="coerce").dropna()
    if len(px) < slow + 5:
        return FSResult(
            "FS18",
            "FAIL",
            f"need ≥{slow + 5} prices for MA({fast}/{slow}) primary",
            {"n": int(len(px))},
        )
    ma_fast = px.rolling(fast).mean()
    ma_slow = px.rolling(slow).mean()
    cross = ((ma_fast > ma_slow) != (ma_fast.shift(1) > ma_slow.shift(1))).fillna(False)
    n_signals = int(cross.sum())
    details = {"n_signals": n_signals, "fast": fast, "slow": slow, "rule": "ma_cross"}
    if n_signals >= 100:
        return FSResult("FS18", "PASS", f"MA cross signals={n_signals} (≥100)", details)
    if n_signals > 0:
        return FSResult("FS18", "WARN", f"MA cross signals={n_signals} (<100)", details)
    return FSResult("FS18", "FAIL", "MA cross produced no signals", details)


def run_suitability(
    df: pd.DataFrame,
    *,
    time_col: str | None = None,
    asset: str | None = None,
) -> dict[str, Any]:
    """Run FS1–FS20 suitability checks (thin AFML where TradingLab absent)."""
    price = _detect_price_col(df)
    checks = [
        check_fs1_time_index(df, time_col),
        check_fs2_price_or_returns(df),
        check_fs3_positivity(df, price),
        check_fs4_ohlcv(df),
        check_fs5_frequency(df, time_col),
        check_fs6_length(df),
        check_fs7_daily_vol(df, price),
        check_fs8_stale_prices(df, price),
        check_fs9_event_count(df, price),
        check_fs10_class_balance(df, price),
        check_fs11_vertical_barrier_share(df, price),
        check_fs12_average_uniqueness(df, price),
        check_fs13_effective_sample_size(df, price),
    ]
    checks.append(check_fs14_return_acf(df, price))
    checks.append(check_fs15_stationarity(df, price))
    checks.append(check_fs16_structural_breaks(df, price))
    checks.append(check_fs17_trend_scanning(df, price))
    checks.append(check_fs18_meta_labelling(df, price))
    checks.append(check_fs19_fixed_horizon(df, price))
    checks.append(check_fs20_leakage(df))

    required_for_tb = {"FS1", "FS2", "FS3", "FS6"}
    failed = [c.code for c in checks if c.status == "FAIL" and c.code in required_for_tb]
    warned = [c.code for c in checks if c.status == "WARN"]
    if failed:
        overall = "NOT_SUITABLE"
    elif warned:
        overall = "SUITABLE_WITH_CAUTIONS"
    else:
        overall = "SUITABLE"

    fh_fail = [
        c.code
        for c in checks
        if c.status == "FAIL" and c.code in {"FS1", "FS2", "FS6", "FS19", "FS20"}
    ]
    methods = {
        "triple_barrier": {
            "status": overall if not failed else "NOT_SUITABLE",
            "failed": failed,
            "warned": warned,
        },
        "fixed_horizon": {
            "status": "NOT_SUITABLE"
            if fh_fail
            else ("SUITABLE_WITH_CAUTIONS" if warned else "SUITABLE"),
            "failed": fh_fail,
            "warned": warned,
        },
        "trend_scanning": _method_verdict(
            checks,
            required={"FS1", "FS2", "FS6", "FS17", "FS20"},
            caution={"FS5"},
        ),
        "meta_labeling": _method_verdict(
            checks,
            required={"FS1", "FS2", "FS3", "FS6", "FS7", "FS9", "FS10", "FS18", "FS20"},
            caution={"FS4", "FS5", "FS8", "FS11", "FS12"},
        ),
    }
    recommendations: list[str] = []
    if "FS4" in warned:
        recommendations.append("Close-only: use close-to-close EWM volatility.")
    if "FS5" in warned or "FS5" in [c.code for c in checks if c.status == "FAIL"]:
        recommendations.append("Forward-fill ≤1 bar or resample to a coarser frequency.")
    if "FS6" in failed:
        recommendations.append("Need ≥500–1000 bars for purged CV with financial labels.")
    if "FS8" in warned or "FS8" in [c.code for c in checks if c.status == "FAIL"]:
        recommendations.append("Stale prices: check liquidity before barrier labelling.")
    if overall == "NOT_SUITABLE":
        recommendations.append("Fall back to a standard supervised target.")

    return {
        "asset": asset,
        "status": overall,
        "checks": [
            {
                "code": c.code,
                "status": c.status,
                "message": c.message,
                "details": c.details,
            }
            for c in checks
        ],
        "methods": methods,
        "recommendations": recommendations,
        "n_rows": int(len(df)),
    }
