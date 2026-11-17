"""Multicollinearity / VIF — MI-14 / ST-ML-02 (ARCHITECTURE §46.1)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor

from labcore.data.infer import infer_schema
from labcore.data.task_detect import detect_task
from labcore.eda.context import EDAContext
from labcore.eda.tables import table_vif
from labcore.insights.rules import run_eda_rules
from labcore.integrity.multicollinearity_policy import (
    CORR_CLUSTER_THRESHOLD,
    LAB_DEFAULT_SEED,
    MI14_RULE,
    VIF_HIGH_THRESHOLD,
    vif_severity,
)

ARTEFACT_ID = "MI.MULTICOLLINEARITY"
STRESS_ID = "ST-ML-02"


class MulticollinearityContractError(ValueError):
    """Raised when MI-14 offline kit contract is violated."""


def _vif_rows(df: pd.DataFrame, cols: list[str]) -> list[dict[str, object]]:
    """Thin wrapper aligned with ``table_vif`` (statsmodels VIF on z-scored numerics)."""
    X = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
    if X.shape[1] < 2 or len(X) < 10:
        return []
    Xn = (X - X.mean()) / (X.std(ddof=0).replace(0, 1))
    arr = Xn.values
    rows: list[dict[str, object]] = []
    for i, col in enumerate(cols):
        try:
            v = float(variance_inflation_factor(arr, i))
        except Exception:
            v = float("nan")
        rows.append(
            {
                "feature": col,
                "vif": v,
                "flag": vif_severity(v),
            },
        )
    return rows


def _collinear_fixture(*, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = 240
    x1 = rng.normal(size=n)
    x2 = x1 + rng.normal(scale=0.02, size=n)
    x3 = rng.normal(size=n)
    y = x1 + rng.normal(scale=0.3, size=n)
    return pd.DataFrame({"x1": x1, "x2": x2, "x3": x3, "y": y})


def assert_mi14_high_vif_on_collinear_pair(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-14: near-duplicate numerics yield VIF > threshold (statsmodels)."""
    df = _collinear_fixture(seed=seed)
    r = float(df["x1"].corr(df["x2"]))
    if abs(r) < CORR_CLUSTER_THRESHOLD:
        raise MulticollinearityContractError(
            f"MI-14: fixture must have |corr| ≥ {CORR_CLUSTER_THRESHOLD}, got {r:.4f}",
        )
    rows = _vif_rows(df, ["x1", "x2", "x3"])
    if not rows:
        raise MulticollinearityContractError("MI-14: VIF rows empty on collinear fixture")
    high = [row for row in rows if row.get("flag") == "high"]
    if not high:
        raise MulticollinearityContractError(
            f"MI-14: expected VIF > {VIF_HIGH_THRESHOLD} on collinear pair",
        )
    v_x1 = next(float(r["vif"]) for r in rows if r["feature"] == "x1")
    v_x3 = next(float(r["vif"]) for r in rows if r["feature"] == "x3")
    if v_x3 > VIF_HIGH_THRESHOLD:
        raise MulticollinearityContractError("MI-14: independent x3 must stay below high threshold")
    return {
        "mi_rule": MI14_RULE,
        "corr_x1_x2": r,
        "vif_x1": v_x1,
        "vif_x3": v_x3,
        "n_high_flags": len(high),
        "seed": seed,
    }


def assert_mi14_eda_vif_table(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-14: ``EDA.T.VIF`` table flags high multicollinearity (same thresholds as §46.1)."""
    df = _collinear_fixture(seed=seed)
    schema = infer_schema(df)
    task = detect_task(df, schema, target="y")
    ctx = EDAContext(df=df, schema=schema, task=task, seed=seed)
    artefact = table_vif(ctx)
    if artefact.id != "EDA.T.VIF":
        raise MulticollinearityContractError("MI-14: expected EDA.T.VIF artefact")
    rows = artefact.table.get("rows") or []
    flags = {r.get("feature"): r.get("flag") for r in rows if "feature" in r}
    if flags.get("x1") != "high" and flags.get("x2") != "high":
        raise MulticollinearityContractError(
            f"MI-14: EDA VIF must flag x1 or x2 high, got {flags}",
        )
    if flags.get("x3") == "high":
        raise MulticollinearityContractError("MI-14: x3 must not be flagged high in EDA table")
    return {
        "mi_rule": MI14_RULE,
        "artefact_id": artefact.id,
        "flags": flags,
        "seed": seed,
    }


def assert_mi14_insights_vif_rule(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    """MI-14: EDA insight rules emit ``vif.high`` when VIF exceeds threshold."""
    df = _collinear_fixture(seed=seed)
    schema = infer_schema(df)
    task = detect_task(df, schema, target="y")
    insights = run_eda_rules(df, schema, task, vif_threshold=VIF_HIGH_THRESHOLD)
    vif_hits = [i for i in insights if i.rule_id == "vif.high"]
    if not vif_hits:
        raise MulticollinearityContractError("MI-14: run_eda_rules must emit vif.high on fixture")
    cols = {i.column for i in vif_hits if i.column}
    if not (cols & {"x1", "x2"}):
        raise MulticollinearityContractError(
            f"MI-14: vif.high must cite collinear column, got {cols}",
        )
    return {
        "mi_rule": MI14_RULE,
        "rule_id": "vif.high",
        "columns": sorted(cols),
        "n_insights": len(vif_hits),
        "seed": seed,
    }


def assert_multicollinearity_contract(*, seed: int = LAB_DEFAULT_SEED) -> list[dict[str, object]]:
    return [
        assert_mi14_high_vif_on_collinear_pair(seed=seed),
        assert_mi14_eda_vif_table(seed=seed),
        assert_mi14_insights_vif_rule(seed=seed),
    ]


def multicollinearity_manifest(*, seed: int = LAB_DEFAULT_SEED) -> dict[str, object]:
    checks = assert_multicollinearity_contract(seed=seed)
    return {
        "id": ARTEFACT_ID,
        "stress_test": STRESS_ID,
        "mi_rule": MI14_RULE,
        "seed": seed,
        "checks": checks,
    }