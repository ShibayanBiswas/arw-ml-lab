"""Tabular readers → Parquet (ARCHITECTURE §9)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from labcore.security.upload_guard import XlsxUploadRejected, inspect_xlsx_archive


def content_hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def content_hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tabular(
    path: str | Path,
    *,
    sheet_name: str | int | None = 0,
    encoding: str | None = None,
) -> pd.DataFrame:
    """Load CSV/TSV/XLSX/Parquet/Feather/JSONL into a pandas DataFrame."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".parquet"}:
        return pd.read_parquet(path)
    if suffix in {".feather", ".arrow"}:
        return pd.read_feather(path)
    if suffix in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True)
    if suffix in {".xlsx", ".xls"}:
        try:
            inspect_xlsx_archive(path)
        except XlsxUploadRejected as exc:
            raise ValueError(exc.message) from exc
        return pd.read_excel(
            path, sheet_name=sheet_name if sheet_name is not None else 0, engine="calamine"
        )
    # CSV / TSV / .data — sniff via pandas + optional charset
    enc = encoding
    if enc is None:
        from charset_normalizer import from_path

        guess = from_path(path).best()
        enc = guess.encoding if guess else "utf-8"
    sep = "\t" if suffix == ".tsv" else None
    return pd.read_csv(path, sep=sep, encoding=enc, engine="python")


def write_parquet(df: pd.DataFrame, path: str | Path) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return content_hash_file(path)


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Dedupe column names; keep originals as .attrs labels."""
    out = df.copy()
    labels: dict[str, str] = {}
    seen: dict[str, int] = {}
    new_cols: list[str] = []
    for c in out.columns:
        raw = str(c)
        base = raw.strip() or "col"
        base = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in base)
        n = seen.get(base, 0)
        seen[base] = n + 1
        name = base if n == 0 else f"{base}_{n}"
        labels[name] = raw
        new_cols.append(name)
    out.columns = new_cols
    out.attrs["column_labels"] = labels
    return out


def dataframe_meta(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "n_rows": int(len(df)),
        "n_cols": int(df.shape[1]),
        "columns": list(map(str, df.columns)),
        "memory_bytes": int(df.memory_usage(deep=True).sum()),
    }
