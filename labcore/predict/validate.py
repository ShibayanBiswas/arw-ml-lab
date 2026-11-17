"""Prediction upload validation — PV01–PV16 (ARCHITECTURE §45.3).

Implemented: PV01–PV09, PV10 (contract-stat OOD), PV11 (PSI/KS when ``reference_df``),
PV12 (sequential time/sort/dupes/lookback when ``time_column``), PV13 (HorizonGuard
when series meta + h_request), PV14–PV16.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from labcore.security.formula_escape import FORMULA_TRIGGER_PREFIXES, escape_formula_export_cell
from labcore.security.upload_guard import XlsxUploadRejected, inspect_xlsx_archive

Severity = Literal["block", "warn", "info", "sanitise", "deferred"]

_BOOL_TRUE = {"true", "1", "yes", "y", "t"}
_BOOL_FALSE = {"false", "0", "no", "n", "f"}

_FORMULA_PREFIXES = FORMULA_TRIGGER_PREFIXES

DEFAULT_MAX_BYTES = 50 * 1024 * 1024  # 50 MB
DEFAULT_MAX_ROWS = 1_000_000


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
    insufficient_history_rows: list[Any] = field(default_factory=list)

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


def check_zip_bomb(path: Path) -> PVIssue | None:
    """PV01 zip-bomb guard for XLSX (SEC-05 / ``labcore.security.upload_guard``)."""
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        return None
    try:
        inspect_xlsx_archive(path)
    except XlsxUploadRejected as exc:
        return PVIssue(
            code="PV01",
            severity="block",
            message=exc.message,
            details=dict(exc.details, source=str(path)),
        )
    return None


def sniff_csv_meta(raw: bytes) -> dict[str, Any]:
    """PV03 — encoding + delimiter sniff (UTF-8 / UTF-8-BOM / cp1252)."""
    encoding = "utf-8"
    if raw.startswith(b"\xef\xbb\xbf"):
        encoding = "utf-8-sig"
        text = raw.decode("utf-8-sig", errors="replace")
    else:
        try:
            text = raw.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            text = raw.decode("cp1252", errors="replace")
            encoding = "cp1252"
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t|;")
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = "\t" if sample.count("\t") > sample.count(",") else ","
    # header + duplicate column names
    reader = csv.reader(io.StringIO(sample), delimiter=delimiter)
    try:
        header = next(reader)
    except StopIteration:
        header = []
    dupes = [h for h in header if header.count(h) > 1]
    return {
        "encoding": encoding,
        "delimiter": delimiter,
        "header": header,
        "duplicate_headers": sorted(set(dupes)),
        "has_header": bool(header),
    }


def _sanitise_formula_cell(val: Any) -> tuple[Any, bool]:
    """PV15 — treat formula-like cells as text (prefix with ')."""
    if not isinstance(val, str):
        return val, False
    escaped = escape_formula_export_cell(val)
    return escaped, escaped != val


def _row_ood_scores(
    work: pd.DataFrame,
    feat_by_name: dict[str, dict[str, Any]],
    required: list[str],
) -> np.ndarray:
    """PV10 proxy: max |z| vs contract median / (p99−p01) scale (no refit)."""
    n = len(work)
    scores = np.zeros(n, dtype=float)
    for name in required:
        feat = feat_by_name.get(name, {})
        if feat.get("kind") != "numeric":
            continue
        med = feat.get("median")
        p01, p99 = feat.get("p01"), feat.get("p99")
        if med is None or p01 is None or p99 is None:
            continue
        scale = abs(float(p99) - float(p01)) / 2.33
        if scale < 1e-12:
            scale = 1.0
        col = pd.to_numeric(work[name], errors="coerce")
        z = ((col - float(med)) / scale).abs().fillna(0.0).to_numpy(dtype=float)
        scores = np.maximum(scores, z)
    return scores


def _lookback_from_contract(contract: dict[str, Any]) -> int:
    """Max lag / lookback from contract (explicit lookback or derived lag features)."""
    raw = contract.get("lookback")
    if raw is not None:
        try:
            return max(0, int(raw))
        except (TypeError, ValueError):
            pass
    max_lag = 0
    for der in contract.get("derived_features") or []:
        if not isinstance(der, dict):
            continue
        for key in ("lookback", "lag", "n_lags", "window"):
            if der.get(key) is None:
                continue
            try:
                max_lag = max(max_lag, int(der[key]))
            except (TypeError, ValueError):
                continue
        name = str(der.get("name") or "")
        if "lag" in name.lower():
            digits = "".join(ch for ch in name if ch.isdigit())
            if digits:
                max_lag = max(max_lag, int(digits))
    return max_lag


def _resolve_upload_col(df: pd.DataFrame, contract_name: str | None) -> str | None:
    """Map a contract column name onto the upload frame (exact then normalised)."""
    if not contract_name:
        return None
    cols = list(map(str, df.columns))
    if contract_name in cols:
        return contract_name
    by_norm = {_norm_name(c): c for c in cols}
    return by_norm.get(_norm_name(contract_name))


def _apply_pv12_sequential(
    df: pd.DataFrame,
    contract: dict[str, Any],
    report: ValidationReport,
) -> None:
    """PV12 — sequential (non-TS) time parse / sort / dupes / lookback (§45.3)."""
    time_col = contract.get("time_column")
    if not time_col:
        report.deferred.append(
            PVIssue(
                code="PV12",
                severity="deferred",
                message="sequential history checks not computed yet",
            )
        )
        return

    upload_time = _resolve_upload_col(df, str(time_col))
    if upload_time is None:
        report.blocking.append(
            PVIssue(
                code="PV12",
                severity="block",
                message=f"time column '{time_col}' missing from upload",
                column=str(time_col),
            )
        )
        return

    parsed = pd.to_datetime(df[upload_time], errors="coerce", utc=False, format="mixed")
    n_bad = int(parsed.isna().sum())
    if n_bad == len(df):
        report.blocking.append(
            PVIssue(
                code="PV12",
                severity="block",
                message=f"time column '{time_col}' did not parse for any row",
                column=str(time_col),
                n_rows=n_bad,
            )
        )
        return
    if n_bad > 0:
        report.warnings.append(
            PVIssue(
                code="PV12",
                severity="warn",
                message=f"time column '{time_col}' failed to parse on {n_bad} row(s)",
                column=str(time_col),
                n_rows=n_bad,
            )
        )

    series_col_name = contract.get("series_column")
    upload_series = _resolve_upload_col(df, str(series_col_name) if series_col_name else None)

    work = pd.DataFrame({"_t": parsed})
    if upload_series is not None:
        work["_s"] = df[upload_series].astype(str)
    else:
        work["_s"] = "_"

    # Sort check (offer auto-sort)
    needs_sort = False
    for _, grp in work.groupby("_s", sort=False):
        t = grp["_t"]
        valid = t.dropna()
        if len(valid) >= 2 and not valid.is_monotonic_increasing:
            needs_sort = True
            break
    if needs_sort:
        report.warnings.append(
            PVIssue(
                code="PV12",
                severity="warn",
                message="rows are not sorted by time within series — auto-sort offered",
                column=str(time_col),
                details={"auto_sort": True},
            )
        )
    else:
        report.info.append(
            PVIssue(
                code="PV12",
                severity="info",
                message="rows sorted by time within series",
                column=str(time_col),
            )
        )

    # Duplicate timestamps per series
    dup_mask = work.duplicated(subset=["_s", "_t"], keep=False) & work["_t"].notna()
    n_dup = int(dup_mask.sum())
    if n_dup > 0:
        report.warnings.append(
            PVIssue(
                code="PV12",
                severity="warn",
                message=f"duplicate timestamps per series on {n_dup} row(s)",
                column=str(time_col),
                n_rows=n_dup,
            )
        )

    lookback = _lookback_from_contract(contract)
    if lookback <= 0:
        report.info.append(
            PVIssue(
                code="PV12",
                severity="info",
                message="no lag lookback required for this contract",
                details={"lookback": 0},
            )
        )
        return

    # Per series: first ``lookback`` rows (after chronological order) lack history
    insufficient_idx: list[Any] = []
    for _, grp in work.groupby("_s", sort=False):
        order = grp["_t"].argsort(kind="mergesort")
        ordered = grp.iloc[order]
        # skip unparseable times at the head of the ranking
        valid_pos = [i for i, ok in enumerate(ordered["_t"].notna().tolist()) if ok]
        for pos in valid_pos[:lookback]:
            insufficient_idx.append(ordered.index[pos])

    n_insuff = len(insufficient_idx)
    if n_insuff > 0 and n_insuff >= int(work["_t"].notna().sum()):
        report.blocking.append(
            PVIssue(
                code="PV12",
                severity="block",
                message=(
                    f"lookback={lookback}: insufficient history for all rows "
                    "(need prior bars for lag features)"
                ),
                column=str(time_col),
                n_rows=n_insuff,
                details={
                    "lookback": lookback,
                    "insufficient_history": True,
                    "row_indices": [int(i) if isinstance(i, (int, np.integer)) else str(i)
                                    for i in insufficient_idx[:50]],
                },
            )
        )
    elif n_insuff > 0:
        report.insufficient_history_rows = list(insufficient_idx)
        report.warnings.append(
            PVIssue(
                code="PV12",
                severity="warn",
                message=(
                    f"lookback={lookback}: {n_insuff} row(s) marked insufficient_history "
                    "for lag features"
                ),
                column=str(time_col),
                n_rows=n_insuff,
                details={
                    "lookback": lookback,
                    "insufficient_history": True,
                    "row_indices": [int(i) if isinstance(i, (int, np.integer)) else str(i)
                                    for i in insufficient_idx[:50]],
                },
            )
        )
    else:
        report.info.append(
            PVIssue(
                code="PV12",
                severity="info",
                message=f"lookback={lookback}: history available for all rows",
                details={"lookback": lookback},
            )
        )


def validate_predict_frame(
    df: pd.DataFrame,
    contract: dict[str, Any],
    *,
    required_names: list[str] | None = None,
    source_name: str | None = None,
    max_rows: int = DEFAULT_MAX_ROWS,
    max_bytes: int | None = None,
    source_bytes: int | None = None,
    csv_meta: dict[str, Any] | None = None,
    reference_df: pd.DataFrame | None = None,
    h_request: int | None = None,
) -> ValidationReport:
    """Run PV checks; return coerced frame aligned to required feature names."""
    report = ValidationReport(ok=True)
    target = contract.get("target")
    required = _required_feature_names(contract, required_names)
    feat_by_name = {str(f["name"]): f for f in _feature_specs(contract)}

    # PV01 — extension hint when source_name provided
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

    # PV02 — size / row caps
    n_rows = int(len(df))
    if n_rows > max_rows:
        report.blocking.append(
            PVIssue(
                code="PV02",
                severity="block",
                message=f"row count {n_rows} exceeds cap {max_rows}",
                n_rows=n_rows,
                details={"max_rows": max_rows},
            )
        )
    cap_bytes = DEFAULT_MAX_BYTES if max_bytes is None else max_bytes
    if source_bytes is not None and source_bytes > cap_bytes:
        report.blocking.append(
            PVIssue(
                code="PV02",
                severity="block",
                message=f"upload size {source_bytes} exceeds cap {cap_bytes}",
                details={"source_bytes": source_bytes, "max_bytes": cap_bytes},
            )
        )
    else:
        report.info.append(
            PVIssue(
                code="PV02",
                severity="info",
                message=f"rows={n_rows} within cap {max_rows}",
                n_rows=n_rows,
            )
        )

    # PV03 — encoding / delimiter / duplicate headers
    if csv_meta is not None:
        dups = list(csv_meta.get("duplicate_headers") or [])
        if dups:
            report.blocking.append(
                PVIssue(
                    code="PV03",
                    severity="block",
                    message=f"duplicate column names: {dups}",
                    details=csv_meta,
                )
            )
        else:
            report.info.append(
                PVIssue(
                    code="PV03",
                    severity="info",
                    message=(
                        f"encoding={csv_meta.get('encoding')} "
                        f"delimiter={csv_meta.get('delimiter')!r}"
                    ),
                    details=csv_meta,
                )
            )
    else:
        # still check duplicate columns on the frame
        dups = [c for c in df.columns if list(df.columns).count(c) > 1]
        if dups:
            report.blocking.append(
                PVIssue(
                    code="PV03",
                    severity="block",
                    message=f"duplicate column names: {sorted(set(map(str, dups)))}",
                )
            )

    rename, missing, extra = _match_columns(list(map(str, df.columns)), required)
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

    # PV11 — batch drift when a training reference frame is supplied (oneshot-c242)
    if reference_df is not None and len(reference_df) > 0 and len(df) > 0:
        try:
            from labcore.monitoring.drift import ks_drift_report, psi_drift_report

            numeric = [
                n
                for n in required
                if n in df.columns
                and n in reference_df.columns
                and feat_by_name.get(n, {}).get("kind", "numeric") == "numeric"
            ]
            if numeric:
                ref = reference_df[numeric].to_numpy(dtype=float)
                cur = df[numeric].to_numpy(dtype=float)
                ks = ks_drift_report(ref, cur, feature_names=numeric)
                psi = psi_drift_report(ref, cur, feature_names=numeric)
                report.warnings.append(
                    PVIssue(
                        code="PV11",
                        severity="warn" if (ks.get("n_drifted") or 0) > 0 else "info",
                        message=(
                            f"batch drift KS drifted={ks.get('n_drifted')} "
                            f"PSI drifted={psi.get('n_drifted')}"
                        ),
                        details={"ks": ks, "psi": psi},
                    )
                )
            else:
                report.deferred.append(
                    PVIssue(
                        code="PV11",
                        severity="deferred",
                        message="batch drift PSI/KS: no overlapping numeric features",
                    )
                )
        except Exception as exc:  # noqa: BLE001 — never block predict on drift I/O
            report.warnings.append(
                PVIssue(
                    code="PV11",
                    severity="warn",
                    message=f"batch drift not computed: {type(exc).__name__}",
                )
            )
    else:
        report.deferred.append(
            PVIssue(code="PV11", severity="deferred", message="batch drift PSI/KS not computed yet")
        )

    # PV16 — flag identifier_like / PII-ish features present in the upload (oneshot-c243)
    pii_cols = [
        n
        for n, spec in feat_by_name.items()
        if spec.get("kind") == "identifier_like" and n in df.columns
    ]
    if pii_cols:
        report.warnings.append(
            PVIssue(
                code="PV16",
                severity="warn",
                message=(
                    "identifier_like columns present — never send cell values to VLM/LLM; "
                    f"columns={pii_cols}"
                ),
                details={"columns": pii_cols, "policy": "redact_before_ai"},
            )
        )
    else:
        report.info.append(
            PVIssue(
                code="PV16",
                severity="info",
                message="no identifier_like columns in this batch",
            )
        )

    # PV13 — HorizonGuard when h_request + series length/freq are known (oneshot-c245)
    series_meta = contract.get("timeseries") or contract.get("series") or {}
    n_series = int(series_meta.get("n") or series_meta.get("n_obs") or 0)
    freq = str(series_meta.get("freq") or series_meta.get("frequency") or "")
    h_req = h_request if h_request is not None else series_meta.get("h_request")
    if h_req is not None and n_series > 0 and freq:
        try:
            from labcore.integrity.horizon_guard_policy import (
                horizon_reject_reasons,
                horizon_request_allowed,
            )

            h_req_i = int(h_req)
            allowed = horizon_request_allowed(n_series, freq, h_req_i)
            if not allowed:
                reasons = horizon_reject_reasons(n_series, freq, h_req_i)
                report.blocking.append(
                    PVIssue(
                        code="PV13",
                        severity="block",
                        message=f"forecast horizon h={h_req_i} exceeds HorizonGuard",
                        details={"reasons": reasons, "n": n_series, "freq": freq},
                    )
                )
            else:
                report.info.append(
                    PVIssue(
                        code="PV13",
                        severity="info",
                        message=f"forecast horizon h={h_req_i} within HorizonGuard",
                        details={"n": n_series, "freq": freq},
                    )
                )
        except Exception as exc:  # noqa: BLE001
            report.warnings.append(
                PVIssue(
                    code="PV13",
                    severity="warn",
                    message=f"TS horizon check failed: {type(exc).__name__}",
                )
            )
    else:
        report.deferred.append(
            PVIssue(code="PV13", severity="deferred", message="TS horizon checks not computed yet")
        )

    # PV12 — sequential time / sort / dupes / lookback (oneshot-c246)
    _apply_pv12_sequential(df, contract, report)

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

    # PV14 — constant / all-NaN columns
    for name in required:
        col = work[name]
        if col.isna().all():
            report.warnings.append(
                PVIssue(
                    code="PV14",
                    severity="warn",
                    message=f"column '{name}' is all-NaN in upload",
                    column=name,
                )
            )
        elif col.nunique(dropna=True) <= 1:
            report.warnings.append(
                PVIssue(
                    code="PV14",
                    severity="warn",
                    message=f"column '{name}' is constant in upload",
                    column=name,
                )
            )

    # PV15 — formula injection sanitise on string-like cells
    sanitised = 0
    for name in required:
        if feat_by_name.get(name, {}).get("kind") == "numeric":
            continue
        if name not in work.columns:
            continue
        new_vals = []
        changed = False
        for v in work[name].tolist():
            nv, hit = _sanitise_formula_cell(v)
            new_vals.append(nv)
            if hit:
                sanitised += 1
                changed = True
        if changed:
            work[name] = new_vals
    if sanitised:
        report.info.append(
            PVIssue(
                code="PV15",
                severity="sanitise",
                message=f"sanitised {sanitised} formula-like cell(s) with leading '",
                n_rows=sanitised,
            )
        )
    else:
        report.info.append(
            PVIssue(code="PV15", severity="info", message="no formula-like cells found")
        )

    # PV10 — row-level OOD from contract numeric stats
    ood = _row_ood_scores(work, feat_by_name, required)
    if ood.size and np.any(ood > 0):
        # flag above ~99th of a unit half-normal proxy: z > 3
        flagged = ood > 3.0
        n_flag = int(flagged.sum())
        if n_flag:
            report.warnings.append(
                PVIssue(
                    code="PV10",
                    severity="warn",
                    message=f"row-level OOD flag on {n_flag} rows (contract-stat z>3)",
                    n_rows=n_flag,
                    details={
                        "threshold": 3.0,
                        "max_score": float(np.max(ood)),
                        "flagged_row_indices": np.where(flagged)[0][:50].tolist(),
                    },
                )
            )
        else:
            report.info.append(
                PVIssue(
                    code="PV10",
                    severity="info",
                    message="no row-level OOD flags",
                    details={"max_score": float(np.max(ood))},
                )
            )
    else:
        report.info.append(
            PVIssue(
                code="PV10",
                severity="info",
                message="OOD not scored (no numeric contract stats)",
            )
        )

    report.coerced = work[required]
    report.ok = True
    return report


def load_predict_table(
    path: str | Path,
    *,
    max_rows: int | None = 100_000,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load CSV/TSV/XLSX/Parquet; return (frame, meta) with PV01/PV03 hints."""
    p = Path(path)
    suf = p.suffix.lower()
    meta: dict[str, Any] = {
        "source_bytes": p.stat().st_size if p.exists() else None,
        "csv_meta": None,
    }
    bomb = check_zip_bomb(p)
    if bomb is not None:
        raise ValueError(bomb.message)

    if suf in {".csv", ".tsv"}:
        raw = p.read_bytes()
        csv_meta = sniff_csv_meta(raw)
        if suf == ".tsv":
            csv_meta["delimiter"] = "\t"
        meta["csv_meta"] = csv_meta
        sep = csv_meta["delimiter"]
        encoding = csv_meta["encoding"]
        df = pd.read_csv(p, sep=sep, nrows=max_rows, encoding=encoding)
        return df, meta
    if suf in {".xlsx", ".xls"}:
        df = pd.read_excel(p, engine="calamine", nrows=max_rows)
        return df, meta
    if suf == ".parquet":
        df = pd.read_parquet(p)
        return (df if max_rows is None else df.iloc[:max_rows]), meta
    raise ValueError(f"unsupported predict file type: {suf}")
