"""Celery OPS-03 heartbeat — oneshot-c108."""

from __future__ import annotations

import time
import uuid
from unittest.mock import MagicMock, patch

from backend.app.jobs_store import JOB_STORE, JobRecord
from backend.worker import heartbeat as hb


def test_heartbeat_interval_ops03() -> None:
    assert hb.HEARTBEAT_INTERVAL_S == 30
    assert hb.HEARTBEAT_SEED == 42


def test_touch_memory_store() -> None:
    job_id = str(uuid.uuid4())
    old = time.time() - 60
    JOB_STORE._jobs[job_id] = JobRecord(job_id=job_id, status="running", heartbeat_at=old)  # noqa: SLF001
    out = hb.touch_job_heartbeat(job_id)
    assert out["backend"] == "memory"
    rec = JOB_STORE.get(job_id)
    assert rec is not None
    assert rec.heartbeat_at is not None
    assert rec.heartbeat_at > old
    JOB_STORE._jobs.pop(job_id, None)  # noqa: SLF001


def test_touch_postgres_sql() -> None:
    job_id = str(uuid.uuid4())
    mock_cur = MagicMock()
    mock_cur.rowcount = 1
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    with patch("backend.worker.maintenance._connect_postgres", return_value=mock_conn):
        out = hb.touch_job_heartbeat(job_id)
    assert out["backend"] == "postgres"
    assert out["postgres_row"] is True
    mock_cur.execute.assert_called_once()
    assert "heartbeat_at" in hb._TOUCH_SQL
    assert mock_cur.execute.call_args.args[1] == (job_id,)
    mock_conn.close.assert_called_once()


def test_parse_job_id_from_args_and_kwargs() -> None:
    jid = str(uuid.uuid4())
    assert hb._parse_job_id((jid, "x"), {}) == jid
    assert hb._parse_job_id((), {"job_id": jid}) == jid
    assert hb._parse_job_id(("not-a-uuid",), {}) is None


def test_task_prerun_starts_loop_and_postrun_stops() -> None:
    job_id = str(uuid.uuid4())
    JOB_STORE._jobs[job_id] = JobRecord(job_id=job_id, status="running")  # noqa: SLF001
    with patch.object(hb, "HEARTBEAT_INTERVAL_S", 0.05):
        hb._on_task_prerun(args=(job_id,), kwargs={})
        time.sleep(0.12)
        hb._on_task_postrun(args=(job_id,), kwargs={})
    rec = JOB_STORE.get(job_id)
    assert rec is not None
    assert rec.heartbeat_at is not None
    JOB_STORE._jobs.pop(job_id, None)  # noqa: SLF001