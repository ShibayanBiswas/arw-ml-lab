"""AI Insights routes — mocked / numbers-only by default (ARCHITECTURE §40)."""

from __future__ import annotations

import json
import os
from typing import Any

from fastapi import APIRouter, Depends
from labcore.ai import get_ai_client, validate_insights_payload
from labcore.ai.numbers_only import NumbersOnlyPolicy, resolve_insight
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["insights"])


class InsightsBody(BaseModel):
    stage: str = "eda"
    facts: dict[str, Any] = Field(default_factory=dict)
    prefer_mock: bool = True
    workspace_class: str = "internal"


@router.post("/api/v1/insights/run")
def insights_run(
    body: InsightsBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Generate insights from FACTS via NVIDIA (or numbers-only). Never send raw rows."""
    _ = user
    policy = NumbersOnlyPolicy(
        workspace_class=body.workspace_class,
        key_present=bool(os.environ.get("NVIDIA_API_KEY")),
    )
    if body.prefer_mock or policy.must_use_numbers_only():
        parsed = resolve_insight(body.facts, policy=policy, seed=42)
        validation = validate_insights_payload(parsed, facts=body.facts)
        return {
            "stage": body.stage,
            "provider": parsed.get("provider", "numbers-only"),
            "model": "numbers-only",
            "insights": parsed,
            "validation": validation,
            "seed": 42,
            "mode": parsed.get("mode"),
        }

    messages = [
        {
            "role": "system",
            "content": (
                "You are the ARW ML Lab insights assistant. "
                "Cite FACTS only. Return JSON with summary, findings, citations, apply_patch."
            ),
        },
        {
            "role": "user",
            "content": json.dumps({"stage": body.stage, "FACTS": body.facts}, default=str),
        },
    ]
    try:
        client = get_ai_client(prefer_mock=False)
        raw = client.chat(messages, temperature=0.0)
    except Exception:
        # Provider unreachable → numbers-only within the request (AC: ≤10 s)
        parsed = resolve_insight(
            body.facts,
            policy=NumbersOnlyPolicy(key_present=False),
            seed=42,
        )
        validation = validate_insights_payload(parsed, facts=body.facts)
        return {
            "stage": body.stage,
            "provider": "numbers-only",
            "model": "numbers-only",
            "insights": parsed,
            "validation": validation,
            "seed": 42,
            "mode": "numbers-only",
            "reason": "provider_error",
        }

    content = raw.get("choices", [{}])[0].get("message", {}).get("content", "{}")
    try:
        parsed = json.loads(content) if isinstance(content, str) else content
    except json.JSONDecodeError:
        parsed = {"summary": str(content), "findings": [], "citations": ["FACTS"]}

    validation = validate_insights_payload(parsed, facts=body.facts)
    return {
        "stage": body.stage,
        "provider": raw.get("provider"),
        "model": raw.get("model"),
        "insights": parsed,
        "validation": validation,
        "seed": 42,
    }
