"""Prediction upload validation — PV core (ARCHITECTURE §45.3).

Thin Phase 3A: PV01 (extension), PV04–PV09. Other codes return deferred /
``not computed`` stubs so callers can surface them without blocking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

Severity = Literal["block", "warn", "info", "sanitise", "deferred"]

_BOOL_TRUE = {"true", "1", "yes", "y", "t"}
_BOOL_FALSE = {"false", "0", "no", "n", "f"}


@dataclass
class PVIssue:
    code: str
    severity: Severity
    message: str
    column: str | None = None
    n_rows: int | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    ok: bool
    blocking: list[PVIssue] = field(default_factory=list)
    warnings: list[PVIssue] = field(default_factory=list)
    info: list[PVIssue] = field(default_factory=list)
    deferred: list[PVIssue] = field(default_factory=list)
    coerced: pd.DataFrame | None = None
    dropped_columns: list[str] = field(default_factory=list)
    rename_map: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        def _ser(items: list[PVIssue]) -> list[dict[str, Any]]:
            return [
                {
                    "code": i.code,
                    "severity": i.severity,
                    "message": i.message,
                    "column": i.column,
                    "n_rows": i.n_rows,
                    "details": i.details,
                }
                for i in items
            ]

        return {
            "ok": self.ok,
            "blocking": _ser(self.blocking),
            "warnings": _ser(self.warnings),
            "info": _ser(self.info),
            "deferred": _ser(self.deferred),
            "dropped_columns": list(self.dropped_columns),
            "rename_map": dict(self.rename_map),
            "n_rows": int(len(self.coerced)) if self.coerced is not None else None,
        }


def _norm_name(name: str) -> str:
    return "".join(str(name).strip().lower().split())


def _feature_specs(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return list(contract.get("features") or [])


def _required_feature_names(
    contract: dict[str, Any],
    required_names: list[str] | None,
) -> list[str]:
    if required_names is not None:
        return list(required_names)
    out: list[str] = []
    for feat in _feature_specs(contract):
        if feat.get("kind") == "identifier_like":
            continue
        if feat.get("role") == "excluded_by_default":
            continue
        out.append(str(feat["name"]))
    return out


def _match_columns(
    df_cols: list[str],
    required: list[str],
) -> tuple[dict[str, str], list[str], list[str]]:
    """Return rename_map (upload→contract), missing required, unmatched upload cols."""
    by_norm = {_norm_name(c): c for c in df_cols}
    rename: dict[str, str] = {}
    missing: list[str] = []
    used: set[str] = set()
    for req in required:
        if req in df_cols:
            rename[req] = req
            used.add(req)
            continue
        hit = by_norm.get(_norm_name(req))
        if hit is not None and hit not in used:
            rename[hit] = req
            used.add(hit)
            continue
        missing.append(req)
    extra = [c for c in df_cols if c not in used]
    return rename, missing, extra


def _coerce_boolean(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Return (coerced bool/nullable, fail mask)."""
    out = pd.Series(pd.NA, index=series.index, dtype="boolean")
    fail = pd.Series(False, index=series.index)
    for i, v in series.items():
        if pd.isna(v) or (isinstance(v, str) and v.strip() == ""):
            continue
        if isinstance(v, (bool, np.bool_)):
            out.loc[i] = bool(v)
            continue
        if isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool):
            if float(v) in (0.0, 1.0):
                out.loc[i] = bool(int(v))
            else:
                fail.loc[i] = True
            continue
        s = str(v).strip().lower()
        if s in _BOOL_TRUE:
            out.loc[i] = True
        elif s in _BOOL_FALSE:
            out.loc[i] = False
        else:
            fail.loc[i] = True
    return out, fail


def _coerce_numeric(series: pd.Series, *, integer: bool) -> tuple[pd.Series, pd.Series]:
    nums = pd.to_numeric(series, errors="coerce")
    fail = series.notna() & (series.astype(str).str.strip() != "") & nums.isna()
    if integer:
        # non-integer floats count as fail when original was non-null
        non_int = nums.notna() & (nums != np.floor(nums))
        fail = fail | non_int
    return nums, fail


