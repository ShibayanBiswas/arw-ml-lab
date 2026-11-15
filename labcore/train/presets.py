"""Optuna tuning budget presets (ARCHITECTURE §13 / Phase 2 thin hook)."""

from __future__ import annotations

from typing import Any, Literal

TuningPreset = Literal["quick", "balanced", "thorough", "exhaustive"]

# Trials × default 5-fold; Balanced is the product default.
TUNING_PRESETS: dict[str, dict[str, Any]] = {
    "quick": {"n_trials": 20, "sampler": "tpe", "pruner": "median"},
    "balanced": {"n_trials": 60, "sampler": "tpe", "pruner": "median"},
    "thorough": {"n_trials": 200, "sampler": "tpe", "pruner": "median"},
    "exhaustive": {"n_trials": 500, "sampler": "tpe", "pruner": "none"},
}


def get_tuning_preset(name: TuningPreset | str = "balanced") -> dict[str, Any]:
    key = (name or "balanced").lower()
    if key not in TUNING_PRESETS:
        raise ValueError(f"unknown tuning preset: {name}")
    return dict(TUNING_PRESETS[key])
