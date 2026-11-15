"""EDA run API — Phase 1."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status

from backend.app.dataset_store import DATASET_STORE
from backend.app.jobs_store import JOB_STORE
from backend.app.schemas import JobCreateResponse
from backend.app.security import AuthUser, get_current_user, require_write_role
from backend.worker.tasks.eda import run_eda_task

router = APIRouter(prefix="/api/v1/eda", tags=["eda"])


@router.post(
    "/{dataset_version_id}/run",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=JobCreateResponse,
)
def start_eda(
    dataset_version_id: str,
    response: Response,
    user: AuthUser = Depends(require_write_role),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> JobCreateResponse:
    _ = user
    ds = DATASET_STORE.get(dataset_version_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="dataset not found")
    if not ds.parquet_path:
        raise HTTPException(status_code=409, detail="dataset not ingested yet")
    rec = JOB_STORE.create(idempotency_key=idempotency_key)
    run = DATASET_STORE.create_eda_run(dataset_version_id=dataset_version_id, job_id=rec.job_id)
    # Seed result before enqueue so eager workers merge onto known ids
    JOB_STORE.update(rec.job_id, result={"eda_run_id": run.id, "dataset_id": dataset_version_id})
    try:
        run_eda_task.delay(rec.job_id, run.id, dataset_version_id)
    except Exception:
        run_eda_task.apply(args=(rec.job_id, run.id, dataset_version_id))
    response.status_code = status.HTTP_202_ACCEPTED
    return JobCreateResponse(job_id=rec.job_id)


@router.get("/{run_id}")
def get_eda_run(run_id: str, user: AuthUser = Depends(get_current_user)) -> dict:
    _ = user
    run = DATASET_STORE.get_eda(run_id)
    if run is None:
        # Also allow lookup by job_id result
        raise HTTPException(status_code=404, detail="eda run not found")
    return {
        "id": run.id,
        "dataset_version_id": run.dataset_version_id,
        "job_id": run.job_id,
        "status": run.status,
        "summary": run.result_summary,
        "insights": run.insights,
        "artefact_count": len(run.artefacts),
        "artefacts": run.artefacts,
    }


@router.get("/by-job/{job_id}")
def get_eda_by_job(job_id: str, user: AuthUser = Depends(get_current_user)) -> dict:
    _ = user
    job = JOB_STORE.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    eda_run_id = (job.result or {}).get("eda_run_id")
    if not eda_run_id:
        found = DATASET_STORE.find_eda_by_job(job_id)
        eda_run_id = found.id if found else None
    if not eda_run_id:
        raise HTTPException(status_code=404, detail="eda run not found for job")
    return get_eda_run(eda_run_id, user)
