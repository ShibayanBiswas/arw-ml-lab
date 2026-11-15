"""In-memory intake proposals / experiments for Phase 1A."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntakeRecord:
    id: str
    workspace_id: str
    dataset_version_id: str
    rules_version: str
    detector_output: dict[str, Any]
    llm_output: dict[str, Any] | None
    merged: dict[str, Any]
    validator_report: dict[str, Any]
    status: str = "proposed"
    user_overrides: dict[str, Any] = field(default_factory=dict)
    confidence_overall: float = 0.0
    versioning: dict[str, Any] | None = None
    created_at: float = field(default_factory=time.time)
    confirmed_at: float | None = None
    experiment_id: str | None = None


@dataclass
class ExperimentRecord:
    id: str
    workspace_id: str
    dataset_version_id: str
    name: str
    family: str
    task_spec: dict[str, Any]
    proposal_id: str
    created_at: float = field(default_factory=time.time)


class IntakeStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._proposals: dict[str, IntakeRecord] = {}
        self._by_version: dict[str, str] = {}  # version_id -> latest proposal_id
        self._experiments: dict[str, ExperimentRecord] = {}
        self._lineage: dict[str, list[str]] = {}  # dataset_id -> version ids
        self._diffs: dict[str, dict[str, Any]] = {}

    def save_proposal(self, **kwargs: Any) -> IntakeRecord:
        with self._lock:
            pid = kwargs.pop("id", None) or str(uuid.uuid4())
            rec = IntakeRecord(id=pid, **kwargs)
            self._proposals[pid] = rec
            self._by_version[rec.dataset_version_id] = pid
            return rec

    def get(self, proposal_id: str) -> IntakeRecord | None:
        with self._lock:
            return self._proposals.get(proposal_id)

    def latest_for_version(self, version_id: str) -> IntakeRecord | None:
        with self._lock:
            pid = self._by_version.get(version_id)
            return self._proposals.get(pid) if pid else None

    def update(self, proposal_id: str, **kwargs: Any) -> IntakeRecord | None:
        with self._lock:
            rec = self._proposals.get(proposal_id)
            if rec is None:
                return None
            for k, v in kwargs.items():
                if hasattr(rec, k):
                    setattr(rec, k, v)
            return rec

    def create_experiment(self, **kwargs: Any) -> ExperimentRecord:
        with self._lock:
            eid = kwargs.pop("id", None) or str(uuid.uuid4())
            exp = ExperimentRecord(id=eid, **kwargs)
            self._experiments[eid] = exp
            return exp

    def list_experiments(self, workspace_id: str | None = None) -> list[ExperimentRecord]:
        with self._lock:
            items = list(self._experiments.values())
        if workspace_id:
            items = [e for e in items if e.workspace_id == workspace_id]
        return items

    def save_diff(self, key: str, payload: dict[str, Any]) -> None:
        with self._lock:
            self._diffs[key] = payload

    def get_diff(self, key: str) -> dict[str, Any] | None:
        with self._lock:
            return self._diffs.get(key)


INTAKE_STORE = IntakeStore()
