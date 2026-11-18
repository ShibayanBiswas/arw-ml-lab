"""Predict + explain routes (Phase 3 / 3A thin Prediction Studio)."""

from __future__ import annotations

import io
from typing import Any, Literal

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.responses import Response
from labcore.explain.ale import ale_1d
from labcore.explain.dice_cf import dice_counterfactuals
from labcore.explain.lime_tabular import lime_explain_row
from labcore.explain.permutation import permutation_explain
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

from backend.app.jobs_store import JOB_STORE
from backend.app.model_store import MODEL_STORE
from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["predict"])

# Sync path ≤5k; larger batches go to q.predict.batch (≤1M)
_BATCH_ROW_CAP = 5_000
_BATCH_ASYNC_CAP = 1_000_000


class PredictSingleBody(BaseModel):
    row: dict[str, Any]
    # ST-FEAT-01: None → apply default HumilityPolicy; False disables; dict overrides
    humility: dict[str, Any] | Literal[False] | None = None


class PredictBatchBody(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=1)


class ExplainBody(BaseModel):
    rows: list[dict[str, Any]] = Field(min_length=1, max_length=200)
    method: Literal["shap", "permutation", "lime", "dice", "ale"] = "shap"
    target_values: list[Any] | None = None
    total_cfs: int = Field(default=3, ge=1, le=10)
    ale_feature: str | None = None


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
            "Content-Disposition": (f'attachment; filename="predict_template_{model_id[:8]}.csv"')
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


def _humility_opts_for_row(m: Any, row: dict[str, Any], humility: dict[str, Any] | None) -> dict[str, Any]:
    """Merge client humility policy with PV10/PV OOR flags from validate (never refits)."""
    opts: dict[str, Any] = dict(humility or {})
    try:
        report = validate_predict_frame(
            pd.DataFrame([row]),
            m.feature_contract,
            required_names=m.feature_names,
        )
    except Exception:
        return opts
    ood_score = 0.0
    for issue in list(report.warnings) + list(report.info):
        if getattr(issue, "code", None) == "PV10":
            details = getattr(issue, "details", None) or {}
            if "max_score" in details:
                ood_score = float(details["max_score"])
    oor: list[str] = []
    for issue in list(report.warnings) + list(getattr(report, "errors", []) or []):
        details = getattr(issue, "details", None) or {}
        if details.get("flag") == "out_of_range":
            feat = details.get("feature") or getattr(issue, "column", None)
            if feat:
                oor.append(str(feat))
    opts.setdefault("ood_score", ood_score)
    if oor:
        opts.setdefault("flag_out_of_range", oor)
    return opts


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
        humility_arg: dict[str, Any] | None
        if body.humility is False:
            humility_arg = None
        else:
            humility_arg = _humility_opts_for_row(
                m, body.row, body.humility if isinstance(body.humility, dict) else None
            )
        return predict_single(
            m.pipeline,
            body.row,
            feature_names=m.feature_names,
            humility=humility_arg,
        )
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
    level = float(
        (m.feature_contract or {}).get("uncertainty", {}).get("confidence_level")
        or (m.feature_contract or {}).get("confidence_level")
        or 0.9
    )
    scored = predict_batch(
        m.pipeline,
        report.coerced,
        feature_names=m.feature_names,
        confidence_level=level,
    )
    out_df = report.coerced.copy()
    out_df["prediction"] = scored["predictions"]
    if scored.get("probabilities") is not None:
        proba = scored["probabilities"]
        if proba and isinstance(proba[0], list):
            for j in range(len(proba[0])):
                out_df[f"proba_{j}"] = [row[j] for row in proba]
        else:
            out_df["probability"] = proba
    for col in scored.get("interval_columns") or []:
        if col == "pred_interval_method":
            out_df[col] = scored.get("pred_interval_method")
        elif col in scored:
            out_df[col] = scored[col]
    for col in scored.get("classification_columns") or []:
        if col not in scored:
            continue
        if col == "pred_set":
            out_df[col] = [str(s) for s in scored[col]]
        else:
            out_df[col] = scored[col]
    # PV12 — row flag for lag lookback shortfall (oneshot-c254)
    insuff = list(getattr(report, "insufficient_history_rows", None) or [])
    if insuff:
        flag = pd.Series(False, index=out_df.index)
        for idx in insuff:
            if idx in flag.index:
                flag.loc[idx] = True
        out_df["insufficient_history"] = flag.to_numpy()
    # §45.4 — probabilities labelled calibrated vs uncalibrated from contract
    from labcore.predict.calibration_label import calibration_status_label
    from labcore.predict.threshold_label import pred_threshold_from_contract

    cal_status = calibration_status_label(m.feature_contract, m.pipeline)
    if scored.get("probabilities") is not None:
        out_df["calibration_status"] = cal_status
    thr = pred_threshold_from_contract(m.feature_contract)
    if thr is not None and scored.get("probabilities") is not None:
        out_df["pred_threshold"] = thr
    csv_bytes = predictions_to_safe_csv(out_df)
    return {
        "validation": payload,
        "scored": True,
        "refit": False,
        "n_rows": scored["n_rows"],
        "predictions": scored["predictions"],
        "probabilities": scored.get("probabilities"),
        "interval_columns": scored.get("interval_columns"),
        "classification_columns": scored.get("classification_columns"),
        "pred_confidence": scored.get("pred_confidence"),
        "pred_margin": scored.get("pred_margin"),
        "pred_entropy": scored.get("pred_entropy"),
        "pred_set": scored.get("pred_set"),
        "pred_set_method": scored.get("pred_set_method"),
        "pred_interval_method": scored.get("pred_interval_method"),
        "confidence_level": scored.get("confidence_level"),
        "calibration_status": cal_status if scored.get("probabilities") is not None else None,
        "pred_threshold": thr,
        "csv": csv_bytes.decode("utf-8"),
    }


