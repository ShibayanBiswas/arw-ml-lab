"""Auth routes — GET /api/v1/auth/me (login/OTP owned by Supabase + Next.js)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.schemas import MeResponse
from backend.app.security import AuthUser, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/me", response_model=MeResponse)
def me(user: AuthUser = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        user_id=user.user_id,
        email=user.email,
        role=user.role,
        workspace_id=user.workspace_id,
    )
