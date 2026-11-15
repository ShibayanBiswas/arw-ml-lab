"""Dataset upload / sample load / preview — Phase 1."""

from __future__ import annotations

from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from labcore.data.samples import list_samples
from pydantic import BaseModel

from backend.app.dataset_store import DATASET_STORE
from backend.app.jobs_store import JOB_STORE
from backend.app.schemas import JobCreateResponse
from backend.app.security import AuthUser, get_current_user, require_write_role
from backend.app.storage import get_storage
from backend.worker.tasks.ingest import ingest_dataset, ingest_sample

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])


class UploadUrlRequest(BaseModel):
    filename: str
    content_type: str = "text/csv"


class CreateDatasetRequest(BaseModel):
    name: str
    storage_key: str
    target: str | None = None
    family_hint: str | None = None


class SchemaPatch(BaseModel):
    column: str
    semantic_type: str | None = None
    role_suggestion: str | None = None


@router.get("/samples")
def get_samples(user: AuthUser = Depends(get_current_user)) -> list[dict]:
    _ = user
    return list_samples()


@router.post("/upload-url")
def upload_url(
    body: UploadUrlRequest,
    user: AuthUser = Depends(require_write_role),
) -> dict:
    storage = get_storage()
    ws = user.workspace_id or "default"
    return storage.create_upload_url(
        workspace_id=ws, filename=body.filename, content_type=body.content_type
    )


@router.put("/upload-local/{key:path}")
async def upload_local(
    key: str,
    request: Request,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, str]:
    _ = user
    data = await request.body()
    if len(data) > 200 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="file too large")
    storage = get_storage()
    storage.put_bytes(key, data)
    return {"key": key, "bytes": str(len(data))}


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=JobCreateResponse)
def create_dataset(
    body: CreateDatasetRequest,
    response: Response,
    user: AuthUser = Depends(require_write_role),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> JobCreateResponse:
    ds = DATASET_STORE.create_dataset(
        workspace_id=user.workspace_id or "default",
        name=body.name,
        source="upload",
        sample_id=None,
        storage_key=body.storage_key,
        parquet_path=None,
        content_hash=None,
    )
    rec = JOB_STORE.create(idempotency_key=idempotency_key)
    JOB_STORE.update(rec.job_id, result={"dataset_id": ds.id})
    try:
        ingest_dataset.delay(
            rec.job_id,
            ds.id,
            storage_key=body.storage_key,
            target=body.target,
            family_hint=body.family_hint,
        )
    except Exception:
        ingest_dataset.apply(
            args=(rec.job_id, ds.id),
            kwargs={
                "storage_key": body.storage_key,
                "target": body.target,
                "family_hint": body.family_hint,
            },
        )
    response.status_code = status.HTTP_202_ACCEPTED
    return JobCreateResponse(job_id=rec.job_id)


@router.post(
    "/samples/{sample_id}/load",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=JobCreateResponse,
)
def load_sample_endpoint(
    sample_id: str,
    response: Response,
    user: AuthUser = Depends(require_write_role),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> JobCreateResponse:
    ds = DATASET_STORE.create_dataset(
        workspace_id=user.workspace_id or "default",
        name=sample_id,
        source="sample",
        sample_id=sample_id,
        storage_key=None,
        parquet_path=None,
        content_hash=None,
    )
    rec = JOB_STORE.create(idempotency_key=idempotency_key)
    JOB_STORE.update(rec.job_id, result={"dataset_id": ds.id})
    try:
        ingest_sample.delay(rec.job_id, ds.id, sample_id)
    except Exception:
        ingest_sample.apply(args=(rec.job_id, ds.id, sample_id))
    response.status_code = status.HTTP_202_ACCEPTED
    return JobCreateResponse(job_id=rec.job_id)


@router.get("")
def list_datasets(user: AuthUser = Depends(get_current_user)) -> list[dict]:
    items = DATASET_STORE.list_datasets(user.workspace_id)
    return [
        {
            "id": d.id,
            "name": d.name,
            "source": d.source,
            "sample_id": d.sample_id,
            "content_hash": d.content_hash,
            "meta": d.meta,
            "task": d.task,
        }
        for d in items
    ]


@router.get("/{dataset_id}/preview")
def preview_dataset(dataset_id: str, user: AuthUser = Depends(get_current_user)) -> dict:
    _ = user
    ds = DATASET_STORE.get(dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="dataset not found")
    rows: list[dict] = []
    if ds.parquet_path and Path(ds.parquet_path).exists():
        import pandas as pd

        df = pd.read_parquet(ds.parquet_path)
        rows = (
            df.head(50)
            .astype(object)
            .where(pd.notnull(df.head(50)), None)
            .to_dict(orient="records")
        )
    return {
        "id": ds.id,
        "name": ds.name,
        "schema": ds.schema,
        "task": ds.task,
        "meta": ds.meta,
        "preview": rows,
    }


@router.patch("/{dataset_id}/schema")
def patch_schema(
    dataset_id: str,
    body: SchemaPatch,
    user: AuthUser = Depends(require_write_role),
) -> dict:
    _ = user
    ds = DATASET_STORE.get(dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="dataset not found")
    schema = list(ds.schema)
    found = False
    for col in schema:
        if col.get("name") == body.column:
            if body.semantic_type is not None:
                col["semantic_type"] = body.semantic_type
            if body.role_suggestion is not None:
                col["role_suggestion"] = body.role_suggestion
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="column not found")
    DATASET_STORE.update(dataset_id, schema=schema)
    return {"id": dataset_id, "schema": schema}


@router.post("/direct-upload", status_code=status.HTTP_202_ACCEPTED)
async def direct_upload(
    response: Response,
    file: UploadFile = File(...),
    user: AuthUser = Depends(require_write_role),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict:
    """Dev helper: multipart upload → local storage → ingest (tests without signed URL round-trip)."""
    data = await file.read()
    storage = get_storage()
    key = f"{user.workspace_id or 'default'}/{file.filename or 'upload.csv'}"
    storage.put_bytes(key, data, content_type=file.content_type or "text/csv")
    ds = DATASET_STORE.create_dataset(
        workspace_id=user.workspace_id or "default",
        name=file.filename or "upload",
        source="upload",
        sample_id=None,
        storage_key=key,
        parquet_path=None,
        content_hash=None,
    )
    rec = JOB_STORE.create(idempotency_key=idempotency_key)
    try:
        ingest_dataset.delay(rec.job_id, ds.id, storage_key=key)
    except Exception:
        ingest_dataset.apply(args=(rec.job_id, ds.id), kwargs={"storage_key": key})
    response.status_code = status.HTTP_202_ACCEPTED
    return {"job_id": rec.job_id, "dataset_id": ds.id}
