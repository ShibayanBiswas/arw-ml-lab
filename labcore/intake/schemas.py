"""Pydantic shapes for intake proposals — ARCHITECTURE §33.9."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

FamilyName = Literal[
    "time_series",
    "supervised_sequential",
    "supervised_non_sequential",
    "unsupervised",
]

HARD_EXCLUDE_REASONS = frozenset(
    {
        "row_id",
        "constant",
        "near_constant",
        "duplicate",
        "text",
        "pii",
        "time_index",
        "entity_id",
    }
)


class IntakeProposal(BaseModel):
    model_config = ConfigDict(extra="allow")

    time_index: dict[str, Any] | None = None
    entity_column: dict[str, Any] | None = None
    frequency: dict[str, Any] | None = None
    family: dict[str, Any]
    task: dict[str, Any] | None = None
    targets: list[dict[str, Any]] = Field(default_factory=list)
    features: list[dict[str, Any]] = Field(default_factory=list)
    excluded: list[dict[str, Any]] = Field(default_factory=list)
    leakage_suspects: list[dict[str, Any]] = Field(default_factory=list)
    cv_recommendation: dict[str, Any] | None = None
    horizon: dict[str, Any] | None = None
    questions_for_user: list[str] = Field(default_factory=list)
    confidence_overall: float = 0.0
    roles: dict[str, dict[str, Any]] = Field(default_factory=dict)
    mode: Literal["rule_based", "ai"] = "rule_based"
    rules_version: str = "intake-1.0"
