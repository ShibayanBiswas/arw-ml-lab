"""Supervised CV runner — thin Phase 2 (seed 42, leakage-safe)."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import KFold, StratifiedKFold, train_test_split

from labcore.preprocess.recipe import RecipeSpec, compile_recipe
from labcore.registry.algorithms import build_estimator, thin_algorithm_specs
from labcore.registry.spec import AlgorithmSpec


class TrainConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: Literal["regression", "binary", "multiclass"] = "binary"
    target: str
    algorithm_keys: list[str] = Field(default_factory=list)
    n_splits: int = 5
    test_size: float = 0.2
    seed: int = 42
    recipe: RecipeSpec = Field(default_factory=RecipeSpec)


def _metrics_reg(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def _metrics_clf(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None,
) -> dict[str, float]:
    out: dict[str, float] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }
    if y_proba is not None and len(np.unique(y_true)) == 2:
        try:
            scores = y_proba[:, 1] if y_proba.ndim == 2 else y_proba
            out["roc_auc"] = float(roc_auc_score(y_true, scores))
        except Exception:
            out["roc_auc"] = float("nan")
    return out


def _with_model(pre_pipe: Any, model: Any) -> Any:
    """Append estimator after recipe steps; keep imblearn Pipeline when SMOTE is on."""
    steps = list(pre_pipe.steps) + [("model", model)]
    if any(name == "resample" for name, _ in pre_pipe.steps):
        from imblearn.pipeline import Pipeline as ImbPipeline  # type: ignore[import-untyped]

        return ImbPipeline(steps)
    from sklearn.pipeline import Pipeline as SkPipeline

    return SkPipeline(steps)


def _select_specs(keys: list[str], task: str) -> list[AlgorithmSpec]:
    all_specs = thin_algorithm_specs()
    if not keys:
        if task == "regression":
            keys = [s.key for s in all_specs if s.family == "regression"]
        else:
            keys = [s.key for s in all_specs if s.family == "classification"]
    by_key = {s.key: s for s in all_specs}
    return [by_key[k] for k in keys if k in by_key]


def run_supervised_cv(
    df: pd.DataFrame,
    config: TrainConfig,
    *,
    spy_fit_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Hold-out test + CV on train; returns leaderboard rows and fold metrics."""
    if config.target not in df.columns:
        raise ValueError(f"target missing: {config.target}")
    y_all = df[config.target]
    X_all = df.drop(columns=[config.target])
    # Drop high-cardinality text-ish object cols with unique ratio ~1
    drop_cols = []
    card_cap = min(100, max(20, len(X_all) // 2))
    for c in list(X_all.columns):
        if X_all[c].dtype == object and X_all[c].nunique(dropna=True) > card_cap:
            drop_cols.append(c)
    if drop_cols:
        X_all = X_all.drop(columns=drop_cols)

    stratify = y_all if config.task != "regression" else None
    X_tr, X_te, y_tr, y_te = train_test_split(
        X_all,
        y_all,
        test_size=config.test_size,
        random_state=config.seed,
        stratify=stratify,
    )

    if config.task == "regression":
        splitter = KFold(n_splits=config.n_splits, shuffle=True, random_state=config.seed)
        split_iter = splitter.split(X_tr)
    else:
        splitter = StratifiedKFold(n_splits=config.n_splits, shuffle=True, random_state=config.seed)
        split_iter = splitter.split(X_tr, y_tr)

    fold_indices = list(split_iter)
    specs = _select_specs(config.algorithm_keys, config.task)
    rows: list[dict[str, Any]] = []

    for spec in specs:
        fold_metrics: list[dict[str, float]] = []
        oof = np.full(len(X_tr), np.nan)
        for _fold_i, (tr_idx, va_idx) in enumerate(fold_indices):
            X_fold_tr = X_tr.iloc[tr_idx]
            y_fold_tr = y_tr.iloc[tr_idx]
            X_fold_va = X_tr.iloc[va_idx]
            y_fold_va = y_tr.iloc[va_idx]
            pre2, _, meta = compile_recipe(X_fold_tr, config.recipe)
            model = build_estimator(spec)
            full = _with_model(pre2, model)
            full.fit(X_fold_tr, y_fold_tr)
            if spy_fit_counts is not None:
                spy_fit_counts[spec.key] = spy_fit_counts.get(spec.key, 0) + 1
            pred = full.predict(X_fold_va)
            oof[va_idx] = pred if config.task == "regression" else pred
            proba = None
            if config.task != "regression" and hasattr(full, "predict_proba"):
                try:
                    proba = full.predict_proba(X_fold_va)
                except Exception:
                    proba = None
            if config.task == "regression":
                fold_metrics.append(_metrics_reg(y_fold_va.to_numpy(), np.asarray(pred)))
            else:
                fold_metrics.append(_metrics_clf(y_fold_va.to_numpy(), np.asarray(pred), proba))

        # Refit on all train, score test
        pre_f, _, meta = compile_recipe(X_tr, config.recipe)
        model = build_estimator(spec)
        full = _with_model(pre_f, model)
        full.fit(X_tr, y_tr)
        test_pred = full.predict(X_te)
        test_proba = None
        if config.task != "regression" and hasattr(full, "predict_proba"):
            try:
                test_proba = full.predict_proba(X_te)
            except Exception:
                test_proba = None
        if config.task == "regression":
            test_m = _metrics_reg(y_te.to_numpy(), np.asarray(test_pred))
            primary = "r2"
        else:
            test_m = _metrics_clf(y_te.to_numpy(), np.asarray(test_pred), test_proba)
            primary = "balanced_accuracy"

        keys0 = fold_metrics[0]
        cv_mean = {k: float(np.nanmean([m[k] for m in fold_metrics])) for k in keys0}
        cv_std = {
            k: float(np.nanstd([m[k] for m in fold_metrics], ddof=1)) for k in keys0
        }
        rows.append(
            {
                "algorithm_key": spec.key,
                "algorithm_id": spec.id,
                "name": spec.name,
                "library": spec.library,
                "primary_metric": primary,
                "cv_mean": cv_mean,
                "cv_std": cv_std,
                "test": test_m,
                "folds": fold_metrics,
                "dropped_constant": meta.get("dropped_constant"),
                "prediction_source": {"cv": "oof", "test": "holdout"},
            }
        )

    rows.sort(key=lambda r: r["cv_mean"].get(r["primary_metric"], float("-inf")), reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
    return {
        "leaderboard": rows,
        "config": config.model_dump(),
        "n_train": int(len(X_tr)),
        "n_test": int(len(X_te)),
        "dropped_high_card": drop_cols,
        "seed": config.seed,
    }
