"""Shared Lightning training helpers — seed 42, AdamW defaults, early-stop, LR finder."""

from __future__ import annotations

from typing import Any

import numpy as np

# ARCHITECTURE §34 defaults
DEFAULT_LR = 1e-3
DEFAULT_WEIGHT_DECAY = 1e-5
DEFAULT_GRAD_CLIP = 1.0
DEFAULT_EARLY_STOP_PATIENCE = 10
DEFAULT_SEED = 42


def set_seed(seed: int = DEFAULT_SEED) -> None:
    """Deterministic flags for numpy / random / torch / Lightning."""
    import random

    import torch
    from lightning.pytorch import seed_everything

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    seed_everything(seed, workers=True)


def adamw_kwargs(
    lr: float = DEFAULT_LR, weight_decay: float = DEFAULT_WEIGHT_DECAY
) -> dict[str, float]:
    return {"lr": lr, "weight_decay": weight_decay}


def early_stopping_callback(
    *,
    monitor: str = "val_loss",
    patience: int = DEFAULT_EARLY_STOP_PATIENCE,
    mode: str = "min",
) -> Any:
    from lightning.pytorch.callbacks import EarlyStopping

    return EarlyStopping(monitor=monitor, patience=patience, mode=mode, verbose=False)


def make_trainer(
    *,
    max_epochs: int = 20,
    patience: int = DEFAULT_EARLY_STOP_PATIENCE,
    accelerator: str = "cpu",
    enable_checkpointing: bool = True,
    gradient_clip_val: float = DEFAULT_GRAD_CLIP,
    default_root_dir: str | None = None,
) -> Any:
    """Lightning Trainer with early stopping + best checkpoint restore."""
    import tempfile

    from lightning.pytorch import Trainer
    from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint

    root = default_root_dir or tempfile.mkdtemp(prefix="lab-dl-")
    callbacks: list[Any] = [
        EarlyStopping(monitor="val_loss", patience=patience, mode="min"),
    ]
    if enable_checkpointing:
        callbacks.append(
            ModelCheckpoint(
                dirpath=root,
                monitor="val_loss",
                mode="min",
                save_top_k=1,
                filename="best",
            )
        )
    return Trainer(
        max_epochs=max_epochs,
        accelerator=accelerator,
        devices=1,
        callbacks=callbacks,
        enable_progress_bar=False,
        enable_model_summary=False,
        logger=False,
        gradient_clip_val=gradient_clip_val,
        deterministic=True,
        default_root_dir=root,
    )


def run_lr_finder(
    lightning_module: Any,
    train_loader: Any,
    *,
    min_lr: float = 1e-8,
    max_lr: float = 1.0,
    num_training: int = 50,
    accelerator: str = "cpu",
) -> dict[str, Any]:
    """Lightning Tuner LR finder — returns suggested LR + curve numbers (DL.P.LR_FINDER)."""
    import tempfile

    from lightning.pytorch import Trainer
    from lightning.pytorch.tuner import Tuner

    trainer = Trainer(
        accelerator=accelerator,
        devices=1,
        enable_progress_bar=False,
        enable_model_summary=False,
        logger=False,
        default_root_dir=tempfile.mkdtemp(prefix="lab-dl-lr-"),
    )
    tuner = Tuner(trainer)
    lr_finder = tuner.lr_find(
        lightning_module,
        train_dataloaders=train_loader,
        min_lr=min_lr,
        max_lr=max_lr,
        num_training=num_training,
    )
    suggestion = float(lr_finder.suggestion()) if lr_finder is not None else DEFAULT_LR
    results = lr_finder.results if lr_finder is not None else {"lr": [], "loss": []}
    lrs = [float(x) for x in results.get("lr", [])]
    losses = [float(x) for x in results.get("loss", [])]
    return {
        "suggested_lr": suggestion,
        "lrs": lrs,
        "losses": losses,
        "min_lr": min_lr,
        "max_lr": max_lr,
        "num_training": num_training,
    }
