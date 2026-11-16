"""MLflow nested run thin wrapper."""

from __future__ import annotations

from pathlib import Path

import mlflow
from labcore.train.mlflow_runs import log_fold_metrics, nested_run


def test_nested_runs_log_real_metrics(tmp_path: Path):
    db = tmp_path / "mlflow.db"
    uri = f"sqlite:///{db.as_posix()}"
    with nested_run(
        experiment="lab-test",
        run_name="parent",
        nested=False,
        tracking_uri=uri,
        tags={"seed": "42"},
    ) as parent:
        parent_id = parent.info.run_id
        with nested_run(
            experiment="lab-test",
            run_name="fold0",
            nested=True,
            tracking_uri=uri,
        ):
            log_fold_metrics(0, {"roc_auc": 0.91, "log_loss": 0.32})
        child_runs = mlflow.search_runs(
            experiment_names=["lab-test"],
            filter_string=f"tags.mlflow.parentRunId = '{parent_id}'",
        )
        assert len(child_runs) >= 1
        assert "metrics.fold_0_roc_auc" in child_runs.columns
        assert float(child_runs["metrics.fold_0_roc_auc"].iloc[0]) == 0.91
