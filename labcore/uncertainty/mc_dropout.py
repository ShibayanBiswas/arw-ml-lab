"""MC-dropout predictive uncertainty — thin torch wrapper (ARCHITECTURE §21 / Phase 2A).

Never refits. Enables modules with a ``training`` flag that behave like Dropout
during ``eval`` by temporarily setting ``train(True)`` on Dropout layers only.
"""

from __future__ import annotations

from typing import Any

import numpy as np

ARTEFACT_ID = "UQ.MC.DROPOUT"


def _enable_dropout_layers(module: Any) -> list[Any]:
    """Set Dropout* modules to train mode; return the ones we touched."""
    touched: list[Any] = []
    for m in module.modules():
        name = type(m).__name__
        if "Dropout" in name and hasattr(m, "train"):
            m.train()
            touched.append(m)
    return touched


def mc_dropout_predict(
    model: Any,
    x: Any,
    *,
    n_samples: int = 30,
    seed: int = 42,
) -> dict[str, Any]:
    """Run ``n_samples`` stochastic forwards; return mean / std of predictions.

    ``model`` must be callable as ``model(x)`` returning a tensor/array.
    Uses torch RNG when torch is importable; otherwise numpy only for seeding docs.
    """
    if n_samples < 2:
        raise ValueError("n_samples must be ≥ 2")

    try:
        import torch
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("MC-dropout requires torch") from exc

    torch.manual_seed(int(seed))
    was_training = bool(getattr(model, "training", False))
    model.eval()
    _enable_dropout_layers(model)

    preds: list[np.ndarray] = []
    with torch.no_grad():
        for _ in range(int(n_samples)):
            out = model(x)
            if hasattr(out, "detach"):
                out = out.detach().cpu().numpy()
            preds.append(np.asarray(out, dtype=float))

    if was_training:
        model.train()
    else:
        model.eval()

    stack = np.stack(preds, axis=0)
    mean = stack.mean(axis=0)
    std = stack.std(axis=0, ddof=1)
    return {
        "id": ARTEFACT_ID,
        "n_samples": int(n_samples),
        "seed": int(seed),
        "mean": mean.tolist(),
        "std": std.tolist(),
        "prediction_source": "mc_dropout",
        "refit": False,
    }
