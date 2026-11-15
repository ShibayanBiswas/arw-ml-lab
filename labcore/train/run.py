"""Supervised CV runner — Phase 2-cont-2 (seed 42, leakage-safe, CV catalogue)."""

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
from sklearn.model_selection import train_test_split

from labcore.cv.schemes import build_splitter, default_scheme_for_task, nested_default
from labcore.cv.visualise import iter_splits, plot_cv_folds
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
    run_eval: bool = True
    cv_scheme: str | None = None  # None → task default; "nested" forces nested flag
    nested: bool | None = None  # None → MI-03 auto (n_train < 2000)


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
    """Hold-out test + CV on train; leaderboard + optional §41/§42 eval on champion."""
    if config.target not in df.columns:
        raise ValueError(f"target missing: {config.target}")
    y_all = df[config.target]
    X_all = df.drop(columns=[config.target])
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

    scheme = config.cv_scheme or default_scheme_for_task(config.task)
    nested_on = config.nested if config.nested is not None else nested_default(len(X_tr))
    if scheme == "nested":
        nested_on = True
        scheme = default_scheme_for_task(config.task)

    splitter = build_splitter(
        scheme,
        n_splits=config.n_splits,
        seed=config.seed,
        task=config.task,
    )
    if splitter is None:
        # holdout on train: single 80/20 of train as one "fold"
        from sklearn.model_selection import ShuffleSplit

        splitter = ShuffleSplit(n_splits=1, test_size=0.2, random_state=config.seed)

    fold_indices = iter_splits(splitter, X_tr, y_tr)
    gap = 0
    if scheme == "time_series_split":
        gap = 0  # TimeSeriesSplit gap param not used in thin build_splitter
    cv_plot = plot_cv_folds(fold_indices, title=f"CV folds ({scheme})", gap=gap)

    specs = _select_specs(config.algorithm_keys, config.task)
    rows: list[dict[str, Any]] = []
    champion_payload: dict[str, Any] | None = None

    for spec in specs:
        fold_metrics: list[dict[str, float]] = []
        fold_preds: list[dict[str, np.ndarray]] = []
        oof_pred = np.full(len(X_tr), np.nan, dtype=float)
        oof_proba: np.ndarray | None = None
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
            pred = np.asarray(full.predict(X_fold_va))
            if config.task == "regression":
                oof_pred[va_idx] = pred.astype(float)
            else:
                oof_pred[va_idx] = pd.Series(pred).astype("category").cat.codes.to_numpy()
            proba = None
            if config.task != "regression" and hasattr(full, "predict_proba"):
                try:
                    proba = np.asarray(full.predict_proba(X_fold_va))
                    if oof_proba is None:
                        oof_proba = np.full((len(X_tr), proba.shape[1]), np.nan)
                    oof_proba[va_idx] = proba
                except Exception:
                    proba = None
            fold_preds.append(
                {
                    "y_true": y_fold_va.to_numpy(),
                    "y_pred": pred,
                    "y_proba": proba,
                }
            )
            if config.task == "regression":
                fold_metrics.append(_metrics_reg(y_fold_va.to_numpy(), pred))
            else:
                fold_metrics.append(_metrics_clf(y_fold_va.to_numpy(), pred, proba))

        pre_f, _, meta = compile_recipe(X_tr, config.recipe)
        model = build_estimator(spec)
        full = _with_model(pre_f, model)
        full.fit(X_tr, y_tr)
        test_pred = np.asarray(full.predict(X_te))
        test_proba = None
        if config.task != "regression" and hasattr(full, "predict_proba"):
            try:
                test_proba = np.asarray(full.predict_proba(X_te))
            except Exception:
                test_proba = None
        y_oof_true = y_tr.to_numpy()
        if config.task == "regression":
            test_m = _metrics_reg(y_te.to_numpy(), test_pred)
            primary = "r2"
            y_oof_hat = oof_pred
        else:
            test_m = _metrics_clf(y_te.to_numpy(), test_pred, test_proba)
            primary = "balanced_accuracy"
            y_oof_hat = np.empty(len(X_tr), dtype=y_oof_true.dtype)
            for (_tr_idx, va_idx), fp in zip(fold_indices, fold_preds, strict=True):
                y_oof_hat[va_idx] = np.asarray(fp["y_pred"]).astype(y_oof_true.dtype, copy=False)

        keys0 = fold_metrics[0]
        cv_mean = {k: float(np.nanmean([m[k] for m in fold_metrics])) for k in keys0}
        cv_std = {k: float(np.nanstd([m[k] for m in fold_metrics], ddof=1)) for k in keys0}
        row = {
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
            "_oof": {
                "y_true": y_oof_true,
                "y_pred": y_oof_hat,
                "y_proba": oof_proba,
                "fold_preds": fold_preds,
                "y_test": y_te.to_numpy(),
                "y_pred_test": test_pred,
                "y_proba_test": test_proba,
            },
        }
        rows.append(row)

    rows.sort(key=lambda r: r["cv_mean"].get(r["primary_metric"], float("-inf")), reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i

    eval_payload = None
    if config.run_eval and rows:
        champ = rows[0]
        oof = champ.pop("_oof")
        for r in rows[1:]:
            r.pop("_oof", None)
        if config.task == "regression":
            from labcore.eval.regression.suite import run_regression_eval

            eval_payload = {
                "regression": run_regression_eval(
                    y_oof=oof["y_true"],
                    y_pred_oof=np.asarray(oof["y_pred"], dtype=float),
                    y_test=oof["y_test"],
                    y_pred_test=np.asarray(oof["y_pred_test"], dtype=float),
                    fold_preds=[
                        {"y_true": fp["y_true"], "y_pred": fp["y_pred"]} for fp in oof["fold_preds"]
                    ],
                )
            }
        else:
            from labcore.eval.classification.suite import run_classification_eval

            eval_payload = {
                "classification": run_classification_eval(
                    y_oof=oof["y_true"],
                    y_pred_oof=oof["y_pred"],
                    y_proba_oof=oof["y_proba"],
                    y_test=oof["y_test"],
                    y_pred_test=oof["y_pred_test"],
                    y_proba_test=oof["y_proba_test"],
                    fold_preds=oof["fold_preds"],
                    task=config.task,
                )
            }
        champion_payload = {"algorithm_key": champ["algorithm_key"], "eval": eval_payload}
    else:
        for r in rows:
            r.pop("_oof", None)

    return {
        "leaderboard": rows,
        "config": config.model_dump(),
        "n_train": int(len(X_tr)),
        "n_test": int(len(X_te)),
        "dropped_high_card": drop_cols,
        "seed": config.seed,
        "cv_scheme": scheme,
        "nested": nested_on,
        "cv_visualiser": cv_plot,
        "eval": eval_payload,
        "champion": champion_payload,
    }
