"""EDA rule engine — CURSOR_PROMPT Phase 1 / ARCHITECTURE education layer."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from labcore.data.infer import ColumnProfile
from labcore.data.task_detect import TaskSpec

Severity = Literal["info", "warning", "critical"]


class RuleInsight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    severity: Severity
    message: str
    column: str | None = None
    value: float | None = None
    threshold: float | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)


def run_eda_rules(
    df: pd.DataFrame,
    schema: list[ColumnProfile],
    task: TaskSpec,
    *,
    corr_threshold: float = 0.9,
    leak_threshold: float = 0.98,
    vif_threshold: float = 10.0,
) -> list[RuleInsight]:
    """Deterministic EDA alerts (no LLM)."""
    insights: list[RuleInsight] = []

    # Missingness 5% / 30%
    for col in schema:
        pct = col.pct_missing * 100
        if pct >= 30:
            insights.append(
                RuleInsight(
                    rule_id="missing.high",
                    severity="critical",
                    message=f"{col.name} is missing {pct:.1f}% of values (≥ 30%).",
                    column=col.name,
                    value=round(pct, 4),
                    threshold=30.0,
                )
            )
        elif pct >= 5:
            insights.append(
                RuleInsight(
                    rule_id="missing.moderate",
                    severity="warning",
                    message=f"{col.name} is missing {pct:.1f}% of values (≥ 5%).",
                    column=col.name,
                    value=round(pct, 4),
                    threshold=5.0,
                )
            )

    # High cardinality / near-zero variance / skew / kurtosis
    for col in schema:
        if col.semantic_type == "high_cardinality":
            insights.append(
                RuleInsight(
                    rule_id="cardinality.high",
                    severity="warning",
                    message=f"{col.name} has high cardinality (n_unique={col.n_unique}).",
                    column=col.name,
                    value=float(col.n_unique),
                )
            )
        if col.semantic_type == "constant":
            insights.append(
                RuleInsight(
                    rule_id="variance.near_zero",
                    severity="warning",
                    message=f"{col.name} is constant / near-zero variance.",
                    column=col.name,
                )
            )
        if col.semantic_type in {"continuous", "numeric_discrete"} and col.name in df.columns:
            s = pd.to_numeric(df[col.name], errors="coerce").dropna()
            if len(s) >= 20:
                skew = float(s.skew())
                kurt = float(s.kurtosis())
                if abs(skew) > 1:
                    insights.append(
                        RuleInsight(
                            rule_id="skew.high",
                            severity="info",
                            message=f"{col.name} skewness = {skew:.2f} (|skew| > 1).",
                            column=col.name,
                            value=skew,
                            threshold=1.0,
                        )
                    )
                if abs(kurt) > 3:
                    insights.append(
                        RuleInsight(
                            rule_id="kurtosis.high",
                            severity="info",
                            message=f"{col.name} excess kurtosis = {kurt:.2f} (|kurt| > 3).",
                            column=col.name,
                            value=kurt,
                            threshold=3.0,
                        )
                    )

    # Pairwise |r| > 0.9 among numeric
    nums = [
        c.name
        for c in schema
        if c.semantic_type in {"continuous", "numeric_discrete", "boolean"} and c.name in df.columns
    ]
    if len(nums) >= 2:
        corr = df[nums].apply(pd.to_numeric, errors="coerce").corr().abs()
        for i, a in enumerate(nums):
            for b in nums[i + 1 :]:
                r = float(corr.loc[a, b]) if a in corr.index and b in corr.columns else float("nan")
                if np.isfinite(r) and r > corr_threshold:
                    insights.append(
                        RuleInsight(
                            rule_id="corr.high",
                            severity="warning",
                            message=f"|r({a},{b})| = {r:.3f} > {corr_threshold}.",
                            value=r,
                            threshold=corr_threshold,
                            evidence={"a": a, "b": b},
                        )
                    )

    # VIF > 10 (lightweight on ≤ 12 cols)
    vif_cols = nums[:12]
    if len(vif_cols) >= 2:
        try:
            from statsmodels.stats.outliers_influence import variance_inflation_factor

            X = df[vif_cols].apply(pd.to_numeric, errors="coerce").dropna()
            if len(X) >= 20:
                Xn = (X - X.mean()) / (X.std(ddof=0).replace(0, 1))
                arr = Xn.values
                for i, name in enumerate(vif_cols):
                    v = float(variance_inflation_factor(arr, i))
                    if np.isfinite(v) and v > vif_threshold:
                        insights.append(
                            RuleInsight(
                                rule_id="vif.high",
                                severity="warning",
                                message=f"VIF({name}) = {v:.1f} > {vif_threshold}.",
                                column=name,
                                value=v,
                                threshold=vif_threshold,
                            )
                        )
        except Exception:
            pass

    # Class imbalance
    if task.task in {"binary", "multiclass"} and task.imbalance_ratio is not None:
        if task.imbalance_ratio > 4 or (
            task.minority_share is not None and task.minority_share < 0.2
        ):
            insights.append(
                RuleInsight(
                    rule_id="imbalance",
                    severity="warning",
                    message=(
                        f"Class imbalance: ratio={task.imbalance_ratio:.2f}, "
                        f"minority_share={task.minority_share}."
                    ),
                    value=task.imbalance_ratio,
                    threshold=4.0,
                )
            )

    # Leakage |corr with target| > 0.98
    if task.target and task.target in df.columns:
        y = pd.to_numeric(df[task.target], errors="coerce")
        if y.notna().sum() >= 20:
            for feat_name in nums:
                if feat_name == task.target:
                    continue
                x = pd.to_numeric(df[feat_name], errors="coerce")
                mask = x.notna() & y.notna()
                if mask.sum() < 20:
                    continue
                r = float(np.corrcoef(x[mask], y[mask])[0, 1])
                if np.isfinite(r) and abs(r) > leak_threshold:
                    insights.append(
                        RuleInsight(
                            rule_id="leakage.corr",
                            severity="critical",
                            message=(
                                f"Potential leakage: |corr({feat_name},{task.target})| = {abs(r):.3f}."
                            ),
                            column=feat_name,
                            value=abs(r),
                            threshold=leak_threshold,
                        )
                    )

    # Duplicates
    dup = int(df.duplicated().sum())
    if dup > 0:
        insights.append(
            RuleInsight(
                rule_id="duplicates",
                severity="warning",
                message=f"{dup} duplicate rows detected.",
                value=float(dup),
            )
        )

    # Non-stationarity (sequential)
    if task.sequential:
        series_col = task.target
        if task.ohlcv:
            series_col = task.ohlcv.get("close", series_col)
        if not series_col or series_col not in df.columns:
            series_col = nums[0] if nums else None
        if series_col:
            try:
                from statsmodels.tsa.stattools import adfuller

                s = pd.to_numeric(df[series_col], errors="coerce").dropna()
                if len(s) >= 30:
                    _stat, p, *_ = adfuller(s, autolag="AIC")
                    if p >= 0.05:
                        insights.append(
                            RuleInsight(
                                rule_id="non_stationarity",
                                severity="warning",
                                message=f"{series_col} fails ADF stationarity (p={p:.3f}).",
                                column=series_col,
                                value=float(p),
                                threshold=0.05,
                            )
                        )
            except Exception:
                pass

    return insights
