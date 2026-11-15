"""Predict + explain thin routes (Phase 3)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from labcore.explain.shap_trees import tree_shap_explain
from labcore.predict.score import predict_batch, predict_single
from pydantic import BaseModel, Field

from backend.app.model_store import MODEL_STORE
from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["predict"])


class PredictSingleBody(BaseModel):
    row: dict[str, Any]


class PredictBatchBody(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=1)


class ExplainBody(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=1, max_length=50)


@router.get("/api/v1/models/{model_id}/schema")
def model_schema(model_id: str, user: AuthUser = Depends(require_write_role)) -> dict[str, Any]:
    _ = user
    m = MODEL_STORE.get(model_id)
    if m is None:
        raise HTTPException(status_code=404, detail="model not found")
    return m.feature_contract


@router.post("/api/v1/models/{model_id}/predict")
def predict_one(
    model_id: str,
    body: PredictSingleBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Thin single-row predict (alias for Prediction Studio POST /predict/single)."""
    _ = user
    m = MODEL_STORE.get(model_id)
    if m is None:
        raise HTTPException(status_code=404, detail="model not found")
    try:
        return predict_single(m.pipeline, body.row, feature_names=m.feature_names)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/predict/single")
def predict_one_studio(
    body: PredictSingleBody,
    model_id: str,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    return predict_one(model_id, body, user)


@router.post("/api/v1/models/{model_id}/predict/batch")
def predict_many(
    model_id: str,
    body: PredictBatchBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    import pandas as pd

    m = MODEL_STORE.get(model_id)
    if m is None:
        raise HTTPException(status_code=404, detail="model not found")
    X = pd.DataFrame(body.rows)
    try:
        return predict_batch(m.pipeline, X, feature_names=m.feature_names)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/explain/{model_id}")
def explain_model(
    model_id: str,
    body: ExplainBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    import pandas as pd

    m = MODEL_STORE.get(model_id)
    if m is None:
        raise HTTPException(status_code=404, detail="model not found")
    X = pd.DataFrame(body.rows)
    # Prefer the final estimator for TreeSHAP when pipeline-wrapped
    model = m.pipeline
    if hasattr(model, "named_steps") and "model" in model.named_steps:
        # Transform through preprocessing then explain leaf model
        pre = model[:-1]
        leaf = model.named_steps["model"]
        Xt = pre.transform(X[m.feature_names])
        return tree_shap_explain(leaf, Xt)
    return tree_shap_explain(model, X[m.feature_names])
