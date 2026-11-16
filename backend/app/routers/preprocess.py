"""Preprocess recipe + pipeline graph API."""

from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from labcore.preprocess.pipeline_graph import pipeline_graph_html
from labcore.preprocess.recipe import RecipeSpec, compile_recipe
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["preprocess"])


class GraphBody(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=1, max_length=5000)
    recipe: dict[str, Any] | None = None


@router.post("/api/v1/preprocess/pipeline-graph")
def preprocess_pipeline_graph(
    body: GraphBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    df = pd.DataFrame(body.rows)
    try:
        recipe = RecipeSpec(**(body.recipe or {}))
        pipe, cols, meta = compile_recipe(df, recipe)
        graph = pipeline_graph_html(pipe)
        return {**graph, "feature_columns": cols, "meta": meta}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
