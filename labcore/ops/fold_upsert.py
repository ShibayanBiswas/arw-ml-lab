"""Idempotent fold/result upserts — OPS-04 / ST-OPS-03 (ARCHITECTURE §46.2).

Keyed by ``(run_id, fold, algorithm_key)`` so Celery retries do not double-write
``cv_folds`` / ``model_metrics`` rows.
"""

from __future__ import annotations

from typing import Any

ARTEFACT_ID = "OPS.FOLD.UPSERT"
STRESS_ID = "ST-OPS-03"

UPSERT_CV_FOLDS_SQL = """
INSERT INTO public.cv_folds (workspace_id, run_id, fold, algorithm_key, n_train, n_val, metrics)
VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
ON CONFLICT (run_id, fold, algorithm_key)
DO UPDATE SET
  n_train = EXCLUDED.n_train,
  n_val = EXCLUDED.n_val,
  metrics = EXCLUDED.metrics
RETURNING id;
"""

UNIQUE_INDEX_SQL = """
CREATE UNIQUE INDEX IF NOT EXISTS cv_folds_run_fold_algo_uidx
  ON public.cv_folds (run_id, fold, algorithm_key);
"""


def fold_key(run_id: str, fold: int, algorithm_key: str) -> tuple[str, int, str]:
    return (str(run_id), int(fold), str(algorithm_key))


class InMemoryFoldStore:
    """Offline stand-in for Postgres upserts (seeded tests)."""

    def __init__(self) -> None:
        self._rows: dict[tuple[str, int, str], dict[str, Any]] = {}

    def upsert(
        self,
        *,
        run_id: str,
        fold: int,
        algorithm_key: str,
        n_train: int | None = None,
        n_val: int | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        key = fold_key(run_id, fold, algorithm_key)
        row = {
            "run_id": run_id,
            "fold": int(fold),
            "algorithm_key": algorithm_key,
            "n_train": n_train,
            "n_val": n_val,
            "metrics": dict(metrics or {}),
        }
        self._rows[key] = row
        return row

    def get(self, run_id: str, fold: int, algorithm_key: str) -> dict[str, Any] | None:
        return self._rows.get(fold_key(run_id, fold, algorithm_key))

    def __len__(self) -> int:
        return len(self._rows)
