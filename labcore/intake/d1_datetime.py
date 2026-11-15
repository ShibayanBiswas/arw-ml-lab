"""D1 — Index / datetime detection — ARCHITECTURE §33.3."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

TIME_NAME_RE = re.compile(
    r"^(date|time|timestamp|datetime|dt|ds|period|month|year|as_?of|trade_?date|"
    r"obs(ervation)?_?date|day|week|quarter)$",
    re.I,
)
ENTITY_NAME_RE = re.compile(
    r"(ticker|symbol|isin|store|sku|customer_id|account|series|unique_id)", re.I
)


def _parse_rate_and_format(series: pd.Series) -> tuple[float, str | None, bool]:
    """Return parse_rate, format hint, ambiguous_day_month."""
    s = series.dropna()
    if s.empty:
        return 0.0, None, False
    if pd.api.types.is_datetime64_any_dtype(s):
        return 1.0, "%Y-%m-%d", False

    # numeric epoch / excel serial
    if pd.api.types.is_numeric_dtype(s):
        vals = s.astype(float)
        # seconds since epoch ~1990–2100
        epoch_ok = ((vals > 631152000) & (vals < 4102444800)).mean()
        if epoch_ok >= 0.95:
            return float(epoch_ok), "epoch_s", False
        excel_ok = ((vals >= 20000) & (vals <= 80000)).mean()
        if excel_ok >= 0.95 and TIME_NAME_RE.search(str(series.name) or ""):
            return float(excel_ok), "excel_serial", False

    text = s.astype(str)
    # Ambiguity: all day/month parts ≤ 12
    ambiguous = False
    dm = text.str.extract(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$")
    if dm.notna().all(axis=1).mean() >= 0.8:
        a = pd.to_numeric(dm[0], errors="coerce")
        b = pd.to_numeric(dm[1], errors="coerce")
        if ((a <= 12) & (b <= 12)).mean() >= 0.95 and not ((a > 12).any() or (b > 12).any()):
            ambiguous = True
        # India default dd/mm
        if (a > 12).any():
            fmt = "%d/%m/%Y"
        elif (b > 12).any():
            fmt = "%m/%d/%Y"
        else:
            fmt = "%d/%m/%Y"  # locale India
        parsed = pd.to_datetime(text, format=fmt, errors="coerce")
        # also try with 2-digit year
        if parsed.isna().mean() > 0.2:
            parsed = pd.to_datetime(text, dayfirst=True, errors="coerce")
        return float(parsed.notna().mean()), fmt, ambiguous

    # ISO / period-like before generic dayfirst
    if text.str.match(r"^\d{4}-\d{2}-\d{2}([ T].*)?$").mean() >= 0.8:
        parsed = pd.to_datetime(text, errors="coerce", utc=False)
        return float(parsed.notna().mean()), "%Y-%m-%d", False
    if text.str.match(r"^\d{4}-\d{2}$").mean() >= 0.8:
        parsed = pd.to_datetime(text, format="%Y-%m", errors="coerce")
        return float(parsed.notna().mean()), "%Y-%m", False

    parsed = pd.to_datetime(text, errors="coerce", utc=False)
    return float(parsed.notna().mean()), None, False


def _to_datetime(series: pd.Series, fmt: str | None) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(series):
        return pd.to_datetime(series)
    if fmt == "epoch_s":
        return pd.to_datetime(series, unit="s", errors="coerce")
    if fmt == "excel_serial":
        return pd.to_datetime(series, unit="D", origin="1899-12-30", errors="coerce")
    text = series.astype(str)
    if fmt == "%Y-%m":
        return pd.to_datetime(text, format="%Y-%m", errors="coerce")
    if fmt and "%" in fmt:
        # ISO date: ignore dayfirst
        if fmt.startswith("%Y-%m-%d"):
            return pd.to_datetime(text, errors="coerce")
        return pd.to_datetime(text, format=fmt, errors="coerce")
    if text.str.match(r"^\d{4}-\d{2}-\d{2}").mean() >= 0.8:
        return pd.to_datetime(text, errors="coerce")
    if text.str.match(r"^\d{4}-\d{2}$").mean() >= 0.8:
        return pd.to_datetime(text, format="%Y-%m", errors="coerce")
    return pd.to_datetime(text, dayfirst=True, errors="coerce")


def detect_datetime_index(df: pd.DataFrame, profile: dict[str, Any]) -> dict[str, Any]:
    cols = profile["columns"]
    candidates: list[dict[str, Any]] = []

    # Composite year + quarter
    names_l = {c.lower(): c for c in df.columns}
    if "year" in names_l and "quarter" in names_l:
        ycol, qcol = names_l["year"], names_l["quarter"]
        y = pd.to_numeric(df[ycol], errors="coerce")
        q = pd.to_numeric(df[qcol], errors="coerce")
        if y.notna().mean() > 0.9 and q.notna().mean() > 0.9:
            try:
                composed = pd.PeriodIndex.from_fields(
                    year=y.astype("Int64"), quarter=q.astype("Int64")
                ).to_timestamp()
            except Exception:
                composed = pd.to_datetime(
                    {
                        "year": y,
                        "month": (q.fillna(1).astype(int) - 1) * 3 + 1,
                        "day": 1,
                    },
                    errors="coerce",
                )
            parse_rate = float(composed.notna().mean())
            mono = (
                float(composed.dropna().is_monotonic_increasing) if composed.notna().any() else 0.0
            )
            # Prefer composite over bare year/quarter parts
            time_score = (
                0.30 * parse_rate
                + 0.20 * mono
                + 0.15 * 0.95
                + 0.15 * 0.5
                + 0.10 * 1.0
                + 0.10 * 0.2
                + 0.15  # composite bonus
            )
            candidates.append(
                {
                    "column": None,
                    "composite_of": [ycol, qcol],
                    "parse_rate": parse_rate,
                    "monotonic_fraction": mono,
                    "format": "year+quarter",
                    "ambiguous": False,
                    "time_score": time_score,
                    "parsed": composed,
                }
            )

    for i, name in enumerate(df.columns):
        meta = cols.get(name, {})
        parse_rate, fmt, ambiguous = _parse_rate_and_format(df[name])
        name_hint = (
            1.0
            if TIME_NAME_RE.search(name) or "date" in name.lower() or "time" in name.lower()
            else 0.0
        )
        if parse_rate < 0.5 and name_hint == 0 and meta.get("semantic_type") != "datetime":
            continue
        if parse_rate < 0.5 and name_hint == 0:
            continue
        parsed = _to_datetime(df[name], fmt)
        mono = float(
            (parsed.dropna().diff().dropna() >= pd.Timedelta(0)).mean()
            if parsed.notna().sum() > 1
            else 0.0
        )
        uniq = float(parsed.nunique(dropna=True) / max(parsed.notna().sum(), 1))
        position_hint = 1.0 if i == 0 else 0.0
        # regularity placeholder filled later by D2; use 0.5 for scoring seed
        time_score = (
            0.30 * parse_rate
            + 0.20 * mono
            + 0.15 * uniq
            + 0.15 * 0.5
            + 0.10 * name_hint
            + 0.10 * position_hint
        )
        candidates.append(
            {
                "column": name,
                "composite_of": None,
                "parse_rate": parse_rate,
                "monotonic_fraction": mono,
                "uniqueness_ratio": uniq,
                "name_hint": name_hint,
                "position_hint": position_hint,
                "format": fmt,
                "ambiguous": ambiguous,
                "time_score": time_score,
                "parsed": parsed,
            }
        )

    if not candidates:
        return {
            "accepted": None,
            "ambiguous_candidates": [],
            "entity": None,
            "questions": [],
        }

    # Prefer composites / high scores
    for c in candidates:
        if "time_score" not in c:
            c["time_score"] = (
                0.30 * c["parse_rate"]
                + 0.20 * c["monotonic_fraction"]
                + 0.15 * 0.9
                + 0.15 * 0.5
                + 0.10 * 1.0
                + 0.10 * 0.0
            )

    ranked = sorted(candidates, key=lambda x: x["time_score"], reverse=True)
    top = ranked[0]
    questions: list[str] = []
    ambiguous_pair: list[dict[str, Any]] = []

    if top.get("ambiguous"):
        questions.append(
            f"Date column '{top.get('column')}' has day and month both ≤ 12; "
            "confirm format (default India dd/mm)."
        )

    if len(ranked) >= 2 and abs(ranked[0]["time_score"] - ranked[1]["time_score"]) <= 0.1:
        top_comp = set(ranked[0].get("composite_of") or [])
        second_col = ranked[1].get("column")
        # Composite year+quarter vs its parts is not ambiguous — prefer composite
        parts_of_composite = bool(top_comp) and second_col in top_comp
        second_comp = set(ranked[1].get("composite_of") or [])
        first_col = ranked[0].get("column")
        reverse_parts = bool(second_comp) and first_col in second_comp
        if not parts_of_composite and not reverse_parts:
            ambiguous_pair = [
                {"column": ranked[0].get("column"), "score": ranked[0]["time_score"]},
                {"column": ranked[1].get("column"), "score": ranked[1]["time_score"]},
            ]
            questions.append(
                f"Ambiguous time index between {ranked[0].get('column')} and {ranked[1].get('column')}; please choose."
            )
        elif reverse_parts:
            # Prefer the composite candidate
            ranked[0], ranked[1] = ranked[1], ranked[0]
            top = ranked[0]

    accepted = None
    if top["time_score"] >= 0.6 and not ambiguous_pair:
        accepted = {
            "column": top.get("column"),
            "composite_of": top.get("composite_of"),
            "format": top.get("format"),
            "timezone": "Asia/Kolkata",
            "confidence": float(min(1.0, top["time_score"])),
            "reasons": [f"time_score={top['time_score']:.2f}"],
            "ambiguous_format": bool(top.get("ambiguous")),
        }

    # Panel entity
    entity = None
    if accepted and accepted.get("column"):
        tser = next(c["parsed"] for c in ranked if c.get("column") == accepted["column"])
        if tser.duplicated().any():
            for name in df.columns:
                if name == accepted["column"]:
                    continue
                nuniq = df[name].nunique(dropna=True)
                if 2 <= nuniq <= max(len(df) // 3, 2):
                    combo = pd.DataFrame({"e": df[name], "t": tser}).dropna()
                    if combo.duplicated().sum() == 0 and (
                        ENTITY_NAME_RE.search(name) or nuniq < len(df) * 0.5
                    ):
                        entity = {
                            "column": name,
                            "confidence": 0.8,
                            "reasons": ["panel_unique_entity_time"],
                        }
                        break

    # strip parsed series from export
    clean_ranked = []
    for c in ranked:
        d = {k: v for k, v in c.items() if k != "parsed"}
        clean_ranked.append(d)

    return {
        "accepted": accepted,
        "candidates": clean_ranked,
        "ambiguous_candidates": ambiguous_pair,
        "entity": entity,
        "questions": questions,
        "_parsed_map": {
            (c.get("column") or tuple(c.get("composite_of") or [])): c.get("parsed") for c in ranked
        },
    }
