"""Tabular DL via pytorch-tabular — T1 MLP, T3 TabNet, T4 FT-Transformer (thin)."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd

from labcore.deep.engine import DEFAULT_EARLY_STOP_PATIENCE, DEFAULT_LR, DEFAULT_SEED, set_seed

ModelKey = Literal["mlp", "tabnet", "ft_transformer"]


def _column_split(df: pd.DataFrame, target: str) -> tuple[list[str], list[str]]:
    feats = [c for c in df.columns if c != target]
    cat: list[str] = []
    cont: list[str] = []
    for c in feats:
        if pd.api.types.is_numeric_dtype(df[c]) and df[c].nunique(dropna=True) > 12:
            cont.append(c)
        elif pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c]):
            # low-cardinality numeric → treat as continuous for smoke simplicity
            cont.append(c)
        else:
            cat.append(c)
            df[c] = df[c].astype(str).fillna("__NA__")
    for c in cont:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).astype("float64")
    return cat, cont


def _model_config(key: ModelKey, task: str, params: dict[str, Any]) -> Any:
    from pytorch_tabular.models import (
        CategoryEmbeddingModelConfig,
        FTTransformerConfig,
        TabNetModelConfig,
    )

    lr = float(params.get("learning_rate", DEFAULT_LR))
    seed = int(params.get("seed", DEFAULT_SEED))
    if key == "mlp":
        return CategoryEmbeddingModelConfig(
            task=task,
            layers=str(params.get("layers", "64-32")),
            activation=str(params.get("activation", "ReLU")),
            dropout=float(params.get("dropout", 0.1)),
            use_batch_norm=bool(params.get("use_batch_norm", True)),
            learning_rate=lr,
            seed=seed,
        )
    if key == "tabnet":
        n_d = int(params.get("n_d", 8))
        return TabNetModelConfig(
            task=task,
            n_d=n_d,
            n_a=int(params.get("n_a", n_d)),
            n_steps=int(params.get("n_steps", 3)),
            gamma=float(params.get("gamma", 1.3)),
            n_independent=int(params.get("n_independent", 1)),
            n_shared=int(params.get("n_shared", 1)),
            mask_type=str(params.get("mask_type", "sparsemax")),
            learning_rate=lr,
            seed=seed,
            virtual_batch_size=int(params.get("virtual_batch_size", 32)),
        )
    # FT-Transformer — small defaults for CPU Quick smoke
    return FTTransformerConfig(
        task=task,
        input_embed_dim=int(params.get("input_embed_dim", 16)),
        num_heads=int(params.get("num_heads", 2)),
        num_attn_blocks=int(params.get("num_attn_blocks", 1)),
        attn_dropout=float(params.get("attn_dropout", 0.1)),
        ff_dropout=float(params.get("ff_dropout", 0.1)),
        learning_rate=lr,
        seed=seed,
    )


def fit_tabular(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    *,
    target: str,
    model_key: ModelKey,
    task: Literal["classification", "regression"],
    params: dict[str, Any] | None = None,
    max_epochs: int = 5,
    batch_size: int = 64,
    auto_lr_find: bool = False,
    early_stopping_patience: int = DEFAULT_EARLY_STOP_PATIENCE,
) -> dict[str, Any]:
    """Fit a pytorch-tabular model; returns metrics + artefact numbers (no fabricated scores)."""
    from pytorch_tabular import TabularModel
    from pytorch_tabular.config import DataConfig, OptimizerConfig, TrainerConfig

    params = dict(params or {})
    set_seed(int(params.get("seed", DEFAULT_SEED)))

    train = train_df.copy()
    val = val_df.copy()
    cat_cols, cont_cols = _column_split(train, target)
    # align val dtypes
    for c in cat_cols:
        val[c] = val[c].astype(str).fillna("__NA__")
    for c in cont_cols:
        val[c] = pd.to_numeric(val[c], errors="coerce").fillna(0.0).astype("float64")

    data_config = DataConfig(
        target=[target],
        continuous_cols=cont_cols,
        categorical_cols=cat_cols,
        normalize_continuous_features=True,
    )
    trainer_config = TrainerConfig(
        batch_size=batch_size,
        max_epochs=max_epochs,
        accelerator="cpu",
        devices=1,
        auto_lr_find=auto_lr_find,
        early_stopping="valid_loss",
        early_stopping_mode="min",
        early_stopping_patience=early_stopping_patience,
        checkpoints="valid_loss",
        load_best=True,
        progress_bar="none",
        trainer_kwargs={"enable_model_summary": False},
    )
    optimizer_config = OptimizerConfig(
        optimizer="AdamW",
        optimizer_params={
            "weight_decay": float(params.get("weight_decay", 1e-5)),
        },
    )
    model_config = _model_config(model_key, task, params)

    tabular_model = TabularModel(
        data_config=data_config,
        model_config=model_config,
        optimizer_config=optimizer_config,
        trainer_config=trainer_config,
        verbose=False,
    )
    tabular_model.fit(train=train, validation=val)

    eval_out = tabular_model.evaluate(val)
    # pytorch-tabular returns list[dict] of metric dicts
    metrics: dict[str, float] = {}
    if isinstance(eval_out, list) and eval_out:
        raw = eval_out[0] if isinstance(eval_out[0], dict) else {}
        for k, v in raw.items():
            try:
                metrics[str(k)] = float(v)
            except (TypeError, ValueError):
                continue

    pred_df = tabular_model.predict(val)
    trainer = getattr(tabular_model, "trainer", None) or getattr(
        getattr(tabular_model, "model", None), "trainer", None
    )
    best_epoch: int | None = None
    stopped_epoch: int | None = None
    if trainer is not None:
        stopped_epoch = int(getattr(trainer, "current_epoch", 0))
        cb = getattr(trainer, "checkpoint_callback", None)
        if cb is not None and getattr(cb, "best_model_path", None):
            best_epoch = int(getattr(cb, "best_model_score", 0) is not None and stopped_epoch or 0)
        # EarlyStopping callback records best_score / wait_count
        for c in getattr(trainer, "callbacks", []) or []:
            if c.__class__.__name__ == "EarlyStopping":
                best_epoch = int(getattr(c, "stopped_epoch", 0) or stopped_epoch or 0)
                break

    loss_curve = _extract_loss_curve(tabular_model)
    suggested_lr = float(params.get("learning_rate", DEFAULT_LR))
    if auto_lr_find:
        # TrainerConfig auto_lr_find mutates learning rate on the model when available
        try:
            suggested_lr = float(tabular_model.model.hparams.learning_rate)  # type: ignore[attr-defined]
        except Exception:
            suggested_lr = float(params.get("learning_rate", DEFAULT_LR))

    return {
        "model_key": model_key,
        "task": task,
        "metrics": metrics,
        "n_train": int(len(train)),
        "n_val": int(len(val)),
        "pred_columns": list(pred_df.columns),
        "loss_curve": loss_curve,
        "suggested_lr": suggested_lr,
        "best_epoch": best_epoch,
        "stopped_epoch": stopped_epoch,
        "seed": int(params.get("seed", DEFAULT_SEED)),
        "library": "pytorch-tabular",
    }


def _extract_loss_curve(tabular_model: Any) -> dict[str, list[float]]:
    """Pull logged train/val losses from Lightning logger if present."""
    train_loss: list[float] = []
    val_loss: list[float] = []
    trainer = getattr(tabular_model, "trainer", None)
    if trainer is None:
        return {"train_loss": train_loss, "val_loss": val_loss}
    metrics_dict = getattr(trainer, "callback_metrics", {}) or {}
    for k, v in metrics_dict.items():
        try:
            fv = float(v.detach().cpu()) if hasattr(v, "detach") else float(v)
        except (TypeError, ValueError):
            continue
        lk = str(k).lower()
        if "train" in lk and "loss" in lk:
            train_loss.append(fv)
        if ("valid" in lk or "val" in lk) and "loss" in lk:
            val_loss.append(fv)
    # Also try logged history via CSV logger / result
    logged = getattr(trainer, "logged_metrics", {}) or {}
    for k, v in logged.items():
        try:
            fv = float(v.detach().cpu()) if hasattr(v, "detach") else float(v)
        except (TypeError, ValueError):
            continue
        lk = str(k).lower()
        if "train" in lk and "loss" in lk and not train_loss:
            train_loss.append(fv)
        if (("valid" in lk or "val" in lk) and "loss" in lk) and not val_loss:
            val_loss.append(fv)
    return {"train_loss": train_loss, "val_loss": val_loss}


def quick_split(
    df: pd.DataFrame,
    target: str,
    *,
    test_size: float = 0.2,
    seed: int = DEFAULT_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    from sklearn.model_selection import train_test_split

    idx = np.arange(len(df))
    tr, va = train_test_split(idx, test_size=test_size, random_state=seed)
    return df.iloc[tr].reset_index(drop=True), df.iloc[va].reset_index(drop=True)
