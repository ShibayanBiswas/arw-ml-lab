"""lab-beat maintenance — OPS-03 reaper, OPS-07 retention, OPS-06 trim (oneshot-c101)."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest
from backend.app.jobs_store import JOB_STORE, JobRecord
from backend.app.model_store import MODEL_STORE, StoredModel
from backend.worker import maintenance as m


def test_run_all_returns_seed() -> None:
    out = m.run_all()
    assert out["seed"] == 42
    assert "reaper" in out
    assert "storage" in out


def test_main_all_exit_zero() -> None:
    assert m.main(["--all"]) == 0


def test_reaper_marks_stale_memory_job() -> None:
    job_id = "00000000-0000-0000-0000-000000000099"
    stale_at = time.time() - m.STALE_SECONDS - 5
    JOB_STORE._jobs[job_id] = JobRecord(  # noqa: SLF001 — test fixture
        job_id=job_id,
        status="running",
        progress=0.1,
        created_at=stale_at,
        heartbeat_at=stale_at,
    )
    stats = m.reaper_stale_heartbeats_memory()
    assert stats["marked_failed"] >= 1
    assert JOB_STORE.get(job_id) is not None
    assert JOB_STORE.get(job_id).status == "error"  # type: ignore[union-attr]
    JOB_STORE._jobs.pop(job_id, None)  # noqa: SLF001


def test_retention_deletes_old_memory_model() -> None:
    mid = "model-retention-test"
    old = time.time() - m.PREDICTION_RETENTION_SECONDS - 1
    MODEL_STORE._models[mid] = StoredModel(  # noqa: SLF001
        id=mid,
        task="classification",
        target="y",
        dataset_id="ds1",
        feature_names=["x"],
        feature_contract={},
        pipeline=None,
        created_at=old,
    )
    stats = m.retention_expired_predictions_memory()
    assert stats["deleted"] >= 1
    assert mid not in MODEL_STORE._models  # noqa: SLF001


def test_reaper_postgres_returns_count() -> None:
    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = [("id1",), ("id2",)]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    stats = m.reaper_stale_heartbeats_postgres(mock_conn)
    assert stats == {"marked_failed": 2, "backend": "postgres"}
    mock_cur.execute.assert_called_once()
    assert mock_cur.execute.call_args.args[1] == (m.STALE_SECONDS, m.STALE_SECONDS)


@patch.object(m, "_connect_postgres", return_value=None)
def test_reaper_falls_back_to_memory(_mock_conn: MagicMock) -> None:
    stats = m.reaper_stale_heartbeats()
    assert stats["backend"] == "memory"


@pytest.mark.parametrize(
    "sql_attr",
    ["_REAPER_SQL", "_RETENTION_SQL", "_TRIM_PREDICTION_RESULTS_SQL"],
)
def test_maintenance_sql_mentions_public_tables(sql_attr: str) -> None:
    sql = getattr(m, sql_attr)
    assert "public." in sql