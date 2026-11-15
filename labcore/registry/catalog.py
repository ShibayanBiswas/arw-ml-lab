"""Catalogue exposed by GET /catalog."""

from __future__ import annotations

import os

from pydantic import BaseModel, ConfigDict, Field

from labcore.cv.schemes import list_cv_schemes
from labcore.registry.algorithms import thin_algorithm_specs
from labcore.registry.spec import AlgorithmSpec
from labcore.train.presets import TUNING_PRESETS


class Catalog(BaseModel):
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
    tuning_presets: list[dict[str, str | int]] = Field(default_factory=list)


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "false").strip().lower() in {"1", "true", "yes"}


def visible_algorithm_specs() -> list[AlgorithmSpec]:
    """Filter licence-gated specs (TabPFN) unless their env flag is on."""
    out: list[AlgorithmSpec] = []
    for spec in thin_algorithm_specs():
        if spec.enabled_env and not _env_flag(spec.enabled_env):
            continue
        out.append(spec)
    return out


def get_catalog() -> Catalog:
    return Catalog(
        algorithms=visible_algorithm_specs(),
        encoders=[
            {"id": "one_hot", "name": "One-Hot"},
            {"id": "ordinal", "name": "Ordinal"},
            {"id": "target", "name": "TargetEncoder"},
        ],
        imputers=[
            {"id": "mean", "name": "Mean"},
            {"id": "median", "name": "Median"},
            {"id": "most_frequent", "name": "Most frequent"},
        ],
        scalers=[
            {"id": "standard", "name": "Standard"},
            {"id": "robust", "name": "Robust"},
            {"id": "minmax", "name": "MinMax"},
            {"id": "none", "name": "None"},
        ],
        cv=list_cv_schemes(),
        metrics=[
            {"id": "r2", "name": "R²"},
            {"id": "rmse", "name": "RMSE"},
            {"id": "balanced_accuracy", "name": "Balanced accuracy"},
            {"id": "roc_auc", "name": "ROC-AUC"},
            {"id": "f1_macro", "name": "F1 macro"},
        ],
        tuning_presets=[
            {"id": k, "name": k.title(), "n_trials": int(v["n_trials"])}
            for k, v in TUNING_PRESETS.items()
        ],
    )
