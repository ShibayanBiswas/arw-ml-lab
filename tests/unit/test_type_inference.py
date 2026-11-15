"""AC: DS3 type inference."""

from __future__ import annotations

from labcore.data.infer import infer_schema
from labcore.data.samples import load_sample_frame
from labcore.data.task_detect import detect_task


def test_ds3_type_inference() -> None:
    df, task, schema = load_sample_frame("DS3")
    by = {c.name: c for c in schema}
    assert "Survived" in by
    assert by["Survived"].semantic_type in {"boolean", "numeric_discrete"}
    assert by["Age"].semantic_type == "continuous"
    assert by["Age"].pct_missing > 0.15
    assert by["Name"].semantic_type == "text"
    assert by["Name"].role_suggestion == "exclude"
    assert by["Cabin"].semantic_type == "high_cardinality"
    # Task is binary
    assert task.task == "binary"
    assert task.target == "Survived"


def test_infer_schema_roundtrip_columns() -> None:
    df, _, _ = load_sample_frame("DS3")
    schema = infer_schema(df)
    assert len(schema) == df.shape[1]
    task = detect_task(df, schema, target="Survived")
    assert task.task == "binary"
