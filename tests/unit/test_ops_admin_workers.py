"""OPS.ADMIN.WORKERS — admin queue panel (oneshot-c276)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from labcore.ops.queue_stats import (
    ARTEFACT_ID,
    KNOWN_QUEUES,
    collect_queue_stats,
    summarize_inspect,
)

ROOT = Path(__file__).resolve().parents[2]


def test_summarize_inspect_counts_queues() -> None:
    snap = summarize_inspect(
        active={
            "w1": [
                {"delivery_info": {"routing_key": "q.train.cpu"}},
                {"delivery_info": {"routing_key": "q.eda"}},
            ]
        },
        reserved={"w1": [{"delivery_info": {"routing_key": "q.train.cpu"}}]},
        stats={"w1": {"pool": {"max-concurrency": 1}}},
        seed=42,
    )
    assert snap["id"] == ARTEFACT_ID
    assert snap["seed"] == 42
    assert snap["queues"]["q.train.cpu"] == 2
    assert snap["queues"]["q.eda"] == 1
    assert snap["n_workers"] == 1
    assert set(KNOWN_QUEUES).issubset(snap["queues"].keys())


def test_collect_offline_empty() -> None:
    snap = collect_queue_stats(seed=42)
    assert snap["broker_reachable"] is False
    assert snap["n_workers"] == 0


def test_admin_workers_route() -> None:
    from backend.app.main import create_app
    from backend.app.security import AuthUser

    app = create_app()
    app.dependency_overrides = getattr(app, "dependency_overrides", {})
    from backend.app.security import require_admin_role

    app.dependency_overrides[require_admin_role] = lambda: AuthUser(
        user_id="admin",
        email="admin@example.com",
        role="admin",
        workspace_id="00000000-0000-0000-0000-000000000001",
    )
    client = TestClient(app)
    res = client.get("/api/v1/admin/workers")
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == ARTEFACT_ID
    assert "queues" in body
    assert "q.predict.batch" in body["queues"]


def test_fe_admin_workers_artefact() -> None:
    src = (
        ROOT / "frontend/src/components/admin/AdminWorkbench.tsx"
    ).read_text(encoding="utf-8")
    assert "OPS.ADMIN.WORKERS" in src
    assert "/api/v1/admin/workers" in src
