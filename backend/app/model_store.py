"""In-memory fitted model registry for thin Phase 3 predict/explain."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class StoredModel:
    id: str
    task: str
    target: str | None
    dataset_id: str
    feature_names: list[str]
    feature_contract: dict[str, Any]
    pipeline: Any
    meta: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class ModelStore:
    def __init__(self) -> None:
        self._models: dict[str, StoredModel] = {}

    def put(self, model: StoredModel) -> StoredModel:
        self._models[model.id] = model
        return model

    def get(self, model_id: str) -> StoredModel | None:
        return self._models.get(model_id)

    def list(self) -> list[StoredModel]:
        return list(self._models.values())

    def create(
        self,
        *,
        task: str,
        target: str | None,
        dataset_id: str,
        feature_names: list[str],
        feature_contract: dict[str, Any],
        pipeline: Any,
        meta: dict[str, Any] | None = None,
    ) -> StoredModel:
        mid = str(uuid4())
        contract = dict(feature_contract)
        contract["model_id"] = mid
        return self.put(
            StoredModel(
                id=mid,
                task=task,
                target=target,
                dataset_id=dataset_id,
                feature_names=feature_names,
                feature_contract=contract,
                pipeline=pipeline,
                meta=meta or {},
            )
        )


MODEL_STORE = ModelStore()
