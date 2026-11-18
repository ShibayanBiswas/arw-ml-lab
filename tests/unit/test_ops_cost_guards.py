"""OPS.COST.GUARDS — Contabo concurrency / quota policy (oneshot-c281)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from labcore.ops.cost_guards import (
    ARTEFACT_ID,
    CostGuardLimits,
    CostGuardUsage,
    evaluate_cost_guards,
    guard_enqueue,
)

ROOT = Path(__file__).resolve().parents[2]


def test_allows_under_limits() -> None:
    out = evaluate_cost_guards(CostGuardUsage(), CostGuardLimits(seed=42))
    assert out["allowed"] is True
    assert out["breaches"] == []
    assert out["id"] == ARTEFACT_ID
    assert out["seed"] == 42


def test_refuses_second_heavy_job() -> None:
    out = guard_enqueue(concurrent_jobs=1, concurrent_heavy=1, heavy=True)
    assert out["allowed"] is False
    assert "max_concurrent_heavy" in out["breaches"]


def test_admin_quotas_route() -> None:
    from backend.app.main import create_app
    from backend.app.security import AuthUser, require_admin_role

    app = create_app()
    app.dependency_overrides[require_admin_role] = lambda: AuthUser(
        user_id="admin",
        email="admin@example.com",
        role="admin",
        workspace_id="00000000-0000-0000-0000-000000000001",
    )
    client = TestClient(app)
    res = client.get("/api/v1/admin/quotas")
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == ARTEFACT_ID
    assert body["allowed"] is True
    assert "limits" in body


def test_fe_quotas_artefact() -> None:
    src = (ROOT / "frontend/src/components/admin/AdminWorkbench.tsx").read_text(encoding="utf-8")
    assert "OPS.COST.GUARDS" in src
    assert "/api/v1/admin/quotas" in src
