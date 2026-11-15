"""Core contracts — CURSOR_PROMPT §4.1 / ARCHITECTURE §14.2."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ParamType = Literal[
    "int",
    "float",
    "categorical",
    "bool",
    "str",
    "int_or_none",
    "float_or_none",
    "tuple",
]

PresetName = Literal["quick", "balanced", "thorough", "exhaustive"]

Family = Literal[
    "regression",
    "classification",
    "sequential",
    "dr",
    "clustering",
    "anomaly",
    "forecast",
]


class ParamSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: ParamType
    default: Any
    low: float | None = None
    high: float | None = None
    log: bool = False
    step: float | None = None
    choices: list[Any] | None = None
    condition: str | None = None
    help_key: str
    presets: dict[PresetName, list[Any] | dict[str, Any]] = Field(default_factory=dict)


class AlgorithmSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    key: str
    family: Family
    name: str
    library: str
    estimator: str
    params: list[ParamSpec] = Field(default_factory=list)
    supports: set[str] = Field(default_factory=set)
    min_rows: int = 0
    max_rows_hint: int | None = None
    needs_scaling: bool = False
    handles_missing: bool = False
    edu_key: str
    tags: list[str] = Field(default_factory=list)
    # Phase 2A+: Celery routing / licence gates (ARCHITECTURE §34.9)
    resources: dict[str, Any] = Field(default_factory=dict)  # {gpu: bool, mem_gb, threads}
    enabled_env: str | None = None  # e.g. TABPFN_ENABLED — hidden in catalog unless env true
