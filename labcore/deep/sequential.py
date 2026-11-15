"""Sequential DL — window builder + LSTM (Q2) + TCN (Q7) thin smokes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from labcore.deep.engine import (
    DEFAULT_LR,
    DEFAULT_SEED,
    DEFAULT_WEIGHT_DECAY,
    make_trainer,
    run_lr_finder,
    set_seed,
)


@dataclass(frozen=True)
class WindowSpec:
    lookback: int = 16
    horizon: int = 1
    stride: int = 1
    purge: int = 0
    embargo: int = 0


def build_windows(
    X: np.ndarray,
    y: np.ndarray,
    *,
    lookback: int,
    horizon: int = 1,
    stride: int = 1,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Sliding windows: features [t-lookback+1 … t] → label at t+horizon.
    Returns (windows, labels, end_indices) where end_indices are the last
    feature timestamps (inclusive) for purge/embargo checks.
    """
    n, f = X.shape
    xs: list[np.ndarray] = []
    ys: list[float] = []
    ends: list[int] = []
    last_start = n - lookback - horizon
    for start in range(0, last_start + 1, stride):
        end = start + lookback - 1
        label_idx = end + horizon
        if label_idx >= n:
            break
        xs.append(X[start : end + 1])
        ys.append(float(y[label_idx]))
        ends.append(end)
    if not xs:
        raise ValueError("no windows produced — shorten lookback/horizon or grow the series")
    return np.stack(xs), np.asarray(ys, dtype=np.float64), np.asarray(ends, dtype=np.int64)


def assert_no_window_label_overlap(
    train_ends: np.ndarray,
    val_label_indices: np.ndarray,
    *,
    lookback: int,
    horizon: int,
    purge: int = 0,
    embargo: int = 0,
) -> None:
    """Raise if a train window's features or predicted label intersects a val label zone."""
    for end in train_ends:
        feat_lo = int(end) - lookback + 1
        feat_hi = int(end)
        pred_lab = feat_hi + horizon
        for lab in val_label_indices:
            zone_lo = int(lab) - purge
            zone_hi = int(lab) + embargo
            # feature overlap with label zone
            if not (feat_hi < zone_lo or feat_lo > zone_hi):
                raise AssertionError(
                    f"train window [{feat_lo},{feat_hi}] overlaps val label zone "
                    f"[{zone_lo},{zone_hi}] (label={lab})"
                )
            # predicted train label falls inside val zone (purge leak)
            if zone_lo <= pred_lab <= zone_hi and pred_lab != int(lab):
                raise AssertionError(
                    f"train pred label {pred_lab} inside val zone [{zone_lo},{zone_hi}]"
                )


def _as_lightning_module(backbone: nn.Module, task: str) -> Any:
    import lightning.pytorch as pl

    class SeqModule(pl.LightningModule):
        def __init__(self, lr: float = DEFAULT_LR) -> None:
            super().__init__()
            self.save_hyperparameters(ignore=["backbone"])
            self.backbone = backbone
            self.task = task
            self.lr = lr
            self.criterion = nn.MSELoss() if task == "regression" else nn.BCEWithLogitsLoss()

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.backbone(x)

        def _step(self, batch: tuple[torch.Tensor, torch.Tensor], stage: str) -> torch.Tensor:
            x, y = batch
            logits = self(x).squeeze(-1)
            loss = self.criterion(logits, y)
            self.log(f"{stage}_loss", loss, on_epoch=True, prog_bar=False)
            return loss

        def training_step(self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> torch.Tensor:
            return self._step(batch, "train")

        def validation_step(self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> torch.Tensor:
            return self._step(batch, "val")

        def configure_optimizers(self) -> Any:
            return torch.optim.AdamW(
                self.parameters(),
                lr=self.lr,
                weight_decay=DEFAULT_WEIGHT_DECAY,
            )

    return SeqModule()


class LSTMBackbone(nn.Module):
    def __init__(self, n_features: int, hidden: int = 32, layers: int = 1, dropout: float = 0.0) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden,
            num_layers=layers,
            batch_first=True,
            dropout=dropout if layers > 1 else 0.0,
        )
        self.head = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :])


