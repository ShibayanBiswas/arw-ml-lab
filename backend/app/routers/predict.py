"""Predict + explain routes (Phase 3 / 3A thin Prediction Studio)."""

from __future__ import annotations

import io
from typing import Any, Literal

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response
from labcore.explain.shap_trees import tree_shap_explain
from labcore.predict.score import predict_batch, predict_single
from labcore.predict.template import (
    predictions_to_safe_csv,
    sample_row_from_contract,
    template_csv_bytes,
    template_xlsx_bytes,
)
from labcore.predict.validate import validate_predict_frame
from pydantic import BaseModel, Field

from backend.app.model_store import MODEL_STORE
from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["predict"])

# Thin sync batch cap (Celery chunking deferred to 3A-cont)
_BATCH_ROW_CAP = 5_000


class PredictSingleBody(BaseModel):
    row: dict[str, Any]


class PredictBatchBody(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=1)


class ExplainBody(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=1, max_length=50)


class StudioBatchBody(BaseModel):
    model_id: str
    rows: list[dict[str, Any]] = Field(min_length=1)


def _get_model(model_id: str):  # noqa: ANN202
    m = MODEL_STORE.get(model_id)
    if m is None:
        raise HTTPException(status_code=404, detail="model not found")
    return m


@router.get("/api/v1/models")
def list_models(user: AuthUser = Depends(require_write_role)) -> list[dict[str, Any]]:
    _ = user
    return [
        {
            "id": m.id,
            "task": m.task,
            "target": m.target,
            "dataset_id": m.dataset_id,
            "n_features": len(m.feature_names),
            "meta": m.meta,
        }
        for m in MODEL_STORE.list()
    ]


@router.get("/api/v1/models/{model_id}/schema")
def model_schema(model_id: str, user: AuthUser = Depends(require_write_role)) -> dict[str, Any]:
    _ = user
    return _get_model(model_id).feature_contract


@router.get("/api/v1/models/{model_id}/template")
def model_template(
    model_id: str,
    format: Literal["csv", "xlsx"] = Query(default="csv"),
    user: AuthUser = Depends(require_write_role),
) -> Response:
    _ = user
    m = _get_model(model_id)
    if format == "xlsx":
        data = template_xlsx_bytes(m.feature_contract, feature_names=m.feature_names)
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="predict_template_{model_id[:8]}.xlsx"'
                )
            },
        )
    data = template_csv_bytes(m.feature_contract, feature_names=m.feature_names)
    return Response(
        content=data,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="predict_template_{model_id[:8]}.csv"'
            )
        },
    )


@router.get("/api/v1/models/{model_id}/sample-row")
def model_sample_row(model_id: str, user: AuthUser = Depends(require_write_role)) -> dict[str, Any]:
    _ = user
    m = _get_model(model_id)
    return {
        "row": sample_row_from_contract(m.feature_contract, feature_names=m.feature_names),
        "feature_names": m.feature_names,
    }


@router.post("/api/v1/models/{model_id}/predict")
def predict_one(
    model_id: str,
    body: PredictSingleBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Thin single-row predict (alias for Prediction Studio POST /predict/single)."""
    _ = user
    m = _get_model(model_id)
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
    m = _get_model(model_id)
    X = pd.DataFrame(body.rows)
    try:
        return predict_batch(m.pipeline, X, feature_names=m.feature_names)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _score_validated(
    m: Any,
    report: Any,
) -> dict[str, Any]:
    payload = report.to_dict()
    if not report.ok or report.coerced is None:
        return {
            "validation": payload,
            "scored": False,
            "predictions": None,
            "csv": None,
        }
    scored = predict_batch(m.pipeline, report.coerced, feature_names=m.feature_names)
    out_df = report.coerced.copy()
    out_df["prediction"] = scored["predictions"]
    if scored.get("probabilities") is not None:
        proba = scored["probabilities"]
        if proba and isinstance(proba[0], list):
            for j in range(len(proba[0])):
                out_df[f"proba_{j}"] = [row[j] for row in proba]
        else:
            out_df["probability"] = proba
    csv_bytes = predictions_to_safe_csv(out_df)
    return {
        "validation": payload,
        "scored": True,
        "refit": False,
        "n_rows": scored["n_rows"],
        "predictions": scored["predictions"],
        "probabilities": scored.get("probabilities"),
        "csv": csv_bytes.decode("utf-8"),
    }


@router.post("/api/v1/predict/batch")
def predict_batch_studio(
    body: StudioBatchBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Validate + score JSON rows (sync thin path ≤5k rows)."""
    _ = user
    m = _get_model(body.model_id)
    if len(body.rows) > _BATCH_ROW_CAP:
        raise HTTPException(
            status_code=422,
            detail=f"PV02: row cap {_BATCH_ROW_CAP} exceeded (thin sync path)",
        )
    df = pd.DataFrame(body.rows)
    report = validate_predict_frame(
        df,
        m.feature_contract,
        required_names=m.feature_names,
        source_name="rows.json",
    )
    try:
        return _score_validated(m, report)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/predict/batch/upload")
async def predict_batch_upload(
    model_id: str = Form(...),
    file: UploadFile = File(...),
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Validate + score an uploaded CSV/XLSX (sync thin path)."""
    _ = user
    m = _get_model(model_id)
    raw = await file.read()
    name = file.filename or "upload.csv"
    suf = name.rsplit(".", 1)[-1].lower() if "." in name else "csv"
    try:
        if suf in {"xlsx", "xls"}:
            df = pd.read_excel(io.BytesIO(raw), engine="calamine")
        else:
            df = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"PV01: cannot parse file ({exc})") from exc
    if len(df) > _BATCH_ROW_CAP:
        raise HTTPException(
            status_code=422,
            detail=f"PV02: row cap {_BATCH_ROW_CAP} exceeded (thin sync path)",
        )
    report = validate_predict_frame(
        df,
        m.feature_contract,
        required_names=m.feature_names,
        source_name=name,
    )
    try:
        return _score_validated(m, report)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/predict/batch/sample/{sample_key}")
def predict_batch_bundled_sample(
    sample_key: str,
    model_id: str,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Score a bundled prediction sample (thin DS3 smoke)."""
    _ = user
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    mapping = {
        "DS3": root / "data" / "samples" / "predict" / "titanic_predict.csv",
        "titanic": root / "data" / "samples" / "predict" / "titanic_predict.csv",
    }
    path = mapping.get(sample_key)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail=f"predict sample '{sample_key}' not found")
    m = _get_model(model_id)
    df = pd.read_csv(path)
    if len(df) > _BATCH_ROW_CAP:
        df = df.iloc[:_BATCH_ROW_CAP]
    report = validate_predict_frame(
        df,
        m.feature_contract,
        required_names=m.feature_names,
        source_name=path.name,
    )
    try:
        return _score_validated(m, report)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/v1/explain/{model_id}")
def explain_model(
    model_id: str,
    body: ExplainBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    _ = user
    m = _get_model(model_id)
    X = pd.DataFrame(body.rows)
    model = m.pipeline
    if hasattr(model, "named_steps") and "model" in model.named_steps:
        pre = model[:-1]
        leaf = model.named_steps["model"]
        Xt = pre.transform(X[m.feature_names])
        return tree_shap_explain(leaf, Xt)
    return tree_shap_explain(model, X[m.feature_names])
