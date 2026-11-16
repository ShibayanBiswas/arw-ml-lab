"""Deep learning smoke routes (ARCHITECTURE §34)."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["deep"])


class SequentialSmokeBody(BaseModel):
    model: Literal["lstm", "tcn"] = "lstm"
    max_epochs: int = Field(default=1, ge=1, le=5)
    seed: int = 42
    n: int = Field(default=120, ge=64, le=500)


@router.post("/api/v1/deep/sequential/smoke")
def sequential_smoke(
    body: SequentialSmokeBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    from labcore.deep.sequential import WindowSpec, fit_sequential

    rng = np.random.default_rng(body.seed)
    X = rng.normal(size=(body.n, 3))
    y = rng.normal(size=body.n)
    try:
        out = fit_sequential(
            X,
            y,
            model=body.model,
            window=WindowSpec(lookback=16, horizon=1, purge=2, embargo=1),
            task="regression",
            max_epochs=body.max_epochs,
            seed=body.seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    # drop heavy tensors / non-JSON
    return {
        k: v
        for k, v in out.items()
        if k
        in {
            "model",
            "task",
            "seed",
            "n_train",
            "n_val",
            "metrics",
            "history",
            "scaler_fit_on",
        }
        or isinstance(v, (str, int, float, bool, list, dict, type(None)))
    }