class TCNBackbone(nn.Module):
    def __init__(self, n_features: int, channels: int = 32, levels: int = 2, kernel: int = 3) -> None:
        super().__init__()
        from pytorch_tcn import TCN

        self.tcn = TCN(
            num_inputs=n_features,
            num_channels=[channels] * levels,
            kernel_size=kernel,
            dropout=0.05,
            causal=True,
        )
        self.head = nn.Linear(channels, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # pytorch-tcn expects (batch, channels, time)
        h = self.tcn(x.transpose(1, 2))
        if h.dim() == 3:
            h = h[:, :, -1]
        return self.head(h)


def fit_sequential(
    X: np.ndarray,
    y: np.ndarray,
    *,
    model: Literal["lstm", "tcn"] = "lstm",
    window: WindowSpec | None = None,
    task: Literal["regression", "classification"] = "regression",
    max_epochs: int = 5,
    batch_size: int = 32,
    seed: int = DEFAULT_SEED,
    run_finder: bool = False,
) -> dict[str, Any]:
    """Window + Lightning train for LSTM/TCN; optional LR finder."""
    set_seed(seed)
    window = window or WindowSpec()
    # z-score features for stable CPU smokes (fit stats on full series is ok for thin smoke;
    # production path will fit scalers inside purged folds in 2A-cont)
    X = np.asarray(X, dtype=np.float64)
    mu = X.mean(axis=0, keepdims=True)
    sigma = X.std(axis=0, keepdims=True)
    sigma = np.where(sigma < 1e-8, 1.0, sigma)
    X = (X - mu) / sigma
    Xw, yw, ends = build_windows(
        X, y, lookback=window.lookback, horizon=window.horizon, stride=window.stride
    )
    n = len(Xw)
    split = max(1, int(n * 0.8))
    ends_va = ends[split:]
    val_labels = ends_va + window.horizon
    # Drop train windows that violate purge/embargo around validation labels
    keep_tr: list[int] = []
    for i in range(split):
        try:
            assert_no_window_label_overlap(
                ends[i : i + 1],
                val_labels,
                lookback=window.lookback,
                horizon=window.horizon,
                purge=window.purge,
                embargo=window.embargo,
            )
            keep_tr.append(i)
        except AssertionError:
            continue
    if not keep_tr:
        raise ValueError("purge/embargo removed all train windows — shorten gaps or series")
    X_tr, y_tr = Xw[keep_tr], yw[keep_tr]
    ends_tr = ends[keep_tr]
    X_va, y_va = Xw[split:], yw[split:]
    assert_no_window_label_overlap(
        ends_tr,
        val_labels,
        lookback=window.lookback,
        horizon=window.horizon,
        purge=window.purge,
        embargo=window.embargo,
    )

    n_features = X_tr.shape[-1]
    backbone: nn.Module = (
        LSTMBackbone(n_features) if model == "lstm" else TCNBackbone(n_features)
    )

    module = _as_lightning_module(backbone, task if task == "regression" else "classification")
    # for binary, cast labels
    if task == "classification":
        y_tr = (y_tr > np.median(y_tr)).astype(np.float64)
        y_va = (y_va > np.median(yw)).astype(np.float64)

    tr_loader = DataLoader(
        TensorDataset(
            torch.tensor(X_tr, dtype=torch.float32),
            torch.tensor(y_tr, dtype=torch.float32),
        ),
        batch_size=batch_size,
        shuffle=False,
    )
    va_loader = DataLoader(
        TensorDataset(
            torch.tensor(X_va, dtype=torch.float32),
            torch.tensor(y_va, dtype=torch.float32),
        ),
        batch_size=batch_size,
        shuffle=False,
    )

    lr_info: dict[str, Any] | None = None
    if run_finder:
        n_steps = max(10, min(40, len(tr_loader) * 3))
        lr_info = run_lr_finder(module, tr_loader, num_training=n_steps)
        suggested = float(lr_info.get("suggested_lr") or DEFAULT_LR)
        backbone = LSTMBackbone(n_features) if model == "lstm" else TCNBackbone(n_features)
        module = _as_lightning_module(backbone, "regression" if task == "regression" else "classification")
        module.lr = suggested

    trainer = make_trainer(max_epochs=max_epochs, patience=3, accelerator="cpu")
    trainer.fit(module, tr_loader, va_loader)

    best_path = None
    ckpt = getattr(trainer, "checkpoint_callback", None)
    if ckpt is not None:
        best_path = getattr(ckpt, "best_model_path", None) or None

    # restore best if path exists (nested LightningModule load is best-effort)
    restored_best = False
    if best_path:
        try:
            module = type(module).load_from_checkpoint(best_path)  # type: ignore[attr-defined]
            restored_best = True
        except Exception:
            restored_best = bool(best_path)

    module.eval()
    with torch.no_grad():
        pred = module(torch.tensor(X_va, dtype=torch.float32)).squeeze(-1).cpu().numpy()
    mse = float(np.mean((pred - y_va) ** 2)) if len(y_va) else float("nan")

    return {
        "model": model,
        "task": task,
        "n_windows": int(n),
        "n_train": int(len(X_tr)),
        "n_val": int(len(X_va)),
        "val_mse": mse,
        "lookback": window.lookback,
        "horizon": window.horizon,
        "purge": window.purge,
        "embargo": window.embargo,
        "lr_finder": lr_info,
        "best_checkpoint": best_path,
        "restored_best": restored_best,
        "stopped_epoch": int(getattr(trainer, "current_epoch", 0)),
        "seed": seed,
        "library": "torch+lightning" if model == "lstm" else "pytorch-tcn+lightning",
    }


def frame_to_xy(
    df: pd.DataFrame,
    *,
    feature_cols: list[str] | None = None,
    target_col: str | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Build numeric X/y from a sequential OHLC-like frame (forward return target)."""
    work = df.copy()
    if target_col is None:
        # prefer Close / Adj Close
        close_col = next((c for c in ("Close", "Adj Close", "close", "adj_close") if c in work.columns), None)
        if close_col is None:
            num = work.select_dtypes(include=[np.number]).columns.tolist()
            if not num:
                raise ValueError("no numeric columns for sequential target")
            close_col = num[0]
        close = pd.to_numeric(work[close_col], errors="coerce")
        work["_fwd_ret"] = np.log(close.shift(-1) / close)
        target_col = "_fwd_ret"
    if feature_cols is None:
        feature_cols = [
            c
            for c in work.select_dtypes(include=[np.number]).columns
            if c != target_col and not str(c).startswith("_")
        ][:6]
        if not feature_cols:
            feature_cols = [c for c in work.columns if c != target_col][:4]
    X = work[feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    y = pd.to_numeric(work[target_col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    # drop last row if NaN forward return was filled — keep aligned length
    return X, y
