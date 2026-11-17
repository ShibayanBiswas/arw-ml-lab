"""JWT verification (Supabase JWKS) and RBAC helpers — ARCHITECTURE §39.5, §46.3 SEC-07."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt import PyJWKClient

from backend.app.settings import Settings, get_settings

Role = Literal["owner", "admin", "scientist", "analyst", "viewer"]

WRITE_ROLES: frozenset[Role] = frozenset({"owner", "admin", "scientist", "analyst"})
ADMIN_ROLES: frozenset[Role] = frozenset({"owner", "admin"})


@dataclass(frozen=True)
class AuthUser:
    user_id: str
    email: str | None
    role: Role
    workspace_id: str | None


_jwk_client: PyJWKClient | None = None


def _get_jwk_client(settings: Settings) -> PyJWKClient:
    global _jwk_client
    if _jwk_client is None:
        _jwk_client = PyJWKClient(settings.supabase_jwks_url, cache_keys=True, lifespan=3600)
    return _jwk_client


def reset_jwk_client() -> None:
    global _jwk_client
    _jwk_client = None


def decode_bearer_token(token: str, settings: Settings) -> dict[str, Any]:
    if settings.auth_mode.lower() == "bff":
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    client = _get_jwk_client(settings)
    signing_key = client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["ES256", "RS256", "HS256"],
        audience="authenticated",
        options={"verify_aud": False},
    )


def _role_from_membership(settings: Settings, user_id: str, workspace_id: str | None) -> Role:
    """Look up workspace_members.role. Falls back to viewer when DB is unavailable."""
    if not workspace_id or not settings.database_url:
        return "viewer"
    try:
        import sqlalchemy as sa

        engine = sa.create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            row = conn.execute(
                sa.text(
                    "select role from public.workspace_members "
                    "where user_id = cast(:uid as uuid) and workspace_id = cast(:ws as uuid)"
                ),
                {"uid": user_id, "ws": workspace_id},
            ).first()
        if row and row[0] in WRITE_ROLES | {"viewer"}:
            return row[0]  # type: ignore[return-value]
    except Exception:
        return "viewer"
    return "viewer"


async def get_current_user(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> AuthUser:
    # Unit-test bypass (AUTH_TEST_BYPASS=true only)
    if settings.auth_test_bypass:
        role = request.headers.get("x-test-role", "viewer")
        if role not in ("owner", "admin", "scientist", "analyst", "viewer"):
            role = "viewer"
        return AuthUser(
            user_id=request.headers.get("x-test-user-id", "00000000-0000-0000-0000-000000000099"),
            email=request.headers.get("x-test-email", "viewer@example.com"),
            role=role,  # type: ignore[arg-type]
            workspace_id=request.headers.get(
                "x-test-workspace-id", "00000000-0000-0000-0000-000000000010"
            ),
        )

    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization Bearer token required",
        )
    token = auth.split(" ", 1)[1].strip()
    try:
        claims = decode_bearer_token(token, settings)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        ) from exc

    user_id = str(claims.get("sub") or claims.get("userId") or "")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing sub")
    workspace_id = request.headers.get("x-workspace-id") or claims.get("workspaceId")
    if isinstance(workspace_id, str) and not workspace_id:
        workspace_id = None
    # BFF roster tokens carry role claim; fall back to membership / scientist
    claim_role = claims.get("role")
    bff_roles = WRITE_ROLES | {"viewer", "member", "admin"}
    if settings.auth_mode.lower() == "bff" and claim_role in bff_roles:
        mapped: Role = "scientist"
        if claim_role in ("owner", "admin", "scientist", "analyst", "viewer"):
            mapped = claim_role  # type: ignore[assignment]
        elif claim_role == "member":
            mapped = "scientist"
        return AuthUser(
            user_id=user_id,
            email=claims.get("email"),
            role=mapped,
            workspace_id=workspace_id or settings.lab_default_workspace_id,
        )
    role = _role_from_membership(settings, user_id, workspace_id)
    return AuthUser(
        user_id=user_id,
        email=claims.get("email"),
        role=role,
        workspace_id=workspace_id,
    )


def require_write_role(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if user.role not in WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{user.role}' cannot mutate resources",
        )
    return user


def require_admin_role(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if user.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{user.role}' cannot access admin audit",
        )
    return user


async def probe_jwks(settings: Settings) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(settings.supabase_jwks_url)
            return resp.status_code == 200
    except Exception:
        return False
