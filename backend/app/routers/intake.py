"""Intake API — ARCHITECTURE §33.12."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Response, status
from labcore.intake.validator import apply_overrides, confirm_guard, validate_proposal
from pydantic import BaseModel, Field

from backend.app.dataset_store import DATASET_STORE
from backend.app.intake_store import INTAKE_STORE
from backend.app.jobs_store import JOB_STORE
from backend.app.schemas import JobCreateResponse
from backend.app.security import AuthUser, get_current_user, require_write_role
from backend.worker.tasks.intake import run_intake_task

router = APIRouter(tags=["intake"])


class IntakeRunBody(BaseModel):
    use_llm: bool = False
    depth: str = "standard"


class IntakePatchBody(BaseModel):
    overrides: dict = Field(default_factory=dict)


class ConfirmBody(BaseModel):
    experiment_name: str | None = None


class FeedbackBody(BaseModel):
    proposal_id: str
    accepted: bool
    overrides: dict | None = None


class NewVersionBody(BaseModel):
    mode: str = "replace"  # append | replace | upsert
    upload_ref: str | None = None
    local_path: str | None = None
    key: str | None = None


def _enqueue_intake(version_id: str, parent_version_id: str | None = None) -> str:
    rec = JOB_STORE.create()
    try:
        run_intake_task.delay(
            rec.job_id, version_id, parent_version_id=parent_version_id, use_llm=False
        )
    except Exception:
        run_intake_task.apply(
            args=(rec.job_id, version_id),
            kwargs={"parent_version_id": parent_version_id, "use_llm": False},
        )
    return rec.job_id


@router.post(
    "/api/v1/intake/{version_id}/run",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=JobCreateResponse,
)
def run_intake_endpoint(
    version_id: str,
    body: IntakeRunBody,
    response: Response,
    user: AuthUser = Depends(require_write_role),
) -> JobCreateResponse:
    _ = body
    ds = DATASET_STORE.get(version_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="version not found")
    _ = user
    job_id = _enqueue_intake(version_id, ds.parent_version_id)
    response.status_code = status.HTTP_202_ACCEPTED
    return JobCreateResponse(job_id=job_id)


@router.get("/api/v1/intake/{version_id}")
def get_intake(version_id: str, user: AuthUser = Depends(get_current_user)) -> dict:
    _ = user
    rec = INTAKE_STORE.latest_for_version(version_id)
    if rec is None:
        # try sync run for tests / missing hook
        ds = DATASET_STORE.get(version_id)
        if ds is None:
            raise HTTPException(status_code=404, detail="version not found")
        raise HTTPException(status_code=404, detail="proposal not found; POST /run first")
    return {
        "id": rec.id,
        "dataset_version_id": rec.dataset_version_id,
        "status": rec.status,
        "rules_version": rec.rules_version,
        "detector_output": rec.detector_output,
        "llm_output": rec.llm_output,
        "merged": rec.merged,
        "validator_report": rec.validator_report,
        "user_overrides": rec.user_overrides,
        "confidence_overall": rec.confidence_overall,
        "versioning": rec.versioning,
        "experiment_id": rec.experiment_id,
    }


@router.patch("/api/v1/intake/proposals/{proposal_id}")
def patch_intake(
    proposal_id: str,
    body: IntakePatchBody,
    user: AuthUser = Depends(require_write_role),
) -> dict:
    _ = user
    rec = INTAKE_STORE.get(proposal_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="proposal not found")
    roles = (rec.merged or {}).get("roles") or {}
    merged = apply_overrides(rec.merged, body.overrides, roles)
    report = validate_proposal(merged, column_names=set(roles.keys()), roles=roles)
    INTAKE_STORE.update(
        proposal_id,
        merged=merged,
        user_overrides=body.overrides,
        validator_report=report,
        status="edited",
    )
    return {"id": proposal_id, "merged": merged, "validator_report": report, "status": "edited"}


@router.post("/api/v1/intake/proposals/{proposal_id}/confirm")
def confirm_intake(
    proposal_id: str,
    body: ConfirmBody,
    user: AuthUser = Depends(require_write_role),
) -> dict:
    rec = INTAKE_STORE.get(proposal_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="proposal not found")
    roles = (rec.merged or {}).get("roles") or {}
    try:
        confirm_guard(rec.merged, roles)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    fam = (rec.merged.get("family") or {}).get("proposed") or "supervised_non_sequential"
    targets = rec.merged.get("targets") or []
    primary = next((t for t in targets if t.get("column") != "__derived__"), targets[0] if targets else None)
    task_spec = {
        "family": fam,
        "financial": bool((rec.merged.get("family") or {}).get("financial")),
        "task": (rec.merged.get("task") or {}).get("type"),
        "target": (primary or {}).get("column"),
        "derived_target": (primary or {}).get("derived"),
        "time_index": rec.merged.get("time_index"),
        "frequency": rec.merged.get("frequency"),
        "features": [f.get("column") for f in (rec.merged.get("features") or [])],
        "excluded": rec.merged.get("excluded"),
        "horizon": rec.merged.get("horizon"),
        "cv": rec.merged.get("cv_recommendation"),
        "roles": roles,
    }
    exp = INTAKE_STORE.create_experiment(
        workspace_id=user.workspace_id or rec.workspace_id,
        dataset_version_id=rec.dataset_version_id,
        name=body.experiment_name or f"intake-{proposal_id[:8]}",
        family=str(fam),
        task_spec=task_spec,
        proposal_id=proposal_id,
    )
    import time as _time

    INTAKE_STORE.update(
        proposal_id,
        status="confirmed",
        confirmed_at=_time.time(),
        experiment_id=exp.id,
    )
    return {"experiment_id": exp.id, "task_spec": task_spec}


@router.post("/api/v1/intake/feedback")
def intake_feedback(body: FeedbackBody, user: AuthUser = Depends(require_write_role)) -> dict:
    _ = user
    rec = INTAKE_STORE.get(body.proposal_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="proposal not found")
    return {
        "ok": True,
        "proposal_id": body.proposal_id,
        "accepted": body.accepted,
        "overrides": body.overrides,
    }


@router.post(
    "/api/v1/datasets/{dataset_id}/versions",
    status_code=status.HTTP_202_ACCEPTED,
)
def new_dataset_version(
    dataset_id: str,
    body: NewVersionBody,
    response: Response,
    user: AuthUser = Depends(require_write_role),
) -> dict:
    parent = DATASET_STORE.get(dataset_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="dataset not found")
    from labcore.data.infer import infer_schema
    from labcore.data.readers import dataframe_meta, normalise_columns, read_tabular, write_parquet
    from labcore.data.task_detect import detect_task

    if body.local_path:
        path = Path(body.local_path)
    elif body.upload_ref:
        from backend.app.storage import get_storage

        storage = get_storage()
        lp = storage.local_path(body.upload_ref)
        path = lp if lp else Path(body.upload_ref)
    else:
        raise HTTPException(status_code=400, detail="upload_ref or local_path required")

    df = normalise_columns(read_tabular(path))
    parent_df = None
    if parent.parquet_path and Path(parent.parquet_path).exists():
        parent_df = pd.read_parquet(parent.parquet_path)
        if body.mode == "append" and parent_df is not None:
            df = pd.concat([parent_df, df], ignore_index=True)

    schema = infer_schema(df)
    task = detect_task(df, schema)
    out_dir = Path(".cache") / "parquet"
    out_dir.mkdir(parents=True, exist_ok=True)
    new_id = __import__("uuid").uuid4().hex
    pq = out_dir / f"{new_id}.parquet"
    digest = write_parquet(df, pq)
    group = parent.dataset_group_id or parent.id
    child = DATASET_STORE.create_dataset(
        id=new_id,
        workspace_id=user.workspace_id or parent.workspace_id,
        name=parent.name,
        source=parent.source,
        sample_id=parent.sample_id,
        storage_key=body.upload_ref,
        parquet_path=str(pq),
        content_hash=digest,
        schema=[c.model_dump() for c in schema],
        task=task.model_dump(),
        meta=dataframe_meta(df),
        parent_version_id=parent.id,
        update_mode=body.mode,
        dataset_group_id=group,
        version=parent.version + 1,
    )
    job_id = _enqueue_intake(child.id, parent.id)
    response.status_code = status.HTTP_202_ACCEPTED
    return {"job_id": job_id, "version_id": child.id}


@router.get("/api/v1/datasets/{dataset_id}/versions/{version_id}/diff")
def get_diff(
    dataset_id: str,
    version_id: str,
    against: str | None = None,
    user: AuthUser = Depends(get_current_user),
) -> dict:
    _ = user
    _ = dataset_id
    child = DATASET_STORE.get(version_id)
    if child is None:
        raise HTTPException(status_code=404, detail="version not found")
    parent_id = against if against and against != "parent" else child.parent_version_id
    if not parent_id:
        raise HTTPException(status_code=400, detail="no parent to diff against")
    key = f"{version_id}:{parent_id}"
    cached = INTAKE_STORE.get_diff(key)
    if cached:
        return cached
    parent = DATASET_STORE.get(parent_id)
    if parent is None or not parent.parquet_path or not child.parquet_path:
        raise HTTPException(status_code=404, detail="parquet missing")
    from labcore.intake.d7_diff import schema_diff
    from labcore.intake.d8_drift import drift_report

    pdf = pd.read_parquet(parent.parquet_path)
    cdf = pd.read_parquet(child.parquet_path)
    payload = {"diff": schema_diff(pdf, cdf), "drift": drift_report(pdf, cdf)}
    INTAKE_STORE.save_diff(key, payload)
    return payload


@router.get("/api/v1/datasets/{dataset_id}/lineage")
def lineage(dataset_id: str, user: AuthUser = Depends(get_current_user)) -> dict:
    _ = user
    root = DATASET_STORE.get(dataset_id)
    if root is None:
        raise HTTPException(status_code=404, detail="dataset not found")
    group = root.dataset_group_id or root.id
    nodes = []
    for d in DATASET_STORE.list_datasets(root.workspace_id):
        if (d.dataset_group_id or d.id) == group or d.id == group or d.parent_version_id == dataset_id:
            nodes.append(
                {
                    "id": d.id,
                    "parent_version_id": d.parent_version_id,
                    "version": d.version,
                    "update_mode": d.update_mode,
                    "content_hash": d.content_hash,
                }
            )
    return {"dataset_id": dataset_id, "nodes": nodes}


@router.get("/api/v1/datasets/{dataset_id}/impact")
def impact(
    dataset_id: str,
    version: str | None = None,
    user: AuthUser = Depends(get_current_user),
) -> dict:
    _ = version
    ws = user.workspace_id
    exps = [
        {"id": e.id, "name": e.name, "dataset_version_id": e.dataset_version_id}
        for e in INTAKE_STORE.list_experiments(ws)
        if e.dataset_version_id == dataset_id or DATASET_STORE.get(e.dataset_version_id)
    ]
    return {
        "dataset_id": dataset_id,
        "experiments": exps,
        "registered_models": [],
        "wfo_runs": [],
        "suggested_actions": ["refresh_eda", "reconfirm_intake"] if exps else ["run_intake"],
    }
