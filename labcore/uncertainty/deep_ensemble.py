"""Deep ensemble predictive uncertainty — thin wrapper (ARCHITECTURE §21 / Phase 2A).

Averages predictions from a list of already-fitted callables. Never refits.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np

ARTEFACT_ID = "UQ.DEEP.ENSEMBLE"


def deep_ensemble_predict(
    members: list[Callable[[Any], Any]],
    x: Any,
    *,
    seed: int = 42,
) -> dict[str, Any]:
    """Mean / std across ensemble member predictions. ``seed`` recorded only."""
    if len(members) < 2:
        raise ValueError("deep ensemble needs ≥ 2 members")
    preds: list[np.ndarray] = []
    for fn in members:
        out = fn(x)
        if hasattr(out, "detach"):
            out = out.detach().cpu().numpy()
        preds.append(np.asarray(out, dtype=float))
    stack = np.stack(preds, axis=0)
    mean = stack.mean(axis=0)
    std = stack.std(axis=0, ddof=1)
    return {
        "id": ARTEFACT_ID,
        "n_members": len(members),
        "seed": int(seed),
        "mean": mean.tolist(),
        "std": std.tolist(),
        "prediction_source": "deep_ensemble",
        "refit": False,
    }
