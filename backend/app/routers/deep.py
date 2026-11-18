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


class McDropoutSmokeBody(BaseModel):
    n_samples: int = Field(default=20, ge=2, le=100)
    seed: int = 42
    n_rows: int = Field(default=8, ge=2, le=64)


@router.post("/api/v1/deep/mc-dropout/smoke")
def mc_dropout_smoke(
    body: McDropoutSmokeBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Tiny torch net + MC-dropout mean/std (never refits a trained lab model)."""
    _ = user
    import torch
    from torch import nn

    from labcore.uncertainty.mc_dropout import mc_dropout_predict

    class _Tiny(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.fc = nn.Linear(2, 1)
            self.drop = nn.Dropout(p=0.5)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.fc(self.drop(x))

    torch.manual_seed(body.seed)
    model = _Tiny()
    x = torch.randn(body.n_rows, 2)
    out = mc_dropout_predict(model, x, n_samples=body.n_samples, seed=body.seed)
    return out


class DeepEnsembleSmokeBody(BaseModel):
    seed: int = 42
    n_rows: int = Field(default=8, ge=2, le=64)


@router.post("/api/v1/deep/ensemble/smoke")
def deep_ensemble_smoke(
    body: DeepEnsembleSmokeBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Two constant offset callables → mean/std (never refits)."""
    _ = user
    from labcore.uncertainty.deep_ensemble import deep_ensemble_predict

    x = np.linspace(0.0, 1.0, body.n_rows).reshape(-1, 1)

    def m1(z: np.ndarray) -> np.ndarray:
        return z * 2.0

    def m2(z: np.ndarray) -> np.ndarray:
        return z * 2.0 + 0.5

    return deep_ensemble_predict([m1, m2], x, seed=body.seed)
