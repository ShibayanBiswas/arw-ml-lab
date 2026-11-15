"""EDA run context."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from labcore.data.infer import ColumnProfile
from labcore.data.task_detect import TaskSpec


@dataclass
class EDAContext:
    df: pd.DataFrame
    schema: list[ColumnProfile]
    task: TaskSpec
    seed: int = 42
    sample_rows: int | None = 100_000
    sampled: bool = False
    render_png: bool = True

    def profile(self, name: str) -> ColumnProfile | None:
        for c in self.schema:
            if c.name == name:
                return c
        return None

    @property
    def numeric_cols(self) -> list[str]:
        return [
            c.name
            for c in self.schema
            if c.semantic_type in {"continuous", "numeric_discrete", "boolean"}
            and c.role_suggestion != "exclude"
        ]

    @property
    def cat_cols(self) -> list[str]:
        return [
            c.name
            for c in self.schema
            if c.semantic_type in {"categorical", "high_cardinality", "boolean"}
            and c.role_suggestion != "exclude"
        ]

    @property
    def feature_cols(self) -> list[str]:
        tgt = self.task.target
        return [
            c.name
            for c in self.schema
            if c.name != tgt and c.role_suggestion not in {"exclude", "id"}
        ]
