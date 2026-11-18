"""VLM decision baselines — numbers-only when provider off (§38)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from labcore.decisions.baseline import rule_baseline_proposal
from labcore.decisions.guards import apply_deterministic_guards
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["decisions"])


class DecisionBody(BaseModel):
    decision_point: str = "VD1"
    facts: dict[str, Any] = Field(default_factory=dict)
    proposal: dict[str, Any] | None = None
    numbers_only: bool = True


@router.post("/api/v1/decisions/propose")
def propose_decision(
    body: DecisionBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Return a guarded proposal; default path is numbers-only baseline."""
    _ = user
    if body.numbers_only or body.proposal is None:
        return rule_baseline_proposal(
            decision_point=body.decision_point,
            facts=body.facts,
            seed=42,
        )
    guarded = apply_deterministic_guards(body.proposal, facts=body.facts)
    return {
        "decision_point": body.decision_point,
        "mode": "vlm",
        "proposal": body.proposal,
        "guards": guarded,
        "seed": 42,
    }


@router.get("/api/v1/decisions/eval-harness")
def decision_eval_harness(
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Offline Phase 6A guard suite (seed 42); never calls a live VLM."""
    _ = user
    from labcore.decisions.eval_harness import run_decision_eval_harness

    return run_decision_eval_harness(seed=42)
