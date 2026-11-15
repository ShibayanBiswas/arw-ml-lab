"""In-memory dataset registry for Phase 1 (DB persistence arrives with hosted stack)."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DatasetVersion:
    id: str
    workspace_id: str
    name: str
    source: str  # upload | sample
    sample_id: str | None
    storage_key: str | None
    parquet_path: str | None
    content_hash: str | None
    schema: list[dict[str, Any]] = field(default_factory=list)
    task: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    parent_version_id: str | None = None
    update_mode: str | None = None  # append | replace | upsert | initial
    dataset_group_id: str | None = None  # logical dataset id across versions
    version: int = 1
    created_at: float = field(default_factory=time.time)


@dataclass
class EDARun:
    id: str
    dataset_version_id: str
    job_id: str
    status: str = "queued"
    result_summary: dict[str, Any] = field(default_factory=dict)
    artefacts: list[dict[str, Any]] = field(default_factory=list)
    insights: list[dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


class DatasetStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._datasets: dict[str, DatasetVersion] = {}
        self._eda: dict[str, EDARun] = {}

    def create_dataset(self, **kwargs: Any) -> DatasetVersion:
        with self._lock:
            ds_id = kwargs.pop("id", None) or str(uuid.uuid4())
            ds = DatasetVersion(id=ds_id, **kwargs)
            self._datasets[ds_id] = ds
            return ds

    def list_datasets(self, workspace_id: str | None = None) -> list[DatasetVersion]:
        with self._lock:
            items = list(self._datasets.values())
        if workspace_id:
            items = [d for d in items if d.workspace_id == workspace_id]
        return sorted(items, key=lambda d: d.created_at, reverse=True)

    def get(self, dataset_id: str) -> DatasetVersion | None:
        with self._lock:
            return self._datasets.get(dataset_id)

    def update(self, dataset_id: str, **kwargs: Any) -> DatasetVersion | None:
        with self._lock:
            ds = self._datasets.get(dataset_id)
            if ds is None:
                return None
            for k, v in kwargs.items():
                if hasattr(ds, k):
                    setattr(ds, k, v)
            return ds

    def create_eda_run(self, *, dataset_version_id: str, job_id: str) -> EDARun:
        with self._lock:
            run = EDARun(id=str(uuid.uuid4()), dataset_version_id=dataset_version_id, job_id=job_id)
            self._eda[run.id] = run
            return run

    def get_eda(self, run_id: str) -> EDARun | None:
        with self._lock:
            return self._eda.get(run_id)

    def update_eda(self, run_id: str, **kwargs: Any) -> EDARun | None:
        with self._lock:
            run = self._eda.get(run_id)
            if run is None:
                return None
            for k, v in kwargs.items():
                if hasattr(run, k):
                    setattr(run, k, v)
            return run

    def find_eda_by_job(self, job_id: str) -> EDARun | None:
        with self._lock:
            for run in self._eda.values():
                if run.job_id == job_id:
                    return run
        return None


DATASET_STORE = DatasetStore()