def validate_predict_frame(
    df: pd.DataFrame,
    contract: dict[str, Any],
    *,
    required_names: list[str] | None = None,
    source_name: str | None = None,
) -> ValidationReport:
    """Run PV core checks; return coerced frame aligned to required feature names."""
    report = ValidationReport(ok=True)
    target = contract.get("target")
    required = _required_feature_names(contract, required_names)
    feat_by_name = {str(f["name"]): f for f in _feature_specs(contract)}

    # PV01 — thin: extension hint only when source_name provided
    if source_name:
        suf = Path(source_name).suffix.lower()
        if suf and suf not in {".csv", ".tsv", ".xlsx", ".xls", ".parquet"}:
            report.blocking.append(
                PVIssue(
                    code="PV01",
                    severity="block",
                    message=f"unsupported file type '{suf}'",
                    details={"source": source_name},
                )
            )

    rename, missing, extra = _match_columns(list(df.columns), required)
    report.rename_map = {k: v for k, v in rename.items() if k != v}

    # PV04 missing required
    if missing:
        report.blocking.append(
            PVIssue(
                code="PV04",
                severity="block",
                message=f"missing required feature columns: {missing}",
                details={"missing": missing},
            )
        )

    # PV05 extras + target
    drop_cols: list[str] = []
    if target and target in df.columns:
        drop_cols.append(str(target))
        report.warnings.append(
            PVIssue(
                code="PV05",
                severity="warn",
                message=f"target column '{target}' present — dropped to avoid leakage",
                column=str(target),
            )
        )
    extras_clean = [c for c in extra if c != target]
    if extras_clean:
        drop_cols.extend(extras_clean)
        report.warnings.append(
            PVIssue(
                code="PV05",
                severity="warn",
                message=f"extra columns ignored: {extras_clean}",
                details={"extra": extras_clean},
            )
        )
    report.dropped_columns = drop_cols

    # Deferred stubs for full §45 matrix
    for code, msg in (
        ("PV02", "size/row caps not computed in thin 3A"),
        ("PV03", "encoding/delimiter sniff not computed in thin 3A"),
        ("PV10", "row-level OOD not computed in thin 3A"),
        ("PV11", "batch drift PSI/KS not computed in thin 3A"),
        ("PV12", "sequential history checks not computed in thin 3A"),
        ("PV13", "TS horizon checks not computed in thin 3A"),
        ("PV14", "constant/all-NaN column scan not computed in thin 3A"),
        ("PV15", "formula sanitise applied on export only in thin 3A"),
        ("PV16", "PII masking not computed in thin 3A"),
    ):
        report.deferred.append(PVIssue(code=code, severity="deferred", message=msg))

    if report.blocking:
        report.ok = False
        return report

    # Build aligned frame via rename
    aligned = df.rename(columns=rename)
    work = pd.DataFrame(index=aligned.index)
    n = len(aligned)
    fail_rows = pd.Series(False, index=aligned.index)

    for name in required:
        feat = feat_by_name.get(name, {})
        kind = feat.get("kind", "numeric")
        raw = aligned[name] if name in aligned.columns else pd.Series(pd.NA, index=aligned.index)

        # PV09 missing in non-nullable
        if not feat.get("nullable", True) and raw.isna().any():
            n_miss = int(raw.isna().sum())
            report.warnings.append(
                PVIssue(
                    code="PV09",
                    severity="warn",
                    message=f"missing values in non-nullable feature '{name}' ({n_miss} rows)",
                    column=name,
                    n_rows=n_miss,
                )
            )

        if kind == "boolean":
            coerced, fail = _coerce_boolean(raw)
            work[name] = coerced
        elif kind == "categorical":
            work[name] = raw.astype("string")
            fail = pd.Series(False, index=raw.index)
            cats = {str(c) for c in (feat.get("categories") or [])}
            if cats:
                present = work[name].dropna().astype(str)
                unseen_mask = ~present.isin(cats)
                # map back to full index
                unseen = pd.Series(False, index=raw.index)
                unseen.loc[present.index[unseen_mask.to_numpy()]] = True
                n_unseen = int(unseen.sum())
                if n_unseen:
                    report.warnings.append(
                        PVIssue(
                            code="PV07",
                            severity="warn",
                            message=f"unseen categories in '{name}' ({n_unseen} rows)",
                            column=name,
                            n_rows=n_unseen,
                            details={
                                "examples": present[unseen_mask].unique()[:5].tolist(),
                            },
                        )
                    )
        else:
            # numeric (default) — also used for unknown kinds
            integer = bool(feat.get("integer", False))
            coerced, fail = _coerce_numeric(raw, integer=integer)
            work[name] = coerced
            # PV08 range
            if coerced.notna().any():
                p01, p99 = feat.get("p01"), feat.get("p99")
                mn, mx = feat.get("min"), feat.get("max")
                vals = coerced.dropna()
                if p01 is not None and p99 is not None:
                    band = (vals < float(p01)) | (vals > float(p99))
                    if band.any():
                        report.warnings.append(
                            PVIssue(
                                code="PV08",
                                severity="warn",
                                message=f"values outside [p01,p99] in '{name}'",
                                column=name,
                                n_rows=int(band.sum()),
                                details={"flag": "range_warning"},
                            )
                        )
                if mn is not None and mx is not None:
                    oob = (vals < float(mn)) | (vals > float(mx))
                    if oob.any():
                        report.warnings.append(
                            PVIssue(
                                code="PV08",
                                severity="warn",
                                message=f"values outside [min,max] in '{name}'",
                                column=name,
                                n_rows=int(oob.sum()),
                                details={"flag": "out_of_range"},
                            )
                        )

        fail_rows = fail_rows | fail
        n_fail = int(fail.sum())
        if n_fail:
            # accumulate per-column dtype fails; PV06 decided below
            report.warnings.append(
                PVIssue(
                    code="PV06",
                    severity="warn",
                    message=f"dtype coercion failed for '{name}' ({n_fail} rows)",
                    column=name,
                    n_rows=n_fail,
                )
            )

    n_fail_rows = int(fail_rows.sum())
    fail_pct = (n_fail_rows / n) if n else 0.0
    if fail_pct > 0.05:
        report.blocking.append(
            PVIssue(
                code="PV06",
                severity="block",
                message=f"dtype coercion failed for {fail_pct:.1%} of rows (>{0.05:.0%} threshold)",
                n_rows=n_fail_rows,
                details={"fail_pct": fail_pct},
            )
        )
        # demote per-column PV06 warns that led to block — keep them as warn details
    if report.blocking:
        report.ok = False
        report.coerced = work
        return report

    report.coerced = work[required]
    report.ok = True
    return report


def load_predict_table(path: str | Path, *, max_rows: int | None = 100_000) -> pd.DataFrame:
    """Load CSV/TSV/XLSX/Parquet for thin predict validation."""
    p = Path(path)
    suf = p.suffix.lower()
    if suf in {".csv", ".tsv"}:
        sep = "\t" if suf == ".tsv" else ","
        return pd.read_csv(p, sep=sep, nrows=max_rows)
    if suf in {".xlsx", ".xls"}:
        return pd.read_excel(p, engine="calamine", nrows=max_rows)
    if suf == ".parquet":
        df = pd.read_parquet(p)
        return df if max_rows is None else df.iloc[:max_rows]
    raise ValueError(f"unsupported predict file type: {suf}")
