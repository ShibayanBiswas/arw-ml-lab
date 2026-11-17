"""Resilient AI chat with circuit → numbers-only — oneshot-c240 (§39.13 AC)."""

from __future__ import annotations

from typing import Any

from labcore.ai.client import AIClient, get_ai_client
from labcore.ai.numbers_only import (
    FALLBACK_LABEL,
    CircuitBreaker,
    NumbersOnlyPolicy,
    numbers_only_insight,
    resolve_insight,
)

ARTEFACT_ID = "AI.RESILIENT.CHAT"

_GLOBAL_BREAKER = CircuitBreaker()


def global_circuit() -> CircuitBreaker:
    return _GLOBAL_BREAKER


def resilient_chat(
    messages: list[dict[str, str]],
    *,
    facts: dict[str, Any] | None = None,
    client: AIClient | None = None,
    circuit: CircuitBreaker | None = None,
    key_present: bool | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Call the AI client; on timeout/error or open circuit, return numbers-only insight."""
    br = circuit or _GLOBAL_BREAKER
    facts = facts or {}
    import os

    present = bool(os.environ.get("NVIDIA_API_KEY")) if key_present is None else key_present
    policy = NumbersOnlyPolicy(key_present=present, circuit=br)
    if policy.must_use_numbers_only():
        out = resolve_insight(facts, policy=policy, seed=seed)
        out["artefact"] = ARTEFACT_ID
        return out

    ai = client or get_ai_client()
    try:
        raw = ai.chat(messages)
        br.record_success()
        return {"mode": "provider", "artefact": ARTEFACT_ID, "raw": raw, "seed": seed}
    except Exception as exc:  # noqa: BLE001 — fall back within 10s budget
        br.record_failure()
        out = numbers_only_insight(facts, seed=seed)
        out["mode"] = FALLBACK_LABEL
        out["reason"] = type(exc).__name__
        out["artefact"] = ARTEFACT_ID
        return out
