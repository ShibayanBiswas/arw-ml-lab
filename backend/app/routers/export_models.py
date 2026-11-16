"""Model export endpoints — skops / ONNX (§25)."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Literal

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from labcore.export.onnx_export import export_sklearn_onnx, onnx_parity
from labcore.export.skops_store import save_skops
from pydantic import BaseModel, Field
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["export"])


class ExportDemoBody(BaseModel):
    """Fit a tiny demo estimator and export (no stored model registry yet)."""

    task: Literal["binary", "regression"] = "binary"
    format: Literal["skops", "onnx"] = "onnx"
    n_samples: int = Field(default=80, ge=20, le=500)
    n_features: int = Field(default=4, ge=2, le=20)
    seed: int = 42


def _fit_demo(body: ExportDemoBody) -> tuple[Any, np.ndarray]:
    rng = np.random.default_rng(body.seed)
    X = rng.normal(size=(body.n_samples, body.n_features)).astype(np.float32)
    if body.task == "binary":
        y = (X[:, 0] + 0.1 * rng.normal(size=body.n_samples) > 0).astype(int)
        est: Any = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=1000, random_state=body.seed)),
            ]
        )
    else:
        y = X[:, 0] * 1.5 + rng.normal(size=body.n_samples) * 0.1
        est = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("reg", Ridge(random_state=body.seed)),
            ]
        )
    est.fit(X, y)
    return est, X


@router.post("/api/v1/models/export-demo")
def export_demo(
    body: ExportDemoBody,
    _user: AuthUser = Depends(require_write_role),
) -> Response:
    """Export a seed-42 demo model as skops or ONNX bytes (parity-checked for ONNX)."""
    est, X = _fit_demo(body)
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        if body.format == "skops":
            meta = save_skops(est, td_path / "model.skops")
            raw = Path(str(meta["path"])).read_bytes()
            media = "application/octet-stream"
            filename = "model.skops"
        else:
            try:
                meta = export_sklearn_onnx(est, X, td_path / "model.onnx")
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(status_code=422, detail=f"ONNX export failed: {exc}") from exc
            parity = onnx_parity(est, td_path / "model.onnx", X[: min(40, len(X))])
            if not parity["passed"]:
                raise HTTPException(status_code=500, detail={"parity": parity})
            raw = Path(str(meta["path"])).read_bytes()
            media = "application/octet-stream"
            filename = "model.onnx"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Lab-SHA256": str(meta["sha256"]),
            "X-Lab-Format": str(meta["format"]),
            "X-Lab-Size": str(meta["size_bytes"]),
        }
        return Response(content=raw, media_type=media, headers=headers)
