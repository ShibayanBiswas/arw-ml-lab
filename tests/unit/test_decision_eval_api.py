"""Decision eval-harness API route — oneshot-c267."""

from __future__ import annotations

from backend.app.routers.decisions import decision_eval_harness
from backend.app.security import AuthUser


def test_decision_eval_harness_route() -> None:
    user = AuthUser(
        user_id="00000000-0000-0000-0000-000000000099",
        email=None,
        role="scientist",
        workspace_id="00000000-0000-0000-0000-000000000010",
    )
    body = decision_eval_harness(user=user)
    assert body["ok"] is True
    assert body["id"] == "DEC.EVAL.HARNESS"
    assert body["n_pass"] == body["n_cases"]
