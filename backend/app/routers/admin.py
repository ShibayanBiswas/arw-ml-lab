"""Admin / enterprise API (ARCHITECTURE §25) — audit log (SEC-11)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from labcore.enterprise.audit import audit_rows_to_csv, demo_audit_rows, normalize_audit_row

from backend.app.security import ADMIN_ROLES, AuthUser, require_admin_role
from backend.app.settings import Settings, get_settings

router = APIRouter(tags=["admin"])


def _fetch_audit_rows(
    settings: Settings,
    workspace_id: str,
    *,
    limit: int,
    offset: int,
) -> list[dict[str, Any]] | None:
    if not settings.database_url:
        return None
    try:
        import sqlalchemy as sa

        engine = sa.create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(
                sa.text(
                    "select id, workspace_id, user_id, action, entity, entity_id, detail, created_at "
                    "from public.audit_log "
                    "where workspace_id = cast(:ws as uuid) "
                    "order by created_at desc "
                    "limit :lim offset :off"
                ),
                {"ws": workspace_id, "lim": limit, "off": offset},
            )
            rows = [normalize_audit_row(dict(m)) for m in result.mappings()]
        return rows
    except Exception:
        return None


@router.get("/api/v1/admin/audit")
def admin_audit_list(
    user: AuthUser = Depends(require_admin_role),
    settings: Settings = Depends(get_settings),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    source: str = Query(default="auto"),
) -> dict[str, Any]:
    ws = user.workspace_id or settings.lab_default_workspace_id
    rows = _fetch_audit_rows(settings, ws, limit=limit, offset=offset)
    data_source = "postgres"
    if not rows:
        data_source = "demo"
        rows = demo_audit_rows(ws, seed=settings.lab_default_seed, count=limit)[offset : offset + limit]
    return {
        "id": "ENT.T.AUDIT_LOG",
        "seed": settings.lab_default_seed,
        "source": source if source != "auto" else data_source,
        "roles_required": sorted(ADMIN_ROLES),
        "limit": limit,
        "offset": offset,
        "count": len(rows),
        "rows": rows,
    }


@router.get("/api/v1/admin/quotas")
def admin_quotas(
    user: AuthUser = Depends(require_admin_role),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Workspace cost-guard limits + current usage snapshot (OPS-08)."""
    from labcore.ops.cost_guards import CostGuardLimits, CostGuardUsage, evaluate_cost_guards

    # Offline / Contabo: usage counters are best-effort zeros until hosted metering wires
    usage = CostGuardUsage()
    limits = CostGuardLimits(seed=settings.lab_default_seed)
    snap = evaluate_cost_guards(usage, limits)
    snap["workspace_id"] = user.workspace_id or settings.lab_default_workspace_id
    snap["note"] = "Usage meters fill from jobs/ai_usage on Contabo; limits are Contabo CPU defaults"
    return snap


@router.get("/api/v1/admin/workers")
def admin_workers(
    user: AuthUser = Depends(require_admin_role),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Workers & queue depths (OPS-12) — Celery inspect when broker is up."""
    _ = user
    from labcore.ops.queue_stats import collect_queue_stats

    def _inspect() -> Any:
        from backend.worker.celery_app import celery_app

        return celery_app.control.inspect(timeout=1.0)

    snap = collect_queue_stats(
        inspect_factory=_inspect,
        seed=settings.lab_default_seed,
    )
    snap["lab_gpu_worker"] = False  # Contabo CPU-only default
    snap["service_role"] = settings.service_role
    return snap


@router.get("/api/v1/admin/audit/export")
def admin_audit_export(
    user: AuthUser = Depends(require_admin_role),
    settings: Settings = Depends(get_settings),
    limit: int = Query(default=500, ge=1, le=5000),
) -> PlainTextResponse:
    ws = user.workspace_id or settings.lab_default_workspace_id
    rows = _fetch_audit_rows(settings, ws, limit=limit, offset=0)
    if not rows:
        rows = demo_audit_rows(ws, seed=settings.lab_default_seed, count=limit)
    csv_text = audit_rows_to_csv(rows)
    return PlainTextResponse(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="audit_log_export.csv"',
            "X-Artefact-Id": "ENT.T.AUDIT_EXPORT",
        },
    )