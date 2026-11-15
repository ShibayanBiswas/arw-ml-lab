"""In-memory experiment / leaderboard store (Phase 2 thin)."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExperimentRecord:
    id: str
    workspace_id: str
    dataset_id: str
    name: str
    family: str
    task_spec: dict[str, Any]
    status: str = "created"
    leaderboard: list[dict[str, Any]] = field(default_factory=list)
    result: dict[str, Any] | None = None
    created_at: float = field(default_factory=time.time)


class ExperimentStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._items: dict[str, ExperimentRecord] = {}

    def create(self, **kwargs: Any) -> ExperimentRecord:
        with self._lock:
            eid = str(uuid.uuid4())
            rec = ExperimentRecord(id=eid, **kwargs)
            self._items[eid] = rec
            return rec

    def get(self, eid: str) -> ExperimentRecord | None:
        return self._items.get(eid)

    def update(self, eid: str, **kwargs: Any) -> ExperimentRecord | None:
        with self._lock:
            rec = self._items.get(eid)
            if not rec:
                return None
            for k, v in kwargs.items():
                setattr(rec, k, v)
            return rec

    def list_for_workspace(self, workspace_id: str) -> list[ExperimentRecord]:
        return [r for r in self._items.values() if r.workspace_id == workspace_id]


EXPERIMENT_STORE = ExperimentStore()
