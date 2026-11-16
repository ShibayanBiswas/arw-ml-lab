"""OpenAI-compatible client for NVIDIA API catalog (server-side key only)."""

from __future__ import annotations

import os
from typing import Any, Protocol


class AIClient(Protocol):
    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> dict[str, Any]: ...


class MockAIClient:
    """Deterministic mock for unit tests — never calls the network."""

    def __init__(self, *, seed: int = 42) -> None:
        self.seed = seed
        self.calls: list[dict[str, Any]] = []

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        self.calls.append({"messages": messages, "model": model, "temperature": temperature})
        # Numbers-only style stub citing FACTS placeholder
        content = (
            '{"summary":"Mock insight (seed 42).","findings":[],'
            '"citations":["FACTS"],"apply_patch":null}'
        )
        return {
            "id": "mock-chat",
            "model": model or "mock/nemotron",
            "choices": [{"message": {"role": "assistant", "content": content}}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            "provider": "mock",
            "seed": self.seed,
        }


class NvidiaAIClient:
    """Live NVIDIA integrate.api.nvidia.com client (key from env only)."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://integrate.api.nvidia.com/v1",
        default_model: str = "nvidia/nemotron-3-super-120b-a12b",
    ) -> None:
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY") or ""
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        if not self.api_key:
            raise RuntimeError("NVIDIA_API_KEY missing — use MockAIClient or numbers-only mode")

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        import httpx

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=60.0) as client:
            r = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            r.raise_for_status()
            data: dict[str, Any] = dict(r.json())
        data["provider"] = "nvidia"
        return data


def get_ai_client(*, prefer_mock: bool | None = None) -> AIClient:
    """Return mock unless NVIDIA_API_KEY is set (or prefer_mock=True)."""
    if prefer_mock is True:
        return MockAIClient()
    if prefer_mock is False or os.environ.get("NVIDIA_API_KEY"):
        try:
            return NvidiaAIClient()
        except RuntimeError:
            return MockAIClient()
    return MockAIClient()