@router.post("/api/v1/predict/batch")
def predict_batch_studio(
    body: StudioBatchBody,
    user: AuthUser = Depends(require_write_role),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    """Validate + score JSON rows.

    ≤5k rows: sync. >5k and ≤1M: enqueue ``lab.predict.batch`` (returns job_id).
    """
    _ = user
    m = _get_model(body.model_id)
    n = len(body.rows)
    if n > _BATCH_ASYNC_CAP:
        raise HTTPException(
            status_code=422,
            detail=f"PV02: row cap {_BATCH_ASYNC_CAP} exceeded",
        )
    if n > _BATCH_ROW_CAP:
        rec = JOB_STORE.create(idempotency_key=idempotency_key)
        from backend.worker.tasks.predict import run_predict_batch_task

        run_predict_batch_task.delay(rec.job_id, body.model_id, body.rows)
        return {
            "async": True,
            "job_id": rec.job_id,
            "n_rows": n,
            "chunk_size": 10_000,
            "message": "scoring on q.predict.batch — poll GET /api/v1/jobs/{job_id}",
        }
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


@router.post("/api/v1/predict/batch/{job_id}/cancel")
def predict_batch_cancel(
    job_id: str,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Cooperative cancel for Celery batch predict jobs."""
    _ = user
    job = JOB_STORE.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    JOB_STORE.update(job_id, status="cancelled", error="cancelled by user")
    return {"job_id": job_id, "status": "cancelled"}


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
            from labcore.security.upload_guard import XlsxUploadRejected, inspect_xlsx_archive

            try:
                inspect_xlsx_archive(raw)
            except XlsxUploadRejected as exc:
                raise HTTPException(status_code=422, detail=f"PV01: {exc.message}") from exc
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
    feats = [c for c in m.feature_names if c in X.columns]
    if body.method == "permutation":
        if not body.target_values or len(body.target_values) != len(body.rows):
            raise HTTPException(
                status_code=422,
                detail="permutation explain requires target_values aligned to rows",
            )
        y = body.target_values
        try:
            return permutation_explain(model, X[feats], y, seed=42)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    if body.method == "lime":
        try:
            return lime_explain_row(
                model,
                X[feats],
                X[feats].iloc[0],
                num_features=min(10, len(feats)),
                num_samples=1000,
                seed=42,
            )
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    if body.method == "dice":
        if not body.target_values or len(body.target_values) != len(body.rows):
            raise HTTPException(
                status_code=422,
                detail="dice explain requires target_values aligned to rows",
            )
        try:
            return dice_counterfactuals(
                model,
                X[feats],
                body.target_values,
                X[feats].iloc[[0]],
                total_cfs=body.total_cfs,
                seed=42,
            )
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    if body.method == "ale":
        feat = body.ale_feature or (feats[0] if feats else None)
        if not feat:
            raise HTTPException(status_code=422, detail="ale_feature required")
        try:
            return ale_1d(model, X[feats], feat, grid_size=15, seed=42)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    if hasattr(model, "named_steps") and "model" in model.named_steps:
        pre = model[:-1]
        leaf = model.named_steps["model"]
        Xt = pre.transform(X[feats])
        return tree_shap_explain(leaf, Xt)
    return tree_shap_explain(model, X[feats])
