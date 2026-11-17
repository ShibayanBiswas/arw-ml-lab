"""Multicollinearity policy — MI-14 (ARCHITECTURE §46.1, EDA VIF table)."""

from __future__ import annotations

MI14_RULE = "MI-14"
LAB_DEFAULT_SEED = 42

VIF_HIGH_THRESHOLD = 10.0
VIF_WARN_THRESHOLD = 5.0
CORR_CLUSTER_THRESHOLD = 0.9


def vif_severity(v: float) -> str:
    """Match ``labcore.eda.tables.table_vif`` flag buckets."""
    if not v or v != v:  # NaN
        return "ok"
    if v > VIF_HIGH_THRESHOLD:
        return "high"
    if v > VIF_WARN_THRESHOLD:
        return "warn"
    return "ok"