"""D7 — Schema diff — ARCHITECTURE §33.11."""

from __future__ import annotations

from typing import Any

import pandas as pd
from scipy import stats

try:
    from rapidfuzz.distance import JaroWinkler
except ImportError:  # pragma: no cover
    JaroWinkler = None  # type: ignore[misc, assignment]


def _jw(a: str, b: str) -> float:
    if JaroWinkler is None:
        # fallback ratio
        return float(a.lower() == b.lower())
    return float(JaroWinkler.similarity(a, b))


def schema_diff(
    parent_df: pd.DataFrame,
    child_df: pd.DataFrame,
    parent_profile: dict[str, Any] | None = None,
    child_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    parent_cols = set(parent_df.columns)
    child_cols = set(child_df.columns)
    added = sorted(child_cols - parent_cols)
    removed = sorted(parent_cols - child_cols)
    changes: list[dict[str, Any]] = []
    breaking = False

    for c in added:
        changes.append({"kind": "column_added", "column": c, "severity": "info"})
    for c in removed:
        changes.append({"kind": "column_removed", "column": c, "severity": "breaking"})
        breaking = True

    # rename detection
    renames: list[dict[str, Any]] = []
    used_new: set[str] = set()
    for old in removed:
        best = None
        best_score = 0.0
        for new in added:
            if new in used_new:
                continue
            score = _jw(old, new)
            if score >= 0.85 and score > best_score:
                # distribution similarity if both numeric
                dist_ok = True
                if old in parent_df.columns and new in child_df.columns:
                    a = pd.to_numeric(parent_df[old], errors="coerce").dropna()
                    b = pd.to_numeric(child_df[new], errors="coerce").dropna()
                    if len(a) > 20 and len(b) > 20:
                        try:
                            _, p = stats.ks_2samp(a, b)
                            dist_ok = float(p) > 0.05
                        except Exception:
                            dist_ok = True
                if dist_ok:
                    best, best_score = new, score
        if best is not None:
            renames.append({"from": old, "to": best, "jw": best_score})
            used_new.add(best)
            changes.append(
                {
                    "kind": "rename_proposed",
                    "from": old,
                    "to": best,
                    "jw": best_score,
                    "severity": "warning",
                }
            )
            # rename is not automatically breaking
            breaking = any(ch for ch in changes if ch.get("kind") == "column_removed" and ch.get("column") != old) or any(
                ch.get("kind") == "type_change" for ch in changes
            )

    # type changes on overlapping columns
    for c in sorted(parent_cols & child_cols):
        pt = str(parent_df[c].dtype)
        ct = str(child_df[c].dtype)
        p_num = pd.api.types.is_numeric_dtype(parent_df[c])
        c_num = pd.api.types.is_numeric_dtype(child_df[c])
        if p_num and not c_num:
            changes.append(
                {
                    "kind": "type_change",
                    "column": c,
                    "from": pt,
                    "to": ct,
                    "severity": "breaking",
                }
            )
            breaking = True
        # missingness
        pm = float(parent_df[c].isna().mean())
        cm = float(child_df[c].isna().mean())
        if abs(cm - pm) > 0.10:
            changes.append(
                {
                    "kind": "missingness_change",
                    "column": c,
                    "delta_pp": (cm - pm) * 100,
                    "severity": "warning",
                }
            )

    # if only renames explain add/remove, compatible
    if renames and len(renames) == len(removed) == len(added):
        # still check type changes
        breaking = any(ch.get("severity") == "breaking" and ch.get("kind") == "type_change" for ch in changes)
        # remove pure add/remove that were paired
        changes = [ch for ch in changes if ch.get("kind") not in {"column_added", "column_removed"}] + [
            ch for ch in changes if ch.get("kind") == "rename_proposed"
        ]

    severity = "breaking" if breaking else ("warning" if changes else "info")
    return {
        "changes": changes,
        "renames": renames,
        "breaking": breaking,
        "severity": severity,
        "compatible": not breaking,
    }
