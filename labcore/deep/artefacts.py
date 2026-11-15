"""Minimal DL artefacts (thin) — loss curve + LR finder numbers for Plotly later."""

from __future__ import annotations

from typing import Any


def dl_loss_curve_artefact(loss_curve: dict[str, list[float]], *, model_key: str) -> dict[str, Any]:
    """DL.P.LOSS_CURVE numbers payload (Plotly rendering deferred to 2A-cont)."""
    return {
        "id": "DL.P.LOSS_CURVE",
        "model_key": model_key,
        "numbers": {
            "train_loss": list(loss_curve.get("train_loss", [])),
            "val_loss": list(loss_curve.get("val_loss", [])),
        },
    }


def dl_lr_finder_artefact(lr_info: dict[str, Any], *, model_key: str) -> dict[str, Any]:
    """DL.P.LR_FINDER numbers payload."""
    return {
        "id": "DL.P.LR_FINDER",
        "model_key": model_key,
        "numbers": {
            "suggested_lr": lr_info.get("suggested_lr"),
            "lrs": list(lr_info.get("lrs", [])),
            "losses": list(lr_info.get("losses", [])),
        },
    }


def pack_dl_artefacts(
    *,
    model_key: str,
    loss_curve: dict[str, list[float]] | None = None,
    lr_info: dict[str, Any] | None = None,
    metrics: dict[str, float] | None = None,
) -> dict[str, Any]:
    plots: list[dict[str, Any]] = []
    if loss_curve:
        plots.append(dl_loss_curve_artefact(loss_curve, model_key=model_key))
    if lr_info:
        plots.append(dl_lr_finder_artefact(lr_info, model_key=model_key))
    return {
        "tables": {
            "DL.T.METRICS": {"model_key": model_key, "metrics": metrics or {}},
        },
        "plots": plots,
    }
