"""AI Insights routes — mocked provider by default (ARCHITECTURE §40)."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from labcore.ai import get_ai_client, validate_insights_payload
from pydantic import BaseModel, Field

from backend.app.security import AuthUser, require_write_role

router = APIRouter(tags=["insights"])


class InsightsBody(BaseModel):
    stage: str = "eda"
    facts: dict[str, Any] = Field(default_factory=dict)
    prefer_mock: bool = True


@router.post("/api/v1/insights/run")
def insights_run(
    body: InsightsBody,
    user: AuthUser = Depends(require_write_role),
) -> dict[str, Any]:
    """Generate insights from FACTS via NVIDIA (or mock). Never send raw rows."""
    _ = user
    # Prompt-injection defence: FACTS only, no dataset cells
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
        client = get_ai_client(prefer_mock=body.prefer_mock)
        raw = client.chat(messages, temperature=0.0)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

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
