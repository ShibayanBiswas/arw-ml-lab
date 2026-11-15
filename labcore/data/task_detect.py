"""Supervised task auto-detection + sequential heuristic — ARCHITECTURE §9."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from statsmodels.stats.diagnostic import acorr_ljungbox

from labcore.data.infer import ColumnProfile

TaskKind = Literal[
    "binary",
    "multiclass",
    "regression",
    "multilabel",
    "multioutput_regression",
    "forecast",
    "unsupervised",
    "rejected",
]


class TaskSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    family: Literal["supervised", "unsupervised", "timeseries"]
    task: TaskKind
    target: str | None = None
    sequential: bool = False
    frequency: str | None = None
    time_column: str | None = None
    imbalance_ratio: float | None = None
    minority_share: float | None = None
    warnings: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    ohlcv: dict[str, str] | None = None


def detect_task(
    df: pd.DataFrame,
    schema: list[ColumnProfile],
    *,
    target: str | None = None,
    family_hint: str | None = None,
    time_column: str | None = None,
) -> TaskSpec:
    warnings: list[str] = []
    by_name = {c.name: c for c in schema}

    # OHLCV detection (DS30)
    ohlcv = _detect_ohlcv(df.columns.tolist())
    if ohlcv and family_hint in (None, "supervised_sequential_financial", "timeseries"):
        freq = infer_frequency(df, ohlcv.get("time") or time_column or _first_datetime(schema))
        return TaskSpec(
            family="supervised",
            task="regression",
            target=target,
            sequential=True,
            frequency=freq,
            time_column=ohlcv.get("time") or time_column,
            warnings=["financial_ohlcv_detected"],
            ohlcv=ohlcv,
        )

    if family_hint == "time_series" or family_hint == "timeseries":
        tcol = time_column or _first_datetime(schema)
        freq = infer_frequency(df, tcol) if tcol else None
        return TaskSpec(
            family="timeseries",
            task="forecast",
            target=target,
            sequential=True,
            frequency=freq,
            time_column=tcol,
        )

    if target is None:
        return TaskSpec(family="unsupervised", task="unsupervised", sequential=False)

    if target not in df.columns:
        return TaskSpec(
            family="supervised",
            task="rejected",
            target=target,
            warnings=[f"target_missing:{target}"],
        )

    y = df[target]
    profile = by_name.get(target) or ColumnProfile(
        name=target,
        physical_dtype=str(y.dtype),
        semantic_type="continuous",
        n_unique=int(y.nunique(dropna=True)),
        pct_unique=0.0,
        pct_missing=float(y.isna().mean()),
    )

    if profile.semantic_type in {"datetime", "text"}:
        return TaskSpec(
            family="supervised",
            task="rejected",
            target=target,
            warnings=["target_datetime_or_text"],
        )

    non_null = y.dropna()
    n_unique = int(non_null.nunique())
    sequential = _suggest_sequential(df, schema, y)
    tcol = time_column or _first_datetime(schema)
    freq = infer_frequency(df, tcol) if tcol and sequential else None

    # Classification vs regression
    if not pd.api.types.is_numeric_dtype(non_null) or profile.semantic_type in {
        "boolean",
        "categorical",
        "numeric_discrete",
    }:
        if n_unique == 2:
            share, ratio = _imbalance(non_null)
            if share is not None and share < 0.2:
                warnings.append("imbalance_warning")
            if share is not None and share < 0.05:
                warnings.append("imbalance_strong")
            return TaskSpec(
                family="supervised",
                task="binary",
                target=target,
                sequential=sequential,
                frequency=freq,
                time_column=tcol,
                minority_share=share,
                imbalance_ratio=ratio,
                warnings=warnings,
            )
        if 3 <= n_unique <= 200:
            if (non_null.value_counts() < 10).any():
                warnings.append("rare_class")
            return TaskSpec(
                family="supervised",
                task="multiclass",
                target=target,
                sequential=sequential,
                frequency=freq,
                time_column=tcol,
                warnings=warnings,
                alternatives=["ordinal_regression"]
                if pd.api.types.is_integer_dtype(non_null)
                else [],
            )

    if pd.api.types.is_numeric_dtype(non_null):
        int_like = pd.api.types.is_integer_dtype(non_null) or bool(
            (non_null == non_null.round()).all()
        )
        n = len(df)
        if int_like and n_unique == 2:
            share, ratio = _imbalance(non_null)
            return TaskSpec(
                family="supervised",
                task="binary",
                target=target,
                sequential=sequential,
                frequency=freq,
                time_column=tcol,
                minority_share=share,
                imbalance_ratio=ratio,
                warnings=warnings,
            )
        if int_like and 3 <= n_unique <= min(20, max(1, int(0.05 * n))):
            warnings.append("could_be_ordinal_or_count")
            return TaskSpec(
                family="supervised",
                task="multiclass",
                target=target,
                sequential=sequential,
                frequency=freq,
                time_column=tcol,
                warnings=warnings,
                alternatives=["poisson_regression", "ordinal"],
            )
        if float(non_null.min()) >= 0 and int_like:
            warnings.append("non_negative_counts_poisson_hint")
        return TaskSpec(
            family="supervised",
            task="regression",
            target=target,
            sequential=sequential,
            frequency=freq,
            time_column=tcol,
            warnings=warnings,
        )

    return TaskSpec(
        family="supervised",
        task="rejected",
        target=target,
        warnings=["unrecognised_target"],
    )


def infer_frequency(df: pd.DataFrame, time_col: str | None) -> str | None:
    if not time_col or time_col not in df.columns:
        return None
    ts = pd.to_datetime(df[time_col], errors="coerce")
    ts = ts.dropna().sort_values()
    if len(ts) < 3:
        return None
    freq = pd.infer_freq(ts)
    if freq:
        # Normalise common codes
        if freq in {"M", "MS", "ME"}:
            return "monthly"
        if freq.startswith("D") or freq in {"B", "C"}:
            return "daily" if freq.startswith("D") else "daily_business"
        if "H" in freq:
            return "hourly"
        if freq.startswith("Q"):
            return "quarterly"
        return freq
    # Mode delta fallback
    deltas = ts.diff().dropna().dt.days
    if deltas.empty:
        return None
    mode = int(deltas.mode().iloc[0]) if len(deltas.mode()) else int(deltas.median())
    if mode >= 28 and mode <= 31:
        return "monthly"
    if mode == 1:
        return "daily"
    if mode == 7:
        return "weekly"
    # Business days: many deltas of 1 with some 3
    if (deltas == 1).mean() > 0.6 and (deltas <= 3).mean() > 0.9:
        return "daily_business"
    return f"irregular_delta_{mode}d"


def _imbalance(y: pd.Series) -> tuple[float | None, float | None]:
    vc = y.value_counts(normalize=True)
    if len(vc) < 2:
        return None, None
    share = float(vc.min())
    ratio = float(vc.max() / max(vc.min(), 1e-12))
    return share, ratio


def _first_datetime(schema: list[ColumnProfile]) -> str | None:
    for c in schema:
        if c.semantic_type == "datetime":
            return c.name
    return None


def _suggest_sequential(df: pd.DataFrame, schema: list[ColumnProfile], y: pd.Series) -> bool:
    tcol = _first_datetime(schema)
    if tcol and tcol in df.columns:
        ts = pd.to_datetime(df[tcol], errors="coerce")
        if ts.notna().mean() > 0.9 and bool(ts.dropna().is_monotonic_increasing):
            return True
    if pd.api.types.is_numeric_dtype(y):
        s = y.dropna()
        if len(s) >= 30:
            try:
                lb = acorr_ljungbox(s, lags=[10], return_df=True)
                p = float(lb["lb_pvalue"].iloc[0])
                if p < 0.01:
                    return True
            except Exception:
                return False
    return False


def _detect_ohlcv(columns: list[Any]) -> dict[str, str] | None:
    lower = {str(c).lower(): str(c) for c in columns}
    need = ["open", "high", "low", "close"]
    if not all(k in lower for k in need):
        return None
    out = {k: lower[k] for k in need}
    for cand in ("volume", "vol"):
        if cand in lower:
            out["volume"] = lower[cand]
            break
    for cand in ("date", "datetime", "timestamp", "time"):
        if cand in lower:
            out["time"] = lower[cand]
            break
    return out
