"""Train Celery payload must carry workspace_id — oneshot-c227."""

from pathlib import Path


def test_experiments_train_injects_workspace_id() -> None:
    src = Path("backend/app/routers/experiments.py").read_text(encoding="utf-8")
    assert 'train_payload["workspace_id"]' in src
    assert "run_train_task.apply_async" in src
