"""ALE (accumulated local effects) via PyALE (ARCHITECTURE §17)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def ale_1d(
    model: Any,
    X: pd.DataFrame,
    feature: str,
    *,
    grid_size: int = 20,
    seed: int = 42,
) -> dict[str, Any]:
    """
    1D ALE curve via ``PyALE.ale``.

    Returns grid centres, effect values, and centred ALE (mean 0).
    """
    from PyALE import ale

    _ = seed
    if feature not in X.columns:
        raise ValueError(f"feature {feature!r} not in columns")
    result = ale(
        X=X,
        model=model,
        feature=[feature],
        grid_size=grid_size,
        include_CI=False,
        plot=False,
    )
    # PyALE returns DataFrame indexed by feature grid with column 'eff'
    grid = [float(x) for x in result.index.to_numpy()]
    eff = np.asarray(result["eff"], dtype=float)
    centred = eff - float(np.mean(eff))
    return {
        "id": "EXPLAIN.T.ALE",
        "feature": feature,
        "grid": grid,
        "effect": eff.tolist(),
        "effect_centred": centred.tolist(),
        "grid_size": grid_size,
        "seed": seed,
    }
