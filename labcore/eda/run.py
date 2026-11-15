"""EDA orchestrator — tables + plots + sampling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from labcore.data.infer import ColumnProfile, infer_schema
from labcore.data.task_detect import TaskSpec, detect_task
from labcore.eda.context import EDAContext
from labcore.eda.plots import PLOT_GROUP_IDS, build_all_plots
from labcore.eda.tables import build_all_tables
from labcore.plots.artefact import Artefact

# Full catalogue of 19 EDA.T.* ids (ARCHITECTURE §10.1)
ALL_TABLE_IDS = (
    "EDA.T.OVERVIEW",
    "EDA.T.SCHEMA",
    "EDA.T.NUMSUMMARY",
    "EDA.T.CATSUMMARY",
    "EDA.T.NORMALITY",
    "EDA.T.DISTFIT",
    "EDA.T.MISSING",
    "EDA.T.OUTLIERS",
    "EDA.T.CORR",
    "EDA.T.MI",
    "EDA.T.VIF",
    "EDA.T.TARGET",
    "EDA.T.FEAT_TARGET",
    "EDA.T.WOE_IV",
    "EDA.T.STATIONARITY",
    "EDA.T.AUTOCORR",
    "EDA.T.BREAKS",
    "EDA.T.FINSTATS",
    "EDA.T.DUPES",
)


@dataclass
class EDAResult:
    artefacts: list[Artefact]
    task: TaskSpec
    schema: list[ColumnProfile]
    sampled: bool
    n_rows: int
    n_cols: int
    table_ids: list[str] = field(default_factory=list)
    plot_ids: list[str] = field(default_factory=list)
    plot_groups: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task.model_dump(),
            "schema": [c.model_dump() for c in self.schema],
            "sampled": self.sampled,
            "n_rows": self.n_rows,
            "n_cols": self.n_cols,
            "table_ids": self.table_ids,
            "plot_ids": self.plot_ids,
            "plot_groups": self.plot_groups,
            "artefacts": [a.model_dump() for a in self.artefacts],
        }


def run_eda(
    df: pd.DataFrame,
    *,
    schema: list[ColumnProfile] | None = None,
    task: TaskSpec | None = None,
    target: str | None = None,
    family_hint: str | None = None,
    seed: int = 42,
    sample_rows: int | None = 100_000,
    render_png: bool = False,
) -> EDAResult:
    """Run full EDA suite. PNG rendering off by default in unit tests (kaleido optional)."""
    schema = schema or infer_schema(df)
    task = task or detect_task(df, schema, target=target, family_hint=family_hint)

    sampled = False
    work = df
    if sample_rows is not None and len(df) > sample_rows:
        work = df.sample(n=sample_rows, random_state=seed)
        sampled = True

    ctx = EDAContext(
        df=work,
        schema=schema,
        task=task,
        seed=seed,
        sample_rows=sample_rows,
        sampled=sampled,
        render_png=render_png,
    )
    tables = build_all_tables(ctx)
    plots = build_all_plots(ctx)
    artefacts = tables + plots
    table_ids = [a.id for a in tables]
    plot_ids = [a.id for a in plots]
    groups = sorted(
        {gid for gid in PLOT_GROUP_IDS if any(p.startswith(gid) or gid in p for p in plot_ids)}
    )
    # Prefer explicit group tags from artefacts numbers
    tagged = sorted(
        {str(a.numbers.get("plot_group")) for a in plots if a.numbers.get("plot_group")}
    )
    return EDAResult(
        artefacts=artefacts,
        task=task,
        schema=schema,
        sampled=sampled,
        n_rows=len(df),
        n_cols=df.shape[1],
        table_ids=table_ids,
        plot_ids=plot_ids,
        plot_groups=tagged or groups,
    )


# Re-export for tests
_ = (ALL_TABLE_IDS, PLOT_GROUP_IDS)
