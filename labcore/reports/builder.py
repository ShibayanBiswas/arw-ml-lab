"""Assemble a run report dict from FACTS (no fabricated metrics)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def build_run_report(
    *,
    title: str,
    stage: str,
    facts: dict[str, Any],
    insights: dict[str, Any] | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Build a structured report payload for the Reports module / exports."""
    return {
        "title": title,
        "stage": stage,
        "created_at": datetime.now(UTC).isoformat(),
        "timezone": "Asia/Kolkata",
        "seed": seed,
        "facts": facts,
        "insights": insights,
        "sections": [
            {"id": "summary", "title": "Summary", "facts_keys": list(facts.keys())[:20]},
            {
                "id": "metrics",
                "title": "Metrics",
                "facts_keys": [k for k in facts if "metric" in k or "score" in k],
            },
            {"id": "insights", "title": "AI Insights", "present": insights is not None},
        ],
        "disclaimer": "All numbers must originate from FACTS; AI text is advisory only.",
    }
