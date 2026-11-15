"""Sample dataset loader — DS1–DS33 via datasets_manifest + presets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from labcore.data.infer import ColumnProfile, infer_schema
from labcore.data.readers import dataframe_meta, normalise_columns, read_tabular, write_parquet
from labcore.data.task_detect import TaskSpec, detect_task

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "data" / "samples"
MANIFEST_PATH = SAMPLES / "datasets_manifest.json"
PRESETS = SAMPLES / "presets"


def list_samples() -> list[dict[str, Any]]:
    man = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    items = list(man.get("bundled", [])) + list(man.get("lazy", []))
    return items


def _resolve_file(entry: dict[str, Any]) -> Path:
    rel = entry["file"]
    path = ROOT / rel if not Path(rel).is_absolute() else Path(rel)
    if not path.exists():
        # bundled files are relative to data/samples
        alt = SAMPLES / Path(rel).name
        if alt.exists():
            return alt
        nested = SAMPLES / str(rel).replace("data/samples/", "")
        if nested.exists():
            return Path(nested)
        raise FileNotFoundError(f"Sample file not found: {rel}")
    return Path(path)


def load_preset(ds_id: str) -> dict[str, Any]:
    key = ds_id.lower()
    path = PRESETS / f"{key}.yaml"
    if not path.exists():
        # ds3.yaml style
        num = "".join(ch for ch in ds_id if ch.isdigit())
        path = PRESETS / f"ds{num}.yaml"
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Preset {path} must be a mapping")
    return loaded


def load_sample(
    ds_id: str,
    *,
    parquet_dir: Path | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Load a catalogue sample into a normalised frame + schema + task spec."""
    _ = seed
    entries = {e["id"]: e for e in list_samples()}
    if ds_id not in entries:
        raise KeyError(f"Unknown sample id: {ds_id}")
    entry = entries[ds_id]
    preset = load_preset(ds_id)
    path = _resolve_file(entry)
    df = read_tabular(path)
    # Headerless datasets
    if ds_id == "DS1":
        df.columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
    df = normalise_columns(df)
    schema = infer_schema(df)
    target = preset.get("target")
    # Strip notes from target field like 'class (col 5)'
    if isinstance(target, str) and "(" in target:
        target = target.split("(")[0].strip().strip('"')
    family = preset.get("family")
    task = detect_task(
        df,
        schema,
        target=target if target and target in df.columns else None,
        family_hint=family,
    )
    out_dir = parquet_dir or (ROOT / ".cache" / "samples")
    out_dir.mkdir(parents=True, exist_ok=True)
    pq = out_dir / f"{ds_id.lower()}.parquet"
    digest = write_parquet(df, pq)
    return {
        "id": ds_id,
        "name": entry.get("name"),
        "preset": preset,
        "path": str(pq),
        "content_hash": digest,
        "meta": dataframe_meta(df),
        "schema": [c.model_dump() for c in schema],
        "task": task.model_dump(),
        "dataframe": df,
    }


def load_sample_frame(ds_id: str) -> tuple[pd.DataFrame, TaskSpec, list[ColumnProfile]]:
    payload = load_sample(ds_id)
    schema = [ColumnProfile.model_validate(c) for c in payload["schema"]]
    task = TaskSpec.model_validate(payload["task"])
    frame = payload["dataframe"]
    assert isinstance(frame, pd.DataFrame)
    return frame, task, schema
