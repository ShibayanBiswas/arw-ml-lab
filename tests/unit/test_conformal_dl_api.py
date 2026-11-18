"""Conformal DL smoke API — oneshot-c270."""

from __future__ import annotations

from backend.app.routers.deep import conformal_dl_smoke
from backend.app.security import AuthUser


def test_conformal_dl_smoke_route() -> None:
    user = AuthUser(
        user_id="00000000-0000-0000-0000-000000000099",
        email=None,
        role="scientist",
        workspace_id="00000000-0000-0000-0000-000000000010",
    )
    from backend.app.routers.deep import ConformalDlSmokeBody

    body = conformal_dl_smoke(ConformalDlSmokeBody(seed=42, n=40), user=user)
    assert body["id"] == "UQ.CONFORMAL.DL"
    assert body["refit"] is False
    assert len(body["pred_lower"]) == 8
