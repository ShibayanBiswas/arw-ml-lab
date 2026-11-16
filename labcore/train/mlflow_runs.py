"""MLflow nested run helpers (ARCHITECTURE §17 / §21) — thin wrappers."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any


@contextmanager
def nested_run(
    *,
    experiment: str,
    run_name: str,
    nested: bool = True,
    tags: dict[str, str] | None = None,
    tracking_uri: str | None = None,
) -> Iterator[Any]:
    """
    Yield an active MLflow run (optionally nested).

    Prefer a DB tracking URI (e.g. ``sqlite:///mlflow.db``). Restores prior
    tracking URI / ``MLFLOW_TRACKING_URI`` on exit. No fabricated metrics.
    """
    import mlflow

    prev_uri = mlflow.get_tracking_uri()
    prev_env = os.environ.get("MLFLOW_TRACKING_URI")
    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
            # Do not export to env — keep Optuna tune tests isolated
        mlflow.set_experiment(experiment)
        with mlflow.start_run(run_name=run_name, nested=nested) as run:
            if tags:
                mlflow.set_tags(tags)
            yield run
    finally:
        mlflow.set_tracking_uri(prev_uri)
        if prev_env is None:
            os.environ.pop("MLFLOW_TRACKING_URI", None)
        else:
            os.environ["MLFLOW_TRACKING_URI"] = prev_env


def log_fold_metrics(
    fold: int,
    metrics: dict[str, float],
    *,
    prefix: str = "fold",
) -> None:
    """Log per-fold scalars onto the active MLflow run."""
    import mlflow

    for key, value in metrics.items():
        if value is None:
            continue
        mlflow.log_metric(f"{prefix}_{fold}_{key}", float(value))
