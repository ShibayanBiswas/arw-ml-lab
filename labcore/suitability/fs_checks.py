"""FS financial labelling suitability (ARCHITECTURE §37).

Implemented without TradingLab: FS1–FS11, FS14–FS15, FS19–FS20.
FS12–FS13 / FS16–FS18 stay DEFERRED until vendor/tradinglab uniqueness/meta adapters.
FS7/FS9–FS11 use AFML-equivalent thin formulas until the submodule lands.
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


def check_fs7_daily_vol(df: pd.DataFrame, price_col: str | None, *, span: int = 100) -> FSResult:
    """FS7 — EWMA volatility estimable (AFML ``get_daily_vol`` equivalent).

    Uses ``pandas.Series.ewm(span=span).std()`` on close-to-close returns.
    PASS if ≥95% non-null after warm-up and vol > 0; WARN 80–95%; else FAIL.
    """
    if price_col is None or price_col not in df.columns:
        return FSResult("FS7", "FAIL", "no price column for EWMA vol")
    px = pd.to_numeric(df[price_col], errors="coerce")
    rets = px.pct_change(fill_method=None)
    vol = rets.ewm(span=span, min_periods=max(span // 2, 10)).std()
    warm = vol.iloc[span:] if len(vol) > span else vol.dropna()
    if len(warm) == 0:
        return FSResult("FS7", "FAIL", "insufficient bars for EWMA vol warm-up", {"span": span})
    non_null = float(warm.notna().mean())
    positive = float((warm.fillna(0) > 0).mean())
    details = {
        "span": span,
        "non_null_share": non_null,
        "positive_share": positive,
        "median_vol": float(warm.median()) if warm.notna().any() else None,
    }
    if non_null >= 0.95 and positive >= 0.95:
        return FSResult("FS7", "PASS", f"EWMA vol ok (non-null={non_null:.1%})", details)
    if non_null >= 0.80 and positive >= 0.80:
        return FSResult("FS7", "WARN", f"EWMA vol thin (non-null={non_null:.1%})", details)
    return FSResult("FS7", "FAIL", f"EWMA vol not estimable (non-null={non_null:.1%})", details)


def check_fs9_event_count(df: pd.DataFrame, price_col: str | None) -> FSResult:
    """FS9 — CUSUM event count with h = mean daily EWMA σ (AFML cusum_filter thin).

    PASS ≥300 events, WARN 100–299, FAIL <100.
    """
    if price_col is None or price_col not in df.columns:
        return FSResult("FS9", "FAIL", "no price column for CUSUM events")
    px = pd.to_numeric(df[price_col], errors="coerce").dropna()
    if len(px) < 50:
        return FSResult("FS9", "FAIL", "too few prices for CUSUM", {"n": len(px)})
    log_r = np.log(px).diff().dropna()
    vol = log_r.ewm(span=100, min_periods=50).std()
    h = float(vol.dropna().mean())
    if not np.isfinite(h) or h <= 0:
        return FSResult("FS9", "FAIL", "CUSUM threshold h not positive", {"h": h})
    # Symmetric CUSUM filter (AFML ch. 2)
    s_pos = 0.0
    s_neg = 0.0
    events = 0
    for r in log_r.to_numpy(dtype=float):
        if not np.isfinite(r):
            continue
        s_pos = max(0.0, s_pos + r)
        s_neg = min(0.0, s_neg + r)
        if s_pos > h:
            events += 1
            s_pos = 0.0
        elif s_neg < -h:
            events += 1
            s_neg = 0.0
    details = {"events": events, "h": h, "n_returns": int(len(log_r))}
    if events >= 300:
        return FSResult("FS9", "PASS", f"{events} CUSUM events", details)
    if events >= 100:
        return FSResult("FS9", "WARN", f"{events} CUSUM events (100–299)", details)
    return FSResult("FS9", "FAIL", f"{events} CUSUM events (<100)", details)


def check_fs10_class_balance(df: pd.DataFrame, price_col: str | None) -> FSResult:
    """FS10 — class balance after trial fixed-horizon ±1σ labels (AFML thin).

    For each bar i, look ahead min(5, n-i-1) bars; label +1 if cum log-return
    ≥ +σ_i, −1 if ≤ −σ_i, else 0 (vertical barrier). Minority share among
    {−1,+1} (ignoring 0): ≥15% PASS, 5–15% WARN, else FAIL.
    """
    if price_col is None or price_col not in df.columns:
        return FSResult("FS10", "FAIL", "no price column for trial labels")
    px = pd.to_numeric(df[price_col], errors="coerce").dropna()
    if len(px) < 60:
        return FSResult("FS10", "FAIL", "too few bars for trial labels", {"n": len(px)})
    log_p = np.log(px.to_numpy(dtype=float))
    rets = np.diff(log_p)
    vol = pd.Series(rets).ewm(span=100, min_periods=30).std().to_numpy()
    labels: list[int] = []
    horizon = 5
    for i in range(len(rets) - 1):
        sigma = vol[i]
        if not np.isfinite(sigma) or sigma <= 0:
            continue
        end = min(i + 1 + horizon, len(log_p))
        path = log_p[i + 1 : end] - log_p[i]
        if len(path) == 0:
            continue
        if np.any(path >= sigma):
            labels.append(1)
        elif np.any(path <= -sigma):
            labels.append(-1)
        else:
            labels.append(0)
    signed = [x for x in labels if x != 0]
    details: dict[str, Any] = {
        "n_labels": len(labels),
        "n_signed": len(signed),
        "pos": int(sum(1 for x in signed if x > 0)),
        "neg": int(sum(1 for x in signed if x < 0)),
        "zero_share": float(labels.count(0) / max(len(labels), 1)),
    }
    if len(signed) < 20:
        return FSResult("FS10", "FAIL", "too few signed trial labels", details)
    minority = min(details["pos"], details["neg"]) / len(signed)
    details["minority_share"] = float(minority)
    if minority >= 0.15:
        return FSResult("FS10", "PASS", f"minority={minority:.1%} after ±1σ trial", details)
    if minority >= 0.05:
        return FSResult("FS10", "WARN", f"minority={minority:.1%} (5–15%)", details)
    return FSResult("FS10", "FAIL", f"minority={minority:.1%} (<5%)", details)


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
    # Spec: d* via TradingLab FFD deferred; report ADF evidence only
    details = {
        "adf_log_price_pvalue": p_price,
        "adf_returns_pvalue": p_ret,
        "ffd_d_star": "deferred (TradingLab)",
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
    px = pd.to_numeric(df[price_col], errors="coerce").dropna()
    n = len(px)
    if horizon > n / 10:
        return FSResult(
            "FS19",
            "FAIL",
            f"horizon h={horizon} > n/10 ({n / 10:.1f})",
            {"n": n, "horizon": horizon},
        )
    rets = px.pct_change(horizon, fill_method=None).dropna()
    if len(rets) < 30:
        return FSResult("FS19", "FAIL", "too few forward returns", {"n_fwd": len(rets)})
    sigma = float(rets.std())
    tau = 0.5 * sigma if sigma > 0 else 0.0
    labeled = np.where(np.abs(rets.to_numpy()) >= tau, np.sign(rets.to_numpy()), 0)
    vals, counts = np.unique(labeled, return_counts=True)
    shares = {int(v): float(c) / len(labeled) for v, c in zip(vals, counts, strict=True)}
    side_shares = [shares[k] for k in (-1, 1) if k in shares]
    minority = float(min(side_shares)) if side_shares else 0.0
    details = {"horizon": horizon, "tau": tau, "shares": shares, "minority": minority}
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


def run_suitability(
    df: pd.DataFrame,
    *,
    time_col: str | None = None,
    asset: str | None = None,
) -> dict[str, Any]:
    """Run implemented FS checks; TradingLab-only codes stay DEFERRED."""
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
    ]
    for code in ("FS12", "FS13"):
        checks.append(
            FSResult(
                code,
                "DEFERRED",
                "requires TradingLab uniqueness / sample-weight adapters (Phase 5)",
            )
        )
    checks.append(check_fs14_return_acf(df, price))
    checks.append(check_fs15_stationarity(df, price))
    for code in ("FS16", "FS17", "FS18"):
        checks.append(
            FSResult(
                code,
                "DEFERRED",
                "requires TradingLab structural/trend/meta adapters",
            )
        )
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
        "trend_scanning": {
            "status": "DEFERRED",
            "failed": [],
            "warned": [],
        },
        "meta_labeling": {
            "status": "DEFERRED",
            "failed": [],
            "warned": [],
        },
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
