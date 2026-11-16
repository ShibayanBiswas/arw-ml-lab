"""FS1–FS5 (and stubs FS6–FS20) financial labelling suitability (ARCHITECTURE §37).

Thin Phase 5B slice: real FS1–FS5 via pandas; remaining codes deferred until
TradingLab label adapters land in Phase 5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

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


def run_suitability(
    df: pd.DataFrame,
    *,
    time_col: str | None = None,
    asset: str | None = None,
) -> dict[str, Any]:
    """Run FS1–FS5 for real; FS6–FS20 deferred until Phase 5 label adapters."""
    price = _detect_price_col(df)
    checks = [
        check_fs1_time_index(df, time_col),
        check_fs2_price_or_returns(df),
        check_fs3_positivity(df, price),
        check_fs4_ohlcv(df),
        check_fs5_frequency(df, time_col),
    ]
    for code in (
        "FS6",
        "FS7",
        "FS8",
        "FS9",
        "FS10",
        "FS11",
        "FS12",
        "FS13",
        "FS14",
        "FS15",
        "FS16",
        "FS17",
        "FS18",
        "FS19",
        "FS20",
    ):
        checks.append(
            FSResult(
                code,
                "DEFERRED",
                "requires TradingLab label adapters (Phase 5)",
            )
        )

    required_for_tb = {"FS1", "FS2", "FS3"}
    failed = [c.code for c in checks if c.status == "FAIL" and c.code in required_for_tb]
    warned = [c.code for c in checks if c.status == "WARN"]
    if failed:
        overall = "NOT_SUITABLE"
    elif warned:
        overall = "SUITABLE_WITH_CAUTIONS"
    else:
        overall = "SUITABLE"

    methods = {
        "triple_barrier": {
            "status": overall if not failed else "NOT_SUITABLE",
            "failed": failed,
            "warned": warned,
        },
        "fixed_horizon": {
            "status": "NOT_SUITABLE"
            if "FS1" in failed or "FS2" in failed
            else ("SUITABLE_WITH_CAUTIONS" if warned else "SUITABLE"),
            "failed": [c for c in failed if c in ("FS1", "FS2")],
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
    if "FS5" in warned or "FS5" in failed:
        recommendations.append("Forward-fill ≤1 bar or resample to a coarser frequency.")
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
