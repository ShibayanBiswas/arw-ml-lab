"""D6 — Leakage suspects — ARCHITECTURE §33.8."""

from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


def detect_leakage(
    df: pd.DataFrame,
    profile: dict[str, Any],
    roles: dict[str, dict[str, Any]],
    targets: list[dict[str, Any]],
    d1: dict[str, Any],
    family: dict[str, Any],
) -> list[dict[str, Any]]:
    suspects: list[dict[str, Any]] = []
    y_col = next((t["column"] for t in targets if t.get("column") and t["column"] != "__derived__"), None)
    if y_col is None or y_col not in df.columns:
        # still check later-event timestamps without target
        y_col = None

    y = pd.to_numeric(df[y_col], errors="coerce") if y_col else None

    # Transform of target / arithmetic identity
    if y is not None:
        for name in df.columns:
            if name == y_col:
                continue
            x = pd.to_numeric(df[name], errors="coerce")
            aligned = pd.concat([x, y], axis=1).dropna()
            if len(aligned) < 20:
                continue
            xx, yy = aligned.iloc[:, 0].to_numpy(), aligned.iloc[:, 1].to_numpy()
            # exact / monotone
            if np.allclose(xx, yy):
                suspects.append(
                    {
                        "column": name,
                        "rule": "transform_of_target",
                        "severity": "critical",
                        "evidence": {"kind": "exact_duplicate"},
                    }
                )
                continue
            if abs(float(pd.Series(xx).corr(pd.Series(yy), method="spearman"))) >= 0.999:
                # linear identity search a*x+b
                lr = LinearRegression().fit(xx.reshape(-1, 1), yy)
                pred = lr.predict(xx.reshape(-1, 1))
                r2 = float(r2_score(yy, pred))
                if r2 >= 0.999:
                    suspects.append(
                        {
                            "column": name,
                            "rule": "transform_of_target",
                            "severity": "critical",
                            "evidence": {"r2": r2, "coef": float(lr.coef_[0]), "intercept": float(lr.intercept_)},
                        }
                    )
                    continue
            # near-perfect single feature
            try:
                if yy.min() == yy.max():
                    continue
                if len(np.unique(yy)) <= 20:
                    stump = DecisionTreeClassifier(max_depth=1, random_state=42)
                    stump.fit(xx.reshape(-1, 1), yy.astype(int) if set(np.unique(yy)) <= {0, 1} else yy)
                    acc = float(stump.score(xx.reshape(-1, 1), yy.astype(int) if set(np.unique(yy)) <= {0, 1} else yy))
                    if acc >= 0.99:
                        suspects.append(
                            {
                                "column": name,
                                "rule": "near_perfect_predictor",
                                "severity": "high",
                                "evidence": {"stump_accuracy": acc},
                            }
                        )
                else:
                    stump = DecisionTreeRegressor(max_depth=1, random_state=42)
                    stump.fit(xx.reshape(-1, 1), yy)
                    r2 = float(stump.score(xx.reshape(-1, 1), yy))
                    if r2 >= 0.98:
                        suspects.append(
                            {
                                "column": name,
                                "rule": "near_perfect_predictor",
                                "severity": "high",
                                "evidence": {"stump_r2": r2},
                            }
                        )
            except Exception:
                pass

        # arithmetic identity over column pairs involving y ≈ a op b
        num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != y_col][:30]
        for i, a in enumerate(num_cols):
            for b in num_cols[i + 1 :]:
                aa = pd.to_numeric(df[a], errors="coerce")
                bb = pd.to_numeric(df[b], errors="coerce")
                for op_name, series in (
                    ("a+b", aa + bb),
                    ("a-b", aa - bb),
                    ("a*b", aa * bb),
                    ("a/b", aa / bb.replace(0, np.nan)),
                ):
                    aligned = pd.concat([series, y], axis=1).dropna()
                    if len(aligned) < 30:
                        continue
                    lr = LinearRegression().fit(aligned.iloc[:, 0].to_numpy().reshape(-1, 1), aligned.iloc[:, 1])
                    r2 = float(r2_score(aligned.iloc[:, 1], lr.predict(aligned.iloc[:, 0].to_numpy().reshape(-1, 1))))
                    if r2 >= 0.999:
                        suspects.append(
                            {
                                "column": f"{a},{b}",
                                "rule": "arithmetic_identity",
                                "severity": "critical",
                                "evidence": {"op": op_name, "r2": r2},
                            }
                        )

    # Post-outcome name hints
    post_re = re.compile(
        r"(_after$|^post_|^final_|^outcome_|^result|^settled|^closed_|^paid|"
        r"^chargeback|^recovered|^days_to_)",
        re.I,
    )
    for name in df.columns:
        if post_re.search(name):
            suspects.append(
                {
                    "column": name,
                    "rule": "post_outcome_name",
                    "severity": "medium",
                    "evidence": {"name": name},
                }
            )

    # Later-event timestamps
    time_col = (d1.get("accepted") or {}).get("column")
    if time_col and time_col in df.columns:
        t0 = pd.to_datetime(df[time_col], errors="coerce", dayfirst=True)
        for name in df.columns:
            if name == time_col:
                continue
            if profile["columns"].get(name, {}).get("semantic_type") != "datetime" and "date" not in name.lower():
                # still try parse
                if "date" not in name.lower() and "time" not in name.lower():
                    continue
            t1 = pd.to_datetime(df[name], errors="coerce", dayfirst=True)
            aligned = pd.concat([t0, t1], axis=1).dropna()
            if len(aligned) < 10:
                continue
            later = float((aligned.iloc[:, 1] > aligned.iloc[:, 0]).mean())
            if later >= 0.95:
                suspects.append(
                    {
                        "column": name,
                        "rule": "later_event_timestamp",
                        "severity": "high",
                        "evidence": {"share_later": later},
                    }
                )

    # Lead/lag for sequential
    if family.get("proposed") in {"supervised_sequential", "time_series"} and y is not None:
        for name in df.select_dtypes(include=[np.number]).columns:
            if name == y_col:
                continue
            x = pd.to_numeric(df[name], errors="coerce")
            c0 = x.corr(y)
            c_lag = x.shift(1).corr(y)
            c_lead = x.shift(-1).corr(y)
            if pd.notna(c_lead) and pd.notna(c_lag) and abs(c_lead) > abs(c_lag) + 0.15:
                suspects.append(
                    {
                        "column": name,
                        "rule": "lead_lag_future_info",
                        "severity": "high",
                        "evidence": {"corr_t": float(c0) if pd.notna(c0) else None, "corr_lead": float(c_lead)},
                    }
                )
            # centred rolling mean
            roll = x.rolling(5, center=True).mean()
            if pd.notna(roll.corr(y.shift(-1))) and abs(float(roll.corr(y.shift(-1)))) > abs(
                float(x.shift(1).corr(y) or 0)
            ):
                suspects.append(
                    {
                        "column": name,
                        "rule": "centred_rolling_future",
                        "severity": "high",
                        "evidence": {"note": "centred_window_correlates_with_future_y"},
                    }
                )

    # Row-id leakage
    if y is not None and family.get("proposed") == "supervised_non_sequential":
        for name, r in roles.items():
            if r.get("role") != "row_id":
                continue
            x = pd.to_numeric(df[name], errors="coerce")
            rho = float(x.corr(y)) if x.notna().any() else 0.0
            if abs(rho) > 0.3:
                suspects.append(
                    {
                        "column": name,
                        "rule": "row_id_leakage",
                        "severity": "medium",
                        "evidence": {"rho": rho},
                    }
                )

    # Duplicate rows
    dup = float(df.duplicated().mean()) if len(df) else 0.0
    if dup > 0.01:
        suspects.append(
            {
                "column": "*",
                "rule": "duplicate_rows",
                "severity": "medium",
                "evidence": {"duplicate_share": dup},
            }
        )

    return suspects
