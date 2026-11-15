"""Optuna Quick/Balanced tune loop — TPE, seed 42 (ARCHITECTURE §13)."""

from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score

from labcore.cv.schemes import build_splitter, nested_default
from labcore.preprocess.recipe import RecipeSpec, compile_recipe
from labcore.registry.algorithms import build_estimator, thin_algorithm_specs
from labcore.registry.spec import AlgorithmSpec
from labcore.train.presets import get_tuning_preset
from labcore.train.run import _with_model


def _suggest_params(trial: Any, spec: AlgorithmSpec) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for p in spec.params:
        if p.name == "random_state":
            params[p.name] = 42
            continue
        if p.type == "float":
            low = float(p.low) if p.low is not None else float(p.default or 1e-3)
            high = float(p.high) if p.high is not None else float(p.default or 1.0) * 10
            if getattr(p, "log", False):
                params[p.name] = trial.suggest_float(p.name, low, high, log=True)
            else:
                params[p.name] = trial.suggest_float(p.name, low, high)
        elif p.type == "int":
            low = int(p.low) if p.low is not None else 1
            high = int(p.high) if p.high is not None else max(low + 1, int(p.default or 10))
            params[p.name] = trial.suggest_int(p.name, low, high)
        elif p.type == "int_or_none":
            # discrete: None via -1 sentinel mapped after
            low = int(p.low) if p.low is not None else 2
            high = int(p.high) if p.high is not None else 32
            v = trial.suggest_int(p.name, low, high)
            params[p.name] = v
        elif p.type == "categorical":
            choices = list(p.choices or [p.default])
            # Optuna cannot suggest None directly in some versions — stringify
            labels = [("__none__" if c is None else str(c)) for c in choices]
            pick = trial.suggest_categorical(p.name, labels)
            params[p.name] = (
                None
                if pick == "__none__"
                else (pick if not isinstance(p.default, bool) else pick == "True")
            )
            # restore original typed choice
            for c in choices:
                if (c is None and pick == "__none__") or str(c) == pick:
                    params[p.name] = c
                    break
        elif p.type == "bool":
            params[p.name] = trial.suggest_categorical(p.name, [True, False])
        else:
            params[p.name] = p.default
    return params


def _primary_scoring(task: str) -> str:
    if task == "regression":
        return "r2"
    return "balanced_accuracy"


def run_optuna_tune(
    df: pd.DataFrame,
    *,
    target: str,
    algorithm_key: str,
    task: str = "binary",
    preset: str = "quick",
    n_splits: int = 5,
    seed: int = 42,
    recipe: RecipeSpec | None = None,
    fixed_params: dict[str, Any] | None = None,
    n_trials: int | None = None,
) -> dict[str, Any]:
    """TPE study; objective = CV mean primary metric. Returns best params + history."""
    import optuna
    from optuna.samplers import TPESampler

    recipe = recipe or RecipeSpec(seed=seed)
    preset_cfg = get_tuning_preset(preset)
    trials = int(n_trials if n_trials is not None else preset_cfg["n_trials"])
    specs = {s.key: s for s in thin_algorithm_specs()}
    if algorithm_key not in specs:
        raise ValueError(f"unknown algorithm: {algorithm_key}")
    spec = specs[algorithm_key]

    y = df[target]
    X = df.drop(columns=[target])
    # drop ultra-high-card object cols (same heuristic as train)
    drop_cols = []
    card_cap = min(100, max(20, len(X) // 2))
    for c in list(X.columns):
        if X[c].dtype == object and X[c].nunique(dropna=True) > card_cap:
            drop_cols.append(c)
    if drop_cols:
        X = X.drop(columns=drop_cols)

    use_nested = nested_default(len(X))
    outer_scheme = "stratified_kfold" if task != "regression" else "kfold"
    splitter = build_splitter(outer_scheme, n_splits=n_splits, seed=seed, task=task)
    scoring = _primary_scoring(task)

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(
        direction="maximize",
        sampler=TPESampler(seed=seed),
    )

    def objective(trial: optuna.Trial) -> float:
        params = _suggest_params(trial, spec)
        if fixed_params:
            params.update(fixed_params)
        pre, _, _ = compile_recipe(X, recipe)
        model = build_estimator(spec, params)
        pipe = _with_model(pre, model)
        scores = cross_val_score(
            pipe,
            X,
            y,
            cv=splitter,
            scoring=scoring,
            n_jobs=1,
            error_score=np.nan,
        )
        mean = float(np.nanmean(scores))
        if np.isnan(mean):
            return float("-inf")
        return mean

    study.optimize(objective, n_trials=trials, show_progress_bar=False)

    history = [
        {
            "number": t.number,
            "value": t.value,
            "params": dict(t.params),
            "state": str(t.state),
        }
        for t in study.trials
    ]
    best_params = dict(study.best_params)
    if fixed_params:
        # ensure user fixed params are recorded on the artefact
        best_params = {**best_params, **fixed_params}

    artefact: dict[str, Any] = {
        "algorithm_key": algorithm_key,
        "preset": preset,
        "n_trials": trials,
        "seed": seed,
        "scoring": scoring,
        "nested_default": use_nested,
        "n_train": int(len(X)),
        "best_value": float(study.best_value) if study.best_trial else None,
        "best_params": best_params,
        "trials": history,
        "dropped_high_card": drop_cols,
    }

    uri = os.environ.get("MLFLOW_TRACKING_URI")
    if uri:
        try:
            import mlflow

            with mlflow.start_run(run_name=f"tune-{algorithm_key}"):
                mlflow.log_params({f"best_{k}": v for k, v in best_params.items()})
                if artefact["best_value"] is not None:
                    mlflow.log_metric("best_value", artefact["best_value"])
            artefact["mlflow"] = {"tracking_uri": uri, "logged": True}
        except Exception as exc:  # noqa: BLE001 — best-effort
            artefact["mlflow"] = {"tracking_uri": uri, "logged": False, "error": str(exc)}
    else:
        artefact["mlflow"] = {"logged": False, "reason": "MLFLOW_TRACKING_URI unset"}

    return artefact
