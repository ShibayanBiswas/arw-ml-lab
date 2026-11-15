"""Catalogue exposed by GET /catalog (Phase 0: empty typed registries)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from labcore.registry.spec import AlgorithmSpec


class Catalog(BaseModel):
    """Typed catalogue. Algorithms are registered in later phases — never invent entries."""

    model_config = ConfigDict(extra="forbid")

    algorithms: list[AlgorithmSpec] = Field(default_factory=list)
    encoders: list[dict[str, str]] = Field(default_factory=list)
    imputers: list[dict[str, str]] = Field(default_factory=list)
    scalers: list[dict[str, str]] = Field(default_factory=list)
    transforms: list[dict[str, str]] = Field(default_factory=list)
    cv: list[dict[str, str]] = Field(default_factory=list)
    metrics: list[dict[str, str]] = Field(default_factory=list)
    plots: list[dict[str, str]] = Field(default_factory=list)
    tests: list[dict[str, str]] = Field(default_factory=list)
    explainers: list[dict[str, str]] = Field(default_factory=list)
    datasets: list[dict[str, str]] = Field(default_factory=list)


def get_catalog() -> Catalog:
    return Catalog()
