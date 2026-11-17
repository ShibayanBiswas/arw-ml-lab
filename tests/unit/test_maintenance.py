"""lab-beat maintenance — OPS-03 reaper, OPS-07 retention, OPS-06 trim (oneshot-c101)."""

from __future__ import annotations

import time
from pathlib import Path
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
    [
        "_REAPER_SQL",
        "_RETENTION_SQL",
        "_TRIM_PREDICTION_RESULTS_SQL",
        "_EXPIRED_PREDICTION_PATHS_SQL",
    ],
)
def test_maintenance_sql_mentions_public_tables(sql_attr: str) -> None:
    sql = getattr(m, sql_attr)
    assert "public." in sql


def test_normalize_prediction_storage_key_strips_bucket() -> None:
    assert m.normalize_prediction_storage_key("predictions/ws/job/input.csv") == "ws/job/input.csv"
    assert m.normalize_prediction_storage_key("/ws/job/output.csv") == "ws/job/output.csv"
    assert m.normalize_prediction_storage_key(None) is None


def test_collect_prediction_storage_keys_dedupes() -> None:
    rows = [
        ("predictions/a/j/in.csv", "predictions/a/j/out.csv"),
        ("predictions/a/j/in.csv", None),
    ]
    keys = m.collect_prediction_storage_keys(rows)
    assert keys == ["a/j/in.csv", "a/j/out.csv"]


def test_retention_postgres_purges_storage_before_delete() -> None:
    mock_cur = MagicMock()
    mock_cur.fetchall.side_effect = [
        [("predictions/w/x/in.csv", "predictions/w/x/out.csv")],
        [("jid",)],
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    with patch.object(m, "purge_prediction_storage", return_value={"storage_removed": 2}) as purge:
        stats = m.retention_expired_predictions_postgres(mock_conn)

    assert stats["deleted"] == 1
    assert stats["storage_removed"] == 2
    purge.assert_called_once_with(["w/x/in.csv", "w/x/out.csv"])
    assert mock_cur.execute.call_count == 2


def test_purge_prediction_storage_local_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from backend.app import storage as st

    monkeypatch.setattr(st, "LOCAL_ROOT", tmp_path)
    key = "ws/pj/input.csv"
    (tmp_path / "ws" / "pj").mkdir(parents=True)
    (tmp_path / key).write_bytes(b"x")
    stats = m.purge_prediction_storage([key])
    assert stats["storage_removed"] == 1
    assert not (tmp_path / key).exists()