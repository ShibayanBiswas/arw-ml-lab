"""Hosted AI client (NVIDIA OpenAI-compatible) — ARCHITECTURE §40."""

from labcore.ai.client import AIClient, MockAIClient, get_ai_client
from labcore.ai.resilient import resilient_chat
from labcore.ai.validator import validate_insights_payload

__all__ = [
    "AIClient",
    "MockAIClient",
    "get_ai_client",
    "resilient_chat",
    "validate_insights_payload",
]
